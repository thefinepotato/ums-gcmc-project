#!/usr/bin/env python3
"""
validate_isotherm.py
Validate GCMC isotherm results against literature (Johnson et al. 1993)

Creates:
1. % deviation plot for gas and liquid phases
2. Parity plot (simulation vs literature) with R²
3. Summary table for report

Usage:
    python3 validate_isotherm.py <isotherm_summary.dat> [T]
    
Example:
    python3 validate_isotherm.py isotherm_L5.0_T0.9_*/isotherm_summary.dat 0.9
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================================
# LITERATURE FITS - Johnson et al. (1993) Mol. Phys. 78:591
# ============================================================================

def lit_P_sat(T):
    """Saturation pressure: ln(P) = 4.54 - 8.06/T"""
    return np.exp(4.54 - 8.06/T)

def lit_rho_gas(T):
    """Gas coexistence density: ln(rho) = 4.36 - 7.24/T"""
    return np.exp(4.36 - 7.24/T)

def lit_rho_liq(T):
    """Liquid coexistence density: rho = 1.42 - 0.72*T"""
    return 1.42 - 0.72*T

T_CRIT = 1.1  # Critical temperature

# ============================================================================
# DATA READING
# ============================================================================

def read_isotherm(filename):
    """Read isotherm_summary.dat file"""
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 7:
                try:
                    pid = float(parts[0])
                    density = float(parts[1])
                    dens_err = float(parts[2])
                    energy = float(parts[3])
                    en_err = float(parts[4])
                    pressure = float(parts[5])
                    pr_err = float(parts[6])
                    data.append([pid, density, dens_err, energy, en_err, pressure, pr_err])
                except ValueError:
                    continue
    return np.array(data)

# ============================================================================
# VALIDATION ANALYSIS
# ============================================================================

def analyze_isotherm(data, T):
    """Analyze isotherm and compare to literature"""
    
    P_sat = lit_P_sat(T)
    rho_gas_lit = lit_rho_gas(T)
    rho_liq_lit = lit_rho_liq(T)
    
    pid = data[:, 0]
    density = data[:, 1]
    dens_err = data[:, 2]
    
    # Classify points as gas or liquid based on density
    # Use midpoint between literature gas and liquid
    rho_mid = (rho_gas_lit + rho_liq_lit) / 2
    
    gas_mask = density < rho_mid
    liq_mask = density >= rho_mid
    
    # Gas phase analysis
    gas_pid = pid[gas_mask]
    gas_rho = density[gas_mask]
    gas_err = dens_err[gas_mask]
    
    # Liquid phase analysis  
    liq_pid = pid[liq_mask]
    liq_rho = density[liq_mask]
    liq_err = dens_err[liq_mask]
    
    # Find transition point (largest density jump)
    if len(density) > 1:
        density_diff = np.diff(density)
        transition_idx = np.argmax(np.abs(density_diff))
        P_trans_sim = (pid[transition_idx] + pid[transition_idx + 1]) / 2
    else:
        P_trans_sim = np.nan
    
    results = {
        'T': T,
        'P_sat_lit': P_sat,
        'P_sat_sim': P_trans_sim,
        'P_sat_err': 100 * abs(P_trans_sim - P_sat) / P_sat if not np.isnan(P_trans_sim) else np.nan,
        'rho_gas_lit': rho_gas_lit,
        'rho_gas_sim': np.mean(gas_rho) if len(gas_rho) > 0 else np.nan,
        'rho_gas_err': 100 * abs(np.mean(gas_rho) - rho_gas_lit) / rho_gas_lit if len(gas_rho) > 0 else np.nan,
        'rho_liq_lit': rho_liq_lit,
        'rho_liq_sim': np.mean(liq_rho) if len(liq_rho) > 0 else np.nan,
        'rho_liq_err': 100 * abs(np.mean(liq_rho) - rho_liq_lit) / rho_liq_lit if len(liq_rho) > 0 else np.nan,
        'gas_mask': gas_mask,
        'liq_mask': liq_mask,
        'n_gas': np.sum(gas_mask),
        'n_liq': np.sum(liq_mask),
    }
    
    return results

def compute_r_squared(sim_values, lit_values):
    """Compute R² between simulation and literature"""
    if len(sim_values) < 2:
        return np.nan
    ss_res = np.sum((sim_values - lit_values)**2)
    ss_tot = np.sum((sim_values - np.mean(sim_values))**2)
    if ss_tot == 0:
        return np.nan
    return 1 - ss_res / ss_tot

# ============================================================================
# PLOTTING
# ============================================================================

def create_validation_plots(data, T, output_prefix):
    """Create validation plots"""
    
    results = analyze_isotherm(data, T)
    
    pid = data[:, 0]
    density = data[:, 1]
    dens_err = data[:, 2]
    
    P_sat = results['P_sat_lit']
    rho_gas_lit = results['rho_gas_lit']
    rho_liq_lit = results['rho_liq_lit']
    
    # =========================================================================
    # FIGURE 1: Isotherm with literature comparison
    # =========================================================================
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot simulation data
    ax1.errorbar(pid, density, yerr=dens_err, fmt='o-', color='blue', 
                 markersize=6, capsize=3, label='Simulation')
    
    # Add literature values
    ax1.axhline(rho_gas_lit, color='green', linestyle='--', alpha=0.7,
                label=f'Literature ρ_gas = {rho_gas_lit:.4f}')
    ax1.axhline(rho_liq_lit, color='red', linestyle='--', alpha=0.7,
                label=f'Literature ρ_liq = {rho_liq_lit:.4f}')
    ax1.axvline(P_sat, color='orange', linestyle=':', alpha=0.7,
                label=f'Literature P_sat = {P_sat:.4f}')
    
    ax1.set_xscale('log')
    ax1.set_xlabel('PID (reservoir pressure)', fontsize=12)
    ax1.set_ylabel('Density ρ*', fontsize=12)
    ax1.set_title(f'Adsorption Isotherm T* = {T}\nValidation against Johnson et al. (1993)', fontsize=12)
    ax1.legend(loc='center right')
    ax1.grid(True, alpha=0.3)
    
    # Add text box with validation metrics
    textstr = '\n'.join([
        f'Validation Metrics:',
        f'  P_sat: {results["P_sat_err"]:.1f}% error' if not np.isnan(results["P_sat_err"]) else '  P_sat: N/A',
        f'  ρ_gas: {results["rho_gas_err"]:.1f}% error' if not np.isnan(results["rho_gas_err"]) else '  ρ_gas: N/A',
        f'  ρ_liq: {results["rho_liq_err"]:.1f}% error' if not np.isnan(results["rho_liq_err"]) else '  ρ_liq: N/A',
    ])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    fig1.savefig(f'{output_prefix}_validation.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_prefix}_validation.png")
    
    # =========================================================================
    # FIGURE 2: Deviation bar chart
    # =========================================================================
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    
    metrics = ['P_sat', 'ρ_gas', 'ρ_liq']
    errors = [results['P_sat_err'], results['rho_gas_err'], results['rho_liq_err']]
    colors = ['orange', 'green', 'red']
    
    # Filter out NaN values
    valid = [(m, e, c) for m, e, c in zip(metrics, errors, colors) if not np.isnan(e)]
    if valid:
        metrics_v, errors_v, colors_v = zip(*valid)
        bars = ax2.bar(metrics_v, errors_v, color=colors_v, alpha=0.7, edgecolor='black')
        
        # Add value labels on bars
        for bar, err in zip(bars, errors_v):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{err:.1f}%', ha='center', va='bottom', fontsize=11)
    
    ax2.axhline(10, color='gray', linestyle='--', alpha=0.5, label='10% threshold')
    ax2.set_ylabel('% Deviation from Literature', fontsize=12)
    ax2.set_title(f'Validation: % Deviation from Johnson et al. (1993)\nT* = {T}', fontsize=12)
    ax2.legend()
    ax2.set_ylim(0, max(errors_v)*1.3 if valid else 50)
    
    plt.tight_layout()
    fig2.savefig(f'{output_prefix}_deviation.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_prefix}_deviation.png")
    
    # =========================================================================
    # FIGURE 3: Parity plot (simulation vs ideal gas law check for gas phase)
    # =========================================================================
    fig3, ax3 = plt.subplots(figsize=(7, 6))
    
    # For ideal gas: PV = NkT -> rho = P/kT = PID/T (in reduced units)
    # This is only valid at low density
    gas_mask = results['gas_mask']
    if np.sum(gas_mask) > 1:
        pid_gas = pid[gas_mask]
        rho_gas = density[gas_mask]
        rho_ideal = pid_gas / T  # ideal gas prediction
        
        ax3.scatter(rho_ideal, rho_gas, s=80, c='green', alpha=0.7, edgecolor='black',
                   label='Gas phase points')
        
        # Perfect agreement line
        max_val = max(np.max(rho_ideal), np.max(rho_gas)) * 1.1
        ax3.plot([0, max_val], [0, max_val], 'k--', label='Perfect agreement')
        
        # R² calculation
        r2 = compute_r_squared(rho_gas, rho_ideal)
        ax3.text(0.05, 0.95, f'R² = {r2:.4f}', transform=ax3.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax3.set_xlabel('Ideal gas density (ρ = PID/T)', fontsize=12)
    ax3.set_ylabel('Simulation density', fontsize=12)
    ax3.set_title(f'Parity Plot: Gas Phase vs Ideal Gas Law\nT* = {T}', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    fig3.savefig(f'{output_prefix}_parity.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {output_prefix}_parity.png")
    
    plt.show()
    
    return results

# ============================================================================
# TABLE OUTPUT
# ============================================================================

def print_summary_table(results, folder_name):
    """Print summary table for report"""
    
    print("\n" + "="*70)
    print("VALIDATION SUMMARY TABLE")
    print("="*70)
    print(f"\nData: {folder_name}")
    print(f"Temperature: T* = {results['T']}")
    print()
    
    print(f"{'Property':<20} {'Literature':<15} {'Simulation':<15} {'% Error':<10}")
    print("-"*60)
    
    print(f"{'P_sat':<20} {results['P_sat_lit']:<15.6f} {results['P_sat_sim']:<15.6f} {results['P_sat_err']:<10.1f}" 
          if not np.isnan(results['P_sat_sim']) else f"{'P_sat':<20} {results['P_sat_lit']:<15.6f} {'N/A':<15} {'N/A':<10}")
    
    print(f"{'ρ_gas':<20} {results['rho_gas_lit']:<15.6f} {results['rho_gas_sim']:<15.6f} {results['rho_gas_err']:<10.1f}"
          if not np.isnan(results['rho_gas_sim']) else f"{'ρ_gas':<20} {results['rho_gas_lit']:<15.6f} {'N/A':<15} {'N/A':<10}")
    
    print(f"{'ρ_liq':<20} {results['rho_liq_lit']:<15.6f} {results['rho_liq_sim']:<15.6f} {results['rho_liq_err']:<10.1f}"
          if not np.isnan(results['rho_liq_sim']) else f"{'ρ_liq':<20} {results['rho_liq_lit']:<15.6f} {'N/A':<15} {'N/A':<10}")
    
    print()
    print(f"Gas phase points: {results['n_gas']}")
    print(f"Liquid phase points: {results['n_liq']}")
    print()
    
    # Task 3 table format
    print("="*70)
    print("FOR TASK 3 TABLE (copy-paste ready):")
    print("="*70)
    print()
    print("| L | T | Transition P* | Gas ρ* | Liquid ρ* | Notes |")
    print("|---|---|---------------|--------|-----------|-------|")
    
    # Extract L from folder name if possible
    L = "?"
    if "L" in folder_name:
        try:
            L = folder_name.split("L")[1].split("_")[0]
        except:
            pass
    
    print(f"| {L} | {results['T']} | {results['P_sat_sim']:.4f} | {results['rho_gas_sim']:.4f} | {results['rho_liq_sim']:.3f} | Validated |")
    print()

# ============================================================================
# MAIN
# ============================================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Try to extract T from filename or use provided value
    if len(sys.argv) >= 3:
        T = float(sys.argv[2])
    else:
        # Try to extract from filename like "isotherm_L5.0_T0.9_..."
        try:
            T = float(filename.split("_T")[1].split("_")[0])
            print(f"Detected T = {T} from filename")
        except:
            T = 0.9  # default
            print(f"Using default T = {T}")
    
    # Check if subcritical
    if T >= T_CRIT:
        print(f"WARNING: T* = {T} >= Tc* = {T_CRIT}")
        print("System is supercritical - no phase transition expected")
        print("Literature fits for coexistence are not applicable")
    
    # Read data
    data = read_isotherm(filename)
    if len(data) == 0:
        print(f"Error: No data found in {filename}")
        sys.exit(1)
    
    print(f"Read {len(data)} data points from {filename}")
    
    # Create output prefix
    folder = str(Path(filename).parent)
    output_prefix = f"{folder}/validation" if folder != "." else "validation"
    
    # Analyze and plot
    results = create_validation_plots(data, T, output_prefix)
    
    # Print table
    print_summary_table(results, filename)

if __name__ == '__main__':
    main()
