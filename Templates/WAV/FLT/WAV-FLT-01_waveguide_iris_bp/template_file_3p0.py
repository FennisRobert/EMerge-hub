# =============================================================================
# EMerge Simulation Template: Waveguide Iris Bandpass Filter
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
#
# =============================================================================

# -----------------------------------------------------------------------------
# This is a fairly simple simulation model of a waveguide iris bandpass filter.
#
# The filter design comes from the book Microwave Filters for Communication Systems
# by Richard J. Cameron et. al.
#
# Because the E-field is translationally symmetrical in the Z-direction, we actually don't
# need to model the height of the waveguid eat all. We can pick the actual height (10.16*mm)
# or something smaller if we want, it doesn't matter for the frequency dependence.
# The effect it would have is on the total losses but in this case we won't model that for now.
#
# The ideal filter when converged with mesh refinement sits exactly at 11GHz
# You can get a better performance by setting the resolution at 0.05 if you model
# the wavegduie height (wgb) at 1*mm for example.
#
# -----------------------------------------------------------------------------
from emerge_config import config
config.set_acc_threads(10)

import emerge as em
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
f1 = 10.5*GHz
f2 = 11.5*GHz
nf = 41

# --- Geometry dimensions ---------------------------------------------------

w1 = 10.499*mm
w2 = 6.706*mm
w3 = 6.147*mm

Lf = 30*mm
L1 = 14.022*mm
L2 = 15.611*mm

wga = 22.86*mm
wgb = 10.16*mm

th = 2*mm

Ltot = 2*Lf + 2*L1 + 2*L2 + 5*th

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

wgbase = em.geo.Box(wga, Ltot, wgb, (-wga/2, -Lf, -wgb/2))

y0 = 0

iris1L = em.geo.Box((wga-w1)/2, th, wgb, (-wga/2, y0, -wgb/2))
iris1R = em.geo.Box((wga-w1)/2, th, wgb, (w1/2, y0, -wgb/2))

irises = [iris1L, iris1R]
for l,w in zip([L1,L2,L2,L1],[w2,w3,w2,w1]):
    y0 += l + th
    irisL = em.geo.Box((wga-w)/2, th, wgb, (-wga/2, y0, -wgb/2))
    irisR = em.geo.Box((wga-w)/2, th, wgb, (w/2, y0, -wgb/2))
    irises.append(irisL)
    irises.append(irisR)

wgfinal = em.geo.subtract(wgbase, em.geo.unite(*irises))

model.commit_geometry()
model.view()

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency_range(f1,f2,nf)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.10)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

p1 = model.mw.bc.RectangularWaveguide(wgfinal.face('-y'), 1)
p2 = model.mw.bc.RectangularWaveguide(wgfinal.face('+y'), 2)
model.mw.bc.SurfaceImpedance(wgfinal.boundary(exclude=['-y','+y']), material=em.lib.COPPER)

############################################################
#                       RUN SIMULATION                      #
############################################################

#model.adaptive_mesh_refinement(15, frequency=(10.8e9, 11e9, 11.2e9), max_tets=200_000)
data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
S21_fit = g.model_S(2, 1, fdense)
plot_sp(fdense, [S11_fit, S21_fit], labels=["S11", "S21"])

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=11e9)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=100_000).scalar('Ez','complex'), symmetrize=True)
display.show()
