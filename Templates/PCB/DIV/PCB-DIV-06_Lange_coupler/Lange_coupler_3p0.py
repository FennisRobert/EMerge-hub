# =============================================================================
# EMerge Simulation Template: Lange Coupler
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
# =============================================================================

# -----------------------------------------------------------------------------
# This models a 3GHz Lange coupler. Under construction
# It requires up to 8GB of RAM
# 
# The model as is is not perfectly tuned for good performance. I (Robert) who made
# The model does not know a whole lot about Lange couplers so, feel free to improve on it!
# -----------------------------------------------------------------------------
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
f0 = 3*GHz
f1 = 1*GHz
f2 = 5*GHz
nf = 21

# --- Geometry dimensions ---------------------------------------------------

w0 = 0.49*mm
w1 = 0.05*mm
r0b = 0.025*mm

margin = 1*mm
Lf = 2*mm
Lt = 15*mm
Lh = Lt/2
ds = 0.2*mm

th = 0.258*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCB(th, 1.0, material=em.lib.DIEL_FR4, trace_material=em.lib.PEC)

print(pcb.calc.z0(50)*1000)
pcb.new(-Lf-w0,-Lh-w0/2-ds-w1, w0, (1,0), 1)[1].straight(Lf).turn(-90, corner_type='champher').straight(ds)
pcb.new(-Lf-w0, Lh+w0/2+ds+w1, w0, (1,0), 1)[2].straight(Lf-2*w1).turn(90, corner_type='champher').straight(ds)

pcb.new(Lf+w0-w1,-Lh-w0/2-ds-w1, w0, (-1,0), 1)[3].straight(Lf-2*w1).turn(90, corner_type='champher').straight(ds)
pcb.new(Lf+w0-w1, Lh+w0/2+ds+w1, w0, (-1,0), 1)[4].straight(Lf).turn(-90, corner_type='champher').straight(ds)


poly1 = pcb.plane(pcb.z(1), w1, Lt+2*w1, (-w1, -Lh-w1))
poly2 = pcb.plane(pcb.z(1), w1, Lh+2*w1, (-5*w1, -Lh-w1))
poly3 = pcb.plane(pcb.z(1), w1, Lt+1*w1, (-3*w1, -Lh))
poly4 = pcb.plane(pcb.z(1), w1, Lt+1*w1, (w1, -Lh-w1))
poly5 = pcb.plane(pcb.z(1), w1, Lh+2*w1, (3*w1, -w1))
trace = pcb.compile_paths(True)

metal = em.geo.unite(poly1, poly2, poly3, poly4, poly5, trace)

pcb.determine_bounds(margin, margin, margin, margin)

p1 = pcb.lumped_port(1, 1)
p2 = pcb.lumped_port(2, 2)
p3 = pcb.lumped_port(3, 3)
p4 = pcb.lumped_port(4, 4)

le = pcb.lumped_elements
diel = pcb.generate_pcb()
air = pcb.generate_air(2*mm)

# bond wires
def make_bondwire(x0, y0):
    boxout = em.geo.Box(2*r0b+4*w1, 2*r0b, 2*w1+r0b, (x0-r0b, y0-r0b, 0))
    boxin = em.geo.Box(-2*r0b+4*w1, 2*r0b, 2*w1-r0b, (x0+r0b, y0-r0b, 0))
    wire = em.geo.subtract(boxout, boxin).set_material(em.lib.PEC).prio_set(20)
    return wire

wire1 = make_bondwire(-4.5*w1,0)
wire2 = make_bondwire(-2.5*w1,-Lh+w1/2)
wire3 = make_bondwire(-2.5*w1,+Lh-w1/2)
wire4 = make_bondwire(-0.5*w1,0)

wires = em.geo.unite(wire1, wire2, wire3, wire4)
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
model.mesher.set_boundary_size(metal, 0.05*mm, growth_rate=5)
model.mesher.set_domain_size(wires, r0b)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

# Set automatically in 3.0

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

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
field.set_excitations(0,1,0)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=500_000, z_range=(-th, th)).scalar('Ez','complex'), symmetrize=True, clim_crop_factor=0.5)
display.show()