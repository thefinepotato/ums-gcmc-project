#!/usr/bin/env python3
"""
plot_isotherm.py
----------------
Makes plots from the isotherm data.
Run this after run_isotherm finishes.

Usage: python3 plot_isotherm.py <folder>/isotherm_summary.dat
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

# check if file is given
if len(sys.argv) < 2:
    print("Usage: python3 plot_isotherm.py isotherm_summary.dat")
    sys.exit(1)

filename = sys.argv[1]

# load the data file
# comments='#' skip lines starting with #
data = np.loadtxt(filename, comments='#')

# handle case of only one data point
if data.ndim == 1:
    data = data.reshape(1, -1)

# pull out columns
# column 0 = PID, column 1 = density, etc
pid = data[:, 0]
density = data[:, 1]
density_err = data[:, 2]
energy = data[:, 3]
energy_err = data[:, 4]
pressure = data[:, 5]
pressure_err = data[:, 6]

# make 3 plots stacked vertically
fig, axes = plt.subplots(3, 1, figsize=(8, 10))

# plot 1: density vs PID (this is the actual isotherm)
ax1 = axes[0]
ax1.errorbar(pid, density, yerr=density_err, fmt='o-', capsize=3, color='blue')
ax1.set_xlabel('PID (reservoir pressure)')
ax1.set_ylabel('Density')
ax1.set_title('Adsorption Isotherm: Density vs Chemical Potential')
ax1.set_xscale('log')  # log scale makes it easier to see the range
ax1.grid(True, alpha=0.3)

# plot 2: energy vs PID
ax2 = axes[1]
ax2.errorbar(pid, energy, yerr=energy_err, fmt='s-', capsize=3, color='red')
ax2.set_xlabel('PID')
ax2.set_ylabel('Energy per particle')
ax2.set_title('Energy vs PID')
ax2.set_xscale('log')
ax2.grid(True, alpha=0.3)

# plot 3: pressure vs PID
ax3 = axes[2]
ax3.errorbar(pid, pressure, yerr=pressure_err, fmt='^-', capsize=3, color='green')
ax3.set_xlabel('PID')
ax3.set_ylabel('Pressure')
ax3.set_title('Pressure vs PID')
ax3.set_xscale('log')
ax3.grid(True, alpha=0.3)

plt.tight_layout()

# save the figure
outfile = filename.replace('.dat', '.png')
plt.savefig(outfile, dpi=150)
print(f"Saved plot to: {outfile}")

plt.show()

# print a table so to see the numbers
print("")
print("Data summary:")
print("-" * 50)
print(f"{'PID':>8} {'Density':>10} {'Energy':>10}")
print("-" * 50)
for i in range(len(pid)):
    print(f"{pid[i]:>8.3f} {density[i]:>10.4f} {energy[i]:>10.4f}")
print("-" * 50)

# sanity check
print("")
print("Quick physics check:")
if density[-1] > density[0]:
    print("  [OK] Density increases with PID (expected)")
else:
    print("  [??] Density decreases with PID (unexpected, check your runs)")

if all(e < 0 for e in energy):
    print("  [OK] Energy is negative (particles are attracting, expected for liquid)")
else:
    print("  [??] Some positive energy values (might be gas phase or error)")

# compare to literature values for LJ fluid
# at T=0.9, bulk liquid density is around 0.7-0.8
print("")
print("Literature comparison:")
print("  For LJ fluid at T*=0.9:")
print("    - Bulk liquid density ~ 0.7-0.8")
print("    - Bulk liquid energy ~ -5 to -6 per particle")
print("  Your slit pore should have slightly different values due to wall effects.")