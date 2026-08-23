# =============================================================================
# EMerge Simulation Template: Wire monopole on a finite ground plane
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
# =============================================================================

# -----------------------------------------------------------------------------
# Wire Monopole on a Finite Ground Plane (2.45 GHz)
#
# A simple vertical wire antenna standing above a small, finite-sized ground
# plane rather than an idealized infinite one. Because the ground plane has
# real edges, some of the antenna's energy diffracts around them instead of
# reflecting cleanly, an effect this template is meant to demonstrate. Tuned
# to 2.45 GHz.
# -----------------------------------------------------------------------------

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
f0 = 2.45*GHz
f1 = 2.30*GHz
f2 = 2.60*GHz

n_freqs = 11

# --- Geometry dimensions ---------------------------------------------------

Zsource = 36 # Omega
length = C0/f0 * 0.22
gap = 1*mm
radius = 1*mm
air_radius = 100*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

antenna = em.geo.Cylinder(radius, length, em.cs(origin=(0,0,gap)), Nsections=12).set_material(em.lib.COPPER).prio_set(20)
port = em.geo.Cylinder(radius, gap, Nsections=12)

air = em.geo.HalfSphere(air_radius, (0,0,0), (0,0,1))

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency_range(f1, f2, n_freqs)
# model.mw.set_frequency_range(f1, f2, n_points)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)
model.mesher.set_boundary_size(port, gap/3)
model.mesher.set_boundary_size(antenna.face('+z'), radius/2)
model.mesher.set_curved_boundary_meshing(20)
############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

boundary_selection = air.outside

lumped_port = model.mw.bc.LumpedPort(port.shell, 1, 2*PI*radius, gap, em.ZAX, Z0=Zsource)
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid

S11 = g.S(1,1)

plot_sp(g.freq, S11)
smith(S11, g.freq)

Zload = Zsource*((1+S11)/(1-S11))

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
model.display.animate().add_field(field.grid(N=200_00).scalar('Ez','complex'), symmetrize=True, clim_crop_factor=0.1)
#
# # Show interactive 3D scene
model.display.show()
