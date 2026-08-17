# EMerge Template Gallery

_Auto-generated on 2026-08-17 13:19 by `generate_template_gallery.py` — do not edit by hand, re-run the script instead._

**20** templates with a preview image, **23** implemented in total, out of **64** catalogued in `Templates/checklist.md`.

## Contents

- [1. PCB & Planar Technology](#1-pcb-planar-technology)
  - [1.1 PCB Antennas](#11-pcb-antennas)
  - [1.2 PCB Filters](#12-pcb-filters)
  - [1.3 PCB Dividers & Couplers](#13-pcb-dividers-couplers)
  - [1.4 PCB Interconnects, Routing & Transitions](#14-pcb-interconnects-routing-transitions)
- [2. Waveguide & Cavity Technology](#2-waveguide-cavity-technology)
  - [2.1 Waveguide Antennas](#21-waveguide-antennas)
  - [2.2 Waveguide Components & Plumbing](#22-waveguide-components-plumbing)
  - [2.3 Cavity & Waveguide Filters](#23-cavity-waveguide-filters)
- [3. Wire & Free-Space Technology](#3-wire-free-space-technology)
  - [3.1 Wire & Classical Antennas](#31-wire-classical-antennas)
  - [3.2 3D Wideband & EMC Antennas](#32-3d-wideband-emc-antennas)
- [Not yet implemented](#not-yet-implemented)

---

## 1. PCB & Planar Technology

### 1.1 PCB Antennas

<table>
<tr>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-01_PIFA"><img src="Templates/PCB/ANT/PCB-ANT-01_PIFA/geo.png" width="230"/></a><br/>
<b>PCB-ANT-01 · Standard Planar PCB Inverted-F (IFA)</b><br/>
<sub>WiFi/BLE 2.4 GHz benchmark antenna.</sub><br/>
<sub>Feed: Microstrip Edge</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-02_Meander"><img src="Templates/PCB/ANT/PCB-ANT-02_Meander/geo.png" width="230"/></a><br/>
<b>PCB-ANT-02 · Meandered Planar Inverted-F (MIFA)</b><br/>
<sub>Compact 868MHz.</sub><br/>
<sub>Feed: Microstrip Edge</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-03_IFA"><img src="Templates/PCB/ANT/PCB-ANT-03_IFA/geo.png" width="230"/></a><br/>
<b>PCB-ANT-03 · Inverted-F (IFA)</b><br/>
<sub>Standard design with metal plates</sub><br/>
<sub>Feed: Vertical Lumped Port</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-05_Monopole"><img src="Templates/PCB/ANT/PCB-ANT-05_Monopole/geo.png" width="230"/></a><br/>
<b>PCB-ANT-05 · Printed Quarter-Wave Monopole</b><br/>
<sub>Beginner baseline; boundary condition test. 2.4GHz</sub><br/>
<sub>Feed: Microstrip Edge</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-06_Meander_monopole"><img src="Templates/PCB/ANT/PCB-ANT-06_Meander_monopole/geo.png" width="230"/></a><br/>
<b>PCB-ANT-06 · Meander-Line Monopole</b><br/>
<sub>Sub-GHz (433/868 MHz) LoRa & RFID.</sub><br/>
<sub>Feed: Microstrip Edge</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-09_Inset_fed_patch"><img src="Templates/PCB/ANT/PCB-ANT-09_Inset_fed_patch/geo.png" width="230"/></a><br/>
<b>PCB-ANT-09 · Inset-Fed Rectangular Patch</b><br/>
<sub>Impedance matching via inset depth.</sub><br/>
<sub>Feed: Microstrip Edge (Inset)</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-10_Qwave_transformer_patch"><img src="Templates/PCB/ANT/PCB-ANT-10_Qwave_transformer_patch/geo.png" width="230"/></a><br/>
<b>PCB-ANT-10 · Quarter-Wave Transformer Patch</b><br/>
<sub>Transmission line matching example.</sub><br/>
<sub>Feed: Microstrip Edge</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-11_coax_fed_patch"><img src="Templates/PCB/ANT/PCB-ANT-11_coax_fed_patch/geo.png" width="230"/></a><br/>
<b>PCB-ANT-11 · Coaxial Probe-Fed Patch</b><br/>
<sub>GPS receivers and high-power boards.</sub><br/>
<sub>Feed: Coax Pin thru Ground</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-13_coax_fed_circ_patch"><img src="Templates/PCB/ANT/PCB-ANT-13_coax_fed_circ_patch/geo.png" width="230"/></a><br/>
<b>PCB-ANT-13 · Probe-Fed Circular Patch</b><br/>
<sub>Circular geometry mesh test; radar/GPS.</sub><br/>
<sub>Feed: Coax Probe</sub><br/>
<sub>⬜ 2.8 &nbsp;·&nbsp; ⬜ 3.0
</sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<a href="Templates/PCB/ANT/PCB-ANT-16_2x1_array_powerdivider"><img src="Templates/PCB/ANT/PCB-ANT-16_2x1_array_powerdivider/geo.png" width="230"/></a><br/>
<b>PCB-ANT-16 · 2x1 Patch Array + Power Divider</b><br/>
<sub>Basic array factor & feed network synthesis.</sub><br/>
<sub>Feed: Microstrip Feed Network</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis (Claude)
</sub>
</td>
<td width="33%"></td>
<td width="33%"></td>
</tr>
</table>

<details>
<summary>Implemented, preview image not committed yet (1)</summary>

| ID | Name | Notes | v2.8 | v3.0 | Contributor |
|---|---|---|---|---|---|
| `PCB-ANT-08` | Ceramic Chip Antenna Model | Simulates chip antenna with PCB keep-out. |  |  |  |

</details>

### 1.2 PCB Filters

<table>
<tr>
<td align="center" width="33%">
<a href="Templates/PCB/FLT/PCB-FLT-01_Stepped_impedance"><img src="Templates/PCB/FLT/PCB-FLT-01_Stepped_impedance/geo.png" width="230"/></a><br/>
<b>PCB-FLT-01 · Stepped-Impedance LPF</b><br/>
<sub>Alternating high/low impedance traces.</sub><br/>
<sub>Feed: Microstrip</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/FLT/PCB-FLT-02_Open_Stub_LPF"><img src="Templates/PCB/FLT/PCB-FLT-02_Open_Stub_LPF/geo.png" width="230"/></a><br/>
<b>PCB-FLT-02 · Open-Stub Low Pass Filter</b><br/>
<sub>Demonstrates Kuroda identities/stubs.</sub><br/>
<sub>Feed: Microstrip</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td width="33%"></td>
</tr>
</table>

<details>
<summary>Implemented, preview image not committed yet (1)</summary>

| ID | Name | Notes | v2.8 | v3.0 | Contributor |
|---|---|---|---|---|---|
| `PCB-FLT-04` | Hairpin Bandpass Filter | U-shaped folded resonators for compact size. |  |  |  |

</details>

### 1.3 PCB Dividers & Couplers

<table>
<tr>
<td align="center" width="33%">
<a href="Templates/PCB/DIV/PCB-DIV-01_Wilkinson"><img src="Templates/PCB/DIV/PCB-DIV-01_Wilkinson/geo.png" width="230"/></a><br/>
<b>PCB-DIV-01 · 2-Way Wilkinson Power Divider</b><br/>
<sub>Equi-phase power split with internal resistor.</sub><br/>
<sub>Feed: Microstrip + Resistor</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/DIV/PCB-DIV-03_Branchline"><img src="Templates/PCB/DIV/PCB-DIV-03_Branchline/geo.png" width="230"/></a><br/>
<b>PCB-DIV-03 · Branchline Coupler (90° Hybrid)</b><br/>
<sub>Quadrature phase generation for mixers.</sub><br/>
<sub>Feed: Microstrip</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/DIV/PCB-DIV-04_Ratrace"><img src="Templates/PCB/DIV/PCB-DIV-04_Ratrace/geo.png" width="230"/></a><br/>
<b>PCB-DIV-04 · Rat-Race Coupler (180° Hybrid)</b><br/>
<sub>Sum and difference monopulse networks.</sub><br/>
<sub>Feed: Microstrip</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
</tr>
<tr>
<td align="center" width="33%">
<a href="Templates/PCB/DIV/PCB-DIV-05_Edge-coupled"><img src="Templates/PCB/DIV/PCB-DIV-05_Edge-coupled/geo.png" width="230"/></a><br/>
<b>PCB-DIV-05 · Edge-Coupled Directional Coupler</b><br/>
<sub>Power monitoring and SWR detection.</sub><br/>
<sub>Feed: Microstrip</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/PCB/DIV/PCB-DIV-06_Lange_coupler"><img src="Templates/PCB/DIV/PCB-DIV-06_Lange_coupler/geo.png" width="230"/></a><br/>
<b>PCB-DIV-06 · Lange Coupler</b><br/>
<sub>Multi-octave bandwidth; tests wire bridges.</sub><br/>
<sub>Feed: Microstrip + Wirebonds</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td width="33%"></td>
</tr>
</table>

### 1.4 PCB Interconnects, Routing & Transitions

_Nothing implemented yet in this category — see below._

## 2. Waveguide & Cavity Technology

### 2.1 Waveguide Antennas

_Nothing implemented yet in this category — see below._

### 2.2 Waveguide Components & Plumbing

_Nothing implemented yet in this category — see below._

### 2.3 Cavity & Waveguide Filters

<details>
<summary>Implemented, preview image not committed yet (1)</summary>

| ID | Name | Notes | v2.8 | v3.0 | Contributor |
|---|---|---|---|---|---|
| `WAV-FLT-02` | Cylindrical Cavity Resonator | $TE_{011}$ eigenmode validation test. | ✅ | ✅ | elektroedde |

</details>

## 3. Wire & Free-Space Technology

### 3.1 Wire & Classical Antennas

<table>
<tr>
<td align="center" width="33%">
<a href="Templates/WIR/ANT/WIR-ANT-01_dipole"><img src="Templates/WIR/ANT/WIR-ANT-01_dipole/geo.png" width="230"/></a><br/>
<b>WIR-ANT-01 · Half-Wave Center-Fed Dipole</b><br/>
<sub>"Hello World" baseline EM antenna.</sub><br/>
<sub>Feed: Discrete Gap Port</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Michael Burbidge
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/WIR/ANT/WIR-ANT-02_folded_dipole"><img src="Templates/WIR/ANT/WIR-ANT-02_folded_dipole/geo.png" width="230"/></a><br/>
<b>WIR-ANT-02 · Folded Dipole Antenna</b><br/>
<sub>$300\ \Omega$ feed antenna for broadcast TV.</sub><br/>
<sub>Feed: Discrete Gap Port</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ⬜ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
<td align="center" width="33%">
<a href="Templates/WIR/ANT/WIR-ANT-03_Monopole"><img src="Templates/WIR/ANT/WIR-ANT-03_Monopole/_template_dir/geo.png" width="230"/></a><br/>
<b>WIR-ANT-03 · Wire Monopole on Finite Ground</b><br/>
<sub>Ground plane edge diffraction benchmark.</sub><br/>
<sub>Feed: Coax Base Feed</sub><br/>
<sub>✅ 2.8 &nbsp;·&nbsp; ✅ 3.0
 &nbsp;·&nbsp; Robert Fennis
</sub>
</td>
</tr>
</table>

### 3.2 3D Wideband & EMC Antennas

_Nothing implemented yet in this category — see below._

---

## Not yet implemented

Planned templates from `checklist.md` with no matching folder under `Templates/` yet. Want to contribute one? Pick an ID below.

| ID | Name | Feed Strategy | Notes |
|---|---|---|---|
| `PCB-ANT-04` | Dual-Band IFA (2.4 / 5 GHz) | Microstrip Edge | Dual-band WiFi routers and gateways. |
| `PCB-ANT-07` | Inverted-L Antenna (ILA) | Microstrip Edge | Compact single-band planar antenna. |
| `PCB-ANT-12` | Aperture-Coupled Patch | Bottom Layer Microstrip | Multi-layer stackups and high isolation. |
| `PCB-ANT-14` | Corner-Truncated Square Patch | Microstrip / Probe | Circular polarization (CP) & axial ratio. |
| `PCB-ANT-15` | Dual-Feed Square CP Patch | 90° Phase-Shift Feeds | Multi-port CP excitation benchmark. |
| `PCB-ANT-17` | 2x2 Planar Patch Array | Microstrip Feed Network | 5G / mmWave beamforming array. |
| `PCB-ANT-18` | Printed PCB Yagi-Uda | Microstrip Balun | Directional drones / FPV video links. |
| `PCB-ANT-19` | Vivaldi Tapered Slot Antenna | Microstrip to Slotline | UWB radar and wideband sensing. |
| `PCB-ANT-20` | Antipodal Vivaldi Antenna | Microstrip Transition | Simplified feeding for UWB designs. |
| `PCB-ANT-21` | Planar Bowtie Antenna | Discrete / Balun Feed | Wideband dipole alternative for GPR. |
| `PCB-ANT-22` | Archimedean Planar Spiral | Balun / Coax | Circularly polarized wideband antenna. |
| `PCB-ANT-23` | Sierpinski Gasket Fractal | Microstrip / Probe | Multi-band response; mesher stress test. |
| `PCB-FLT-03` | Edge-Coupled Bandpass Filter | Microstrip | Parallel coupled lines for RF front-ends. |
| `PCB-FLT-05` | Interdigital Bandpass Filter | Microstrip / Stripline | High-performance filter with grounded vias. |
| `PCB-FLT-06` | Combline Bandpass Filter | Microstrip | Compact resonator layout for cellular bands. |
| `PCB-FLT-07` | Defected Ground Structure (DGS) | Etched Ground Notch | Ground plane etching for harmonic rejection. |
| `PCB-FLT-08` | Split-Ring Resonator (SRR) | Microstrip Notch | Narrowband notch filter for interference. |
| `PCB-DIV-02` | Gysel Power Divider | Microstrip | High-power alternative to Wilkinson. |
| `PCB-INT-01` | SMA Edge-Launch Transition | Coax / Waveguide Port | Board-to-connector transition tuning. |
| `PCB-INT-02` | Microstrip to CPW Transition | Microstrip to Waveguide | On-board IC and probing interface. |
| `PCB-INT-03` | Mitered 90° Microstrip Bend | Waveguide / Lumped Port | Chamfering bend discontinuities. |
| `PCB-INT-04` | Microstrip T-Junction | Waveguide / Lumped Port | Unmatched power division discontinuity. |
| `PCB-INT-05` | GCPW with Via Fence | Waveguide Port | Substrate mode suppression at high GHz. |
| `PCB-INT-06` | Differential Pair Routing | Differential Multi-Mode | High-speed digital (PCIe, USB) odd/even mode. |
| `WAV-ANT-01` | Pyramidal Horn Antenna | Rectangular Waveguide | Standard reference antenna for ranges. |
| `WAV-ANT-02` | Conical Horn Antenna | Circular Waveguide | Satellite communication feeds. |
| `WAV-ANT-03` | Corrugated Horn Antenna | Circular Waveguide | Low cross-polarization reflector feeds. |
| `WAV-CMP-01` | Magic Tee (Waveguide Hybrid) | Rectangular Waveguide | E-plane and H-plane 180° hybrid junction. |
| `WAV-CMP-02` | Multi-Hole Directional Coupler | Rectangular Waveguide | High-power directional sampling. |
| `WAV-CMP-03` | Coax to Rectangular Waveguide | Coax Probe | Standard coaxial-to-waveguide adapter. |
| `WAV-FLT-01` | Waveguide Iris Bandpass Filter | Rectangular Waveguide | Inductive metallic posts/irises in guide. |
| `WAV-FLT-03` | Coaxial Cavity Filter (Combline) | Coax Probe Ports | High-Q cellular base station filter. |
| `WAV-FLT-04` | Dielectric Resonator Filter | Coax / Microstrip Feed | High-Q ceramic puck filter for 5G. |
| `WIR-ANT-04a` | 3-Element Yagi-Uda Antenna | Discrete Gap Port | Parasitic director and reflector dynamics. |
| `WIR-ANT-04b` | 5-Element Yagi-Uda Antenna | Discrete Gap Port | Parasitic director and reflector dynamics. |
| `WIR-ANT-05` | Electrically Small Wire Loop | Discrete Gap Port | Near-field magnetic sensing / NFC baseline. |
| `WIR-ANT-06` | Resonant Full-Wave Loop | Discrete Gap Port | Directional wire antenna for radio receivers. |
| `WIR-ANT-07` | Axial-Mode Helical Antenna | Coax + Ground Plane | 3D curve meshing & circular polarization. |
| `WIR-ANT-08` | Normal-Mode (Rubber Ducky) Helix | Coax Base Feed | Compact helical monopole for walkie-talkies. |
| `WIR-UWB-01` | 3D Discone Antenna | Coax Feed | Wideband omnidirectional receiving antenna. |
| `WIR-UWB-02` | 3D Biconical Antenna | Discrete Gap Port | Standard EMC/EMI compliance testing antenna. |
