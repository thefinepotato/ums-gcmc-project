"""
Grand-Canonical Monte Carlo (GCMC) Simulation
Lennard-Jones Fluid

This is a simplified Python version of the Fortran Case Study 9 code.
Written for learning - heavily commented.

Author: Educational version for UMS project
"""

import numpy as np
import random

# =============================================================================
# WHAT THIS CODE DOES (Big Picture)
# =============================================================================
#
# Imagine a box of particles (like gas molecules).
# The box is connected to a "reservoir" - an infinite supply of particles
# at a fixed temperature T and chemical potential μ.
#
# The simulation does three things repeatedly:
#   1. Try to MOVE a random particle to a new position
#   2. Try to INSERT a new particle from the reservoir
#   3. Try to DELETE a random particle (send it back to reservoir)
#
# Whether each attempt succeeds depends on energy - moves that lower
# energy are always accepted, moves that raise energy are sometimes accepted.
#
# After many cycles, we measure the average density, energy, pressure.
# This tells us: at this chemical potential, how many particles want to be
# in the box? That's the basis of an adsorption isotherm.
#
# =============================================================================


# =============================================================================
# SIMULATION PARAMETERS
# =============================================================================

# Box and particles
N_INITIAL = 50          # Starting number of particles
DENSITY_INITIAL = 0.6   # Starting density (particles per volume)
TEMPERATURE = 0.9       # Temperature (in reduced units: T* = T/(ε/kB))

# Reservoir
PID = 0.016            # Ideal gas pressure of reservoir
                        # This controls chemical potential: higher pid = more particles want to enter

# Simulation length  
N_EQUIL = 100           # Equilibration cycles (let system relax, don't measure)
N_PROD = 200            # Production cycles (measure averages here)
SAMPLE_FREQ = 2         # Measure every this many cycles

# Move parameters
N_DISPLACE = 100        # Displacement attempts per cycle
N_EXCHANGE = 10         # Insert/delete attempts per cycle
DR_MAX = 0.1            # Maximum displacement distance (will be adjusted)

# Potential parameters
RC = 2.5                # Cutoff radius - ignore interactions beyond this distance
                        # (saves computation, doesn't affect results much)

#My own paramters
#Slit width
SLITWIDTH = 5


# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

# These will be set during initialization
box = 0.0               # Box length
beta = 0.0              # 1/temperature (appears everywhere in stat mech)
zz = 0.0                # "Activity" = beta * pid (controls insert/delete probability)

# Particle positions - stored as lists (will grow/shrink as particles added/removed)
x = []
y = []
z = []


# =============================================================================
# LENNARD-JONES POTENTIAL
# =============================================================================
#
# The Lennard-Jones potential describes how two particles interact:
#
#   U(r) = 4ε [(σ/r)^12 - (σ/r)^6]
#
# Where:
#   r = distance between particles
#   ε = energy scale (depth of the attractive well)
#   σ = length scale (particle "diameter")
#
# In "reduced units", we set ε = 1 and σ = 1, so:
#
#   U(r) = 4 [1/r^12 - 1/r^6]
#
# The (σ/r)^12 term = strong repulsion at short range (particles can't overlap)
# The (σ/r)^6 term = weak attraction at longer range (van der Waals)
#
# =============================================================================

def lj_energy(r2):
    """
    Calculate Lennard-Jones energy given r² (distance squared).
    
    We pass r² instead of r to avoid computing sqrt (faster).
    
    Parameters
    ----------
    r2 : float
        Square of distance between two particles
        
    Returns
    -------
    energy : float
        LJ potential energy (0 if beyond cutoff)
    """
    if r2 > RC * RC:
        # Beyond cutoff - no interaction
        return 0.0
    
    # r^2, r^6, r^12
    r2i = 1.0 / r2          # 1/r^2
    r6i = r2i * r2i * r2i   # 1/r^6
    r12i = r6i * r6i        # 1/r^12
    
    # U = 4 * (1/r^12 - 1/r^6)
    return 4.0 * (r12i - r6i)


# =============================================================================
# PERIODIC BOUNDARY CONDITIONS (PBC)
# =============================================================================
#
# Problem: We simulate ~50 particles, but want to model bulk fluid (infinite).
# Solution: Wrap the box around on itself, like a video game screen.
#
# If a particle exits the right side, it re-enters from the left.
# This way, there are no "edges" - every particle sees the same environment.
#
# For distances: if two particles are "far apart" in the box, they might
# actually be close through the periodic boundary. We use the "minimum image"
# convention - always use the shortest distance.
#
#   Example: box = 10, particle A at x=1, particle B at x=9
#   Naive distance: 9 - 1 = 8
#   But through the boundary: 1 - (9-10) = 1 - (-1) = 2  ← shorter!
#
# =============================================================================

