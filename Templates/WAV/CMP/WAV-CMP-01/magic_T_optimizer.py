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
# -----------------------------------------------------------------------------
# AI ASSISTANCE NOTICE (Uncomment if generated/assisted by an LLM):
# This script was generated or assisted using Large Language Models (LLMs).
# In accordance with EU copyright principles, pure AI-generated output resides 
# in the public domain (CC0 1.0 Universal). Human edits, architectural layout,
# and solver integrations are licensed under GNU GPL v2.
# =============================================================================

# -----------------------------------------------------------------------------
# <SHORT, CATCHY TITLE OF THE DEMO> (e.g. "Grounded Coplanar Waveguide Filter")
#
# <One or two sentence summary of what this demo shows and why it's
#  interesting/useful. Mention the EMerge feature(s) being highlighted,
#  e.g. "This demo shows how to use the PCBLayouter to route a stripline
#  filter and extract its S-parameters."
#
#  Optional extras worth including here:
#   - Reference to a textbook / paper / video the design is based on
#   - Expected RAM / runtime if the simulation is heavy
#   - Author credit, e.g. "Demo by <name>"
#   - Any known caveats (e.g. "resonance is a bit low due to coarse mesh")
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


# --- Frequency ------------------------------------------------------------
f1 = 9*GHz
f2 = 11*GHz
nf = 21

# --- Geometry dimensions ---------------------------------------------------

wga = 22.86*mm
wgb = 10.16*mm
L = 50*mm


Ri = 1*mm

Ro = 14.938*mm
Hlarge = 4.969*mm
Hsmall = 8.179*mm
ydist = 8.500*mm
iris_open = 895.062*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo", loglevel='INFO')
model.check_version("3.0.0")  # Checks version compatibility.

model.opt.add_param('Ro', Ro, (5*mm, 15*mm))
model.opt.add_param('Hlarge', Hlarge, (2*mm, 15*mm))
model.opt.add_param('Hsmall', Hsmall, (2*mm, 15*mm))
model.opt.add_param('ydist', Hsmall, (2*mm, 15*mm))
model.opt.add_param('iris_open', iris_open, (0.1, 0.9))
model.opt.set_method('direct')

for Ro, Hlarge, Hsmall, ydist, iris_open, in model.opt.run(200, True):
        
    ############################################################
    #                          GEOMETRY                        #
    ############################################################

    wg_sum = em.geo.Box(wga, L-1*mm, wgb, (-wga/2, -L, -wgb))
    wg_12 = em.geo.Box(2*L, wga, wgb, (-L, 0, -wgb))
    wg_diff = em.geo.Box(wgb, wga, L, (-wgb/2, 0, 0))
    iris_wg = em.geo.Box(wga*iris_open, 1*mm, wgb, (-wga/2*iris_open, -1*mm, -wgb))
        
    wgtot = em.geo.unite(wg_sum, wg_12, wg_diff, iris_wg)

    cone1 = em.geo.Cone((0, wga-ydist, -wgb), em.ZAX.np*Hlarge, Ro, Ri)
    cyl = em.geo.Cylinder(Ri, Hsmall, em.cs(origin=(0, wga-ydist, -wgb+Hlarge)))

    matcher = em.geo.add(cone1, cyl)
    final = em.geo.subtract(wgtot, matcher)
    
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
    model.mw.set_resolution(0.15)
    ############################################################
    #                    GENERATE & VIEW MESH                   #
    ############################################################
    model.generate_mesh()
    #model.view(plot_mesh=True)
    ############################################################
    #                    BOUNDARY CONDITIONS                    #
    ############################################################


    p1 = model.mw.bc.RectangularWaveguide(final.face('-x'), 3)
    p2 = model.mw.bc.RectangularWaveguide(final.face('+x'), 4)
    p3 = model.mw.bc.RectangularWaveguide(final.face('-y'), 1)
    p4 = model.mw.bc.RectangularWaveguide(final.face('+z'), 2)

    ############################################################
    #                       RUN SIMULATION                      #
    ############################################################

    data = model.mw.run_sweep()
    g = data.scalar.grid
    S11 = (np.max(np.abs(g.S(1,1))))
    S22 = (np.max(np.abs(g.S(2,2))))
    p = 2
    score = max(S11,S22)
    
    model.opt.update(score)
    model.reset(data=True)
    

answer, value = model.opt.best
for key,value in answer.items():
    print(f'{key} = {value*1000:.3f}*mm')
############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
S21 = g.S(2, 1)
S31 = g.S(3, 1)
S41 = g.S(4, 1)

plot_sp(f, [S11, S21, S31, S41], labels=["S11", "S21", "S31", "S41"], dblim=[-40, 6])

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=8e9)
field.set_excitations(1,0,0,0)
display = model.display
display.populate()
display.add_portmode(p1, k0=field.k0)
display.add_portmode(p2, k0=field.k0)
display.add_portmode(p3, k0=field.k0)
display.add_portmode(p4, k0=field.k0)
display.animate().add_field(field.grid(N=200_000).scalar('Emag','complex'), symmetrize=False)
display.show()