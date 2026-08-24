# =============================================================================
# EMerge Simulation Template: PCB-ANT-16
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
# -----------------------------------------------------------------------------
# AI ASSISTANCE NOTICE:
# This script was generated or assisted using Large Language Models (LLMs).
# In accordance with EU copyright principles, pure AI-generated output resides 
# in the public domain (CC0 1.0 Universal). Human edits, architectural layout,
# and solver integrations are licensed under GNU GPL v2.
# =============================================================================
# -----------------------------------------------------------------------------
# 2x1 Patch Antenna Array with Power Divider
#
# Two patch antennas side by side, powered from a single input that splits
# into two branches at a T-junction in the feed trace. Each branch has a
# short impedance-matching section before it reaches its patch, so both
# patches radiate together in phase, forming a small array. Built on
# RO4003C substrate and tuned to 2.4 GHz.
# -----------------------------------------------------------------------------

import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar

############################################################
#                     UNITS & CONSTANTS                     #
############################################################

mm = 0.001               # meters per millimeter
c0 = 299792458.0         # speed of light in vacuum (m/s)

############################################################
#             SUBSTRATE / FREQUENCY PARAMETERS              #
############################################################

er = 3.38                # relative permittivity (RO4003C-like)
tand = 0.0027             # loss tangent (informational)
th = 1.524 * mm           # substrate thickness

f0 = 2.40e9               # design / center frequency (ISM band)
f1, f2 = 2.30e9, 2.50e9   # sweep band
n_points = 11

lambda0 = c0 / f0          # free-space wavelength at f0

############################################################
#     STEP 1: PATCH DIMENSIONS (TRANSMISSION-LINE MODEL)   #
############################################################

# Patch width for good radiation efficiency
W_patch = c0 / (2 * f0) * np.sqrt(2 / (er + 1))

# Effective dielectric constant seen by the patch
eps_eff_patch = (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * th / W_patch) ** -0.5

# Fringing-field length extension (each open end)
dL = (
    0.412 * th * (eps_eff_patch + 0.3) * (W_patch / th + 0.264)
    / ((eps_eff_patch - 0.258) * (W_patch / th + 0.8))
)

# Physical patch length, corrected for fringing
L_eff = c0 / (2 * f0 * np.sqrt(eps_eff_patch))
L_patch = L_eff - 2 * dL

# We make the patch a little shorter ot make it resonate at 2.4GHz at a coarser mesh
# With a fine mesh the resonance frequency approaches 2.4GHz
# To save some RAM we make it a bit shorter to correct for the drift due to the
# discretization
L_patch = L_patch * 0.975

# Approximate radiating-edge resistance (Balanis' single-slot approximation)
R_edge = 90 * (er ** 2 / (er - 1)) * (L_patch / W_patch) ** 2

print(f"Patch size:        {W_patch / mm:.2f} mm (W) x {L_patch / mm:.2f} mm (L)")
print(f"Edge impedance:     {R_edge:.1f} ohm (approx.)")

############################################################
#   STEP 2: FEED-LINE WIDTHS & QUARTER-WAVE TRANSFORMER      #
############################################################


def microstrip_eps_eff(w: float, h: float, er: float) -> float:
    """Effective permittivity of a microstrip line (Hammerstad-Jensen approx)."""
    ratio = w / h
    if ratio >= 1:
        return (er + 1) / 2 + (er - 1) / 2 * (1 + 12 / ratio) ** -0.5
    return (er + 1) / 2 + (er - 1) / 2 * (
        (1 + 12 / ratio) ** -0.5 + 0.04 * (1 - ratio) ** 2
    )


# We use the PCB layouter purely for its microstrip impedance calculator here;
# the actual trace geometry is routed with it further below.
pcb = em.geo.PCB(th, unit=1.0, material=em.lib.DIEL_RO4003C)

Z_in = 50.0                       # main input line impedance
Z_branch = 100.0                  # impedance each branch must present at the T
Z_t = np.sqrt(Z_branch * R_edge)  # quarter-wave transformer impedance

w_in = pcb.calc.z0(Z_in)       # 50 ohm trunk line width
w_t = pcb.calc.z0(Z_t)         # transformer line width
w_branch = pcb.calc.z0(Z_branch)  # matched 100 ohm line width (past the transformer)

eps_eff_t = microstrip_eps_eff(w_t, th, er)
lambda_g_t = lambda0 / np.sqrt(eps_eff_t)
Lq = lambda_g_t / 4        # physical quarter-wave transformer length

print(f"Transformer:        Zt = {Z_t:.1f} ohm, width = {w_t / mm:.2f} mm, length = {Lq / mm:.2f} mm")

############################################################
#            STEP 3: ARRAY SPACING & FEED ROUTING            #
############################################################

# The quarter-wave transformer's length (Lq) is fixed by physics, but it is
# far too short to also serve as the lateral offset between the two patches.
# So we keep the transformer as a dedicated straight segment right after the
# T-junction, then continue routing at the (already matched) 100 ohm width -
# extra length here does not affect the match, only the physical layout.
element_spacing = 0.75 * lambda0  
d_up = 8 * mm 
d_branch = element_spacing / 2 - Lq  
############################################################
#                      SIMULATION SETUP                     #
############################################################

model = em.Simulation("PatchArray2x1")
model.check_version("3.0.0")  # Checks version compatibility.

