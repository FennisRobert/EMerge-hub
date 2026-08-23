# =============================================================================
# EMerge Simulation Template: PCB-ANT-05 (Tuned)
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
# Printed Quarter-Wave Monopole (2.4 GHz)
#
# The simplest antenna in this library: a single straight strip of copper,
# printed on a 40 by 80 mm board next to a ground plane with a cleared-out
# gap. Tuned to 2.4 GHz and modeled with a realistic copper thickness rather
# than an idealized paper-thin sheet.
# -----------------------------------------------------------------------------

import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar

############################################################
#                     UNITS & CONSTANTS                    #
############################################################

mm = 0.001      # meters per millimeter
mil = 0.0254 * mm
inch = 25.4 * mm

C0 = 299792458
Z0 = 376.73031366857
PI = 3.14159265358979323846
EPS0 = 8.854187818814e-12
MU0 = 1/(C0*C0*EPS0)

############################################################
#                   DESIGN / GEOMETRY PARAMETERS           #
############################################################

# --- Frequency ------------------------------------------------------------
f0 = 2.4e9
f1 = 2.3e9
f2 = 2.5e9
n_points = 7

# --- PCB & Ground Dimensions -----------------------------------------------
WPCB = 40*mm
LPCB = 80*mm
thpcb = 1.5*mm
thmetal = 0.035*mm          # 1 oz copper (35 um)
gnd_clearance = 27*mm       # Expanded ground keepout zone

# --- Monopole Element Dimensions ------------------------------------------
w_ant = 2.5*mm              # Width of printed monopole trace
l_ant = 26*mm             # Radiating arm length (increased to achieve X = 0 at 2.4 GHz)
l_port = 1.0*mm             # Feed gap height over ground edge

air_margin = 50*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################

model = em.Simulation("PrintedMonopoleTuned")
model.check_version("3.0.0")

############################################################
#                          GEOMETRY                        #
############################################################

# 1. Substrate
pcb_sub = em.geo.Box(WPCB, LPCB, thpcb, (-WPCB/2, -LPCB/2, -thpcb)).set_material(em.lib.DIEL_FR4)

# 2. Ground plane (covers bottom area up to clearance boundary)
y_gnd_edge = LPCB/2 - gnd_clearance
gnd_plane = em.geo.Box(WPCB, LPCB - gnd_clearance, thmetal, (-WPCB/2, -LPCB/2, 0)).set_material(em.lib.COPPER)

# 3. Printed Monopole Strip
y_ant_start = y_gnd_edge + l_port
monopole = em.geo.Box(w_ant, l_ant, thmetal, (-w_ant/2, y_ant_start, 0)).set_material(em.lib.COPPER)

# 4. Port Plate (spans the gap from ground edge to monopole base)
ant_port = em.geo.Plate((-w_ant/2, y_gnd_edge, 0), (w_ant, 0, 0), (0, l_port, 0))

# 5. Air Box Domain
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

# Local mesh refinements
model.mesher.set_boundary_size(monopole, 0.5 * mm)
model.mesher.set_face_size(ant_port, 0.25 * mm)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

model.mw.bc.LumpedPort(ant_port, 1, width=w_ant, height=l_port, direction=em.YAX)
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

ff_xy = data.field.find(freq=f0).farfield_2d(em.XAX, em.YAX, air.boundary())
ff_xz = data.field.find(freq=f0).farfield_2d(em.XAX, em.ZAX, air.boundary())
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
display.animate().add_field(field.grid(N=100_000).scalar('Ey', 'complex'), symmetrize=True, clim_crop_factor=0.5)
display.show()