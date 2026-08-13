# =============================================================================
# EMerge Simulation Template: [WIR-ANT-01]
#
# Copyright (C) [2026] [mikeb127]
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
#   Half-Wave Center-Fed Dipole
#
# The 'Hello World' of antenna simulations. Simulates a basic Half-
# Wave Center-Fed Dipole operating at 1Ghz and outputs the antenna gain charts
# as well as an E-field 3d visualization
# -----------------------------------------------------------------------------

import emerge as em
import numpy as np
from emerge.plot import plot_ff, plot_ff_polar, plot as needed

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
PI = 3.14159265358979323846
EPS0 = 8.854187818814e-12
MU0 = 1/(C0*C0*EPS0)

############################################################
#                   DESIGN / GEOMETRY PARAMETERS           #
############################################################

# Collect all dimensions, frequencies and material properties here as named
# variables so the geometry section below stays clean and the design is easy
# to tweak.

# --- Frequency ------------------------------------------------------------
f0 = 1e9       # center / operating frequency (Hz)
# f1, f2 = ..., ...   # sweep start/stop, if using a frequency range

# --- Geometry dimensions ---------------------------------------------------
airbox_hght = 500 * mm
airbox_wdth = 300 * mm
airbox_dpt = 300 * mm

antenna_height = 300*mm
antenna_radius = 1*mm

cut_port_height = 1*mm
cut_port_radius = 1*mm

port_width = 2 * mm
port_height = 1 * mm


############################################################
#                    MATERIAL DEFINITIONS                  #
############################################################

# mymat = em.Material(er=er, tand=tand, color="#217627", opacity=0.3)

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation('HalfWaveDipole')
model.check_version("2.8.2")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

airbox = em.geo.Box(airbox_wdth, airbox_dpt, airbox_hght,  position=(-(airbox_wdth/2),
                                                                     -(airbox_dpt/2),
                                                                    -100*mm))
half_wave_dipole = em.geo.Cylinder(antenna_radius,antenna_height)
port_cut = em.geo.Cylinder(cut_port_radius,cut_port_height)
port_cut = em.geo.translate(port_cut, dx=0, dy=0, dz=149.5*mm)
half_wave_dipole = em.geo.subtract(half_wave_dipole, port_cut)

port = em.geo.Plate((-1*mm, 0*mm, 149.5*mm),(2*mm,0,0),(0,0,1*mm))

half_wave_dipole.set_material(em.lib.PEC)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency(f0)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)

# Optional: refine the mesh locally around critical features
# (edges, ports, small gaps, vias, etc.)
# model.mesher.set_boundary_size(<selection>, 0.5 * mm)
# model.mesher.set_face_size(<selection>, 0.5 * mm)
# model.mesher.set_domain_size(<selection>, 1 * mm)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################


model.view()
model.generate_mesh()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

boundary_selection = airbox.boundary()
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)
port_bc = model.mw.bc.LumpedPort(port, 1, width=port_width, height=port_height, direction=(0,0,1), Z0=50.0)

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

#g = data.scalar.grid
#f = g.freq
#S11 = g.S(1, 1)
#S21 = g.S(2, 1)
#plot_sp(f, [S11, S21], labels=["S11", "S21"], dblim=[-40, 6])

# Optional: supersample with Vector Fitting for smoother curves
# fdense = g.dense_f(2001)
# S11_fit = g.model_S(1, 1, fdense)
# S21_fit = g.model_S(2, 1, fdense)
# plot_sp(fdense, [S11_fit, S21_fit], labels=["S11", "S21"])

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff = data.field.find(freq=f0).farfield_2d((1, 0, 0), (0, 1, 0), boundary_selection)
plot_ff(ff.ang * 180 / np.pi, ff.gain.norm, dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff.ang, ff.gain.norm, dB=True, dBfloor=-40)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

### Note - this is a visualization of the E-field magnitude not
### antenna gain

# # Add geometry for context
model.display.add_object(half_wave_dipole)
model.display.add_object(airbox)
#
# # Compute full 3D far-field (at the same frequency) and display
ff3d = data.field.find(freq=1.0e9).farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d, dB='True', rmax=300*mm / 2, offset=(0, 0, 150*mm))
#
# # Show interactive 3D scene
model.display.show()
