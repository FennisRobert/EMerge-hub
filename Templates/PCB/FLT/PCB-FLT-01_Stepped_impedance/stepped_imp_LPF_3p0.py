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
# Stepped-Impedance Low-Pass Filter
#
# A low-pass filter built from six alternating sections of wide and narrow
# microstrip trace. Wide sections behave like small inductors and narrow
# sections like small capacitors, so the alternating pattern approximates a
# classic LC low-pass filter using only trace geometry. Swept from 1 to
# 5 GHz on a 1.58 mm substrate.
#
# Based on / Reference Design:
# "Design and simulation of a stepped impedance low-pass filter using Altair FEKO"
# Author: Saranraj Karuppuswami_21591
# Source: https://community.altair.com/discussion/33328/design-and-simulation-of-a-stepped-impedance-low-pass-filter-using-altair-feko
#
# Note: This file is an independent implementation of the filter geometry
# and parameters described in the reference post above.
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
f2 = 5*GHz
nf = 51

# --- Geometry dimensions ---------------------------------------------------

Ws = (11.3*mm, 0.428*mm, 11.3*mm, 0.428*mm, 11.3*mm, 0.428*mm)
Ls = (2.05*mm, 6.63*mm, 7.69*mm, 9.04*mm, 5.63*mm, 2.41*mm)
w0 = 3.1*mm
Lf = 10*mm
margin = 5*mm


th = 1.58*mm

############################################################
#                    MATERIAL DEFINITIONS                  #
############################################################

material = em.Material(er=4.2, tand=0.01, color="#4bc41c", opacity=0.2)

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCB(th, 1.0, material=material, trace_material=em.lib.PEC)

pcb.new(0,0, w0, (1,0), 1)[1].straight(Lf)\
    .straight(Ls[0], Ws[0])\
    .straight(Ls[1], Ws[1])\
    .straight(Ls[2], Ws[2])\
    .straight(Ls[3], Ws[3])\
    .straight(Ls[4], Ws[4])\
    .straight(Ls[5], Ws[5])\
    .straight(Lf, w0)[2]


trace = pcb.compile_paths(True)

pcb.determine_bounds(0, margin, 0, margin)

p1 = pcb.modal_port(1, 1, height=4*mm)
p2 = pcb.modal_port(2, 2, height=4*mm)

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
plot_sp(f, [S11, S21], labels=["S11", "S21"], dblim=[-40, 6])

# Optional: supersample with Vector Fitting for smoother curves
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
S21_fit = g.model_S(2, 1, fdense)
plot_sp(fdense, [S11_fit, S21_fit], labels=["S11", "S21"])

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=1.5e9)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=200_000).scalar('Ez','complex'), symmetrize=True)
display.show()