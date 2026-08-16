# =============================================================================
# EMerge Simulation Template: [Model Name / ID]
#
# Copyright (C) [Year] [Author Name or GitHub Handle]
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
# =============================================================================

# -----------------------------------------------------------------------------
# This is an example for a 5-element Yagi-uda antenna. The parameters are calculated
# using the calculator at: https://www.changpuak.ch/electronics/yagi_uda_antenna_DL6WU.php

# -----------------------------------------------------------------------------
from emerge_config import config
config.set_acc_threads(4)

import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar, plot

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
f0 = 1500*MHz
f1 = 1300*MHz
f2 = 1700*MHz
nfreq = 11

# --- Geometry dimensions ---------------------------------------------------

ZSource = 50
Ls = [98*mm, 47.6*mm*2, 91*mm, 90*mm, 89*mm]
xpos = [0, 48*mm, 63*mm, 99*mm, 142*mm]
gap = 1*mm
rad = 1*mm
margin = 50*mm

l_scaling = 1.45/1.50

Ls = [l*l_scaling for l in Ls]

############################################################
#                    MATERIAL DEFINITIONS                  #
############################################################

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo",loglevel='DEBUG')
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

def make_wire(x, L):
    return em.geo.Cylinder(rad, L, em.YAX.construct_cs(origin=(x, -L/2, 0)), Nsections=8)


reflector = make_wire(xpos[0], Ls[0]).set_material(em.lib.COPPER)
dipole = make_wire(xpos[1], Ls[1]).set_material(em.lib.COPPER)
dir1 = make_wire(xpos[2], Ls[2]).set_material(em.lib.COPPER)
dir2 = make_wire(xpos[3], Ls[3]).set_material(em.lib.COPPER)
dir3 = make_wire(xpos[4], Ls[4]).set_material(em.lib.COPPER)

port = make_wire(xpos[1], gap).prio_set(20)
dipole = em.geo.subtract(dipole, port, remove_tool=False)

air = em.geo.open_region(margin, margin, margin)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency_range(f1,f2, nfreq)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)
model.mesher.set_boundary_size(port, rad/2)
model.mesher.set_boundary_size(em.select(reflector, dipole, dir1, dir2, dir3), 2*rad)
############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view(assigned_materials=True)

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

boundary_selection = air.boundary()

model.mw.bc.AbsorbingBoundary(boundary_selection)
model.mw.bc.LumpedPort(port.shell, 1, 2*PI*rad, gap, em.YAX, Z0=ZSource)

############################################################
#                       RUN SIMULATION                      #
############################################################
model.view(bc=True)
data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid

S11 = g.S(1,1)

plot_sp(g.freq, S11)
smith(S11, g.freq)

Zload = ZSource * ((1+S11)/(1-S11))

plot(g.freq/GHz, [Zload.real, Zload.imag], labels=['Real','Imag'], xlabel="Frequency (GHz)", ylabel="Load Impedance (Ω)")

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff = data.field.find(freq=f0).farfield_2d(em.ZAX, em.XAX, boundary_selection)
plot_ff(ff.ang * 180 / np.pi, ff.gain.norm, dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff.ang, ff.gain.norm, dB=True, dBfloor=-40)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################
field = data.field.find(freq=f0)

# # Add geometry for context
model.display.populate()
#field = data.field.find(freq=f0)
# # Compute full 3D far-field (at the same frequency) and display
ff3d = field.farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d, dB=True, rmax=150*mm / 2, offset=(0, 0, 150*mm), opacity=0.4)
model.display.animate().add_field(field.grid(N=200_00).scalar('Ey','complex'), symmetrize=True, clim_crop_factor=0.1)
#
# # Show interactive 3D scene
model.display.show()
