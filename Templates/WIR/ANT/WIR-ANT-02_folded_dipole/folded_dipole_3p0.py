# =============================================================================
# EMerge Simulation Template: Folded Dipole
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
# =============================================================================

# -----------------------------------------------------------------------------
# Folded Dipole Antenna (300 Ohm Feed)
#
# A folded dipole, the loop-shaped variant of a straight dipole, built from a
# smooth curved wire path instead of straight segments. Folded dipoles
# naturally present a 300 ohm feed impedance, which is why they were
# historically used with the 300 ohm twin-lead cable that fed broadcast TV
# and FM antennas. Tuned near 1.45 GHz.
#
# This template needs a solver feature only available in EMerge 3.0, so
# there is no 2.8 version. It requires up to 10 GB of RAM.
# -----------------------------------------------------------------------------
import emerge as em
import numpy as np
from emerge.plot import plot_sp, smith, plot_ff, plot_ff_polar, plot

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
f1 = 1.2e9
f2 = 1.7e9
nfreq = 11

# --- Geometry dimensions ---------------------------------------------------

Zsource = 300.0

radius = 0.35*mm
Lhalf = 44.1*mm
rad = 6.1*mm
gap = 0.5*mm

x_left = 0.0
x_mid = rad
x_right = 2 * rad
y_gap = gap / 2.0

degree = 2
w_arc = np.sqrt(2) / 2

air_margin = 40*mm

# --- 15 Control Points (exact geometry, every piece its own Bezier) -------
xs_path = np.array([
    x_left,   # 0  gap top
    x_left,   # 1  mid of upper-left leg
    x_left,   # 2  top of left leg          (shared: line1 end / arc1 start)
    x_left,   # 3  top-left tangent corner
    x_mid,    # 4  top apex                 (shared: arc1 end / arc2 start)
    x_right,  # 5  top-right tangent corner
    x_right,  # 6  top of right leg         (shared: arc2 end / line2 start)
    x_right,  # 7  mid of right leg
    x_right,  # 8  bottom of right leg      (shared: line2 end / arc3 start)
    x_right,  # 9  bot-right tangent corner
    x_mid,    # 10 bottom apex              (shared: arc3 end / arc4 start)
    x_left,   # 11 bot-left tangent corner
    x_left,   # 12 bottom of left leg       (shared: arc4 end / line3 start)
    x_left,   # 13 mid of lower-left leg
    x_left,   # 14 gap bottom
])

zs_path = np.array([
    y_gap,
    (y_gap + Lhalf) / 2.0,
    Lhalf,
    Lhalf + rad,
    Lhalf + rad,
    Lhalf + rad,
    Lhalf,
    0.0,
    -Lhalf,
    -(Lhalf + rad),
    -(Lhalf + rad),
    -(Lhalf + rad),
    -Lhalf,
    -(Lhalf + y_gap) / 2.0,
    -y_gap,
])

weights = np.array([
    1.0, 1.0, 1.0,
    w_arc, 1.0, w_arc,
    1.0, 1.0, 1.0,
    w_arc, 1.0, w_arc,
    1.0, 1.0, 1.0,
])

knots = np.array([0, 1, 2, 3, 4, 5, 6, 7], dtype=float)
multiplicities = np.array([3, 2, 2, 2, 2, 2, 2, 3], dtype=int)

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
                    weights=weights, knots=knots, multiplicities=multiplicities, degree=degree).pipe(disc).set_material(em.lib.COPPER)

port = em.geo.Cylinder(radius, gap, em.cs(origin=(0,0,-gap/2)))

air = em.geo.open_region(air_margin, air_margin, air_margin)

############################################################
#                      COMMIT GEOMETRY                     #
############################################################

# Once the geometry is finalized, hand it over to the solver.
model.commit_geometry()

############################################################
#                    SOLVER / MESH SETTINGS                 #
############################################################

# Set either a single frequency or a frequency sweep.
model.mw.set_frequency_range(f1, f2, nfreq)

# Set the overall mesh resolution as a fraction of the wavelength.
model.mw.set_resolution(0.2)

############################################################
#                    GENERATE & VIEW MESH                   #
############################################################

model.generate_mesh()
model.view()

############################################################
#                    BOUNDARY CONDITIONS                    #
############################################################

boundary_selection = air.boundary()

port = model.mw.bc.LumpedPort(port.shell, 1, 2*PI*radius, gap, em.ZAX, Z0=Zsource)
abc = model.mw.bc.AbsorbingBoundary(boundary_selection)

############################################################
#                       RUN SIMULATION                      #
############################################################

data = model.mw.run_sweep()

############################################################
#                   POST-PROCESSING: S-PARAMS                #
############################################################

g = data.scalar.grid

S11 = g.S(1,1)

plot_sp(g.freq, S11)
smith(S11, g.freq)

Zload = Zsource*((1+S11)/(1-S11))

plot(g.freq/GHz, [Zload.real, Zload.imag], labels=['Real','Imag'], xlabel="Frequency (GHz)", ylabel="Load Impedance (Ω)")

############################################################
#              POST-PROCESSING: FAR-FIELD (ANTENNAS)         #
############################################################

ff = data.field.find(freq=f0).farfield_2d((0,0,1), (0, 1, 0), boundary_selection)
plot_ff(ff.ang * 180 / np.pi, ff.gain.norm, dB=True, ylabel="Gain [dBi]")
plot_ff_polar(ff.ang, ff.gain.norm, dB=True, dBfloor=-40)

############################################################
#                     3D FIELD VISUALIZATION                 #
############################################################

### Note - this is a visualization of the E-field magnitude not
### antenna gain

# # Add geometry for context
model.display.populate()
field = data.field.find(freq=f0)
# # Compute full 3D far-field (at the same frequency) and display
ff3d = field.farfield_3d(boundary_selection)
model.display.add_farfield3d(ff3d, dB='True', rmax=150*mm / 2, offset=(0, 0, 150*mm), opacity=0.4)
model.display.animate().add_field(field.grid(N=200_00).scalar('Ez','complex'), symmetrize=True)
#
# # Show interactive 3D scene
model.display.show()
