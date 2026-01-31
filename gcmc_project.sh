#!/bin/bash
#===============================================================================
#
#  GCMC SLIT PORE ISOTHERM - PROJECT A.1 COMPLETE SCRIPT
#  
#  University of Amsterdam - Understanding Molecular Simulation
#  
#  Temperatures:
#    T* = 0.8  - SUBCRITICAL (below T_c*)
#    T* = 1.3  - CRITICAL (at T_c* ≈ 1.31)
#    T* = 2.0  - SUPERCRITICAL (above T_c*)
#
#  Reference: Johnson, Zollweg & Gubbins, Mol. Phys. 78, 591 (1993)
#    T_c* = 1.313 ± 0.001
#    ρ_c* = 0.316 ± 0.001
#    For T* = 0.8: P_sat* ≈ 0.00395, ρ_gas* ≈ 0.0092, ρ_liq* ≈ 0.844
#
#===============================================================================

set +e

#===============================================================================
# CONFIGURATION
#===============================================================================

if [[ -d "$HOME/gcmc_test/CaseStudy_9" ]]; then
    SOURCE_PROJECT="$HOME/gcmc_test/CaseStudy_9"
elif [[ -d "$HOME/ums-gcmc-project/PROJECT FILES HERE/CaseStudy_9" ]]; then
    SOURCE_PROJECT="$HOME/ums-gcmc-project/PROJECT FILES HERE/CaseStudy_9"
else
    echo "ERROR: Cannot find CaseStudy_9 project!"
    exit 1
fi

WORKSPACE="/dev/shm/gcmc_final_run"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="$HOME/gcmc_project_results_$TIMESTAMP"

# Physical parameters
RHO_INIT=0.5
NPART=50
NSAMP=2
RC=2.5

# Reference values from Johnson et al. (1993) Mol. Phys. 78, 591
# These are for BULK LJ fluid with tail corrections
T_CRIT_REF=1.313      # Critical temperature
RHO_CRIT_REF=0.316    # Critical density
P_CRIT_REF=0.1279     # Critical pressure

# T* = 0.8 coexistence values (Johnson 1993 correlations)
T08_PSAT=0.00395      # Saturation pressure
T08_RHO_GAS=0.0092    # Gas density at coexistence
T08_RHO_LIQ=0.844     # Liquid density at coexistence

# Conditions: L × T (subcritical, critical, supercritical)
declare -a CONDITIONS=(
    "2.0:0.8"
    "5.0:0.8"
    "2.0:1.3"
    "5.0:1.3"
    "2.0:2.0"
    "5.0:2.0"
)

#===============================================================================
# SETUP
#===============================================================================

echo ""
echo "============================================================"
echo "  GCMC SLIT PORE ADSORPTION ISOTHERMS"
echo "  Project A.1 - Understanding Molecular Simulation"
echo "============================================================"
echo ""
echo "  Temperatures: T* = 0.8 (sub), 1.3 (crit), 2.0 (super)"
echo "  Pore widths:  L* = 2.0σ, 5.0σ"
echo "  Reference:    Johnson et al. (1993) Mol. Phys. 78, 591"
echo ""
echo "  Results: $RESULTS_DIR"
echo ""

