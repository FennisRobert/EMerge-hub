# =============================================================================
# EMerge Simulation Template: PCB-ANT-02
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
# Standard PCB Inverted-F (IFA)
#
# This is a simple model of a meandering IFA antenna tuned to 868MHz. 
# We use the PCB design class to easily route the meandering line.
#
# The model claims approximately 4GB of RAM
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


# --- Frequency ------------------------------------------------------------
f0 = 2.4*GHz
f1 = 2.2*GHz
f2 = 2.6*GHz
n_points = 11

# --- Geometry dimensions ---------------------------------------------------

Wpatch = 32*mm
Lpatch = 28.7*mm
inset_distance = 10*mm
inset_gap = 1*mm
feed_length = 10*mm
l_transformer = 15*mm

w0 = 2.88*mm
w1 = 0.5*mm

WPCB = 60*mm
LPCB = 70*mm

th_pcb = 1.5*mm
############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("2.8.3")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCBNew(th_pcb, 1.0, material=em.lib.DIEL_FR4)

pcb.new(-feed_length-l_transformer, 0, w0, (1,0), pcb.z(1))['port'].straight(feed_length).straight(l_transformer, width=w1).straight(Lpatch, Wpatch)

trace = pcb.compile_paths(True)

pcb.determine_bounds(15*mm, 15*mm, 15*mm, 15*mm)


diel = pcb.generate_pcb()
air = pcb.generate_air(20*mm)
lumped_port_face = pcb.lumped_port('port')

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
model.mesher.set_boundary_size(trace, 1 * mm)
model.mesher.set_face_size(lumped_port_face, 0.5 * mm)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view(assigned_materials=True)
model.view(plot_mesh=True)
############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

abc_boundary = air.boundary(exclude='bottom')
model.mw.bc.AbsorbingBoundary(abc_boundary)
model.mw.bc.LumpedPort(lumped_port_face, 1)
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

ff_xz = data.field.find(freq=f0).farfield_2d(em.ZAX, em.YAX, abc_boundary)
ff_yz = data.field.find(freq=f0).farfield_2d(em.ZAX, em.XAX, abc_boundary)
plot_ff(ff_xz.ang * 180 / np.pi, [ff_xz.gain.norm, ff_yz.gain.norm], labels=['XZ Plane','YZ Plane'], dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff_xz.ang, ff_yz.gain.norm, dB=True, dBfloor=-20)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
ff3d = field.farfield_3d(abc_boundary)
display = model.display
display.populate()
display.add_farfield3d(ff3d, 'gain.norm', 'abs', dB=True, dBfloor=-20, rmax=50*mm, opacity=0.5)
display.animate().add_field(field.grid(N=500_000).scalar('Ex','complex'), symmetrize=True, clim_crop_factor=0.5)
display.show()