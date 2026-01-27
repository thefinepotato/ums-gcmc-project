# Path Metadynamics with PLUMED

This directory contains exercises on enhanced sampling methods using PLUMED, focusing on metadynamics and path metadynamics for studying rare events and barrier crossing.

## Overview

The exercises use a 2D Muller-Brown-like potential energy surface to demonstrate:
1. Standard molecular dynamics and its limitations
2. Metadynamics for enhanced sampling
3. Fixed path metadynamics
4. Adaptive path metadynamics

## Directory Structure

### Notebooks (Analysis and Visualization)
- **`1_md_on_potential.ipynb`**: Standard MD on 2D PES, visualization of trajectories and sampling limitations
- **`2_metadynamics.ipynb`**: Metadynamics simulations, bias evolution, and free energy reconstruction
- **`3_path_metadynamics.ipynb`**: Path metadynamics (fixed and adaptive), path evolution, and free energy profiles

### PLUMED Installation
- **`plumed/`**: PLUMED 2.3.0 installation directory with custom modules
  - Custom modules: `MetaD.cpp`, `PathCV.cpp`, `PES.cpp`, `LatticeReduction.cpp`
  - Binaries in `plumed/bin/`
  - Libraries in `plumed/lib/`

### Exercises
- **`Exercise/`**: Simulation input files and results
  - `input`: Common input parameters (temperature, friction, timestep, etc.)
  - `0_md/`: Standard MD simulation
  - `1_metadynamics/`: Standard metadynamics simulation
  - `2_fixedpathmetadynamics/`: Fixed path metadynamics
  - `3_adaptivepathmetadynamics/`: Adaptive path metadynamics

### Auxiliary Files
- **`potential.dat`**: 2D potential energy surface data
- **`make_potential.sh`**: Script to generate the potential using AWK
- **`script.awk`**: AWK script defining the potential function

## Setup

### Prerequisites
- Python 3.x with NumPy, Matplotlib, SciPy
- C++ compiler (for building PLUMED)
- MPI (optional, for parallel execution)

### Installation

PLUMED has already been compiled and installed in the `plumed/` directory. To use it:

```bash
# Set up environment (in the day7_path_meta_dynamics directory)
export PATH=$PWD/plumed/bin:$PATH
export PLUMED_KERNEL=$PWD/plumed/lib/libplumedKernel.dylib
```

## Running the Tutorials

### 1. Generate the Potential

```bash
bash make_potential.sh > potential.dat
```

### 2. Run Simulations

Each exercise directory contains a `plumed.dat` file with PLUMED input. To run:

```bash
# Standard MD
cd Exercise/0_md
../../plumed/bin/plumed pesmd < ../input

# Metadynamics
cd ../1_metadynamics
../../plumed/bin/plumed pesmd < ../input
../../plumed/bin/plumed sum_hills --hills HILLS --outfile fes.dat --min -3.0,-1.5 --max 2.0,3.5 --bin 99,99

# Fixed path metadynamics
cd ../2_fixedpathmetadynamics
../../plumed/bin/plumed pesmd < ../input
../../plumed/bin/plumed sum_hills --hills HILLS --outfile fes.dat

# Adaptive path metadynamics
cd ../3_adaptivepathmetadynamics
../../plumed/bin/plumed pesmd < ../input
../../plumed/bin/plumed sum_hills --hills HILLS --outfile fes.dat
```

### 3. Analyze Results

Open and run the Jupyter notebooks in order:
1. `1_md_on_potential.ipynb`
2. `2_metadynamics.ipynb`
3. `3_path_metadynamics.ipynb`

## Key Concepts

### Metadynamics
- Enhanced sampling method that fills energy basins with Gaussian hills
- Bias potential: V_bias(s,t) = Σ W exp[-(s-s(t'))²/2σ²]
- Free energy: F(s) ≈ -V_bias(s, t→∞)

### Path Collective Variables
- **s**: Progress along the path (0 to 1)
- **z**: Distance from the path
- Defined using weighted averages over reference path nodes

### Path Metadynamics Variants
- **Fixed**: Predefined path, metadynamics along s
- **Adaptive**: Path evolves to find minimum free energy path (MFEP)

## Output Files

Each exercise generates:
- **`colvar.out`**: Collective variables, bias potential vs time
- **`HILLS`**: Deposited Gaussian hills (time, center, sigma, height)
- **`fes.dat`**: Reconstructed free energy surface
- **`path.out`**: Path evolution (adaptive only)

## Parameters

### Simulation (in `Exercise/input`)
- Temperature: 0.5 K
- Friction: 0.1
- Timestep: 0.001
- Steps: 500,000
- Initial position: (0.6, 0.0)

### Metadynamics (in `plumed.dat`)
- Hill height: 0.1 K (standard), 0.8 K (path)
- Hill width: σ = 0.1
- Deposition pace: every 500 steps

## References

1. Laio, A., & Parrinello, M. (2002). Escaping free-energy minima. PNAS, 99(20), 12562-12566.
2. Branduardi, D., Gervasio, F. L., & Parrinello, M. (2007). From A to B in free energy space. J. Chem. Phys., 126(5), 054103.
3. Díaz Leines, G., & Ensing, B. (2012). Path finding on high-dimensional free energy landscapes. Phys. Rev. Lett., 109(2), 020601.
4. Pérez de Alba Ortíz, A., et al. (2018). Advances in enhanced sampling along adaptive paths of collective variables. J. Chem. Phys., 149(7), 072320.
5. Tribello, G. A., et al. (2014). PLUMED 2: New feathers for an old bird. Comp. Phys. Comm., 185(2), 604-613.

## Tips and Troubleshooting

- If PLUMED commands fail, check that the environment variables are set correctly
- The MPI warnings about shared memory can be safely ignored
- For better convergence in metadynamics, consider using well-tempered metadynamics
- Path metadynamics requires careful choice of initial path and number of nodes
- The adaptive algorithm may need longer simulations to fully converge

## Learning Objectives

After completing these exercises, you should understand:
1. Why standard MD has difficulty sampling rare events
2. How metadynamics accelerates sampling by filling energy basins
3. The relationship between bias potential and free energy
4. How path collective variables reduce dimensionality
5. The difference between fixed and adaptive path approaches
6. How to interpret free energy profiles along reaction coordinates