def minimum_image(dx, box_length):
    """
    Apply minimum image convention.
    
    If dx > box/2, the particle is closer through the other side.
    
    Parameters
    ----------
    dx : float
        Raw distance in one dimension
    box_length : float
        Size of periodic box
        
    Returns
    -------
    dx : float
        Shortest distance accounting for periodicity
    """
    if dx > box_length / 2:
        dx = dx - box_length
    elif dx < -box_length / 2:
        dx = dx + box_length
    return dx


def wrap_position(pos, box_length):
    """
    Wrap a position back into the box [0, box_length).
    
    If particle moves outside, put it back on the other side.
    """
    if pos < 0:
        pos = pos + box_length
    elif pos >= box_length:
        pos = pos - box_length
    return pos


# =============================================================================
# ENERGY CALCULATIONS
# =============================================================================

def energy_of_particle(i):
    """
    Calculate energy of particle i with ALL other particles.
    
    This is used when we want to move/delete particle i - we need to know
    how much energy we'd lose.
    
    Parameters
    ----------
    i : int
        Index of the particle
        
    Returns
    -------
    energy : float
        Total interaction energy of particle i with all others
    """
    energy = 0.0
    n = len(x)
    
    for j in range(n):
        if j == i:
            continue  # Don't calculate self-interaction
            
        # Distance in each dimension
        dx = x[i] - x[j]
        dy = y[i] - y[j]
        dz = z[i] - z[j]
        
        # Apply minimum image (periodic boundaries)
        dx = minimum_image(dx, box)
        dy = minimum_image(dy, box)
        dz = minimum_image(dz, box)
        
        # Squared distance
        r2 = dx*dx + dy*dy + dz*dz
        
        # Add LJ energy
        energy += lj_energy(r2)
    
    return energy


def energy_at_position(xp, yp, zp, exclude=-1):
    """
    Calculate energy if a particle were placed at position (xp, yp, zp).
    
    Used for:
    - Trial moves (what would energy be if we moved here?)
    - Trial insertions (what would energy be if we added a particle here?)
    
    Parameters
    ----------
    xp, yp, zp : float
        Trial position
    exclude : int
        Particle index to exclude (use when moving existing particle)
        Set to -1 for insertions (no exclusion)
        
    Returns
    -------
    energy : float
        Total interaction energy at this position
    """
    energy = 0.0
    n = len(x)
    
    for j in range(n):
        if j == exclude:
            continue
            
        dx = xp - x[j]
        dy = yp - y[j]
        dz = zp - z[j]
        
        dx = minimum_image(dx, box)
        dy = minimum_image(dy, box)
        dz = minimum_image(dz, box)
        
        r2 = dx*dx + dy*dy + dz*dz
        energy += lj_energy(r2)
    
    return energy


def total_energy():
    """
    Calculate total energy of the entire system.
    
    Sum over all pairs (count each pair once).
    """
    energy = 0.0
    n = len(x)
    
    for i in range(n):
        for j in range(i + 1, n):  # j > i to avoid double counting
            dx = x[i] - x[j]
            dy = y[i] - y[j]
            dz = z[i] - z[j]
            
            dx = minimum_image(dx, box)
            dy = minimum_image(dy, box)
            dz = minimum_image(dz, box)
            
            r2 = dx*dx + dy*dy + dz*dz
            energy += lj_energy(r2)
    
    return energy


# =============================================================================
# MONTE CARLO MOVE: DISPLACEMENT
# =============================================================================
#
# Algorithm:
# 1. Pick a random particle
# 2. Propose moving it by a small random amount
# 3. Calculate energy change ΔE = E_new - E_old
# 4. Accept or reject using Metropolis criterion:
#    - If ΔE < 0 (lower energy): ALWAYS accept
#    - If ΔE > 0 (higher energy): Accept with probability exp(-βΔE)
#
# The Metropolis criterion ensures we sample the Boltzmann distribution:
# States with lower energy are more likely, but higher energy states
# are still possible (thermal fluctuations).
#
# =============================================================================

