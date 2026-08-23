# =============================================================================
# EMerge Simulation Template: Microstrip tapered lines
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

# -----------------------------------------------------------------------------
# Microstrip Impedance Taper (50 to 15 Ohm)
#
# Compares different ways of gradually widening a transmission line to
# transform its impedance from 50 to 15 ohm, instead of stepping it in one
# abrupt jump. Four taper shapes are precomputed and selectable: exponential,
# triangular, linear, and Klopfenstein (the smoothest, lowest-ripple option
# from classic microwave filter theory). Built on a 0.508 mm RO4003C
# substrate, centered at 1.5 GHz and swept from 100 MHz to 5 GHz.
# -----------------------------------------------------------------------------
from emerge_config import config

config.set_acc_threads(4)

import emerge as em
from emerge.plot import plot_sp
import numpy as np

# ---------------------------------------------------------------------------
# TAPER SELECTION
# ---------------------------------------------------------------------------
"""
    Set TAPER_TYPE variable according to the desired impedance profile:
        - exponential
        - triangular
        - klopfenstein
        - linear
        - all: Simulate all profiles on a row
    See [1], section 5.8 for reference.
    [1] D. M. Pozar, "Microwave Engineering," 4th ed., Wiley, 2012
"""
# The following profiles can be automatically generated with python scripts.
# Check the /advanced/ directory for the full scripts!

w_profiles = {
    "exponential": [1.155,1.192,1.230,1.269,1.309,1.350,1.392,1.435,1.478,1.523,1.568,1.615,1.663,1.711,1.761,1.812,1.864,1.917,1.971,2.027,2.083,2.141,2.201,2.261,2.323,2.386,2.451,2.516,2.584,2.652,2.723,2.794,2.868,2.943,3.019,3.097,3.177,3.259,3.342,3.427,3.514,3.602,3.693,3.785,3.880,3.976,4.075,4.175,4.278,4.383,4.490,4.599,4.711,4.824,4.941,5.060,5.181,5.305,5.431,5.560],
    "triangular": [1.137,1.139,1.144,1.151,1.161,1.174,1.189,1.206,1.227,1.250,1.276,1.306,1.338,1.374,1.413,1.457,1.504,1.555,1.611,1.671,1.736,1.807,1.884,1.966,2.055,2.152,2.255,2.367,2.488,2.618,2.758,2.899,3.042,3.184,3.327,3.469,3.610,3.750,3.888,4.024,4.157,4.287,4.414,4.536,4.654,4.766,4.874,4.975,5.071,5.159,5.241,5.316,5.383,5.443,5.494,5.537,5.572,5.598,5.616,5.625],
    "klopfenstein": [1.339,1.362,1.385,1.410,1.437,1.465,1.494,1.525,1.558,1.592,1.628,1.665,1.705,1.746,1.788,1.833,1.880,1.928,1.978,2.030,2.084,2.140,2.198,2.257,2.319,2.382,2.447,2.513,2.582,2.652,2.723,2.797,2.871,2.947,3.024,3.103,3.182,3.263,3.344,3.426,3.508,3.591,3.674,3.757,3.841,3.924,4.006,4.088,4.169,4.250,4.329,4.407,4.484,4.560,4.633,4.705,4.775,4.842,4.908,4.971],
    "linear": [1.147,1.169,1.191,1.214,1.238,1.262,1.286,1.312,1.338,1.365,1.392,1.421,1.450,1.480,1.511,1.543,1.576,1.609,1.644,1.680,1.717,1.756,1.795,1.836,1.878,1.922,1.968,2.015,2.063,2.114,2.166,2.220,2.277,2.335,2.397,2.460,2.526,2.596,2.668,2.743,2.822,2.904,2.991,3.081,3.176,3.276,3.381,3.492,3.609,3.733,3.864,4.002,4.149,4.306,4.472,4.650,4.841,5.045,5.264,5.501]
}

TAPER_TYPE = "triangular"

############################################################
#                     UNITS & CONSTANTS                    #
############################################################

# EMerge works in SI units internally, so it's convenient to define a few
# unit helpers at the top of the script.
mm = 0.001      # meters per millimeter
mil = 0.0254 * mm
inch = 25.4 * mm

MHz = 1e6
GHz = 1e9

C0 = 299792458
Z0 = 376.73031366857
PI = np.pi
EPS0 = 8.854187818814e-12
MU0 = 1/(C0*C0*EPS0)

