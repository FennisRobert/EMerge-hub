# EMerge Model Library & Compatibility Tracker

This checklist tracks community-contributed simulation templates for **EMerge**. To claim an item or update compatibility status, submit a Pull Request editing this file.

---

## 1. PCB & Planar Technology

### 1.1 PCB Antennas

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `PCB-ANT-01` | **Standard Planar PCB Inverted-F (IFA)** | Microstrip Edge | WiFi/BLE 2.4 GHz benchmark antenna. | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-02` | **Meandered Planar Inverted-F (MIFA)** | Microstrip Edge | Compact 868MHz. | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-03` | **Inverted-F (IFA)** | Vertical Lumped Port | Standard design with metal plates | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-04` | **Dual-Band IFA (2.4 / 5 GHz)** | Microstrip Edge | Dual-band WiFi routers and gateways. | - [ ] | - [ ] |  |
| `PCB-ANT-05` | **Printed Quarter-Wave Monopole** | Microstrip Edge | Beginner baseline; boundary condition test. 2.4GHz | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-06` | **Meander-Line Monopole** | Microstrip Edge | Sub-GHz (433/868 MHz) LoRa & RFID. | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-07` | **Inverted-L Antenna (ILA)** | Microstrip Edge | Compact single-band planar antenna. | - [ ] | - [ ] |  |
| `PCB-ANT-08` | **Ceramic Chip Antenna Model** | SMT Pad + Keepout | Simulates chip antenna with PCB keep-out. | - [ ] | - [ ] |  |
| `PCB-ANT-09` | **Inset-Fed Rectangular Patch** | Microstrip Edge (Inset) | Impedance matching via inset depth. | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-10` | **Quarter-Wave Transformer Patch** | Microstrip Edge | Transmission line matching example. | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-11` | **Coaxial Probe-Fed Patch** | Coax Pin thru Ground | GPS receivers and high-power boards. | - [x] | - [x] | Robert Fennis |
| `PCB-ANT-12` | **Aperture-Coupled Patch** | Bottom Layer Microstrip | Multi-layer stackups and high isolation. | - [ ] | - [ ] |  |
| `PCB-ANT-13` | **Probe-Fed Circular Patch** | Coax Probe | Circular geometry mesh test; radar/GPS. | - [ ] | - [ ] |  |
| `PCB-ANT-14` | **Corner-Truncated Square Patch** | Microstrip / Probe | Circular polarization (CP) & axial ratio. | - [ ] | - [ ] |  |
| `PCB-ANT-15` | **Dual-Feed Square CP Patch** | 90° Phase-Shift Feeds | Multi-port CP excitation benchmark. | - [ ] | - [ ] |  |
| `PCB-ANT-16` | **2x1 Patch Array + Power Divider** | Microstrip Feed Network | Basic array factor & feed network synthesis. | - [x] | - [x] | Robert Fennis (Claude) |
| `PCB-ANT-17` | **2x2 Planar Patch Array** | Microstrip Feed Network | 5G / mmWave beamforming array. | - [ ] | - [ ] |  |
| `PCB-ANT-18` | **Printed PCB Yagi-Uda** | Microstrip Balun | Directional drones / FPV video links. | - [ ] | - [ ] |  |
| `PCB-ANT-19` | **Vivaldi Tapered Slot Antenna** | Microstrip to Slotline | UWB radar and wideband sensing. | - [ ] | - [ ] |  |
| `PCB-ANT-20` | **Antipodal Vivaldi Antenna** | Microstrip Transition | Simplified feeding for UWB designs. | - [ ] | - [ ] |  |
| `PCB-ANT-21` | **Planar Bowtie Antenna** | Discrete / Balun Feed | Wideband dipole alternative for GPR. | - [ ] | - [ ] |  |
| `PCB-ANT-22` | **Archimedean Planar Spiral** | Balun / Coax | Circularly polarized wideband antenna. | - [ ] | - [ ] |  |
| `PCB-ANT-23` | **Sierpinski Gasket Fractal** | Microstrip / Probe | Multi-band response; mesher stress test. | - [ ] | - [ ] |  |

### 1.2 PCB Filters

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `PCB-FLT-01` | **Stepped-Impedance LPF** | Microstrip | Alternating high/low impedance traces. | - [x] | - [x] | Robert Fennis |
| `PCB-FLT-02` | **Open-Stub Low Pass Filter** | Microstrip | Demonstrates Kuroda identities/stubs. | - [x] | - [x] | Robert Fennis |
| `PCB-FLT-03` | **Edge-Coupled Bandpass Filter** | Microstrip | Parallel coupled lines for RF front-ends. | - [ ] | - [ ] |  |
| `PCB-FLT-04` | **Hairpin Bandpass Filter** | Microstrip | U-shaped folded resonators for compact size. | - [ ] | - [ ] |  |
| `PCB-FLT-05` | **Interdigital Bandpass Filter** | Microstrip / Stripline | High-performance filter with grounded vias. | - [ ] | - [ ] |  |
| `PCB-FLT-06` | **Combline Bandpass Filter** | Microstrip | Compact resonator layout for cellular bands. | - [ ] | - [ ] |  |
| `PCB-FLT-07` | **Defected Ground Structure (DGS)** | Etched Ground Notch | Ground plane etching for harmonic rejection. | - [ ] | - [ ] |  |
| `PCB-FLT-08` | **Split-Ring Resonator (SRR)** | Microstrip Notch | Narrowband notch filter for interference. | - [ ] | - [ ] |  |

### 1.3 PCB Dividers & Couplers

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `PCB-DIV-01` | **2-Way Wilkinson Power Divider** | Microstrip + Resistor | Equi-phase power split with internal resistor. | - [x] | - [x] | Robert Fennis |
| `PCB-DIV-02` | **Gysel Power Divider** | Microstrip | High-power alternative to Wilkinson. | - [ ] | - [ ] |  |
| `PCB-DIV-03` | **Branchline Coupler (90° Hybrid)** | Microstrip | Quadrature phase generation for mixers. | - [x] | - [x] | Robert Fennis |
| `PCB-DIV-04` | **Rat-Race Coupler (180° Hybrid)** | Microstrip | Sum and difference monopulse networks. | - [x] | - [x] | Robert Fennis |
| `PCB-DIV-05` | **Edge-Coupled Directional Coupler** | Microstrip | Power monitoring and SWR detection. | - [x] | - [x] | Robert Fennis |
| `PCB-DIV-06` | **Lange Coupler** | Microstrip + Wirebonds | Multi-octave bandwidth; tests wire bridges. | - [x] | - [x] | Robert Fennis |

### 1.4 PCB Interconnects, Routing & Transitions

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `PCB-INT-01` | **SMA Edge-Launch Transition** | Coax / Waveguide Port | Board-to-connector transition tuning. | - [ ] | - [ ] |  |
| `PCB-INT-02` | **Microstrip to CPW Transition** | Microstrip to Waveguide | On-board IC and probing interface. | - [ ] | - [ ] |  |
| `PCB-INT-03` | **Mitered 90° Microstrip Bend** | Waveguide / Lumped Port | Chamfering bend discontinuities. | - [ ] | - [ ] |  |
| `PCB-INT-04` | **Microstrip T-Junction** | Waveguide / Lumped Port | Unmatched power division discontinuity. | - [ ] | - [ ] |  |
| `PCB-INT-05` | **GCPW with Via Fence** | Waveguide Port | Substrate mode suppression at high GHz. | - [ ] | - [ ] |  |
| `PCB-INT-06` | **Differential Pair Routing** | Differential Multi-Mode | High-speed digital (PCIe, USB) odd/even mode. | - [ ] | - [ ] |  |

### 1.5 PCB Matching circuits

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `PCB-MTH-01` | **PCB Tapers** | Microstrip | Different tapers (exponential, linear, etc.). | - [x] | - [x] | andresmmera |

## 2. Waveguide & Cavity Technology

### 2.1 Waveguide Antennas

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `WAV-ANT-01` | **Pyramidal Horn Antenna** | Rectangular Waveguide | Standard reference antenna for ranges. | - [ ] | - [ ] |  |
| `WAV-ANT-02` | **Conical Horn Antenna** | Circular Waveguide | Satellite communication feeds. | - [ ] | - [ ] |  |
| `WAV-ANT-03` | **Corrugated Horn Antenna** | Circular Waveguide | Low cross-polarization reflector feeds. | - [ ] | - [ ] |  |

### 2.2 Waveguide Components & Plumbing

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `WAV-CMP-01` | **Magic Tee (Waveguide Hybrid)** | Rectangular Waveguide | E-plane and H-plane 180° hybrid junction. | - [x] | - [x] | Robert Fennis |
| `WAV-CMP-02` | **Multi-Hole Directional Coupler** | Rectangular Waveguide | High-power directional sampling. | - [ ] | - [ ] |  |
| `WAV-CMP-03` | **Coax to Rectangular Waveguide** | Coax Probe | Standard coaxial-to-waveguide adapter. | - [ ] | - [ ] |  |

### 2.3 Cavity & Waveguide Filters

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `WAV-FLT-01` | **Waveguide Iris Bandpass Filter** | Rectangular Waveguide | Inductive metallic posts/irises in guide. | - [ ] | - [ ] |  |
| `WAV-FLT-02` | **Cylindrical Cavity Resonator** | Eigenmode (No Ports) | $TE_{011}$ eigenmode validation test. | - [x] | - [x] | elektroedde |
| `WAV-FLT-03` | **Coaxial Cavity Filter (Combline)** | Coax Probe Ports | High-Q cellular base station filter. | - [ ] | - [ ] |  |
| `WAV-FLT-04` | **Dielectric Resonator Filter** | Coax / Microstrip Feed | High-Q ceramic puck filter for 5G. | - [ ] | - [ ] |  |

---

## 3. Wire & Free-Space Technology

### 3.1 Wire & Classical Antennas

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `WIR-ANT-01` | **Half-Wave Center-Fed Dipole** | Discrete Gap Port | "Hello World" baseline EM antenna. | - [X] | - [x] | Michael Burbidge |
| `WIR-ANT-02` | **Folded Dipole Antenna** | Discrete Gap Port | $300\ \Omega$ feed antenna for broadcast TV. | - [X] | - [ ] | Robert Fennis |
| `WIR-ANT-03` | **Wire Monopole on Finite Ground** | Coax Base Feed | Ground plane edge diffraction benchmark. | - [x] | - [x] | Robert Fennis |
| `WIR-ANT-04a` | **3-Element Yagi-Uda Antenna** | Discrete Gap Port | Parasitic director and reflector dynamics. | - [x] | - [x] | Michael Burbidge |
| `WIR-ANT-04b` | **5-Element Yagi-Uda Antenna** | Discrete Gap Port | Parasitic director and reflector dynamics. | - [x] | - [x] | Robert Fennis |
| `WIR-ANT-05` | **Electrically Small Wire Loop** | Discrete Gap Port | Near-field magnetic sensing / NFC baseline. | - [ ] | - [ ] |  |
| `WIR-ANT-06` | **Resonant Full-Wave Loop** | Discrete Gap Port | Directional wire antenna for radio receivers. | - [X] | - [x] | Michael Burbidge  |
| `WIR-ANT-07` | **Axial-Mode Helical Antenna** | Coax + Ground Plane | 3D curve meshing & circular polarization. | - [ ] | - [ ] |  |
| `WIR-ANT-08` | **Normal-Mode (Rubber Ducky) Helix** | Coax Base Feed | Compact helical monopole for walkie-talkies. | - [ ] | - [ ] |  |

### 3.2 3D Wideband & EMC Antennas

| ID | Model Name | Feed Strategy | Target Application / Notes | v2.8 | v3.0 | Contributor |
| --- | --- | --- | --- | --- | --- | --- |
| `WIR-UWB-01` | **3D Discone Antenna** | Coax Feed | Wideband omnidirectional receiving antenna. | - [ ] | - [ ] |  |
| `WIR-UWB-02` | **3D Biconical Antenna** | Discrete Gap Port | Standard EMC/EMI compliance testing antenna. | - [ ] | - [ ] |  |

---
