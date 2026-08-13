# Welcome to EMerge Hub!
Hello visitors! Welcome to EMerge-hub, a platform/repository where I want to share as many useful stuff with the community relating to the EMerge solver as possible.

My dream for EMerge hub is to turn into a gigantic database of example files, tutorials and other design resources that everybody on the planet can use to learn about and develop their EM simulation skills (specifically applied ot EMerge).

For now, we are focussing on building out the Templates directory, just a large list of simulation files for every possible RF component imaginable.

The idea for EMerge-hub is to be very much community driven. While helping working on the FEM solver may be more difficult, contributing with example files, templates and other simulation utilities may not be! Lets build this amazing repository together!

# EMerge versions and installation
The current latest version of EMerge is 2.8. This version is on PyPI. I am working on version 3.0 on branch `v3.0-dev`. Files may be written for 3.0 already. I try to keep it stable.

### Version 2.8 Installation:
```bash
# Windows + Linux
pip install emerge

# MacOS
pip install emerge
pip install git+https://github.com/FennisRobert/emerge-aasds
```
### Version 3.0 Installation:
```bash
# Windows + Linux
pip install git+https://github.com/FennisRobert/EMerge.git@v3.0-dev

# MacOS
pip install git+https://github.com/FennisRobert/EMerge.git@v3.0-dev
pip install git+https://github.com/FennisRobert/emerge-aasds
```


## What is in this hub?
The hub contains many resources for people who want to get started with EMerge. It was created on August 11th 2026 so its mostly empty. It will be filled as time goes on.
* **`Template/`**: A directory with all sorts of template files for different passive RF components that you can use to model your design of choice.
* **`Materials/`**: An even larger community managed curated library of PCB substrates (FR-4, Rogers, Isola), conductors, and frequency-dependent dielectric models.
* **`Components/`**: Drop-in 3D geometry macros, wave port feeds, and SMA edge-launch connector setups.
* **`Benchmarks/`**: High-precision validation models against textbook analytical solutions and published papers.
* **`Tutorials/`**: Step-by-step interactive Jupyter Notebooks designed to guide non-RF engineers through full-wave simulation from scratch.

Most of these are to come. Feel free to initiate Pull Requests to add features. Because the repository is largely consisting of separate files etc, its very easy for me to move things around in folders later on without the fear of breaking anything. So do shy away of just adding something where you believe it should be. I'll clean things up later.

## Exploring the Hub

We are actively building out our **Simulation Templates** library to give engineers, makers, and students drop-in RF examples.

### Active Directory Structure (`/templates`)

Our templates are organized by **Technology Domain** and sub-categorized to match our main `CHECKLIST.md` tracking index:

```text
templates/
├── PCB/
│   ├── ANT/    # PCB Antennas (IFAs, Patches, Arrays, Vivaldi, etc.)
│   ├── FLT/    # Planar Filters (Stepped-Impedance, Edge-Coupled, Hairpin)
│   ├── DIV/    # Power Dividers & Couplers (Wilkinson, Rat-Race, Branchline)
│   └── INT/    # Interconnects, Routing & Bends (SMA launches, GCPW, Differential)
├── WAV/
│   ├── ANT/    # Waveguide Antennas (Pyramidal, Conical, Corrugated Horns)
│   ├── CMP/    # Waveguide Plumbing & Hybrid Tees (Magic Tee, Couplers)
│   └── FLT/    # Cavity & Waveguide Filters (Irises, Resonators)
└── WIR/
    ├── ANT/    # Wire & Classic Antennas (Dipoles, Monopoles, Yagi-Uda, Loops)
    └── UWB/    # 3D Wideband & EMC Antennas (Discones, Biconicals)

```

> **Where do I start?** Check out `CHECKLIST.md`! It contains the master index of all planned templates, their target application, and their current status. If something is missing, feel free to add it!

---

## Join the Mission: Become a Contributor!

EMerge is built by the community, for the community. You don't need a PhD in computational electromagnetics to contribute—helping build and verify a single antenna or filter script makes a huge difference!

### How to Contribute a Template:

