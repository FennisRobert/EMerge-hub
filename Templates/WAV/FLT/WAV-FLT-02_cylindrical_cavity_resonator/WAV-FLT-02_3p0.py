# =============================================================================
# EMerge Simulation Template: WAV-FLT-02
#
# Copyright (C) 2026 elektroedde
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
# Cylindrical Cavity Resonator (Eigenmode)
#
# This demo shows how to model a closed metallic cylindrical cavity and
# extract its resonant modes with EMerge's eigenmode solver. There are no
# ports and no excitation, the solver searches for the frequencies that 
# resonate inside the PEC-walled cavity. This is a good starting 
# point for learning model building, meshing, solving and post-processing 
# of eigenmode problems
#
# Note that unassigned outer boundaries of a solid default to PEC (metal)
# for the eigenmode solver, so no explicit boundary condition needs to be
# set for a simple closed cavity like this one.
# -----------------------------------------------------------------------------

import emerge as em
import numpy as np
from emerge.plot import plot_sp

############################################################
#                     UNITS & CONSTANTS                    #
############################################################

# EMerge works in SI units internally, so it's convenient to define a few
# unit helpers at the top of the script.
mm = 0.001      # meters per millimeter
cm = 0.01       # meters per centimeter
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
f0 = 4e9      # search frequency for the eigenmode solver (Hz)
n_modes = 4      # number of eigenmodes to solve for

# --- Geometry dimensions ---------------------------------------------------
radius = 3*cm   # cavity radius
height = 6*cm   # cavity height (along z)

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("CylindricalCavityResonator")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

# A cylinder of the given radius and height, centered on the origin
# along z. The z-position is offset by -height/2 so the cylinder
# base sit at z=-height/2 and its top at z=+height/2.
cavity = em.geo.Cylinder(radius, height, em.CS(em.XAX, em.YAX, em.ZAX, (0, 0, -height/2)))

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                #
############################################################

# Eigenmode studies need a reference frequency for meshing purposes.
model.mw.set_frequency(f0)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.15)

############################################################
#                    GENERATE & VIEW MESH                  #
############################################################

model.generate_mesh()
# Set the objects material opacity to 1 (solid) for viewing
cavity.material.opacity = 1
model.view()
model.view(plot_mesh=True)

############################################################
#                    BOUNDARY CONDITIONS                   #
############################################################

# None needed, the cavity walls default to PEC for the eigenmode solver.

############################################################
#                       RUN SIMULATION                     #
############################################################

data = model.mw.eigenmode(f0, nmodes=n_modes)

############################################################
#                   POST-PROCESSING: EIGENMODES            #
############################################################

# Print the eigenfrequency of every solution found around f0.
for i in range(n_modes):
    mode_field = data.field[i]
    print(f'Mode {i}: Frequency = {mode_field.freq/1e9:.4f} GHz')

############################################################
#                     3D FIELD VISUALIZATION               #
############################################################

# Inspect the field of the first eigensolution with three z-cutplanes of
# the real part of Ez, plus the cavity outline.
# Set the objects material opacity to 0.1 (10%) for visualizing results
cavity.material.opacity = 0.1

field = data.field[0]
display = model.display
display.add_field(field.cutplane(ds=0.01*cm, z=0).scalar('Ez', 'real'), cmap='rainbow')
display.add_field(field.cutplane(ds=0.01*cm, z=height/3).scalar('Ez', 'real'), cmap='rainbow')
display.add_field(field.cutplane(ds=0.01*cm, z=-height/3).scalar('Ez', 'real'), cmap='rainbow')
display.add_field(field.cutplane(ds=0.01*cm, y=0).scalar('Ez', 'real'), cmap='rainbow')
display.add_field(field.cutplane(ds=0.01*cm, x=0).scalar('Ez', 'real'), cmap='rainbow')

display.populate()
display.show()