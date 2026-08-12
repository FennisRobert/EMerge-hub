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
f0 = 10e9       # center / operating frequency (Hz)
# f1, f2 = ..., ...   # sweep start/stop, if using a frequency range

# --- Geometry dimensions ---------------------------------------------------



############################################################
#                    MATERIAL DEFINITIONS                  #
############################################################

# mymat = em.Material(er=er, tand=tand, color="#217627", opacity=0.3)

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################


############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency(f0)
# model.mw.set_frequency_range(f1, f2, n_points)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)

# Optional: refine the mesh locally around critical features
# (edges, ports, small gaps, vias, etc.)
# model.mesher.set_boundary_size(<selection>, 0.5 * mm)
# model.mesher.set_face_size(<selection>, 0.5 * mm)
# model.mesher.set_domain_size(<selection>, 1 * mm)

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

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

# g = data.scalar.grid
# f = g.freq
# S11 = g.S(1, 1)
# S21 = g.S(2, 1)
# plot_sp(f, [S11, S21], labels=["S11", "S21"], dblim=[-40, 6])

# Optional: supersample with Vector Fitting for smoother curves
# fdense = g.dense_f(2001)
# S11_fit = g.model_S(1, 1, fdense)
# S21_fit = g.model_S(2, 1, fdense)
# plot_sp(fdense, [S11_fit, S21_fit], labels=["S11", "S21"])

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

# ff = data.field.find(freq=f0).farfield_2d((1, 0, 0), (0, 1, 0), <boundary>)
# plot_ff(ff.ang * 180 / np.pi, ff.gain.norm, dB=True, ylabel="Gain [dBi]")
# plot_ff_polar(ff.ang, ff.gain.norm, dB=True, dBfloor=-20)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=f0)
display = model.display
display.populate()