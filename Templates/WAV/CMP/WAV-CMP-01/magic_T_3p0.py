# =============================================================================
# EMerge Simulation Template: Magig-Tee | WAV-CMP-02
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
# =============================================================================

# -----------------------------------------------------------------------------
# Waveguide Magic-Tee
#
# This model is a rectangular waveguide (WR90) Magic-Tee. A magic-tee is a 4 port
# waveguide component that has similar characteristics as a Ratrace combiner in 
# stripline circuits.
# Two of its ports are called the sum (Σ) (port 1) and delta (Δ) (port 2) which when
# driven excite the two other ports in the same phase when driven by the sum port
# and in opposite phase when driven at the delta port. 
#
# The matching circuit is optimized using the script called magic_T_optimizer.py.
# It requires emerge version 3.0.0a12 or later if you want to optimize from scratch using
# the "direct" optimizer. It takes about 200 runs to find an optimum.
#
# -----------------------------------------------------------------------------

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


# --- Frequency ------------------------------------------------------------
f1 = 8*GHz
f2 = 12*GHz
nf = 21

# --- Geometry dimensions ---------------------------------------------------

wga = 22.86*mm
wgb = 10.16*mm
L = 50*mm

Ri = 1*mm

Ro = 14.739*mm
Hlarge = 5.672*mm
Hsmall = 8.350*mm
ydist = 8.330*mm
iris_open = 894.206*mm

############################################################
#                      SIMULATION SETUP                    #
############################################################


model = em.Simulation("WaveguideMagicT")
model.check_version("3.0.0")  # Checks version compatibility.

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
model.mw.set_resolution(0.12)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################
model.generate_mesh()

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

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid
f = g.freq
S11 = g.S(1, 1)
S22 = g.S(2, 2)
S31 = g.S(3, 1)
S32 = g.S(3, 2)

plot_sp(f, [S11, S22, S31, S32], labels=["S11", "S22", "S31", "S32"], dblim=[-40, 6], spec_area=[(9e9, 11e9, -20,0)])

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

field = data.field.find(freq=10e9)
field.set_excitations(1,0,0,0)
display = model.display
display.populate()
display.add_portmode(p1, k0=field.k0)
display.add_portmode(p2, k0=field.k0)
display.add_portmode(p3, k0=field.k0)
display.add_portmode(p4, k0=field.k0)
display.cbar('|E|', clim=[0,3e3]).animate().add_field(field.grid(N=200_000).scalar('Emag','complex'), symmetrize=False)
display.add_title('Sum Port')
display.show()

field.set_excitations(0,1,0,0)
display = model.display
display.populate()
display.add_portmode(p1, k0=field.k0)
display.add_portmode(p2, k0=field.k0)
display.add_portmode(p3, k0=field.k0)
display.add_portmode(p4, k0=field.k0)
display.cbar('|E|', clim=[0,3e3]).animate().add_field(field.grid(N=200_000).scalar('Emag','complex'), symmetrize=False)
display.add_title('Difference Port')
display.show()