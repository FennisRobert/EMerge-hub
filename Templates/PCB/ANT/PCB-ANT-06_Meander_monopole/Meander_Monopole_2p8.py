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
# Meander-Line Monopole for Sub-GHz LoRa/RFID (868 MHz)
#
# A quarter-wave monopole antenna folded into a compact zigzag shape so it
# fits in a small area, similar in idea to PCB-ANT-02's meandered trace but
# as a monopole instead of an inverted-F. Built on a 60 by 120 mm board and
# tuned to 868 MHz, a common frequency for LoRa and RFID devices. Routed
# using EMerge's PCB path tool.
# -----------------------------------------------------------------------------
from emerge_config import config
config.set_acc_threads(10)

import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar

############################################################
#                     UNITS & CONSTANTS                    #
############################################################

mm = 0.001      # meters per millimeter
mil = 0.0254 * mm
inch = 25.4 * mm

MHz = 1e6

C0 = 299792458
Z0 = 376.73031366857
PI = 3.14159265358979323846
EPS0 = 8.854187818814e-12
MU0 = 1/(C0*C0*EPS0)

############################################################
#                   DESIGN / GEOMETRY PARAMETERS           #
############################################################

# --- Frequency ------------------------------------------------------------
f0 = 868*MHz
f1 = 600*MHz
f2 = 1000*MHz
n_points = 11

# --- Board Dimensions -----------------------------------------------------
WPCB = 60*mm
LPCB = 120*mm
gnd_clearance = 25*mm
thpcb = 1.5*mm
wfeed = 1.5*mm
lport = 1*mm

# --- Meander Specification ------------------------------------------------
N_meander = 2          # Number of full meander periods
wmeander = 25*mm       # Peak-to-peak horizontal span
lstep = 6*mm         # Vertical pitch per meander leg

air_margin = 50*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################

model = em.Simulation("MeanderMonopoleDemo")
model.check_version("2.8.3")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

# Substrate
dielectric = em.geo.Box(WPCB, LPCB, thpcb, (-WPCB/2, -LPCB/2, -thpcb)).set_material(em.lib.DIEL_FR4)

# Top Ground Plane with clearance region at top (+Y)
y_gnd_edge = LPCB/2 - gnd_clearance
top_gnd = em.geo.XYPlate(WPCB, LPCB - gnd_clearance, (-WPCB/2, -LPCB/2, 0)).set_material(em.lib.COPPER)

# Feed origin at ground edge center
x0 = 0.0
y0 = y_gnd_edge + lport

# PCB Router setup for Monopole Trace
pcbd = em.geo.PCBNew(thpcb, 1.0, em.GCS.displace(x0, y0, 0), trace_material=em.lib.COPPER)

# Start routing stem extending vertically (+Y direction)
router = pcbd.new(0, 0, wfeed, (0, 1), z=pcbd.z(1)).straight(lstep).pturn(90).straight(wmeander / 2)

# Build serpentine meander path
for _ in range(N_meander):
    router = (router.pturn(-90)
                    .straight(lstep)
                    .pturn(-90)
                    .straight(wmeander)
                    .pturn(90)
                    .straight(lstep)
                    .pturn(90)
                    .straight(wmeander))

# Compile path to metal geometry
monopole = pcbd.compile_paths(True)

# Port plate filling the gap from ground plane to monopole base
ant_port = em.geo.XYPlate(wfeed, lport, (-wfeed/2, y_gnd_edge, 0))

# Enclosing air box
air = em.geo.open_region(air_margin, air_margin, air_margin)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

model.mw.set_frequency_range(f1, f2, n_points)
model.mw.set_resolution(0.2)

# Mesh refinements
model.mesher.set_boundary_size(monopole, 1 * mm)
model.mesher.set_face_size(ant_port, 0.5 * mm)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

model.mw.bc.LumpedPort(ant_port, 1, width=wfeed, height=lport, direction=em.YAX)
model.mw.bc.AbsorbingBoundary(air.boundary())

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
plot_sp(f, [S11], labels=["S11"], dblim=[-40, 6])
smith(S11, f)

# Vector Fitting interpolation
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
plot_sp(fdense, [S11_fit], labels=["S11 Fitted"])

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff_xy = data.field.find(freq=f0).farfield_2d(em.XAX, em.ZAX, air.boundary())
ff_xz = data.field.find(freq=f0).farfield_2d(em.XAX, em.YAX, air.boundary())
plot_ff(ff_xy.ang * 180 / np.pi, [ff_xy.gain.norm, ff_xz.gain.norm], labels=['XY Plane', 'XZ Plane'], dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff_xy.ang, ff_xy.gain.norm, dB=True, dBfloor=-20)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
ff3d = field.farfield_3d(air.boundary())
display = model.display
display.populate()
display.add_farfield3d(ff3d, 'gain.norm', 'abs', dB=True, dBfloor=-20, rmax=50*mm, opacity=0.5)
display.animate().add_field(field.grid(N=100_000).scalar('Ey', 'complex'), symmetrize=True, clim_crop_factor=0.1)
display.show()