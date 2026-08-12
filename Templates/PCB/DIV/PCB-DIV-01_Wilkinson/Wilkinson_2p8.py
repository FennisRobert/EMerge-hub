# =============================================================================
# EMerge Simulation Template: Stepped Impedance Low-Pass Filter
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
# Basic Wilkinson power divider on an 0.508mm FR4 substrate
# -----------------------------------------------------------------------------
from emerge_config import config
config.set_acc_threads(10)

import emerge as em
import numpy as np
from emerge.plot import plot_sp  # + smith, plot_ff, plot_ff_polar, plot as needed

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
f1 = 2*GHz
f2 = 3*GHz
nf = 31

# --- Geometry dimensions ---------------------------------------------------

w0 = 0.98*mm
w1 = 0.51*mm

Lf = 5*mm
Ltot = 22.5*mm
Lside = 5*mm
Lgap = 1*mm
Lforward = Ltot-Lside-Lgap-Lside
margin = 5*mm

th = 0.508*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("2.8.3")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCBNew(th, 1.0, material=em.lib.DIEL_FR4, trace_material=em.lib.PEC)

print(f'z0 50 = {pcb.calc.z0(50)*1000:.2f}mm')
print(f'z0 70 = {pcb.calc.z0(2**0.5*50)*1000:.2f}mm')

pcb.new(0,0,w0,(1,0), z=pcb.z(1))[1].straight(Lf)\
    .split((0,1), width=w1).straight(Lside).pturn(90, corner_type='champher')\
    .straight(Lforward).pturn(90, corner_type='champher').straight(Lside-Lgap/2)\
    .lumped_element(lambda f: 100.0, (Lgap, Lgap/2))\
    .jump(0, Lgap+w0/2, w0, (1,0)).curve(-90, Lf).straight(1*mm)[2].merge()\
    .split((0,-1), width=w1).straight(Lside).pturn(-90, corner_type='champher')\
    .straight(Lforward).pturn(-90, corner_type='champher').straight(Lside-Lgap/2)\
    .jump(0, -w0/2, w0, (1,0)).curve(90, Lf).straight(1*mm)[3]

trace = pcb.compile_paths(True)

pcb.determine_bounds(margin, margin,margin, margin)

p1 = pcb.lumped_port(1)
p2 = pcb.lumped_port(2)
p3 = pcb.lumped_port(3)

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

lp1 = model.mw.bc.LumpedPort(p1, 1)
lp2 = model.mw.bc.LumpedPort(p2, 2)
lp3 = model.mw.bc.LumpedPort(p3, 3)
le = model.mw.bc.LumpedElement(le[0])

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
plot_sp(f, [S11, S21, S31], labels=["S11", "S21","S31"], dblim=[-40, 6])

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 2)
S21 = g.S(2, 2)
S31 = g.S(3, 2)
plot_sp(f, [S11, S21, S31], labels=["Reverse Transmission (S12)", "Output RL(S22)","Output Isolation (S31)"], dblim=[-40, 6])

# Optional: supersample with Vector Fitting for smoother curves
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1)
S21_fit = g.model_S(2, 1)
S31_fit = g.model_S(3, 1)
plot_sp(fdense, [S11_fit, S21_fit, S31_fit], labels=["S11", "S21", "S31"])

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
field.set_excitations(0,1,0)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=200_000).scalar('Ez','complex'), symmetrize=True, clim_crop_factor=0.25)
display.show()