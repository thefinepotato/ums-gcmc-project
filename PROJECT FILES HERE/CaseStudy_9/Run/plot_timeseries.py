#!/usr/bin/env python3
"""
plot_timeseries.py
Plot energy, pressure, density vs MC cycle from a .prt file

Usage:
    python3 plot_timeseries.py <prt_file>
    python3 plot_timeseries.py isotherm_folder/prt_pid_0.012088.dat
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

def read_prt_file(filename):
    """Read fort.66 / prt file format: cycle, energy, pressure, density"""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    cycle = int(parts[0])
                    energy = float(parts[1])
                    pressure = float(parts[2])
                    density = float(parts[3])
                    data.append([cycle, energy, pressure, density])
                except ValueError:
                    continue
    return np.array(data)

def plot_timeseries(filename, output=None):
    """Create 3-panel time series plot"""
    data = read_prt_file(filename)
    
    if len(data) == 0:
        print(f"Error: No data found in {filename}")
        return
    
    cycles = data[:, 0]
    energy = data[:, 1]
    pressure = data[:, 2]
    density = data[:, 3]
    
    # Calculate means
    mean_energy = np.mean(energy)
    mean_pressure = np.mean(pressure)
    mean_density = np.mean(density)
    
    # Create figure
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle(f'GCMC Simulation Results\n{filename}', fontsize=12)
    
    # Energy plot
    axes[0].plot(cycles, energy, 'b-', linewidth=0.5)
    axes[0].axhline(mean_energy, color='r', linestyle='--', linewidth=1.5, 
                    label=f'mean = {mean_energy:.3f}')
    axes[0].set_ylabel('Energy/particle')
    axes[0].legend(loc='lower left')
    axes[0].grid(True, alpha=0.3)
    
    # Pressure plot
    axes[1].plot(cycles, pressure, 'g-', linewidth=0.5)
    axes[1].axhline(mean_pressure, color='r', linestyle='--', linewidth=1.5,
                    label=f'mean = {mean_pressure:.3f}')
    axes[1].set_ylabel('Pressure')
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3)
    
    # Density plot
    axes[2].plot(cycles, density, 'm-', linewidth=0.5)
    axes[2].axhline(mean_density, color='r', linestyle='--', linewidth=1.5,
                    label=f'mean = {mean_density:.3f}')
    axes[2].set_ylabel('Density')
    axes[2].set_xlabel('MC Cycle')
    axes[2].legend(loc='upper right')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save or show
    if output is None:
        output = filename.replace('.dat', '_timeseries.png').replace('.prt', '_timeseries.png')
    plt.savefig(output, dpi=150, bbox_inches='tight')
    print(f"Saved: {output}")
    plt.show()
    
    # Print statistics
    print(f"\nStatistics:")
    print(f"  Cycles: {int(cycles[0])} to {int(cycles[-1])} ({len(cycles)} samples)")
    print(f"  Energy:   {mean_energy:.4f} ± {np.std(energy):.4f}")
    print(f"  Pressure: {mean_pressure:.4f} ± {np.std(pressure):.4f}")
    print(f"  Density:  {mean_density:.4f} ± {np.std(density):.4f}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    plot_timeseries(sys.argv[1])
