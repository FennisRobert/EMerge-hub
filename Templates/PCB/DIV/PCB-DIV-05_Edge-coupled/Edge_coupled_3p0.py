# =============================================================================
# EMerge Simulation Template: Edge coupled power coupler
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
# Edge-Coupled Directional Coupler (3 GHz)
#
# Two transmission lines running side by side with a very small gap between
# them (40 micrometers), so part of the signal on one line couples across to
# the other. Couplers like this are used to sample a small, known fraction of
# a signal for power monitoring or SWR detection without interrupting the
# main path. Tuned to 3 GHz. The tiny coupling gap needs a fine mesh to
# resolve accurately, so this template needs around 10 GB of RAM to solve.
# -----------------------------------------------------------------------------
from emerge_config import config
config.set_acc_threads(4)

import emerge as em
import numpy as np
from emerge.plot import plot_sp, plot  # + smith, plot_ff, plot_ff_polar, plot as needed

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
f0 = 3.0*GHz
f1 = 1.0*GHz
f2 = 5.0*GHz
nf = 21

# --- Geometry dimensions ---------------------------------------------------

Z0 = 50 # Ohm
c = 0.5 # Coupling coefficient
Z0e = Z0*((1+c)/(1-c))**0.5
Z0o = Z0*((1-c)/(1+c))**0.5

# We can use: https://hforsten.com/field_solver.html to compute our odd and even mode impedances
print(f'Z0 even = {Z0e:.1f} Ω')
print(f'Z0 odd  = {Z0o:.1f} Ω')

w0 = 0.98*mm
w1 = 0.58*mm

Lf = 10*mm
Lq = 14*mm
gap = 0.04*mm
margin = 5*mm
y0 = Lf+w1+gap/2
dy = (w1-w0)/2

thcu = 35e-6
th = 0.508*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCB(th, 1.0, material=em.lib.DIEL_FR4, trace_material=em.lib.PEC, trace_thickness=thcu, thick_traces=True)

pcb.new(0, y0, w0, (0,-1), 1)[1].straight(Lf)\
    .move(dx=w0/2, dy=-w1/2, direction=(1,0), width=w1).straight(Lq)\
    .move(dx=w0/2, dy=w1/2, direction=(0,1), width=w0).straight(Lf, w0)[3]
pcb.new(0, -y0, w0, (0,1), 1)[2].straight(Lf)\
    .move(dx=w0/2, dy=w1/2, direction=(1,0), width=w1).straight(Lq)\
    .move(dx=w0/2, dy=-w1/2, direction=(0,-1), width=w0).straight(Lf, w0)[4]

trace = pcb.compile_paths(True)

pcb.determine_bounds(margin, margin, margin, margin)

p1 = pcb.lumped_port(1, 1)
p2 = pcb.lumped_port(2, 2)
p3 = pcb.lumped_port(3, 3)
p4 = pcb.lumped_port(4, 4)

le = pcb.lumped_elements
diel = pcb.generate_pcb()
air = pcb.generate_air(5*mm)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.

model.mw.set_frequency_range(f1, f2, nf)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)
model.mesher.set_boundary_size(trace, 0.5*mm)
model.mesher.set_trace_refinement(trace.face('-z'), qualtity_factor=1.5)
############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################


############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep(frequency_groups=4)

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
S21 = g.S(2, 1)
S31 = g.S(3, 1)
S41 = g.S(4, 1)

plot_sp(f, [S11, S21, S31, S41], labels=["S11", "S21","S31","S41"], dblim=[-40, 6])

ratio_3 = np.abs(S31)
ratio_2 = np.abs(S21)

plot(f/GHz, [ratio_3, ratio_2], labels=['Amplitude 3','Amplitude 2'], xlabel='Frequency (GHz)',ylabel='Coupling Ratio', ylim=[0,1])
############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
field.set_excitations(1,0,0,0)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=200_000).scalar('Ez','complex'), symmetrize=True, clim_crop_factor=0.25)
display.show()