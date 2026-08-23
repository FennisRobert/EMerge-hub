"""
MicrostripTaper_post.py
------------------------
Two modes:

1) Single-taper mode:
       python MicrostripTaper_post.py [project_name]
   Loads one taper's saved data and plots S11/S21 vs frequency, the
   impedance/width profile, and a Smith chart of the S11.

2) Comparison mode:
       python MicrostripTaper_post.py --compare proj1 proj2 [proj3 ...]

"""
import sys

import emerge as em
from emerge.plot import smith

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


def dB(s):
    return 20 * np.log10(np.abs(s) + 1e-30)


def load_taper_data(project_name):
    d = np.load(project_name + "_data.npz", allow_pickle=True)
    return {
        'f': d['f'], 'S11': d['S11'], 'S21': d['S21'],
        'z_profile': d['z_profile'], 'Z_profile': d['Z_profile'],
        'W_profile': d['W_profile'], 'taper_type': str(d['taper_type']),
    }


# ---------------------------------------------------------------------------
# Single-taper plots
# ---------------------------------------------------------------------------
def plot_single(project_name):
    data = load_taper_data(project_name)
    f, S11, S21 = data['f'], data['S11'], data['S21']
    z_profile, Z_profile, W_profile = data['z_profile'], data['Z_profile'], data['W_profile']
    taper_type = data['taper_type']

    f_MHz = f / 1e6 # Convert to MHz

    # --- Figure 1: S-parameter magnitudes -----------------------------
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(f_MHz, dB(S21), label='S21 (insertion loss)', lw=1.8, color='r')
    ax1.plot(f_MHz, dB(S11), label='S11 (return loss)', lw=1.8, color='b')
    ax1.set_xlabel('Frequency [MHz]')
    ax1.set_ylabel('Magnitude [dB]')
    ax1.set_title(f'{project_name} ({taper_type} taper) — S-parameters')
    ax1.set_ylim(-40, 2)
    ax1.set_xlim(f_MHz[0], f_MHz[-1])
    ax1.xaxis.set_major_locator(MultipleLocator(500))
    ax1.legend()
    ax1.grid(True, alpha=0.4)
    fig1.tight_layout()

    # --- Figure 2: Taper profile (impedance + physical width) -----------
    fig2, axL = plt.subplots(figsize=(8, 4))
    axR = axL.twinx()
    axL.plot(z_profile, Z_profile, color='b', lw=1.8, label='Z(z)')
    axR.plot(z_profile, W_profile, color='darkorange', lw=1.8, ls='--', label='W(z)')
    axL.set_xlabel('Position along taper [mm]')
    axL.set_ylabel('Characteristic impedance [Ω]', color='b')
    axR.set_ylabel('Trace width [mm]', color='darkorange')
    axL.set_title(f'{taper_type.capitalize()} taper profile')
    axL.grid(True, alpha=0.4)
    fig2.tight_layout()

    # --- Figure 3: Smith Chart -----------------------------------------
    model = em.Simulation(project_name, load_file=True)
    grid = model.mw.data.scalar.grid
    f_dense = grid.dense_f(2001)
    S11_dense = grid.model_S(1, 1, Npoles=10)

    smith(S11_dense, labels="S11", f=f_dense)


# ---------------------------------------------------------------------------
# Comparison plots across several tapers
# ---------------------------------------------------------------------------
def plot_comparison(project_names):
    datasets = [load_taper_data(p) for p in project_names]
    colors = plt.get_cmap('tab10').colors

    # --- S11 / S21 side by side -----------------------------------------
    fig1, (axA, axB) = plt.subplots(1, 2, figsize=(13, 5))
    for i, data in enumerate(datasets):
        c = colors[i % len(colors)]
        f_MHz = data['f'] / 1e6 # to MHz
        axA.plot(f_MHz, dB(data['S11']), color=c, lw=1.8, label=data['taper_type'])
        axB.plot(f_MHz, dB(data['S21']), color=c, lw=1.8, label=data['taper_type'])

    axA.set_ylim(-40, 2)
    axB.set_ylim(-2, 1)
    for ax, title in [(axA, 'S11 (return loss)'), (axB, 'S21 (insertion loss)')]:
        ax.set_xlabel('Frequency [MHz]')
        ax.set_ylabel('Magnitude [dB]')
        ax.set_title(title)
        ax.xaxis.set_major_locator(MultipleLocator(500))
        ax.grid(True, alpha=0.4)
        ax.legend()
    fig1.suptitle('Taper comparison — S-parameters')
    fig1.tight_layout()

    # --- Impedance / width profiles side by side --------------------------
    fig2, (axZ, axW) = plt.subplots(1, 2, figsize=(13, 4.5))
    for i, data in enumerate(datasets):
        c = colors[i % len(colors)]
        axZ.plot(data['z_profile'], data['Z_profile'], color=c, lw=1.8, label=data['taper_type'])
        axW.plot(data['z_profile'], data['W_profile'], color=c, lw=1.8, label=data['taper_type'])
    axZ.set_xlabel('Position along taper [mm]')
    axZ.set_ylabel('Z(z) [Ω]')
    axW.set_xlabel('Position along taper [mm]')
    axW.set_ylabel('W(z) [mm]')
    axZ.set_title('Impedance profile')
    axW.set_title('Width profile')
    axZ.grid(True, alpha=0.4)
    axW.grid(True, alpha=0.4)
    axZ.legend()
    axW.legend()
    fig2.suptitle('Taper comparison — impedance / width profiles')
    fig2.tight_layout()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    args = sys.argv[1:]

    if args and args[0] == "--compare":
        project_names = args[1:]
        if len(project_names) < 2:
            raise SystemExit(
                "Usage: python MicrostripTaper_post.py --compare proj1 proj2 [proj3 ...]"
            )
        plot_comparison(project_names)
    else:
        project_name = args[0] if args else "MicrostripTaper_klopfenstein"
        plot_single(project_name)

    plt.show()
