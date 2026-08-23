# =============================================================================
# EMerge Simulation Template: Branchline Coupler
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
# Branchline Coupler / 90 Degree Hybrid (3 GHz)
#
# A four-port coupler built from a square ring of quarter-wavelength
# transmission lines. Power entering one port splits evenly between two
# outputs with a 90 degree phase difference between them, useful for mixers
# and phase-shifting circuits. Tuned to 3 GHz.
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
f1 = 2.5*GHz
f2 = 3.5*GHz
nf = 21

# --- Geometry dimensions ---------------------------------------------------

w0 = 0.98*mm
w1 = 1.7067*mm

Lf = 5*mm
Lq = 14*mm
Lv = 14*mm
dx = 2*mm
dy = 2*mm
o = (w1-w0)/2
w3 = w0*0.5
margin = 5*mm

th = 0.508*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCB(th, 1.0, material=em.lib.DIEL_FR4, trace_material=em.lib.PEC)

print(f'z0 50 = {pcb.calc.z0(50)*1000:.2f}mm')
print(f'z0 50 = {pcb.calc.z0(50/2**0.5)*1000:.2f}mm')

pcb.new(0, 0, w0,(1,0), 1)[1].straight(Lf)['m1'].straight(Lq-2*dx, w1, dx=dx, dy=o).straight(0, w0, dx=dx, dy=-o)['m2'].straight(Lf, w0)[3]
pcb.new(0,-Lv,w0,(1,0), 1)[2].straight(Lf).straight(Lq-2*dx, w1, dx=dx, dy=-o).straight(0, w0, dx=dx, dy=o).straight(Lf, w0)[4]
pcb.new(*pcb['m1'].xy, w3, (0,-1), 1).taper(dy, w0).straight(Lv-2*dy).taper(dy, w3)
pcb.new(*pcb['m2'].xy, w3, (0,-1), 1).taper(dy, w0).straight(Lv-2*dy).taper(dy, w3)

trace = pcb.compile_paths(True)

pcb.determine_bounds(margin, margin,margin, margin)

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

total = np.abs(S31)**2 + np.abs(S41)**2
ratio_3 = np.abs(S31)**2/total
ratio_4 = np.abs(S41)**2/total

plot(f/GHz, [ratio_3, ratio_4], labels=['P3/Ptot','P4/Ptot'], xlabel='Frequency (GHz)',ylabel='Power Ratio', ylim=[0,1])
############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
field.set_excitations(0,1,0)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=200_000).scalar('Ez','complex'), symmetrize=True, clim_crop_factor=0.25)
display.show()