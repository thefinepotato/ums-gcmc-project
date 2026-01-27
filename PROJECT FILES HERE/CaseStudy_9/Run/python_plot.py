#!/usr/bin/env python3
"""
Plot Grand-Canonical MC simulation output
Usage: python plot_mc.py lj.prt
"""

import numpy as np
import matplotlib.pyplot as plt
import sys

# Load data
filename = sys.argv[1] if len(sys.argv) > 1 else 'lj.prt'
data = np.loadtxt(filename)

cycle = data[:, 0]
energy = data[:, 1]
pressure = data[:, 2]
density = data[:, 3]

# Create figure with 3 subplots
fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# Energy
axes[0].plot(cycle, energy, 'b-', linewidth=0.8)
axes[0].axhline(np.mean(energy), color='r', linestyle='--', label=f'mean = {np.mean(energy):.3f}')
axes[0].set_ylabel('Energy/particle')
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Pressure
axes[1].plot(cycle, pressure, 'g-', linewidth=0.8)
axes[1].axhline(np.mean(pressure), color='r', linestyle='--', label=f'mean = {np.mean(pressure):.3f}')
axes[1].set_ylabel('Pressure')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# Density
axes[2].plot(cycle, density, 'm-', linewidth=0.8)
axes[2].axhline(np.mean(density), color='r', linestyle='--', label=f'mean = {np.mean(density):.3f}')
axes[2].set_ylabel('Density')
axes[2].set_xlabel('MC Cycle')
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.suptitle(f'GCMC Simulation Results\n{filename}')
plt.tight_layout()
plt.savefig('mc_results.png', dpi=150)
plt.show()

print(f"\nSummary:")
print(f"  Energy:   {np.mean(energy):.4f} ± {np.std(energy):.4f}")
print(f"  Pressure: {np.mean(pressure):.4f} ± {np.std(pressure):.4f}")
print(f"  Density:  {np.mean(density):.4f} ± {np.std(density):.4f}")