############################################################
#                    FEED NETWORK ROUTING                   #
############################################################

L_in = 20 * mm  # trunk length from the input connector to the T-junction

# Trunk up to the T-junction at (0,0), then a point-symmetric pair of
# branches: each one heads sideways (transformer, then matched line), then
# turns the SAME way relative to its own heading, so both end up running
# parallel and feed both patches from the same relative edge (in phase).
pcb.new(0, -L_in, w_in, (0, 1)).store("pin").straight(L_in) \
    .split(direction=(-1, 0)) \
    .straight(Lq, w_t) \
    .straight(d_branch, w_branch) \
    .turn(90) \
    .straight(d_up, w_branch).store("feedL") \
    .merge() \
    .split(direction=(1, 0)) \
    .straight(Lq, w_t) \
    .straight(d_branch, w_branch) \
    .turn(-90) \
    .straight(d_up, w_branch).store("feedR")

# All segments connect back to the T-junction, so merging gives one trace
traces = pcb.compile_paths(merge=True)

############################################################
#                    PATCH RADIATOR ELEMENTS                #
############################################################

# Read back the ACTUAL routed feed-point coordinates rather than computing
# them by hand - this keeps the script correct regardless of the exact sign
# convention .turn() uses internally.
xL, yL = pcb.load("feedL").xy
xR, yR = pcb.load("feedR").xy

# Patches are oriented with their radiating edges along X (width W_patch)
# and their resonant/feed axis along Y (length L_patch), fed at the center
# of the edge the routed branch arrives at.
patch_L = em.geo.XYPlate(W_patch, L_patch, position=(xL - W_patch / 2, yL, 0))
patch_R = em.geo.XYPlate(W_patch, L_patch, position=(xR - W_patch / 2, yR, 0))

copper = em.geo.unite(traces, patch_L)
copper = em.geo.unite(copper, patch_R)
copper.set_material(em.lib.PEC)

############################################################
#                   PORT + PCB / AIR VOLUMES                 #
############################################################

# Lumped port at the open (bottom) end of the input trunk
pin_port = pcb.lumped_port(pcb.load("pin"), 1)

# Extend the board bounds so it fully covers both patches, not just the
# trace. We pad top AND bottom generously since the exact side the bends
# land on depends on the turn() sign convention - a little extra dielectric
# and ground is harmless.
pcb.determine_bounds(
    leftmargin=W_patch / 2 + 30 * mm,
    rightmargin=W_patch / 2 + 30 * mm,
    topmargin=W_patch + 20 * mm,
    bottommargin=10*mm,
)

ground = pcb.plane(pcb.z(0))   # full ground plane on the bottom copper layer
diel = pcb.generate_pcb()       # substrate dielectric block

# Open radiation boundary enclosing the whole board with room to spare
air_margin = 0.5 * lambda0
air = em.geo.open_region(0, 0, (0, air_margin))

############################################################
#                      COMMIT GEOMETRY                       #
############################################################

model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                  #
############################################################

model.mw.set_frequency_range(f1, f2, n_points)
model.mw.set_resolution(0.15)

model.mesher.set_boundary_size(copper, 1 * mm)
model.mesher.set_face_size(pin_port, 0.3 * mm)

############################################################
#                    GENERATE & VIEW MESH                    #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                     #
############################################################
abc_boundary = air.boundary(exclude='-z')
abc = model.mw.bc.AbsorbingBoundary(abc_boundary)

model.view(bc=True)

############################################################
#                       RUN SIMULATION                       #
############################################################

data = model.mw.run_sweep()

############################################################
#                  POST-PROCESSING: S-PARAMETERS              #
############################################################

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
plot_sp(f, [S11], labels=["S11"], dblim=[-30, 3])
smith(S11, f=f)

# Supersample with Vector Fitting for a smoother curve
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)
plot_sp(fdense, [S11_fit], labels=["S11"])

############################################################
#              POST-PROCESSING: FAR-FIELD PATTERNS            #
############################################################

field = data.field.find(freq=f0)

# farfield_2d takes the broadside direction and the cut-plane's normal.
# Broadside is +Z; the E-plane cut (containing the resonant/feed axis, Y)
# has normal X, and the H-plane cut (along the array axis, X) has normal Y.
ff_E = field.farfield_2d(em.ZAX, em.XAX, abc_boundary)
ff_H = field.farfield_2d(em.ZAX, em.YAX, abc_boundary)

plot_ff(
    ff_E.ang * 180 / np.pi,
    [ff_E.gain.norm, ff_H.gain.norm],
    labels=["E-plane", "H-plane"],
    dB=True,
    ylabel="Gain [dBi]",
    xlabel="Theta (deg)",
)
plot_ff_polar(ff_E.ang, ff_E.gain.norm, dB=True, dBfloor=-20)

############################################################
#                    3D FIELD VISUALIZATION                   #
############################################################

model.display.populate()

ff3d = field.farfield_3d(abc_boundary)
model.display.add_farfield3d(
    ff3d, "gain.norm", "abs", dB=True, dBfloor=-20, rmax=0.5 * element_spacing, opacity=0.5
)

# Horizontal cut a few mm above the array shows the interference pattern
# between the two elements - the whole point of building an array!
model.display.animate().add_field(
    field.grid(N=200_000).scalar("Ey", "complex"), symmetrize=True, clim_crop_factor=0.2
)
model.display.show()