#!/usr/bin/env python3
"""
Plot all isotherms on a single figure with connecting lines.
Run from results directory: python3 plot_all_isotherms.py
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

def load_data(results_dir, L, T):
    filepath = os.path.join(results_dir, f'L{L}_T{T}', 'raw_data.dat')
    if not os.path.exists(filepath):
        return None
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 3:
                try:
                    pid, rho, rho_err = float(parts[0]), float(parts[1]), float(parts[2])
                    if rho > 0.0001:
                        data.append([pid, rho, rho_err])
                except:
                    continue
    return np.array(data) if data else None

# Load all data
results_dir = '.'
isotherms = {}
for L in [2.0, 5.0]:
    for T in [0.8, 1.3, 2.0]:
        data = load_data(results_dir, L, T)
        if data is not None:
            isotherms[(L, T)] = data
            print(f"Loaded L={L}, T={T}: {len(data)} points")

if not isotherms:
    print("No data found! Run from results directory.")
    exit(1)

# Colors: blue=subcritical, orange=critical, red=supercritical
colors = {0.8: '#1f77b4', 1.3: '#ff7f0e', 2.0: '#d62728'}
markers = {2.0: 'o', 5.0: 's'}  # circle for L=2, square for L=5
linestyles = {2.0: '-', 5.0: '--'}  # solid for L=2, dashed for L=5
regime_names = {0.8: 'Subcrit', 1.3: 'Crit', 2.0: 'Supercrit'}

# Create figure
fig, ax = plt.subplots(figsize=(10, 7))

ax.set_title('Complete Dataset: All Adsorption Isotherms', fontweight='bold', fontsize=14)
ax.set_xlabel('Reservoir Pressure PID', fontsize=12)
ax.set_ylabel('Pore Density ρ*', fontsize=12)
ax.set_xscale('log')

# Plot each isotherm with markers AND lines
for (L, T), d in sorted(isotherms.items()):
    label = f'L*={L}, T*={T} ({regime_names[T]})'
    ax.errorbar(d[:,0], d[:,1], yerr=d[:,2], 
                fmt=markers[L] + linestyles[L],  # marker + linestyle
                color=colors[T],
                label=label, 
                capsize=2, 
                markersize=6,
                linewidth=1.5,
                markeredgecolor='white',
                markeredgewidth=0.5)

# Reference line for P_sat at T=0.8
ax.axvline(0.00395, color='gray', ls=':', lw=1.5, alpha=0.7, label='P_sat* (T*=0.8, Johnson 1993)')

ax.legend(loc='upper left', fontsize=9, ncol=2)
ax.set_ylim(bottom=0)
ax.set_xlim(left=0.0003)
ax.grid(True, alpha=0.3)

fig.tight_layout()
fig.savefig('all_isotherms_with_lines.png', dpi=150, bbox_inches='tight')
fig.savefig('all_isotherms_with_lines.pdf', bbox_inches='tight')
print("\nSaved: all_isotherms_with_lines.png/pdf")
