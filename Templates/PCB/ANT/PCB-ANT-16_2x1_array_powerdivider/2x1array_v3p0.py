# =============================================================================
# EMerge Simulation Template: PCB-ANT-04
#
# Copyright (C) 2026 Robert Fennis
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
#
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# 2x1 Patch Antenna Array with a Quarter-Wave T-Junction Power Divider
#
# This demo builds a broadside two-element microstrip patch array on a single
# feed port. A single 50-ohm input line splits at a T-junction into two
# branches. Each branch is a quarter-wave impedance transformer that matches
# the (high) edge impedance of a patch element back down to 100 ohm, so that
# the two 100-ohm branches combine in parallel to a clean 50 ohm at the
# T-junction - a classic "corporate feed" network.
#
#            patch_L                         patch_R
#           +--------+                      +--------+
#           |        |----Lq (Zt)   Lq (Zt)----|      |
#           |        |         \   /            |      |
#           +--------+          \ /              +--------+
#                                 T  <- junction (0,0)
#                                 |
#                                 | 50 ohm trunk (w_in)
#                                 |
#                               (port 1)
#
# The patch dimensions are derived from the classic transmission-line model,
# and the edge impedance is estimated with Balanis' approximate formula. This
# gives a physically-motivated starting geometry - real designs are typically
# refined further with a few iterations in EMerge (or an inset feed) to
# fine-tune the match.
#
# Similar in scale to the single-patch demo (demo4_patch_antenna.py); expect a
# runtime of a few minutes and several GB of RAM depending on mesh settings.
# -----------------------------------------------------------------------------

import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar

############################################################
#                     UNITS & CONSTANTS                     #
############################################################

mm = 0.001               # meters per millimeter
c0 = 299792458.0         # speed of light in vacuum (m/s)

############################################################
#             SUBSTRATE / FREQUENCY PARAMETERS              #
############################################################

er = 3.38                # relative permittivity (RO4003C-like)
tand = 0.0027             # loss tangent (informational)
th = 1.524 * mm           # substrate thickness

f0 = 2.45e9               # design / center frequency (ISM band)
f1, f2 = 2.30e9, 2.60e9   # sweep band
n_points = 21

lambda0 = c0 / f0          # free-space wavelength at f0

############################################################
#      STEP 1: PATCH DIMENSIONS (TRANSMISSION-LINE MODEL)   #
############################################################

# Patch width for good radiation efficiency
W_patch = c0 / (2 * f0) * np.sqrt(2 / (er + 1))

# Effective dielectric constant seen by the patch
eps_eff_patch = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * th / W_patch) ** -0.5

# Fringing-field length extension (each open end)
dL = (
    0.412 * th * (eps_eff_patch + 0.3) * (W_patch / th + 0.264)
    / ((eps_eff_patch - 0.258) * (W_patch / th + 0.8))
)

# Physical patch length, corrected for fringing
L_eff = c0 / (2 * f0 * np.sqrt(eps_eff_patch))
L_patch = L_eff - 2 * dL

# Approximate radiating-edge resistance (Balanis' single-slot approximation)
R_edge = 90 * (er ** 2 / (er - 1)) * (L_patch / W_patch) ** 2

print(f"Patch size:        {W_patch / mm:.2f} mm (W) x {L_patch / mm:.2f} mm (L)")
print(f"Edge impedance:     {R_edge:.1f} ohm (approx.)")

############################################################
#   STEP 2: FEED-LINE WIDTHS & QUARTER-WAVE TRANSFORMER      #
############################################################


def microstrip_eps_eff(w: float, h: float, er: float) -> float:
    """Effective permittivity of a microstrip line (Hammerstad-Jensen approx)."""
    ratio = w / h
    if ratio >= 1:
        return (er + 1) / 2 + (er - 1) / 2 * (1 + 12 / ratio) ** -0.5
    return (er + 1) / 2 + (er - 1) / 2 * (
        (1 + 12 / ratio) ** -0.5 + 0.04 * (1 - ratio) ** 2
    )


# We use the PCB layouter purely for its microstrip impedance calculator here;
# the actual trace geometry is routed with it further below.
pcb = em.geo.PCB(th, unit=1.0, material=em.lib.DIEL_RO4003C)

Z_in = 50.0                       # main input line impedance
Z_branch = 100.0                  # impedance each branch must present at the T
Z_t = np.sqrt(Z_branch * R_edge)  # quarter-wave transformer impedance

w_in = pcb.calc.z0(Z_in)   # 50 ohm trunk line width
w_t = pcb.calc.z0(Z_t)     # transformer line width

eps_eff_t = microstrip_eps_eff(w_t, th, er)
lambda_g_t = lambda0 / np.sqrt(eps_eff_t)
Lq = lambda_g_t / 4        # physical quarter-wave transformer length

center_spacing = L_patch + 2 * Lq  # element-to-element (center) spacing

