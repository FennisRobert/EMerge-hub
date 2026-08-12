# =============================================================================
# EMerge Simulation Template: Open-Circuited Stub Low-Pass Filter
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
# Based on / Reference Design:
# Video: "Design of an Open-Circuited Stub Microstrip Low Pass Filter"
# Channel: The Frequency Domain
# Source: https://www.youtube.com/watch?v=J824cc60xpo
#
# Note: This code is an independent simulation implementation of the 5th-order 
# Chebyshev open-stub microstrip low-pass filter design and geometry presented 
# in the reference tutorial above.
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
f1 = 1*GHz
f2 = 20*GHz
nf = 31

# --- Geometry dimensions ---------------------------------------------------

w0, w1, wu1, w2, wu2, w3 = (1.12*mm, 0.07*mm, 0.5*mm, 2.25*mm, 0.33*mm, 2.97*mm)
l0, l1, lu1, l2, lu2, l3 = (2.5*mm, 2.44*mm, 2.31*mm, 2.16*mm, 2.35*mm, 2.13*mm)

Lf = 10*mm
margin = 5*mm


th = 0.508*mm

############################################################
#                    MATERIAL DEFINITIONS                  #
############################################################

material = em.Material(er=3.55, tand=0.0027, color="#4bc41c", opacity=0.2)

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("2.8.3")  # Checks version compatibility.

# We need to set this because otherwise EMerge 2.8 concludes that the Quasi-TEM mode
# is a TE mode which will cause it to make the wrong assumption about the 
# out of plane propagation constant.

model.settings.qtem_limit = 0.1

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCBNew(th, 1.0, material=material, trace_material=em.lib.PEC)

pcb.new(0,0, w0, (1,0), pcb.z(1))[1].straight(l0)\
    .stub((0,-1), w1, l1+w0/2)\
    .straight(lu1+w2/2, wu1)\
    .stub((0,-1), w2, l2+wu1/2)\
    .straight(lu2+w2/2+w3/2, wu2)\
    .stub((0,-1), w3, l3+wu2/2)\
    .straight(lu2+w2/2+w3/2, wu2)\
    .stub((0,-1), w2, l2+wu1/2)\
    .straight(lu1+w2/2, wu1)\
    .stub((0,-1), w1, l1+w0/2)\
    .straight(l0, w0)[2]
    


trace = pcb.compile_paths(True)

pcb.determine_bounds(0, margin, 0, margin)

p1 = pcb.modal_port(1, height=4*mm)
p2 = pcb.modal_port(2, height=4*mm)

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

port1 = model.mw.bc.ModalPort(p1, 1, modetype='TEM')
port2 = model.mw.bc.ModalPort(p2, 2, modetype='TEM')

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
plot_sp(f, [S11, S21], labels=["S11", "S21"], dblim=[-40, 6])

# Optional: supersample with Vector Fitting for smoother curves
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
S21_fit = g.model_S(2, 1, fdense)
plot_sp(fdense, [S11_fit, S21_fit], labels=["S11", "S21"])

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=9e9)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=200_000).scalar('Ez','complex'), symmetrize=True)
display.show()