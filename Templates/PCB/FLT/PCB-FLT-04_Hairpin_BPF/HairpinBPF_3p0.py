# =============================================================================
# EMerge Simulation Template: Hairpin Bandpass Filter
#
# Copyright (C) 2026 Andrés Martínez Mera
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
# Hairpin BPF (fc = 2500 MHz, RBW = 8 %) 20 mil RO4003C substrate
# -----------------------------------------------------------------------------

from emerge_config import config
config.set_acc_threads(10)

import os
import sys

import emerge as em
import numpy as np
from emerge.plot import plot_sp  # + smith, plot_ff, plot_ff_polar, plot as needed
from datetime import datetime
import time

import matplotlib

for _backend in ("TkAgg", "Qt5Agg", "QtAgg"):
    try:
        matplotlib.use(_backend)
        break
    except Exception:
        continue
else:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

project_name = "HairpinBPF"

############################################################
#                     UNITS & CONSTANTS                    #
############################################################

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

# --- Frequency sweep ---------------------------------------------------------
f1 = 2000*MHz       # [Hz] Start
f2 = 3000*MHz       # [Hz] Stop
nf = 40             # Number of points


# --- Geometry dimensions -----------------------------------------------------
W_50  = 1.1*mm      # [m] 50 ohm feed line width
Lf = 10*mm          # [m] Length of the feed line

Wres  = 0.85*mm     # [m] Resonator trace width (The same for all sections)

Lin    = 3*mm       # [m] Line length of the first/last resonator between the stup and the first corner
Lstub  = 6.5*mm     # [m] Length of the open stub at the input/output
Lside  = 6*mm       # [m] Length of the uncoupled side of the resonator

# Coupled sections
# First and last resonator
L1 = 15.2*mm        # [m] Coupling length
S1 = 0.1*mm         # [m] Coupling gap

# Middle resonators
L2 = 15.42*mm       # [m] Coupling length
S2 = 0.4*mm         # [m] Coupling gap


margin = 10*mm      # [m] Margin betweent the filter and the PCB edge

th = 0.508*mm       # [m] Substrate thickness

############################################################
#                    MATERIAL DEFINITIONS                  #
############################################################

material = em.Material(er=3.55, tand=0.0027, color="#4bc41c", opacity=0.2)

############################################################
#                      SIMULATION SETUP                    #
############################################################

model = em.Simulation("CoupledLineBPF", loglevel='DEBUG')
model.check_version("3.0.0")  # Checks version compatibility.

# We need to set this because otherwise EMerge 2.8 concludes that the Quasi-TEM mode
# is a TE mode which will cause it to make the wrong assumption about the
# out of plane propagation constant.

model.settings.qtem_limit = 0.1

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCB(th, 1.0, material=material, trace_material=em.lib.PEC)
path = pcb.new(0,0, W_50, (1,0), 1)[1]


def add_coupled_resonator(prev, gap, side, reverse_len, seg_len, turn_dir,
                           end_len, taper_back=True):
    """
    Build the Hairpin resonator

    gap        : coupling gap to the previous line (S1 or S2)
    side       : which side of `prev` to jump to ('left'/'right')
    reverse_len: how far back along `prev` the new line starts
    seg_len    : length of the first straight segment (before Wres offset)
    turn_dir   : +90 or -90, sets the "hook" direction of this resonator
    end_len    : length of the final straight segment
    taper_back : if True, step the line width back down by -Wres at the end
    """
    res = prev.jump(gap=gap, side=side, reverse=reverse_len, width=Wres)
    res.straight(seg_len - Wres)
    res.turn(turn_dir)
    res.straight(Lside)
    res.turn(turn_dir)
    res.straight(end_len)
    if taper_back:
        res.straight(-Wres)
    return res


# ---- Input feed + T-junction with open matching stub -----------------------
path.straight(Lf)
path.straight(Wres, Wres)
path.straight(-Wres)
path.store("input_stub")
path.turn(-90)
path.straight(Lstub, Wres)

anchor = pcb.load("input_stub")
path = pcb.new(anchor.x, anchor.y, anchor.width, anchor.direction)

# ---- Resonator 1  --------------------------------------------------
path.turn(90)
path.straight(Lin, Wres)
path.turn(-90)
path.straight(Lside)
path.turn(-90)
path.straight(L1)  # Coupling section between resonators 1 and 2
path.straight(-Wres)

res1 = add_coupled_resonator(path, S1, 'right', L1, L1, +90, L2)

# ---- Resonators 2-3  -----------------------------------------------
res2 = add_coupled_resonator(res1, S2, 'left',  L2, L2, -90, L2)
res3 = add_coupled_resonator(res2, S2, 'right', L2, L2, +90, L1)

# ---- Resonator 5  --------------------------------------------------
res4 = add_coupled_resonator(res3, S1, 'left', L1, L1, -90, Lin,
                              taper_back=False)

# ---- Output matching --------------------------------------------------
output_section = res4
output_section.store("output_stub")
output_section.turn(90)
output_section.straight(Lf, W_50)

anchor = pcb.load("output_stub")

output_stub = pcb.new(anchor.x, anchor.y, anchor.width, anchor.direction)
output_stub.straight(Lstub, Wres)

output_section[2] # Output port


trace = pcb.compile_paths(True)

pcb.determine_bounds(0, margin, 0, margin)

p1 = pcb.modal_port(1, 1, height=4*mm)
p2 = pcb.modal_port(2, 2, height=4*mm)

diel = pcb.generate_pcb()
air = pcb.generate_air(5*mm)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

model.commit_geometry()
#model.export("hairpin.step") # This is useful to check the geometry in FreeCAD

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

model.mw.set_frequency_range(f1, f2, nf)

# Overall mesh resolution
model.mw.set_resolution(0.25)

# The tightest coupling gap (S1 = 0.1 mm) needs a fine mesh here
model.mesher.set_boundary_size(trace, 0.1*mm, growth_rate=10)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view(plot_mesh=True)

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

port1 = model.mw.bc.ModalPort(p1, 1, modetype='TEM')
port2 = model.mw.bc.ModalPort(p2, 2, modetype='TEM')

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep(frequency_groups=8)

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

grid = data.scalar.grid
fdense = grid.dense_f(2001)
S11_fit = grid.model_S(1, 1, fdense)
S21_fit = grid.model_S(2, 1, fdense)
plot_sp(fdense, [S11_fit, S21_fit], labels=["S11", "S21"])

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = project_name + "_EMerge_" + timestamp

comments = [
    "Hairpin bandpass filter",
    f"Wres  = {Wres / mm:.4f} mm",
    f"Lin   = {Lin / mm:.4f} mm",
    f"Lstub = {Lstub / mm:.4f} mm",
    f"Lside = {Lside / mm:.4f} mm",
    f"L1 = {L1 / mm:.4f} mm, S1 = {S1 / mm:.4f} mm",
    f"L2 = {L2 / mm:.4f} mm, S2 = {S2 / mm:.4f} mm",
]

grid.export_touchstone(
    file_name,
    Z0ref=50.0,
    custom_comments=comments,
    dense_freq=fdense,
)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=2.5e9)
display = model.display
display.populate()
display.animate().add_field(field.grid(N=200_000).scalar('Ez', 'complex'), symmetrize=True, clim_crop_factor=0.6)
display.show()