1. **Pick an Unassigned Model**: Open `CHECKLIST.md` and find a model marked as `- [ ]`.
2. **Use the Base Template**: Copy and paste the `_template_dir` directory from the repository root (or copy an existing script from the same category) as your starting point. Inside is at least the `template_file.py` which is sufficient for a minimal simulation. For reasons you might want to add extra files, `README.md`, images, data which can all be in this folder.
    * Make sure to rename the directory to the code used in `checklist.md` followed by an optional human readable name. For example `WIR-ANT-01_half_wave_center_fed_dipole` for example.
3. **Build & Verify**: Write your geometry code, set up the frequency sweep, and verify that the simulation converges cleanly.
4. **Claim Your Credit**: Place your script into its corresponding category folder (e.g., `templates/PCB/ANT/pcb_ifa_2g4.py`) and submit a Pull Request!
5. **Sign Your Name**: In your PR, register your contribution using an alias of your choice to the `Contributor` column in `CHECKLIST.md`and mark the checkbox `- [x]`.

--- 
## Template file Rules
 0. You may make templates for either 2.8, 3.0 or both 2.8 and 3.0. Files might be automatically compatible. The biggest difference is that 3.0 sometimes automatically assigns boundary conditions.
 1. Unless absolutely necessary, there shouldn't be dependencies besides what is already used for EMerge.
    - Use the build in plot functions from `emerge.plot` if possible. If the plot functions don't support what you need (which is very possible) feel free to use your own custom matplotlib import and plotting.
 2. Designs should be as parametric as possible. That is to say that values for dimensions and parameters should follow from variables defined in the `DESIGN / GEOMETRY PARAMETERS` section of the file. 
 3. Demos should never use STEP files or other external file formats if they can be modeled with EMerge operations.
 4. Use SI units as much as possible. For many components that have logical sizes because they are based on inches etc you can of course use inches. 
    - Use multiplication for small values. For example: `width = 0.0025` should be `width = 2.5*mm`. 
    - If units are missing, add them to the `UNITS` section.
 5. You must stick to the template file formatting (largely). You can of course add comment lines etc but don't do something completely different.
 6. Don't add features that pull data from the internet. EMerge template file should not connect to the internet or read/write to the hard-drive unprompted except in rare circumstances. You may use the EMerge read and write functionality (`cache_run()` for example) in files if it is useful. If possible it should run on machines with 16GB of RAM. This is not always possible of course.
 7. Try to make simulation models as RAM efficient as possible. 
    - Minimize the number of frequency points
    - Make use of the `frequency_groups` argument where possible.
    - If you use `cache_harddisk` be very mindful of how much data EMerge will be writing.
 8. Keep the designs to a minimum. They should be starting points when people want to learn how to model certain antennas or EM designs. 
 9. Models do not have to auto-design themselves. For example: a patch antenna simulation does not have to derive the patch length from a desired frequency. Its cool if it works that way but it makes it harder to adjust. Just use absolute lengths. You may add a Python function or section to explain users how to derive specific dimensions.

### Material guidelines
 1. When making PCB files, the default material is FR4 (`em.lib.DIEL_FR4`). This is not for any specific reason other than that its likely the most common.
 2. If you make a single layer PCB, use standardized dimensions like 1.5mm, 0.8mm etc. 

### Use of LLMs for template scripts
 1. In principle there is no objection to the use of LLMs for template scripts.
 2. If you did **not** use AI to generate your script. REMOVE the AI lisence notice at the top of the script.
 2. If you did use AI to generate your script: *LEAVE IN* the lisence notice.

 Lisence notice:
 ```python
 # -----------------------------------------------------------------------------
# AI ASSISTANCE NOTICE (Uncomment if generated/assisted by an LLM):
# This script was generated or assisted using Large Language Models (LLMs).
# In accordance with EU copyright principles, pure AI-generated output resides 
# in the public domain (CC0 1.0 Universal). Human edits, architectural layout,
# and solver integrations are licensed under GNU GPL v2.
# =============================================================================
```
---

## Contributor Recognition & Hall of Fame

We believe every contribution deserves recognition!

* **Top Contributors** who build multiple verified models or help maintain core directories will be featured prominently on the [www.emerge-software.com](https://www.emerge-software.com) website and right here on the main README.

Ready to build the future of open-source RF simulation? **Fork the repo, grab `template_file.py`, and let's start modeling!**