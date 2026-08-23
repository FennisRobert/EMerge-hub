# =============================================================================
# microstrip_taper_utils.py
#
# Copyright (C) 2026 Andrés Martínez Mera
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
# =============================================================================

"""
Helper functions for designing impedance-matching microstrip tapers:

    - Exponential taper  [1] Sec 5.8 (page 262)
    - Triangular taper   [2] Sec 5.8 (page 263)
    - Klopfenstein taper [3] Sec 5.8 (page 264)


References
----------
[1] D. M. Pozar, "Microwave Engineering," 4th ed., Wiley, 2012
"""

import numpy as np
from scipy.special import iv
from scipy.integrate import quad


# ---------------------------------------------------------------------------
# Microstrip synthesis: Z0, er  ->  W/h  (Pozar closed-form synthesis)
# ---------------------------------------------------------------------------
def microstrip_width(Z0, er, h):
    """
    Closed-form synthesis of microstrip trace width for a target
    characteristic impedance Z0 given a subtrate.
    See [1] page 148. Eq. 3.197
    """
    A = Z0 / 60.0 * np.sqrt((er + 1) / 2.0) + (er - 1) / (er + 1) * (0.23 + 0.11 / er)
    W_h = 8 * np.exp(A) / (np.exp(2 * A) - 2)

    if W_h <= 2.0:
        W_h = W_h
    else:
        B = 377 * np.pi / (2 * Z0 * np.sqrt(er))
        W_h = (2 / np.pi) * (
            B - 1 - np.log(2 * B - 1)
            + (er - 1) / (2 * er) * (np.log(B - 1) + 0.39 - 0.61 / er)
        )

    return W_h * h # = W


def microstrip_width_array(Z0_array, er, h):
    """Vectorised version of microstrip_width()."""
    return np.array([microstrip_width(Z0, er, h) for Z0 in np.atleast_1d(Z0_array)])


# ---------------------------------------------------------------------------
# Taper impedance profiles Z(z), 0 <= z <= L
# ---------------------------------------------------------------------------
def z_exponential(z, L, Z1, Z2):
    # [1] Eq. 5.68
    z = np.clip(z, 0, L)
    a = (1 / L) * np.log(Z2 / Z1) # 5.69
    return Z1 * np.exp(a*z)


def z_triangular(z, L, Z1, Z2):
    """
    [1] Eq. 5.71

        Z(z) = Z0 * exp[2(z/L)^2 * ln(ZL/Z0)]              for 0 <= z <= L/2
        Z(z) = Z0 * exp[(4z/L - 2z^2/L^2 - 1) * ln(ZL/Z0)] for L/2 <= z <= L
    """
    z = np.clip(z, 0, L)
    lnR = np.log(Z2 / Z1)

    Z = np.empty_like(np.atleast_1d(z), dtype=float)
    z = np.atleast_1d(z)

    first_half = z <= L / 2
    second_half = ~first_half

    Z[first_half] = Z1 * np.exp(2.0 * (z[first_half] / L) ** 2 * lnR)
    Z[second_half] = Z1 * np.exp(
        (4.0 * z[second_half] / L - 2.0 * z[second_half] ** 2 / L ** 2 - 1.0) * lnR
    )

    return Z

def z_linear(z, L, Z1, Z2):
    # Straight line between Z1 and Z2
    z = np.clip(z, 0, L)
    return Z1 + z * (Z2 - Z1) / L


def _klopfenstein_phi(x, A):
    #phi(x, A) as defined in [1] Eq. 5.74

    if x == 0:
        return 0.0

    def integrand(y):
        arg = A * np.sqrt(max(1.0 - y**2, 0.0))
        if arg < 1e-9:
            return 0.5  # lim_{t->0} I1(t)/t = 0.5
        return iv(1, arg) / arg

    val, _ = quad(integrand, 0.0, x, limit=200)
    return val


def z_klopfenstein(z, L, Z1, Z2, gamma_max=0.02):
    # See [1] page 264
    z = np.atleast_1d(np.clip(z, 0, L)).astype(float)
    gamma0 = 0.5 * np.log(Z2 / Z1)          # Eq. 5.77
    A = np.arccosh(abs(gamma0) / gamma_max) # Eq. 5.78

    Zout = np.empty_like(z)
    for i, zi in enumerate(z):
        if zi <= 1e-12:
            Zout[i] = Z1
        elif zi >= L - 1e-12:
            Zout[i] = Z2
        else:
            x = 2 * zi / L - 1
            phi = _klopfenstein_phi(x, A) # Eq. 5.75
            lnZ = 0.5 * np.log(Z1 * Z2) + (gamma0 / np.cosh(A)) * A * A * phi # Eq. 5.74
            Zout[i] = np.exp(lnZ)
    return Zout


# ---------------------------------------------------------------------------
# Convenience: build a Z(z), W(z) pair for a chosen taper type
# ---------------------------------------------------------------------------
def taper_width_profile(taper_type, z, L, Z1, Z2, er, h, gamma_max=0.02):
    taper_type = taper_type.lower()
    if taper_type == "exponential":
        Z = z_exponential(z, L, Z1, Z2)
    elif taper_type == "triangular":
        Z = z_triangular(z, L, Z1, Z2)
    elif taper_type == "linear":
        Z = z_linear(z, L, Z1, Z2)
    elif taper_type == "klopfenstein":
        Z = z_klopfenstein(z, L, Z1, Z2, gamma_max=gamma_max)
    else:
        raise ValueError(
            f"Unknown taper_type '{taper_type}'. "
            "Choose 'exponential', 'triangular', 'linear' or 'klopfenstein'."
        )
    W = microstrip_width_array(Z, er, h)
    return Z, W
