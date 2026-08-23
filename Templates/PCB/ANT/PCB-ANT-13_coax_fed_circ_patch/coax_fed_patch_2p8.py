# =============================================================================
# EMerge Simulation Template: PCB-ANT-13
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

# -----------------------------------------------------------------------------
# Dual-Feed Circular Patch for Circular Polarization (2.4 GHz)
#
# A round patch antenna fed from two points 90 degrees apart around its edge,
# using the same coax probe feed as PCB-ANT-11. Combining the two feeds with
# a 90 degree phase difference, done after the simulation with
# set_excitations() rather than during it, produces circular polarization,
# commonly used for GPS and radar. Built on a 60 by 70 mm board and tuned to
# 2.4 GHz.
# -----------------------------------------------------------------------------
import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar

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
f0 = 2.4*GHz
f1 = 2.2*GHz
f2 = 2.6*GHz
n_points = 11

# --- Geometry dimensions ---------------------------------------------------

Rpatch = 16.8*mm
feed_distance = 6*mm

ro = 1*mm
ri = em.coax_rin(ro, eps_r=2.1) # Teflon

Lfeed = 5*mm

w0 = 2.88*mm
w1 = 0.5*mm

WPCB = 60*mm
LPCB = 70*mm

th_pcb = 1.5*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("TemplateDemo")
model.check_version("2.8.3")  # Checks version compatibility.

############################################################
#                          GEOMETRY                        #
############################################################

pcb = em.geo.PCBNew(th_pcb, 1.0, material=em.lib.DIEL_FR4)

th = np.linspace(0, 2*PI, 31)[:-1]

pcb.add_poly(Rpatch*np.cos(th), Rpatch*np.sin(th), z=pcb.z(1))

trace = pcb.compile_paths(True)

pcb.determine_bounds(15*mm, 15*mm, 15*mm, 15*mm)

diel = pcb.generate_pcb()
air = pcb.generate_air(20*mm)

# Coax Feed
coax_out_1 = em.geo.Cylinder(ro, Lfeed, em.cs(origin=(-feed_distance, 0, -th_pcb-Lfeed)), Nsections=15).set_material(em.lib.DIEL_TEFLON)
coax_in_1 = em.geo.Cylinder(ri, Lfeed+th_pcb, em.cs(origin=(-feed_distance, 0, -th_pcb-Lfeed)), Nsections=12).set_material(em.lib.COPPER).foreground()
coax_out_2 = em.geo.Cylinder(ro, Lfeed, em.cs(origin=(0,-feed_distance, -th_pcb-Lfeed)), Nsections=15).set_material(em.lib.DIEL_TEFLON)
coax_in_2 = em.geo.Cylinder(ri, Lfeed+th_pcb, em.cs(origin=(0, -feed_distance, -th_pcb-Lfeed)), Nsections=12).set_material(em.lib.COPPER).foreground()

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency_range(f1, f2, n_points)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)

model.mesher.set_boundary_size(trace, 1 * mm)
model.mesher.set_domain_size(coax_out_1, ri)
model.mesher.set_domain_size(coax_out_2, ri)
############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view(assigned_materials=True)
model.view(plot_mesh=True)
############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

abc_boundary = air.boundary(exclude='bottom')
model.mw.bc.AbsorbingBoundary(abc_boundary)

# We will excite circular polarization
model.mw.bc.ModalPort(coax_out_1.face('-z'), 1)
model.mw.bc.ModalPort(coax_out_2.face('-z'), 2)

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
plot_sp(f, [S11], labels=["S11"], dblim=[-40, 6])
smith(S11, f)
# supersample with Vector Fitting for smoother curves
fdense = g.dense_f(2001)
S11_fit = g.model_S(1, 1, fdense)

plot_sp(fdense, [S11_fit], labels=["S11"])

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################
field = data.field.find(freq=f0)
# We will excite 90 degrees out of phase

field.set_excitations(1.0, 1.0*1j)

ff_xz = field.farfield_2d(em.ZAX, em.YAX, abc_boundary)
ff_yz = field.farfield_2d(em.ZAX, em.XAX, abc_boundary)

plot_ff(ff_xz.ang * 180 / np.pi, [ff_xz.gain.lhcp, 
                                  ff_yz.gain.lhcp,
                                  ff_xz.gain.rhcp, 
                                  ff_yz.gain.rhcp], 
        labels=['XZ Plane LHCP','YZ Plane LHCP', 'XZ Plane RHCP','YZ Plane RHCP'], dB=True, ylabel="Gain Circular polarized [dBi]")
plot_ff_polar(ff_xz.ang, ff_yz.gain.norm, dB=True, dBfloor=-20)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################


ff3d = field.farfield_3d(abc_boundary)
display = model.display
display.populate()
display.add_farfield3d(ff3d, 'gain.norm', 'abs', dB=True, dBfloor=-20, rmax=50*mm, opacity=0.5)
display.animate().add_field(field.grid(N=500_000).scalar('Ex','complex'), symmetrize=True, clim_crop_factor=0.5)
display.show()