############################################################
#                    DESIGN PARAMETERS                     #
############################################################
f0 = 1500 * MHz        # [Hz] Center frequency
lambda_ = C0/ (np.sqrt(3.55)*f0)
Z1 = 50.0              # [Ohm] source impedance
Z2 = 15.0              # [Ohm] load impedance (matches the Chebyshev example)

th   = 0.508           # [mm] substrate thickness
Lfeed  = 5             # [mm] straight Z1 / Z2 feed lines at each end
Ltaper = 1e3*lambda_   # [mm] taper length
N_seg  = 60            # number of straight segments approximating the taper

Hair = 5              # [mm] air box height

############################################################
#                     FREQUENCY SWEEP                      #
############################################################

f_start = 100 * MHz
f_stop  = 5000 * MHz
n_points = 40

# ---------------------------------------------------------------------------
# Build the impedance / width profile for the chosen taper
# ---------------------------------------------------------------------------
z_mid = (np.arange(N_seg) + 0.5) * (Ltaper / N_seg)   # midpoint of each segment [mm]
W_profile = w_profiles[TAPER_TYPE]

# Widths for the clean uniform feed lines at each end
W_feed_in  = 1.136
W_feed_out = 5.625

dz = Ltaper / N_seg

############################################################
#                      SIMULATION SETUP                    #
############################################################

model = em.Simulation("taper")
model.check_version("2.8.6")

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCBNew(th, unit=mm, material=em.lib.DIEL_RO4003C, trace_material=em.lib.PEC)

# ---------------------------------------------------------------------------
# Layout: feed(Z1) -> N_seg tapered segments -> feed(Z2)
# ---------------------------------------------------------------------------
pcb_margin = 25  # Space at both sides of the copper traces

path = pcb.new(0, 0, W_feed_in, (1, 0), z=pcb.z(1))[1].straight(Lfeed, W_feed_in)

for w in W_profile:
    path = path.taper(dz, w)

path = path.straight(Lfeed, W_feed_out)[2]

# --- Compile traces ------------------------------------------------------
stripline = pcb.compile_paths(True)

# ---------------------------------------------------------------------------
# Bounding box, dielectric and air
# ---------------------------------------------------------------------------
pcb.determine_bounds(topmargin=pcb_margin, bottommargin=pcb_margin, leftmargin=0, rightmargin=0)
diel = pcb.generate_pcb(merge=True)
air  = pcb.generate_air(Hair)

# ---------------------------------------------------------------------------
# Modal ports
# ---------------------------------------------------------------------------
p1 = pcb.modal_port(1, height=Hair, width=15) # Input
p2 = pcb.modal_port(2, height=Hair, width=15) # Output

############################################################
#                   SOLVER / MESH SETTINGS                 #
############################################################
model.mw.set_resolution(0.2)
model.mw.set_frequency_range(f_start, f_stop, n_points)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################
model.commit_geometry()

############################################################
#               GENERATE, REFINE & VIEW MESH               #
############################################################
model.mesher.set_boundary_size(stripline, 0.5 * mm, growth_rate=10)

model.generate_mesh()

model.view()

############################################################
#                   BOUNDARY CONDITIONS                    #
############################################################
port1 = model.mw.bc.ModalPort(p1, 1, modetype='TEM')
port2 = model.mw.bc.ModalPort(p2, 2, modetype='TEM')

############################################################
#                      RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   EXTRACT S-PARAMETERS                   #
############################################################
grid = data.scalar.grid
f    = grid.freq

S11 = grid.S(1, 1)
S21 = grid.S(2, 1)

plot_sp(f, [S11,S21], labels=['S11','S21'])

############################################################
#                VECTOR FITTING (supersampled plot)        #
############################################################

f_fit = np.linspace(f_start, f_stop, 2001)
f_MHz = f_fit / 1e6    # Used for displaying the graphs
S11_fit = grid.model_S(1, 1, f_fit)
S21_fit = grid.model_S(2, 1, f_fit)

plot_sp(f_fit, [S11_fit,S21_fit], labels=['S11','S21'])

############################################################
#                    3D FIELD VISUALIZATION                #
############################################################

field = data.field.find(freq=f0)
model.display.add_object(diel)
model.display.add_object(stripline)
model.display.animate().add_field(
    field.grid(N=100_000, z_range=(-th * mm, th*mm)).scalar('Ez', 'complex'),
    symmetrize=True,
)
model.display.show()