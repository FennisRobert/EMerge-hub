# =============================================================================
# EMerge Simulation Template: PCB-ANT-01
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
# Planar Inverted-F Antenna (PIFA) for 2.4 GHz WiFi/BLE
#
# A microstrip inverted-F trace etched into the top copper layer of a 70 by
# 150 mm, 1.5 mm FR4 board next to a partial ground plane. The F-shaped trace
# is fed by a lumped port at its base and tuned to resonate across the
# 2.4 GHz WiFi/BLE band, swept from 2.2 to 2.6 GHz over 11 points.
#
# The reference benchmark antenna for this library: a minimal, single-layer,
# single-port geometry with local mesh refinement at the antenna edge and
# port face. Needs roughly 4 GB of RAM to solve.
# -----------------------------------------------------------------------------

import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar

############################################################
#                     UNITS & CONSTANTS                    #
############################################################

# EMerge works in SI units internally, so it's convenient to define a few
# unit helpers at the top of the script.
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
f1 = 2.2e9
f2 = 2.6e9
n_points = 11
# --- Geometry dimensions ---------------------------------------------------

WPCB = 70*mm
LPCB = 150*mm
xpos_feed = 5*mm
ydist = 5*mm
want = 1*mm
wfeed = 1*mm
lport = 1*mm
lant = 22.5*mm

thpcb = 1.5*mm
air_margin = 50*mm
############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("2.8.2")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

dielectric = em.geo.Box(WPCB, LPCB, thpcb, (-WPCB/2, -LPCB/2, -thpcb)).set_material(em.lib.DIEL_FR4)

top_gnd = em.geo.XYPlate(WPCB, LPCB-ydist, (-WPCB/2, -LPCB/2, 0)).set_material(em.lib.COPPER)

x0 = -WPCB/2
y0 = LPCB/2-ydist

ant_poly = em.geo.XYPolygon(
    xs = [x0, x0+want, x0+want, x0 + lant, x0 + lant, x0],
    ys = [y0, y0, y0+ydist-want, y0+ydist-want, y0+ydist, y0+ydist],).geo(em.GCS).set_material(em.lib.COPPER)

ant_feed = em.geo.XYPlate(wfeed, ydist-wfeed-lport, (x0+xpos_feed-wfeed/2, y0+lport, 0)).set_material(em.lib.COPPER)

ant_poly = em.geo.add(ant_poly, ant_feed)
ant_port = em.geo.XYPlate(wfeed, lport, (x0+xpos_feed-wfeed/2, y0, 0))


air = em.geo.open_region(air_margin,air_margin,air_margin)


############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency_range(f1, f2, n_points)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)

# Optional: refine the mesh locally around critical features
# (edges, ports, small gaps, vias, etc.)
model.mesher.set_boundary_size(ant_poly, 0.5 * mm)
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
# supersample with Vector Fitting for smoother curves
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
plot_sp(fdense, [S11_fit], labels=["S11"])

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff_xy = data.field.find(freq=f0).farfield_2d(em.XAX, em.ZAX, air.boundary())
ff_xz = data.field.find(freq=f0).farfield_2d(em.XAX, em.YAX, air.boundary())
plot_ff(ff_xy.ang * 180 / np.pi, [ff_xy.gain.norm, ff_xz.gain.norm], labels=['XY Plane','XZ Plane'], dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff_xy.ang, ff_xy.gain.norm, dB=True, dBfloor=-20)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
ff3d = field.farfield_3d(air.boundary())
display = model.display
display.populate()
display.add_farfield3d(ff3d, 'gain.norm', 'abs', dB=True, dBfloor=-20, rmax=50*mm, opacity=0.5)
display.animate().add_field(field.grid(N=100_000).scalar('Ex','complex'), symmetrize=True, clim_crop_factor=0.1)
display.show()