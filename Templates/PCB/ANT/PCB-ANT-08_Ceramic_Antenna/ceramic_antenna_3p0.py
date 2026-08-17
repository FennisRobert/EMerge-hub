# =============================================================================
# EMerge Simulation Template: PCB-ANT-07
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
# Surface-Mount Ceramic Chip Antenna (2.4 GHz ISM / BLE / WiFi)
#
# Demonstrates a compact LTCC ceramic chip antenna (5x2x1.2 mm, er=18) 
# mounted over a PCB ground clearance area with a 50 Ohm microstrip feed.
#
# The model claims approximately 3.8GB of RAM
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

GHz = 1e9

C0 = 299792458
Z0 = 376.73031366857
PI = 3.14159265358979323846
EPS0 = 8.854187818814e-12
MU0 = 1/(C0*C0*EPS0)

############################################################
#                   DESIGN / GEOMETRY PARAMETERS           #
############################################################

# --- Frequency ------------------------------------------------------------
f0 = 2.45*GHz
f1 = 2.1*GHz
f2 = 2.8*GHz
n_points = 15

# --- Board & Ground Keepout Dimensions ------------------------------------
WPCB = 40*mm
LPCB = 80*mm
thpcb = 1.0*mm              # 1.0 mm FR-4 substrate
w_ms = 1.9*mm               # 50 Ohm microstrip width on 1.0mm FR-4

clearance_w = 12*mm         # Ground clearance width (X)
clearance_h = 6*mm          # Ground clearance height (Y)

# --- Ceramic Chip Antenna Dimensions -------------------------------------
l_chip = 5.0*mm             # Chip X dimension
w_chip = 2.0*mm             # Chip Y dimension
h_chip = 1.2*mm             # Chip Z height
eps_ceramic = 18.0          # LTCC Relative Permittivity
tan_delta = 0.002

# Internal meander conductor on ceramic top face
w_trace = 0.3*mm
n_turns = 4
pitch = 1.0*mm

lport = 1.0*mm
air_margin = 40*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################

model = em.Simulation("CeramicChipAntennaDemo")
model.check_version("3.0.0")

############################################################
#                          GEOMETRY                        #
############################################################

# 1. PCB Dielectric Substrate
pcb_sub = em.geo.Box(WPCB, LPCB, thpcb, (-WPCB/2, -LPCB/2, -thpcb)).set_material(em.lib.DIEL_FR4)

# 2. Main Ground Plane (Top Copper with Clearance Cutout)
y_gnd_edge = LPCB/2 - clearance_h

gnd_left = em.geo.XYPlate((WPCB - clearance_w)/2, clearance_h, (-WPCB/2, y_gnd_edge, 0)).set_material(em.lib.COPPER)
gnd_right = em.geo.XYPlate((WPCB - clearance_w)/2, clearance_h, (clearance_w/2, y_gnd_edge, 0)).set_material(em.lib.COPPER)
gnd_main = em.geo.XYPlate(WPCB, LPCB - clearance_h, (-WPCB/2, -LPCB/2, 0)).set_material(em.lib.COPPER)

ground = em.geo.unite(gnd_left, gnd_right, gnd_main)

# 3. Microstrip Feed Line (50 Ohm line extending to clearance boundary)
feed_line = em.geo.XYPlate(w_ms, y_gnd_edge + LPCB/2 - lport, (-w_ms/2, -LPCB/2 + lport, 0)).set_material(em.lib.COPPER)

# 4. Ceramic Body
ceramic_mat = em.lib.Material(er=eps_ceramic, tand=tan_delta, name="LTCC_Ceramic")
x_chip_start = -l_chip/2
y_chip_start = y_gnd_edge + 1.5*mm

chip_body = em.geo.Box(l_chip, w_chip, h_chip, (x_chip_start, y_chip_start, 0)).set_material(ceramic_mat)

# 5. Metallization Pattern on Ceramic (Internal / Surface Wrapped Conductor)
meander_parts = []

# Feed pad transition from microstrip to chip
feed_pad = em.geo.XYPlate(w_ms, y_chip_start - y_gnd_edge, (-w_ms/2, y_gnd_edge, 0)).set_material(em.lib.COPPER)

# Top surface helical/serpentine trace on ceramic body
z_top = h_chip
x_curr = x_chip_start + 0.2*mm
y_bottom = y_chip_start + 0.2*mm
y_top = y_chip_start + w_chip - 0.2*mm

for i in range(n_turns):
    # Vertical segment on chip top face
    seg_y = em.geo.Box(w_trace, w_chip - 0.4*mm, 0.035*mm, (x_curr, y_bottom, z_top)).set_material(em.lib.COPPER)
    meander_parts.append(seg_y)
    
    # Rung connection
    if i < n_turns - 1:
        x_next = x_curr + pitch
        y_rung = y_top if (i % 2 == 0) else y_bottom
        seg_x = em.geo.Box(pitch, w_trace, 0.035*mm, (x_curr, y_rung - w_trace/2, z_top)).set_material(em.lib.COPPER)
        meander_parts.append(seg_x)
        x_curr = x_next

chip_trace = em.geo.unite(*meander_parts)

# 6. Lumped Port Plate at PCB Edge
ant_port = em.geo.Plate((-w_ms/2, -LPCB/2, -thpcb), (w_ms, 0, 0), (0, 0, thpcb))

# 7. Air Domain
air = em.geo.open_region(air_margin, air_margin, air_margin)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

model.mw.set_frequency_range(f1, f2, n_points)
model.mw.set_resolution(0.18)

# Local fine meshing on the high-permittivity ceramic chip and fine traces
model.mesher.set_domain_size(chip_body, 1.3 * mm)
model.mesher.set_boundary_size(chip_trace, 0.1 * mm)
model.mesher.set_face_size(ant_port, 0.25 * mm)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

model.mw.bc.LumpedPort(ant_port, 1, width=w_ms, height=thpcb, direction=em.ZAX)
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
display.animate().add_field(field.grid(N=100_000).scalar('Ez', 'complex'), symmetrize=True, clim_crop_factor=0.1)
display.show()