print(f"Transformer:        Zt = {Z_t:.1f} ohm, width = {w_t / mm:.2f} mm, length = {Lq / mm:.2f} mm")
print(f"Element spacing:    {center_spacing / mm:.2f} mm ({center_spacing / lambda0:.2f} * lambda0)")
############################################################
#                      SIMULATION SETUP                     #
############################################################

model = em.Simulation("PatchArray2x1")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                    FEED NETWORK ROUTING                   #
############################################################

L_in = 20 * mm  # trunk length from the input connector to the T-junction

# Trunk: 50 ohm line running from the input port up to the T-junction at (0,0)
pcb.new(0, -L_in, w_in, (0, 1)).store("pin").straight(L_in)

# Left / right branches: quarter-wave transformers out to each patch
pcb.new(0, 0, w_t, (-1, 0)).straight(Lq)
pcb.new(0, 0, w_t, (1, 0)).straight(Lq)

# All three segments touch at the origin, so merging gives one T-shaped trace
traces = pcb.compile_paths(merge=True)

############################################################
#                    PATCH RADIATOR ELEMENTS                #
############################################################

# Patches are oriented with their resonant (feed) axis along X and their
# radiating edges along Y, so each transformer branch feeds straight into
# the inner edge of its patch without needing any bends.
patch_L = em.geo.XYPlate(L_patch, W_patch, position=(-Lq - L_patch, -W_patch / 2, 0))
patch_R = em.geo.XYPlate(L_patch, W_patch, position=(Lq, -W_patch / 2, 0))

copper = em.geo.unite(traces, patch_L)
copper = em.geo.unite(copper, patch_R)
copper.set_material(em.lib.PEC)

############################################################
#                   PORT + PCB / AIR VOLUMES                 #
############################################################

# Lumped port at the open (bottom) end of the input trunk
pin_port = pcb.lumped_port(pcb.load("pin"), 1)

# Extend the board bounds so it fully covers both patches, not just the trace
pcb.determine_bounds(
    leftmargin=L_patch + 10 * mm,
    rightmargin=L_patch + 10 * mm,
    topmargin=W_patch / 2 + 10 * mm,
    bottommargin=W_patch / 2 + 10 * mm,
)

ground = pcb.plane(pcb.z(0))   # full ground plane on the bottom copper layer
diel = pcb.generate_pcb()       # substrate dielectric block

# Open radiation boundary enclosing the whole board with room to spare
air_margin = 0.5 * lambda0
air = em.geo.open_region(air_margin, air_margin, air_margin)

############################################################
#                      COMMIT GEOMETRY                       #
############################################################

model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                  #
############################################################

model.mw.set_frequency_range(f1, f2, n_points)
model.mw.set_resolution(0.15)

model.mesher.set_boundary_size(copper, 0.5 * mm)
model.mesher.set_face_size(pin_port, 0.3 * mm)

############################################################
#                    GENERATE & VIEW MESH                    #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                     #
############################################################

port1 = model.mw.bc.LumpedPort(pin_port, 1)
abc = model.mw.bc.AbsorbingBoundary(air.boundary())

model.view(bc=True)

############################################################
#                       RUN SIMULATION                       #
############################################################

data = model.mw.run_sweep()

############################################################
#                  POST-PROCESSING: S-PARAMETERS              #
############################################################

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
plot_sp(f, [S11], labels=["S11"], dblim=[-30, 3])
smith(S11, f=f)

# Supersample with Vector Fitting for a smoother curve
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
plot_sp(fdense, [S11_fit], labels=["S11"])

############################################################
#              POST-PROCESSING: FAR-FIELD PATTERNS            #
############################################################

field = data.field.find(freq=f0)

# E-plane (along the patch length / feed axis) and H-plane (along the array axis)
ff_E = field.farfield_2d(em.YAX, em.ZAX, air.boundary())
ff_H = field.farfield_2d(em.XAX, em.ZAX, air.boundary())

plot_ff(
    ff_E.ang * 180 / np.pi,
    [ff_E.gain.norm, ff_H.gain.norm],
    labels=["E-plane", "H-plane"],
    dB=True,
    ylabel="Gain [dBi]",
)
plot_ff_polar(ff_E.ang, ff_E.gain.norm, dB=True, dBfloor=-20)

############################################################
#                    3D FIELD VISUALIZATION                   #
############################################################

model.display.populate()

ff3d = field.farfield_3d(air.boundary())
model.display.add_farfield3d(
    ff3d, "gain.norm", "abs", dB=True, dBfloor=-20, rmax=0.5 * center_spacing, opacity=0.5
)

# Horizontal cut a few mm above the array shows the interference pattern
# between the two elements - the whole point of building an array!
model.display.animate().add_field(
    field.cutplane(1 * mm, z=5 * mm).scalar("Ey", "complex"), symmetrize=True
)
model.display.add_portmode(port1, k0=field.k0)
model.display.show()