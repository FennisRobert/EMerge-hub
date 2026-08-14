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
f0 = 1.45e9       # center / operating frequency (Hz)
# f1, f2 = ..., ...   # sweep start/stop, if using a frequency range

# --- Geometry dimensions ---------------------------------------------------

radius = 0.5*mm
Lhalf = 50*mm
rad = 5*mm
gap = 1*mm
# Key coordinates
x_left = 0.0
x_mid = rad
x_right = 2 * rad

y_gap = gap / 2.0
y_top_stem = Lhalf
y_top_apex = Lhalf + rad
y_bot_stem = -Lhalf
y_bot_apex = -(Lhalf + rad)

# --- 12 Control Points (Exact Geometry) ---
# Left stem -> Top arc 1 -> Top arc 2 -> Right stem -> Bot arc 1 -> Bot arc 2 -> Left stem
# --- 12 Control Points (Fixed Tangents) ---
xs_path = np.array([
    x_left,   # 0: Feed gap top
    x_left,   # 1: Top of left leg
    x_left,   # 2: Top-left tangent corner (y stays at Lhalf!)
    x_mid,    # 3: Top apex
    x_right,  # 4: Top-right tangent corner (y stays at Lhalf!)
    x_right,  # 5: Top of right leg
    x_right,  # 6: Bottom of right leg
    x_right,  # 7: Bot-right tangent corner (y stays at -Lhalf!)
    x_mid,    # 8: Bottom apex
    x_left,   # 9: Bot-left tangent corner (y stays at -Lhalf!)
    x_left,   # 10: Bottom of left leg
    x_left    # 11: Feed gap bottom
])

zs_path = np.array([
    y_gap,       # 0
    Lhalf,       # 1
    Lhalf + rad, # 2
    Lhalf + rad, # 3
    Lhalf + rad, # 4
    Lhalf,       # 5
    -Lhalf,      # 6
    -(Lhalf + rad), # 7
    -(Lhalf + rad), # 8
    -(Lhalf + rad), # 9
    -Lhalf,      # 10
    -y_gap       # 11
])
degree = 2
w_arc = np.sqrt(2) / 2  # 0.70710678...

weights = np.array([
    1.0, 1.0, w_arc, 1.0, w_arc, 1.0, 1.0, w_arc, 1.0, w_arc, 1.0, 1.0
])

knots = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype=float)
multiplicities = np.array([3, 1, 2, 1, 2, 1, 2, 3], dtype=int)
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

disc = em.geo.XYPolygon.circle(radius, Nsections=8)
path = em.geo.Curve(xs_path, 0*xs_path, zs_path, ctype="BSpline",
                    weights=weights, knots=knots, multiplicities=multiplicities, degree=degree).pipe(disc)

model.view(use_gmsh=True)

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