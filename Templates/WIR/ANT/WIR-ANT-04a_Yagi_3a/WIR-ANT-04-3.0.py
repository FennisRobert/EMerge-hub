# =============================================================================
# EMerge Simulation Template: [WIR-ANT-04]
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
#   3-Element Yagi-Uda Antenna
#
# This is a model of a three element Yagi optimized at 868 MHz for use with
# Mesh radio etc. Outputs impedance, S value, antenna gain charts
# as well as an E-field 3d visualization. It uses a PFTE boom (3dp or similar)
# Uses up to 8GB
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
f0 = 868*MHz      # center / operating frequency (Hz)

# --- Geometry dimensions ---------------------------------------------------
airbox_hght = 150 * mm
airbox_wdth = 250 * mm
airbox_dpt = 350 * mm

wavelength = C0/f0

# Everything in the simulation can be adjusted by tuning the parameters below
# except for the width of the driven port. This is hardcoded further down as there
# isn't really a need for this to change

driven_length = 0.46 * wavelength
reflector_length = .5 * wavelength
parasite_length = .43 * wavelength
element_spacing = 0.17 * wavelength
element_radius = 1 * mm

boom_length = (2 * element_spacing) + 20*mm
boom_width = 10 * mm
boom_height = 10 * mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation('YagiAntenna')
model.check_version("3.0.0")  # Checks version compatibility.
model.settings.size_check = False

############################################################
#                          GEOMETRY                        #
############################################################

airbox = em.geo.Box(airbox_wdth, airbox_dpt, airbox_hght,  alignment=em.CENTER)
boom = em.geo.Box(boom_width, boom_length, boom_height,  alignment=em.CENTER)

# Create the driven element slot
driver_slot = em.geo.Cylinder(element_radius,boom_width, cs=em.cs(origin=(boom_width/2,0,boom_width/2)))
driver_slot = em.geo.rotate(driver_slot,[boom_width/2,0,boom_width/2],[0,1,0],angle=90)
boom = em.geo.remove(boom,driver_slot)

# Add the driven element
driven_element = em.geo.Cylinder(element_radius,driven_length, cs=em.cs(origin=(driven_length/2,0,boom_width/2)))
driven_element = em.geo.rotate(driven_element,[driven_length/2,0,boom_width/2],[0,1,0],angle=90)

# Remove the piece from the driven element for the port
cut_piece = em.geo.Cylinder(element_radius, 1*mm, cs=em.cs(origin=(.5*mm,0,boom_width/2)))
cut_piece = em.geo.rotate(cut_piece, [.5*mm,0,boom_width/2], [0,1,0],angle=90)
driven_element = em.geo.remove(driven_element,cut_piece)

# Add the surface for our excitation port
sheet = em.geo.XYPlate(1*mm, 2 * element_radius,
                       (-.5*mm,-1 * element_radius,boom_width/2))

# Cut the slot for the reflector
reflector_slot = em.geo.Cylinder(element_radius,boom_width, cs=em.cs(origin=(boom_width/2,element_spacing,boom_width/2)))
reflector_slot = em.geo.rotate(reflector_slot,[boom_width/2,element_spacing,boom_width/2],[0,1,0],angle=90)
boom = em.geo.remove(boom, reflector_slot)

# Add the driven element
reflector_element = em.geo.Cylinder(element_radius,reflector_length, cs=em.cs(origin=(reflector_length/2,
                                                                                      element_spacing,boom_width/2)))
reflector_element = em.geo.rotate(reflector_element,[reflector_length/2,element_spacing,boom_width/2],[0,1,0],angle=90)

# Cut the slot for the director
director_slot = em.geo.Cylinder(element_radius,boom_width, cs=em.cs(origin=(boom_width/2,-element_spacing,boom_width/2)))
director_slot = em.geo.rotate(director_slot,[boom_width/2,-element_spacing,boom_width/2],[0,1,0],angle=90)
boom = em.geo.remove(boom, director_slot)

# Add the director element
director_element = em.geo.Cylinder(element_radius,parasite_length, cs=em.cs(origin=(parasite_length/2,-element_spacing,boom_width/2)))
director_element = em.geo.rotate(director_element,[parasite_length/2,-element_spacing,boom_width/2],[0,1,0],angle=90)

driven_element.set_material(em.lib.COPPER)
reflector_element.set_material(em.lib.COPPER)
director_element.set_material(em.lib.COPPER)
boom.set_material(em.lib.DIEL_PTFE)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()
#model.view()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency(f0)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)


############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()
model.view(plot_mesh=True)
############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

boundary_selection = airbox.boundary()
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)
port_bc = model.mw.bc.LumpedPort(sheet, 1, width=1*mm,
                                 height=2*element_radius,
                                 direction=(1,0,0), Z0=50.0)

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid

S11 = g.S(1,1)[0]
S11dB = 20*np.log10(np.abs(S11))
Zload = 50*((1+S11)/(1-S11))
print(f'S11 = {S11dB:.1f} dB')
print(f'Load impedance = {Zload:.1f} Ω')

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff = data.field.find(freq=f0).farfield_2d((0, -1, 0), (0, 0, 1), boundary_selection)
plot_ff(ff.ang * 180 / np.pi, ff.gain.norm, dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff.ang, ff.gain.norm, dB=True, dBfloor=-15)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

### Note - this is a visualization of the E-field magnitude not
### antenna gain

# # Add geometry for context
model.display.add_object(boom)
model.display.add_object(airbox)
model.display.add_object(driven_element)
model.display.add_object(director_element)
model.display.add_object(driven_element)
#
# # Compute full 3D far-field (at the same frequency) and display
ff3d = data.field.find(freq=f0).farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d, dB='True', rmax=110*mm, offset=(0,0,0))
#
# # Show interactive 3D scene
model.display.show()