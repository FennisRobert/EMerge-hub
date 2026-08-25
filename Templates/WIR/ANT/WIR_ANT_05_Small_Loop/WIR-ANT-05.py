# =============================================================================
# EMerge Simulation Template: [WIR-ANT-05]
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
#   Electrically Small Loop
#
# This is a model of a Electrically Small loop antenna in a perfect circle shape.
# Outputs the impedance, the antenna gain charts
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
KHz = 1e3

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
f0 = 14*MHz      # center / operating frequency (Hz)
wavelength = C0/f0
print(wavelength)
# --- Geometry dimensions ---------------------------------------------------
airbox_hght = 1500 * mm
airbox_wdth = 1500 * mm
airbox_dpt = 800 * mm
loop_rad = 500 * mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation('ElectricallySmallLoop')
model.check_version("3.0.0")  # Checks version compatibility.
model.settings.size_check = False

############################################################
#                          GEOMETRY                        #
############################################################

# Build our loop with BSplines
x_arr = np.array([loop_rad,loop_rad, 0, -loop_rad,
                  -loop_rad, -loop_rad, 0, loop_rad, loop_rad])
z_arr = np.array([0, loop_rad, loop_rad, loop_rad,
                  0, -loop_rad, -loop_rad, -loop_rad, 0])
weights = np.array([1, 0.70710678118, 1, 0.70710678118,
                    1, 0.70710678118, 1, 0.70710678118, 1])
knots = np.array([0, 0.25, 0.5, 0.75, 1])
mults = np.array([3, 2, 2, 2, 3])

cr_radius = 2*mm
cross_section = em.geo.XYPolygon.circle(cr_radius, Nsections=12)
loop_antenna = em.geo.Curve(xpts=x_arr, ypts=x_arr*0, zpts=z_arr,
                            degree=2, multiplicities=mults,
                            weights=weights, knots=knots,
                 ctype='Bspline').pipe(cross_section).set_material(em.lib.PEC)

# Set up airbox and sheet for excitation
slice_box = em.geo.Box(1*mm, 8*mm, 8*mm,
                       cs=em.cs(origin=(0, 0, -loop_rad)),
                       alignment=em.CENTER)
airbox = em.geo.Box(airbox_wdth, airbox_dpt, airbox_hght,
                    alignment=em.CENTER)
loop_antenna = em.geo.remove(loop_antenna, slice_box)
sheet = em.geo.XYPlate(1 * mm, 2 * cr_radius,
                       (-.5*mm, -cr_radius, -loop_rad))



############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()
model.view(use_gmsh=True)

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency(f0)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.003)
model.mesher.set_curved_boundary_meshing(20)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view(plot_mesh=True)

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

boundary_selection = airbox.boundary()
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)
port_bc = model.mw.bc.LumpedPort(sheet, 1, width=1*mm,
                                 height=2 * cr_radius,
                                 direction=(1, 0, 0), Z0=50.0)

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid

S11 = g.S(1, 1)[0]
S11dB = 20*np.log10(np.abs(S11))
Zload = 50*((1+S11)/(1-S11))
print(f'S11 = {S11dB:.8f} dB')
print(f'Load impedance = {Zload:.8f} Ω')

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff = data.field.find(freq=f0).farfield_2d((0, 1, 0),
                                          (0, 0, 1),
                                          boundary_selection)
plot_ff(ff.ang * 180 / np.pi, ff.gain.norm, dB=True,
        ylabel="Gain [dBi]")
plot_ff_polar(ff.ang, ff.gain.norm, dB=True,
              dBfloor=-150)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

### Note - this is a visualization of the E-field magnitude not
### antenna gain

# # Add geometry for context
model.display.add_object(loop_antenna)
model.display.add_object(airbox)
#
# # Compute full 3D far-field (at the same frequency) and display
ff3d = data.field.find(freq=f0).farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d, dB='True',
                             dBfloor=-150, rmax=250*mm, offset=(0, 0, 0))
#
# # Show interactive 3D scene
model.display.show()