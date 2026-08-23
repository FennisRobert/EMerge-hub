# =============================================================================
# EMerge Simulation Template: Microstrip tapered lines
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
# Tapered transmission lines on a 20 mil RO4003C substrate
# -----------------------------------------------------------------------------

import subprocess  # Used to run the post-processing script
import time
from datetime import datetime

import numpy as np
import emerge as em

from microstrip_taper_utils import taper_width_profile


# ---------------------------------------------------------------------------
# TAPER SELECTION
# ---------------------------------------------------------------------------
"""
    Set TAPER_TYPE variable according to the desired impedance profile:
        - exponential
        - triangular
        - klopfenstein
        - linear
        - all: Simulate all profiles on a row
    See [1], section 5.8 for reference.
    [1] D. M. Pozar, "Microwave Engineering," 4th ed., Wiley, 2012
"""

ALL_TAPER_TYPES = ["exponential", "triangular", "klopfenstein", "linear"]
TAPER_TYPE = "all"

if TAPER_TYPE == "all":
    RUN_ALL_TAPERS = True
else:
    RUN_ALL_TAPERS = False

GAMMA_MAX  = 0.1         # Maximum return loss. Klopfenstein taper only


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
PI = np.pi
EPS0 = 8.854187818814e-12
MU0 = 1/(C0*C0*EPS0)


############################################################
#                    SUBSTRATE MATERIAL                    #
############################################################
er   = 3.55            # RO4003C relative permittivity
th   = 0.508           # [mm] substrate thickness
tand = 0.0029          # loss tangent


############################################################
#                    DESIGN PARAMETERS                     #
############################################################
f0 = 1500 * MHz        # [Hz] Center frequency
lambda_ = C0/ (np.sqrt(er)*f0)
Z1 = 50.0              # [Ohm] source impedance
Z2 = 15.0              # [Ohm] load impedance (matches the Chebyshev example)

Lfeed  = 5             # [mm] straight Z1 / Z2 feed lines at each end
Ltaper = 1e3*lambda_   # [mm] taper length
N_seg  = 60            # number of straight segments approximating the taper

Hair = 10              # [mm] air box height


############################################################
#                     FREQUENCY SWEEP                      #
############################################################
f_start = 100 * MHz
f_stop  = 5000 * MHz
n_points = 40

