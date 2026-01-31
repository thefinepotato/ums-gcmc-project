#!/usr/bin/env python3
"""
GCMC Slit Pore Isotherms - Publication Plots
Temperatures: T* = 0.8 (sub), 1.3 (crit), 2.0 (super)
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
    print("No data found!")
    exit(1)

# Colors: blue=subcritical, orange=critical, red=supercritical
colors = {0.8: '#1f77b4', 1.3: '#ff7f0e', 2.0: '#d62728'}
labels = {0.8: 'T*=0.8 (Subcritical)', 1.3: 'T*=1.3 (Critical)', 2.0: 'T*=2.0 (Supercritical)'}

# Figure 1: By pore width
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

for ax, L in zip([ax1, ax2], [2.0, 5.0]):
    ax.set_title(f'Slit Pore L* = {L}σ', fontweight='bold')
    ax.set_xlabel('Reservoir Pressure PID')
    ax.set_ylabel('Pore Density ρ*')
    ax.set_xscale('log')
    
    for T in [0.8, 1.3, 2.0]:
        if (L, T) in isotherms:
            d = isotherms[(L, T)]
            ax.errorbar(d[:,0], d[:,1], yerr=d[:,2], fmt='o-', color=colors[T],
                       label=labels[T], capsize=3, markersize=5)
    
    # Reference line for P_sat at T=0.8
    ax.axvline(0.00395, color='gray', ls='--', alpha=0.5, label='P_sat* (T*=0.8)')
    ax.legend(loc='best', fontsize=9)
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)

fig1.suptitle('GCMC Adsorption Isotherms in Slit Pores', fontweight='bold')
fig1.tight_layout()
fig1.savefig('isotherms_by_pore_width.png', dpi=150, bbox_inches='tight')
fig1.savefig('isotherms_by_pore_width.pdf', bbox_inches='tight')
print("Saved: isotherms_by_pore_width.png/pdf")

# Figure 2: By temperature
fig2, axes = plt.subplots(1, 3, figsize=(14, 4.5))
L_colors = {2.0: '#1f77b4', 5.0: '#ff7f0e'}
regime_names = {0.8: 'Subcritical', 1.3: 'Critical', 2.0: 'Supercritical'}

for ax, T in zip(axes, [0.8, 1.3, 2.0]):
    ax.set_title(f'T* = {T} ({regime_names[T]})', fontweight='bold')
    ax.set_xlabel('Reservoir Pressure PID')
    ax.set_ylabel('Pore Density ρ*')
    ax.set_xscale('log')
    
    for L in [2.0, 5.0]:
        if (L, T) in isotherms:
            d = isotherms[(L, T)]
            ax.errorbar(d[:,0], d[:,1], yerr=d[:,2], fmt='o-', color=L_colors[L],
                       label=f'L* = {L}σ', capsize=3, markersize=5)
    
    if T == 0.8:
        ax.axvline(0.00395, color='gray', ls='--', alpha=0.5)
    ax.legend()
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)

fig2.suptitle('Effect of Pore Width at Each Temperature', fontweight='bold')
fig2.tight_layout()
fig2.savefig('isotherms_by_temperature.png', dpi=150, bbox_inches='tight')
fig2.savefig('isotherms_by_temperature.pdf', bbox_inches='tight')
print("Saved: isotherms_by_temperature.png/pdf")

# Figure 3: Phase transition detail for T=0.8
fig3, ax3 = plt.subplots(figsize=(8, 6))
ax3.set_title('Subcritical Phase Transition (T* = 0.8)', fontweight='bold')
ax3.set_xlabel('Reservoir Pressure PID')
ax3.set_ylabel('Pore Density ρ*')
ax3.set_xscale('log')

for L in [2.0, 5.0]:
    if (L, 0.8) in isotherms:
        d = isotherms[(L, 0.8)]
        ax3.errorbar(d[:,0], d[:,1], yerr=d[:,2], fmt='o-', color=L_colors[L],
                    label=f'L* = {L}σ', capsize=4, markersize=7, linewidth=1.5)

ax3.axvline(0.00395, color='red', ls='--', lw=2, label='P_sat* = 0.00395 (Johnson 1993)')
ax3.axhline(0.844, color='green', ls=':', alpha=0.7, label='ρ_liq* = 0.844 (bulk)')
ax3.axhline(0.0092, color='blue', ls=':', alpha=0.7, label='ρ_gas* = 0.0092 (bulk)')
ax3.legend(loc='best')
ax3.set_ylim(bottom=0)
ax3.grid(True, alpha=0.3)

fig3.tight_layout()
fig3.savefig('phase_transition_T08.png', dpi=150, bbox_inches='tight')
fig3.savefig('phase_transition_T08.pdf', bbox_inches='tight')
print("Saved: phase_transition_T08.png/pdf")

# Figure 4: All combined
fig4, ax4 = plt.subplots(figsize=(10, 7))
ax4.set_title('Complete Dataset: All Isotherms', fontweight='bold')
ax4.set_xlabel('Reservoir Pressure PID')
ax4.set_ylabel('Pore Density ρ*')
ax4.set_xscale('log')

markers = {2.0: 'o', 5.0: 's'}
for (L, T), d in sorted(isotherms.items()):
    ax4.errorbar(d[:,0], d[:,1], yerr=d[:,2], fmt=markers[L], color=colors[T],
                label=f'L*={L}, T*={T}', capsize=2, markersize=4, alpha=0.8)

ax4.legend(loc='upper left', ncol=2, fontsize=9)
ax4.set_ylim(bottom=0)
ax4.grid(True, alpha=0.3)
fig4.tight_layout()
fig4.savefig('all_isotherms.png', dpi=150, bbox_inches='tight')
fig4.savefig('all_isotherms.pdf', bbox_inches='tight')
print("Saved: all_isotherms.png/pdf")

print("\nAll plots generated!")