def mc_move(dr_max):
    """
    Attempt to displace a random particle.
    
    Parameters
    ----------
    dr_max : float
        Maximum displacement in each direction
        
    Returns
    -------
    accepted : bool
        Whether the move was accepted
    """
    global x, y, z
    
    n = len(x)
    if n == 0:
        return False
    
    # 1. Pick random particle
    i = random.randint(0, n - 1)
    
    # 2. Calculate current energy of this particle
    energy_old = energy_of_particle(i)
    
    # 3. Propose new position (random displacement)
    x_new = x[i] + (random.random() - 0.5) * dr_max
    y_new = y[i] + (random.random() - 0.5) * dr_max
    z_new = z[i] + (random.random() - 0.5) * dr_max

    if z_new < 0 or z_new > SLITWIDTH:
        return False

    # 4. Calculate energy at new position
    energy_new = energy_at_position(x_new, y_new, z_new, exclude=i)
    
    # 5. Acceptance test (Metropolis criterion)
    delta_e = energy_new - energy_old
    
    if delta_e < 0:
        # Lower energy - always accept
        accept = True
    else:
        # Higher energy - accept with probability exp(-β * ΔE)
        accept = random.random() < np.exp(-beta * delta_e)
    
    # 6. If accepted, update position (with periodic wrapping)
    if accept:
        x[i] = wrap_position(x_new, box)
        y[i] = wrap_position(y_new, box)
        z[i] = wrap_position(z_new, box)
        
    return accept


# =============================================================================
# MONTE CARLO MOVE: INSERTION / DELETION
# =============================================================================
#
# In grand-canonical ensemble, particles can enter/leave the system.
# This is how we control density via chemical potential.
#
# INSERTION:
# 1. Pick a random position in the box
# 2. Calculate energy if we put a particle there
# 3. Accept with probability: min(1, (zz * V / (N+1)) * exp(-β * ΔE))
#
# DELETION:
# 1. Pick a random particle
# 2. Calculate energy we'd lose by removing it
# 3. Accept with probability: min(1, (N / (zz * V)) * exp(-β * ΔE))
#
# The factors (zz * V / N) come from the statistical mechanics of
# grand-canonical ensemble. They ensure detailed balance:
# rate of insertion = rate of deletion at equilibrium.
#
# zz = β * pid is the "activity" - controls how eager particles are
# to enter the system. Higher zz = more insertions accepted.
#
# =============================================================================

def mc_exchange():
    """
    Attempt to insert or delete a particle.
    
    Randomly choose insertion (50%) or deletion (50%).
    
    Returns
    -------
    accepted : bool
        Whether the move was accepted
    """
    global x, y, z
    
    n = len(x)
    vol = box ** 3
    
    if random.random() < 0.5:
        # ===== INSERTION =====
        
        # 1. Pick random position
        x_new = random.random() * box
        y_new = random.random() * box
        z_new = random.random() * box
        
        # 2. Calculate energy of inserting particle here
        energy_new = energy_at_position(x_new, y_new, z_new)
        
        # 3. Acceptance probability
        # P_acc = min(1, (zz * V / (N+1)) * exp(-β * E_new))
        arg = (zz * vol / (n + 1)) * np.exp(-beta * energy_new)
        
        if random.random() < arg:
            # Accept: add particle
            x.append(x_new)
            y.append(y_new)
            z.append(z_new)
            return True
        else:
            return False
            
    else:
        # ===== DELETION =====
        
        if n == 0:
            return False  # Can't delete from empty box
        
        # 1. Pick random particle
        i = random.randint(0, n - 1)
        
        # 2. Calculate energy we'd lose
        energy_old = energy_of_particle(i)
        
        # 3. Acceptance probability
        # P_acc = min(1, (N / (zz * V)) * exp(+β * E_old))
        # Note: +β*E because we GAIN energy by removing attractive interactions
        arg = (n / (zz * vol)) * np.exp(beta * energy_old)
        
        if random.random() < arg:
            # Accept: remove particle (swap with last, then pop)
            x[i] = x[-1]
            y[i] = y[-1]
            z[i] = z[-1]
            x.pop()
            y.pop()
            z.pop()
            return True
        else:
            return False


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_lattice():
    """
    Place particles on a simple cubic lattice.
    
    This gives a reasonable starting configuration.
    The exact starting positions don't matter much - the simulation
    will relax to equilibrium during the equilibration phase.
    """
    global x, y, z, box, beta, zz
    
    # Calculate box size from density
    # density = N / V = N / box^3
    # box = (N / density)^(1/3)
    box = (N_INITIAL / DENSITY_INITIAL) ** (1.0/3.0)
    
    # Calculate derived quantities
    beta = 1.0 / TEMPERATURE
    zz = beta * PID
    
    # Clear particle lists
    x = []
    y = []
    z = []
    
    # Calculate lattice spacing
    n_side = int(np.ceil(N_INITIAL ** (1.0/3.0)))  # Particles per side
    spacing = box / n_side
    
    # Place particles on lattice
    count = 0
    for ix in range(n_side):
        for iy in range(n_side):
            for iz in range(n_side):
                if count >= N_INITIAL:
                    break
                x.append(ix * spacing)
                y.append(iy * spacing)
                z.append(iz * spacing)
                count += 1
            if count >= N_INITIAL:
                break
        if count >= N_INITIAL:
            break
    
    print(f"Initialized {len(x)} particles on lattice")
    print(f"Box size: {box:.3f}")
    print(f"Temperature: {TEMPERATURE}, beta: {beta:.3f}")
    print(f"Activity zz: {zz:.6f}")