# ---------------------------------------------------------------------------
# Run the simulation according to the taper profile selected
# ---------------------------------------------------------------------------
def simulate_taper(taper_type):
    project_name = f"MicrostripTaper_{taper_type}"
    print(f"\n=== Simulating {taper_type} taper -> {project_name} ===")

    # ---------------------------------------------------------------------------
    # Build the impedance / width profile for the chosen taper
    # ---------------------------------------------------------------------------
    z_mid = (np.arange(N_seg) + 0.5) * (Ltaper / N_seg)   # midpoint of each segment [mm]
    Z_profile, W_profile = taper_width_profile(
        taper_type, z_mid, Ltaper, Z1, Z2, er, th, gamma_max=GAMMA_MAX
    )

    # Widths for the clean uniform feed lines at each end
    W_feed_in  = taper_width_profile(taper_type, np.array([0.0]), Ltaper, Z1, Z2, er, th)[1][0]
    W_feed_out = taper_width_profile(taper_type, np.array([Ltaper]), Ltaper, Z1, Z2, er, th)[1][0]

    dz = Ltaper / N_seg


    ############################################################
    #                      SIMULATION SETUP                    #
    ############################################################
    model = em.Simulation(project_name, save_file=True)
    model.check_version("2.8.3")


    ############################################################
    #                          GEOMETRY                        #
    ############################################################
    material = em.Material(er=er, tand=tand, color="#4bc41c", opacity=0.2)
    pcb = em.geo.PCBNew(th, unit=mm, material=material, trace_material=em.lib.PEC)

    # ---------------------------------------------------------------------------
    # Layout: feed(Z1) -> N_seg tapered segments -> feed(Z2)
    # ---------------------------------------------------------------------------
    pcb_margin = 25  # Space at both sides of the copper traces

    path = pcb.new(0, 0, W_feed_in, (1, 0)).store("p1").straight(Lfeed, W_feed_in)

    for w in W_profile:
        path = path.straight(dz, w)

    path = path.straight(Lfeed, W_feed_out).store("p2")

    # --- Compile traces ------------------------------------------------------
    stripline = pcb.compile_paths(True)

    # ---------------------------------------------------------------------------
    # Bounding box, dielectric and air
    # ---------------------------------------------------------------------------
    pcb.determine_bounds(topmargin=pcb_margin, bottommargin=pcb_margin, leftmargin=0, rightmargin=0)
    diel = pcb.generate_pcb(merge=True)
    air  = pcb.generate_air(Hair)

    # ---------------------------------------------------------------------------
    # Modal ports
    # ---------------------------------------------------------------------------
    p1 = pcb.modal_port(pcb.load("p1"), width_multiplier=3, height=Hair)   # Input
    p2 = pcb.modal_port(pcb.load("p2"), width_multiplier=3, height=Hair)   # Output

    ############################################################
    #                   SOLVER / MESH SETTINGS                 #
    ############################################################
    model.mw.set_resolution(0.2)
    model.mw.set_frequency_range(f_start, f_stop, n_points)

    ############################################################
    #                      COMMIT GEOMETRY                     #
    ############################################################
    model.commit_geometry()

    ############################################################
    #               GENERATE, REFINE & VIEW MESH               #
    ############################################################
    model.mesher.set_boundary_size(stripline, 0.5 * mm, growth_rate=10)
    model.mesher.set_face_size(p1, 0.5 * mm)
    model.mesher.set_face_size(p2, 0.5 * mm)

    model.generate_mesh()
    if (not RUN_ALL_TAPERS):
        # Show the mesh only when one individual taper is shown
        model.view(plot_mesh=False)

    ############################################################
    #                   BOUNDARY CONDITIONS                    #
    ############################################################
    port1 = model.mw.bc.ModalPort(p1, 1, modetype='TEM')   # Input
    port2 = model.mw.bc.ModalPort(p2, 2, modetype='TEM')   # Output


    ############################################################
    #                      RUN SIMULATION                      #
    ############################################################
    start_time = time.time()
    data = model.mw.run_sweep(parallel=True, n_workers=8, frequency_groups=8)
    run_time = (time.time() - start_time) / 60
    print(f"Simulation completed in {run_time:.2f} minutes")

    ############################################################
    #                   EXTRACT S-PARAMETERS                   #
    ############################################################
    grid = data.scalar.grid
    f    = grid.freq

    S11 = grid.S(1, 1)
    S21 = grid.S(2, 1)

    ############################################################
    #                VECTOR FITTING (supersampled plot)        #
    ############################################################
    f_fit = np.linspace(f_start, f_stop, 2001)
    f_MHz = f_fit / 1e6    # Used for displaying the graphs
    S11_fit = grid.model_S(1, 1, f_fit)
    S21_fit = grid.model_S(2, 1, f_fit)


    ############################################################
    #                    3D FIELD VISUALIZATION                #
    ############################################################
    field = data.field.find(freq=f0)
    model.display.add_object(diel)
    model.display.add_object(stripline)
    model.display.add_portmode(port1, k0=field.k0)
    model.display.add_field(
        field.cutplane(0.5 * mm, z=-0.5 * th * mm).scalar('Ez', 'real'),
        symmetrize=True,
    )
    if (not RUN_ALL_TAPERS):
        # Hide visualization when running all simulations
        model.display.show()

    ############################################################
    #                     EXPORT TOUCHSTONE                    #
    ############################################################
    grid = data.scalar.grid
    comments = [
        "Substrate: RO4003C",
        f"h = {th} mm",
        f"Taper type: {taper_type}",
        f"Z1 = {Z1} Ohm, Z2 = {Z2} Ohm",
        f"Taper length = {Ltaper} mm, N_seg = {N_seg}",
        f"Lfeed = {Lfeed} mm",
        f"Run time = {run_time:.2f} min",
    ]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = project_name + "_EMerge_" + timestamp
    grid.export_touchstone(
        file_name,
        Z0ref=50.0,
        custom_comments=comments,
        dense_freq=f_fit,
    )

    # Save data for post-processing
    np.savez(
        project_name + "_data.npz",
        f=f_fit, S11=S11_fit, S21=S21_fit,
        z_profile=z_mid, Z_profile=Z_profile, W_profile=W_profile,
        taper_type=taper_type,
    )

    model.save()  # Save EM model for later postprocessing
    return project_name


    ############################################################
    #                       ENTRY POINT                        #
    ############################################################
postfile = "MicrostripTaper_post.py" # Postprocessing script
if RUN_ALL_TAPERS:
    # 1) Simulate all possible impedance profiles
    project_names = [simulate_taper(t) for t in ALL_TAPER_TYPES]
    # 2) Run postprocessing script for comparing all tapered lines
    subprocess.run(["python", postfile, "--compare"] + project_names, check=True)
else:
    # 1) Simulate a single impedance profile
    project_name = simulate_taper(TAPER_TYPE)
    # 2) Run postprocessing script
    subprocess.run(["python", postfile, project_name], check=True)