rm -rf "$WORKSPACE"
mkdir -p "$WORKSPACE"
cp -r "$SOURCE_PROJECT"/* "$WORKSPACE/"

# Fix Fortran (READ 15 -> READ 5)
cd "$WORKSPACE/Source"
for f in *.f; do
    sed -i 's/READ(15/READ(5/g' "$f" 2>/dev/null
    sed -i 's/READ (15/READ (5/g' "$f" 2>/dev/null
done
make clean > /dev/null 2>&1
make > /dev/null 2>&1

if [[ ! -x "mc_grand" ]]; then
    echo "ERROR: Compilation failed!"
    exit 1
fi

echo "[OK] Fortran compiled"

mkdir -p "$RESULTS_DIR"

#===============================================================================
# SIMULATION FUNCTION
#===============================================================================

run_simulation() {
    local L="$1"
    local T="$2"
    local pid="$3"
    local EQUIL="$4"
    local PROD="$5"
    local OUTDIR="$6"
    
    RUNDIR="$WORKSPACE/Run/temp_$$"
    rm -rf "$RUNDIR"
    mkdir -p "$RUNDIR"
    
    cp "$WORKSPACE/Source/mc_grand" "$RUNDIR/"
    cp "$WORKSPACE/Block/block" "$RUNDIR/"
    cp "$WORKSPACE/Run/lj.model" "$RUNDIR/fort.25"
    cp "$WORKSPACE/Run/lj.res" "$RUNDIR/fort.11"
    cp "$WORKSPACE/Run/lj.prth" "$RUNDIR/"
    
    # Safe seed to avoid Fortran integer overflow
    SEED=$((RANDOM % 700000 + 1))
    
    cat > "$RUNDIR/input.txt" << EOF
  ibeg  , nequil  , lmax   nsamp iseed
   0      $EQUIL      $PROD   $NSAMP      $SEED
  dr      
  0.09   
  ndispl  nexch
  100      10
npart temp rho      pid
$NPART     $T $RHO_INIT    $pid
slitwidth
$L
rv
$RC 
EOF
    
    sync
    
    cd "$RUNDIR"
    ./mc_grand < input.txt > output.txt 2>&1
    cd "$WORKSPACE/Run"
    
    if [[ -s "$RUNDIR/fort.66" ]]; then
        cd "$RUNDIR"
        cp lj.prth fort.31
        cp fort.66 fort.32
        ./block > block_output.txt 2>&1
        cd "$WORKSPACE/Run"
        
        # Extract all values with block averaging errors
        local DENSITY=$(grep '###### dens' "$RUNDIR/block_output.txt" | awk '{print $3}')
        local DENS_ERR=$(grep '###### dens' "$RUNDIR/block_output.txt" | awk '{print $4}')
        local ENERGY=$(grep '###### energy' "$RUNDIR/block_output.txt" | awk '{print $3}')
        local EN_ERR=$(grep '###### energy' "$RUNDIR/block_output.txt" | awk '{print $4}')
        local PRESSURE=$(grep '###### press' "$RUNDIR/block_output.txt" | awk '{print $3}')
        local PR_ERR=$(grep '###### press' "$RUNDIR/block_output.txt" | awk '{print $4}')
        local NPART_AVG=$(grep '###### npart' "$RUNDIR/block_output.txt" | awk '{print $3}')
        local NPART_ERR=$(grep '###### npart' "$RUNDIR/block_output.txt" | awk '{print $4}')
        
        # Extract acceptance ratios
        local DISPL_ACC=$(grep "Number of att. to displ" "$RUNDIR/output.txt" | tail -1 | grep -oP '\(\s*\K[0-9.]+(?=%)' || echo "N/A")
        local EXCH_ACC=$(grep "Number of att. to exch" "$RUNDIR/output.txt" | tail -1 | grep -oP '\(\s*\K[0-9.]+(?=%)' || echo "N/A")
        
        # Extract chemical potential
        local MU_EX=$(grep "Excess chemical potential" "$RUNDIR/output.txt" | awk '{print $NF}')
        
        if [[ -n "$DENSITY" ]]; then
            # Write to data file (all values)
            echo "$pid $DENSITY $DENS_ERR $ENERGY $EN_ERR $PRESSURE $PR_ERR $NPART_AVG $NPART_ERR $MU_EX $DISPL_ACC $EXCH_ACC" >> "$OUTDIR/raw_data.dat"
            rm -rf "$RUNDIR"
            echo "$DENSITY:$DENS_ERR"
            return 0
        fi
    fi
    
    rm -rf "$RUNDIR"
    echo "FAILED"
    return 1
}

#===============================================================================
# RUN ALL CONDITIONS
#===============================================================================

cd "$WORKSPACE/Run"

GRAND_SUCCESS=0
GRAND_TOTAL=0

for cond in "${CONDITIONS[@]}"; do
    L="${cond%:*}"
    T="${cond#*:}"
    
    echo ""
    echo "============================================================"
    echo "  L* = $L, T* = $T"
    echo "============================================================"
    
    # Determine regime and parameters
    if [[ "$T" == "0.8" ]]; then
        REGIME="SUBCRITICAL"
        TC_EST=500
        P_SAT=0.00395
        echo "  Regime: $REGIME (T* < T_c* = 1.31)"
        echo "  Reference (Johnson 1993): P_sat* = $P_SAT"
        echo ""
        
        # PID values around saturation pressure
        PID_VALUES=(0.000395 0.001185 0.001975 0.002765 0.003357 0.003950 0.004542 0.005135 0.005925 0.007900 0.011850 0.019750 0.039500 0.197500)
        
    elif [[ "$T" == "1.3" ]]; then
        REGIME="CRITICAL"
        TC_EST=500
        echo "  Regime: $REGIME (T* ≈ T_c* = 1.31)"
        echo "  At critical point - large density fluctuations expected"
        echo ""
        
        # Wide range of PID for critical
        PID_VALUES=(0.01 0.02 0.05 0.08 0.10 0.12 0.15 0.20 0.30 0.50 1.0 2.0 5.0 10.0)
        
    else
        REGIME="SUPERCRITICAL"
        TC_EST=50
        echo "  Regime: $REGIME (T* > T_c* = 1.31)"
        echo "  Continuous isotherm - no phase transition"
        echo ""
        
        PID_VALUES=(0.05 0.1 0.2 0.5 1.0 2.0 3.0 5.0 7.0 10.0)
    fi
    
    EQUIL=$((10 * TC_EST))
    PROD=$((200 * TC_EST))
    
    echo "  N_equil = $EQUIL, N_prod = $PROD"
    echo ""
    
    OUTDIR="$RESULTS_DIR/L${L}_T${T}"
    mkdir -p "$OUTDIR"
    
    # Header for raw data
    echo "# PID rho rho_err E E_err P P_err N N_err mu_ex displ% exch%" > "$OUTDIR/raw_data.dat"
    
    NRUNS=${#PID_VALUES[@]}
    IRUN=0
    COND_SUCCESS=0
    
    for pid in "${PID_VALUES[@]}"; do
        ((IRUN++))
        ((GRAND_TOTAL++))
        printf "  [%2d/%2d] PID = %-10s ... " "$IRUN" "$NRUNS" "$pid"
        
        result=$(run_simulation "$L" "$T" "$pid" "$EQUIL" "$PROD" "$OUTDIR")
        
        if [[ "$result" != "FAILED" ]]; then
            rho="${result%:*}"
            err="${result#*:}"
            printf "ρ* = %.5f ± %.5f\n" "$rho" "$err"
            ((COND_SUCCESS++))
            ((GRAND_SUCCESS++))
        else
            echo "FAILED"
        fi
    done
    
    echo ""
    echo "  Completed: $COND_SUCCESS/$NRUNS"
    
    # Sort raw data by PID
    if [[ -f "$OUTDIR/raw_data.dat" ]]; then
        head -1 "$OUTDIR/raw_data.dat" > "$OUTDIR/temp.dat"
        tail -n +2 "$OUTDIR/raw_data.dat" | sort -g >> "$OUTDIR/temp.dat"
        mv "$OUTDIR/temp.dat" "$OUTDIR/raw_data.dat"
    fi
done

#===============================================================================
# GENERATE REPORT TABLES
#===============================================================================

echo ""
echo "============================================================"
echo "  GENERATING REPORT TABLES"
echo "============================================================"

cat > "$RESULTS_DIR/REPORT_TABLES.txt" << 'TABLEHEADER'
================================================================================
                    GCMC ADSORPTION ISOTHERMS - REPORT TABLES
================================================================================

Reference: Johnson, Zollweg & Gubbins, Mol. Phys. 78, 591 (1993)
  T_c* = 1.313 ± 0.001
  For T* = 0.8: P_sat* = 0.00395, ρ_gas* = 0.0092, ρ_liq* = 0.844

Notation (Frenkel & Smit):
  L*       Slit pore width (units of σ)
  T*       Reduced temperature (units of ε/k_B)
  PID      Reservoir ideal gas pressure P* = ρ_res * T*
  ρ*       Reduced pore density (N/V*)
  σ(ρ*)    Block averaging standard error
  %err     Relative error = 100 × σ(ρ*)/ρ*
  
================================================================================
TABLEHEADER

for cond in "${CONDITIONS[@]}"; do
    L="${cond%:*}"
    T="${cond#*:}"
    
    # Determine regime
    if [[ "$T" == "0.8" ]]; then
        REGIME="Subcritical"
    elif [[ "$T" == "1.3" ]]; then
        REGIME="Critical"
    else
        REGIME="Supercritical"
    fi
    
    cat >> "$RESULTS_DIR/REPORT_TABLES.txt" << CONDHEADER

--------------------------------------------------------------------------------
TABLE: L* = $L, T* = $T ($REGIME)
--------------------------------------------------------------------------------

    PID         ρ*          σ(ρ*)       %err      <N>        Acc_displ   Acc_exch
    ----------  ----------  ----------  ------    -------    ---------   --------
CONDHEADER
    
    if [[ -f "$RESULTS_DIR/L${L}_T${T}/raw_data.dat" ]]; then
        tail -n +2 "$RESULTS_DIR/L${L}_T${T}/raw_data.dat" | while read pid rho rho_err en en_err pr pr_err npart npart_err mu_ex displ exch; do
            if [[ -n "$rho" ]] && [[ "$rho" != "0" ]]; then
                # Calculate relative error
                rel_err=$(awk "BEGIN {if ($rho > 0.0001) printf \"%.2f\", 100*$rho_err/$rho; else print \"N/A\"}")
                printf "    %-10s  %-10.6f  %-10.6f  %-6s    %-7.1f    %-9s   %-8s\n" \
                    "$pid" "$rho" "$rho_err" "$rel_err" "$npart" "$displ%" "$exch%" >> "$RESULTS_DIR/REPORT_TABLES.txt"
            fi
        done
    fi
done

#===============================================================================
# VALIDATION AGAINST JOHNSON 1993
#===============================================================================

cat >> "$RESULTS_DIR/REPORT_TABLES.txt" << 'VALIDHEADER'

================================================================================
                         VALIDATION: COMPARISON TO LITERATURE
================================================================================

Expected behavior for BULK LJ fluid (Johnson et al. 1993):

T* = 0.8 (Subcritical):
  - Phase transition at P_sat* ≈ 0.00395
  - Gas density: ρ_gas* ≈ 0.0092 at P < P_sat
  - Liquid density: ρ_liq* ≈ 0.844 at P > P_sat
  - Sharp jump in ρ* around P_sat

T* = 1.3 (Critical):
  - Near critical point T_c* = 1.313
  - Large density fluctuations
  - No sharp phase transition
  - ρ_c* ≈ 0.316

T* = 2.0 (Supercritical):
  - Above critical point
  - Continuous, monotonic isotherm
  - No phase transition

CONFINEMENT EFFECTS (slit pore vs bulk):
  - Narrow pore (L*=2): Strong confinement, modified transition
  - Wide pore (L*=5): More bulk-like, transition near P_sat ≈ 0.004

--------------------------------------------------------------------------------
VALIDATION CHECKS:
--------------------------------------------------------------------------------

VALIDHEADER

# Check L=5, T=0.8 transition location
echo "Checking L*=5, T*=0.8 phase transition location..." >> "$RESULTS_DIR/REPORT_TABLES.txt"
echo "" >> "$RESULTS_DIR/REPORT_TABLES.txt"

if [[ -f "$RESULTS_DIR/L5.0_T0.8/raw_data.dat" ]]; then
    echo "  PID range around expected transition (P_sat* ≈ 0.00395):" >> "$RESULTS_DIR/REPORT_TABLES.txt"
    echo "" >> "$RESULTS_DIR/REPORT_TABLES.txt"
    
    prev_rho=0
    tail -n +2 "$RESULTS_DIR/L5.0_T0.8/raw_data.dat" | while read pid rho rho_err rest; do
        if [[ -n "$rho" ]]; then
            # Detect jump (density increases by more than 0.3)
            jump=$(awk "BEGIN {print ($rho - $prev_rho > 0.3) ? 1 : 0}")
            if [[ "$jump" == "1" ]] && [[ "$prev_rho" != "0" ]]; then
                echo "  *** TRANSITION DETECTED ***" >> "$RESULTS_DIR/REPORT_TABLES.txt"
                echo "  Between PID values with jump from ρ* ≈ $prev_rho to ρ* ≈ $rho" >> "$RESULTS_DIR/REPORT_TABLES.txt"
                echo "" >> "$RESULTS_DIR/REPORT_TABLES.txt"
            fi
            printf "    PID = %-10s  ρ* = %.5f\n" "$pid" "$rho" >> "$RESULTS_DIR/REPORT_TABLES.txt"
            prev_rho=$rho
        fi
    done
    
    echo "" >> "$RESULTS_DIR/REPORT_TABLES.txt"
    echo "  Expected: Transition near PID ≈ 0.004 (bulk P_sat*)" >> "$RESULTS_DIR/REPORT_TABLES.txt"
    echo "  For L*=5 pore, transition may shift slightly due to confinement" >> "$RESULTS_DIR/REPORT_TABLES.txt"
fi

# Summary validation
cat >> "$RESULTS_DIR/REPORT_TABLES.txt" << 'VALIDFOOTER'

--------------------------------------------------------------------------------
ACCEPTANCE RATIO CHECK (Frenkel & Smit, Ch. 3):
--------------------------------------------------------------------------------

  Displacement moves: Target 30-50% for efficient sampling
    - If too low (<20%): Maximum displacement too large
    - If too high (>70%): Maximum displacement too small
    
  Exchange moves: Depends on density
    - Gas phase: Higher acceptance (20-40%)
    - Liquid phase: Lower acceptance (1-10%)
    - Very low acceptance in dense liquid is NORMAL

--------------------------------------------------------------------------------
BLOCK AVERAGING ERROR CHECK:
--------------------------------------------------------------------------------

  Relative error %err = 100 × σ(ρ*)/ρ* should be:
    - < 5% for well-converged simulations
    - < 10% acceptable for most purposes
    - > 10% may need longer production runs
    
  Large errors in gas phase are normal (low density = few particles)
  
================================================================================
VALIDFOOTER

echo "[OK] Report tables generated"

#===============================================================================
# GENERATE PLOTS
#===============================================================================

echo ""
echo "Generating plots..."

cat > "$RESULTS_DIR/plot_isotherms.py" << 'PLOTEOF'
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
PLOTEOF

chmod +x "$RESULTS_DIR/plot_isotherms.py"
cd "$RESULTS_DIR"
python3 plot_isotherms.py 2>/dev/null && echo "[OK] Plots generated" || echo "[WARN] Plotting failed (matplotlib?)"

#===============================================================================
# FINAL SUMMARY
#===============================================================================

echo ""
echo "============================================================"
echo "  COMPLETE"
echo "============================================================"
echo ""
echo "  Simulations: $GRAND_SUCCESS / $GRAND_TOTAL successful"
echo ""
echo "  Results: $RESULTS_DIR"
echo ""
echo "  Files:"
echo "    REPORT_TABLES.txt    - Tables for report + validation"
echo "    L{L}_T{T}/raw_data.dat - Raw simulation data"
echo "    *.png, *.pdf         - Publication plots"
echo ""
echo "  Quick commands:"
echo "    cat $RESULTS_DIR/REPORT_TABLES.txt"
echo "    eog $RESULTS_DIR/*.png"
echo ""

# Show quick validation
echo "  Quick validation (L=5, T=0.8 transition):"
if [[ -f "$RESULTS_DIR/L5.0_T0.8/raw_data.dat" ]]; then
    echo "    Expected: transition near PID ≈ 0.004"
    echo "    Your data:"
    tail -n +2 "$RESULTS_DIR/L5.0_T0.8/raw_data.dat" | awk '{if ($2 > 0.0001) printf "      PID=%s -> rho=%.4f\n", $1, $2}' | head -10
fi

echo ""
echo "============================================================"

rm -rf "$WORKSPACE"
