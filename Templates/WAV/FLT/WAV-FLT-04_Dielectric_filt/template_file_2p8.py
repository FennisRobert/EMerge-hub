# =============================================================================
# EMerge Simulation Template: Dielectric Resonator Filter
#
# Copyright (C) 2026, Robert Fennis
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
# This is a model of an L-band dielectric resonator filter.
# The design comes from the book:
# Microwave Filters for Communication Systems by Richard J. Cameron et. al. (page 474 approximately)
#
# The model is not converged in terms of the mesh because it is quite a heavy model to solve accurately on simpler hardware.
# An adaptive mesh refinement process is advised for more accurate simulations.
#
# -----------------------------------------------------------------------------
from emerge_config import config
config.set_acc_threads(10)

import emerge as em
from emerge.plot import plot_sp  # + smith, plot_ff, plot_ff_polar, plot as needed
from emerge.ext import GeoVolume # Just for type hinting return types

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
f1 = 1.9*GHz
f2 = 1.95*GHz
nf = 21

# --- Geometry dimensions ---------------------------------------------------
Lf = 10*mm
Ld = 12.21*mm
Ds = 14.22*mm
Ls = 20.32*mm
er_1 = 34
ers = 10
C = 50.8*mm
S = 51.5*mm
T = 3.81*mm
W12 = 10.058*mm
W34 = W12
W23 = 6.6548*mm
D14 = 29.87*mm
D23 = 29.66*mm
H = 37.84*mm
G = 0.254*mm
a = 1.117*mm
b = 2.54*mm
F = 7.47*mm

############################################################
#                    MATERIAL DEFINITIONS                  #
############################################################

matres1 = em.Material(er=er_1, color="#ffffff", opacity=0.2)
matres2 = em.Material(er=ers, color="#ffffff", opacity=0.2)

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("2.8.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################
# We create this convenience function for generating resonance elements

def create_cavity(x: float, D: float) -> tuple[GeoVolume, GeoVolume, GeoVolume]:
    box = em.geo.Box(C,C,S, (x, -C/2, 0)).prio_set(5)
    post = em.geo.Cylinder(Ds/2, Ls, em.cs(origin=(x+C/2, 0, 0))).set_material(matres2)
    resonator = em.geo.Cylinder(D/2, Ld, em.cs(origin=(x+C/2, 0, Ls))).set_material(matres1)
    return box, post, resonator

b1, p1, r1 = create_cavity(0, D14)
b2, p2, r2 = create_cavity(C+T, D23)
b3, p3, r3 = create_cavity(2*C+2*T, D23)
b4, p4, r4 = create_cavity(3*C+3*T, D14)

w1 = em.geo.Box(T, W12, S, (C, C/2-W12, 0))
w2 = em.geo.Box(T, W23, S, (C+T+C, C/2-W23, 0))
w3 = em.geo.Box(T, W34, S, (C+2*T+2*C, C/2-W34, 0))

feed_center_1 = em.geo.Cylinder(a, H+Lf, em.XAX.construct_cs((-Lf, -F,Ls+Ld+G+a)), Nsections=12).set_material(em.lib.PEC).prio_set(15)
feed_center_1_out = em.geo.Cylinder(b, Lf, em.XAX.construct_cs((-Lf, -F,Ls+Ld+G+a)), Nsections=14)

feed_center_2 = em.geo.mirror(feed_center_1, (2*C+1.5*T, 0, 0), (1,0,0))
feed_center_2_out = em.geo.mirror(feed_center_1_out, (2*C+1.5*T, 0, 0), (1,0,0))
############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()
model.view()
############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.

model.mw.set_frequency_range(f1, f2, nf)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.1)


############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()


############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

p1 = model.mw.bc.ModalPort(feed_center_1_out.face('-x'), 1)
p2 = model.mw.bc.ModalPort(feed_center_2_out.face('-x'), 2)

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid

# Optional: supersample with Vector Fitting for smoother curves
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
S21_fit = g.model_S(2, 1, fdense)
plot_sp(fdense, [S11_fit, S21_fit], labels=["S11", "S21"])

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=1.925e9)

display = model.display
display.populate()
display.cbar('Ey',clim=(-5e3,5e3)).animate().add_field(field.grid(N=100_000).scalar('Ey','complex'), symmetrize=True)
display.show()