# =============================================================================
# MAIN SIMULATION
# =============================================================================

def run_simulation():
    """
    Run the full GCMC simulation.
    """
    global DR_MAX
    
    # Initialize
    initialize_lattice()
    
    # Check initial energy
    e_init = total_energy()
    print(f"Initial energy: {e_init:.3f}")
    print()
    
    # Storage for measurements
    energies = []
    densities = []
    
    # Counters for acceptance rates
    move_attempts = 0
    move_accepts = 0
    exch_attempts = 0
    exch_accepts = 0
    
    # ===== MAIN LOOP =====
    for phase in ["equilibration", "production"]:
        
        n_cycles = N_EQUIL if phase == "equilibration" else N_PROD
        print(f"Starting {phase} ({n_cycles} cycles)")
        
        # Reset counters for this phase
        move_attempts = 0
        move_accepts = 0
        exch_attempts = 0
        exch_accepts = 0
        
        for cycle in range(1, n_cycles + 1):
            
            # Each cycle: do many moves
            n_moves = N_DISPLACE + N_EXCHANGE
            
            for _ in range(n_moves):
                # Randomly choose displacement or exchange
                if random.random() < N_DISPLACE / n_moves:
                    # Displacement move
                    move_attempts += 1
                    if mc_move(DR_MAX):
                        move_accepts += 1
                else:
                    # Exchange move (insert/delete)
                    exch_attempts += 1
                    if mc_exchange():
                        exch_accepts += 1
            
            # Sample observables (production phase only)
            if phase == "production" and cycle % SAMPLE_FREQ == 0:
                n = len(x)
                vol = box ** 3
                e = total_energy() / n if n > 0 else 0
                rho = n / vol
                
                energies.append(e)
                densities.append(rho)
            
            # Progress report
            if cycle % (n_cycles // 5) == 0:
                n = len(x)
                print(f"  Cycle {cycle}/{n_cycles}, N = {n}")
                
                # Adjust displacement for ~50% acceptance
                if move_attempts > 0:
                    acc_rate = move_accepts / move_attempts
                    if acc_rate > 0.55:
                        DR_MAX *= 1.1  # Increase displacement
                    elif acc_rate < 0.45:
                        DR_MAX *= 0.9  # Decrease displacement
        
        # End of phase statistics
        print(f"  Move acceptance: {100*move_accepts/max(1,move_attempts):.1f}%")
        print(f"  Exchange acceptance: {100*exch_accepts/max(1,exch_attempts):.1f}%")
        print()
    
    # ===== RESULTS =====
    print("="*50)
    print("RESULTS")
    print("="*50)
    print(f"Energy/particle: {np.mean(energies):.4f} ± {np.std(energies):.4f}")
    print(f"Density:         {np.mean(densities):.4f} ± {np.std(densities):.4f}")
    print(f"Final N:         {len(x)}")
    
    return energies, densities


# =============================================================================
# RUN IT
# =============================================================================

if __name__ == "__main__":
    energies, densities = run_simulation()
    
    # Optional: plot if matplotlib available
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))
        
        ax1.plot(energies)
        ax1.axhline(np.mean(energies), color='r', linestyle='--')
        ax1.set_ylabel('Energy/particle')
        ax1.set_title('GCMC Simulation Results')
        
        ax2.plot(densities)
        ax2.axhline(np.mean(densities), color='r', linestyle='--')
        ax2.set_ylabel('Density')
        ax2.set_xlabel('Sample')
        
        plt.tight_layout()
        plt.savefig('gcmc_python_results_0016.png', dpi=150)
        plt.show()
        
    except ImportError:
        print("\n(Install matplotlib to see plots)")