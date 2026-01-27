#!/usr/bin/env python

import sys
from raspalib import *
from tqdm.autonotebook import tqdm
from time import sleep

# change input fugacity/pressure [Pa]
inputFugacity = 1e3

# change input temperature [K]
temperature = 200

swapProbability = 0.0
swapCBMCProbability = 0.0
swapCFCMCProbability = 1.0
swapCBCFCMCProbability = 0.0
widomProbability = 1.0

numberOfCycles = 10000
numberOfInitializationCycles = 5000
numberOfEquilibrationCycles = 10000

printEvery = 100

atomTypes = [
    PseudoAtom(name="Cu1", frameworkType=True, mass=63.5460, charge=1.248, atomicNumber=29),
    PseudoAtom(name="O1", frameworkType=True, mass=15.9994, charge=-0.624, atomicNumber=8),
    PseudoAtom(name="C1", frameworkType=True, mass=12.0107, charge=0.494, atomicNumber=6),
    PseudoAtom(name="C2", frameworkType=True, mass=12.0107, charge=0.13, atomicNumber=6),
    PseudoAtom(name="C3", frameworkType=True, mass=12.0107, charge=-0.156, atomicNumber=6),
    PseudoAtom(name="H1", frameworkType=True, mass=1.00794, charge=0.156, atomicNumber=1),
    PseudoAtom(name="C_co2", frameworkType=False, mass=12.0, charge=0.6512, atomicNumber=6),
    PseudoAtom(name="O_co2", frameworkType=False, mass=15.9994, charge=-0.3256, atomicNumber=8)
]


parameters = [
    VDWParameters(2.5161, 3.11369),
    VDWParameters(48.1581, 3.03315),
    VDWParameters(47.8562, 3.47299),
    VDWParameters(47.8562, 3.47299),
    VDWParameters(47.8562, 3.47299),
    VDWParameters(7.64893, 2.84642),
    VDWParameters(29.933, 2.745),
    VDWParameters(85.671, 3.017)
]

force_field = ForceField(
    pseudoAtoms=atomTypes,
    parameters=parameters,
    mixingRule=ForceField.MixingRule.Lorentz_Berthelot,
    cutOffFrameworkVDW=12.0,
    cutOffMoleculeVDW=12.0,
    cutOffCoulomb=12.0,
    shifted=True,
    tailCorrections=False,
    useCharge=True,
)


framework = Framework(
    frameworkId=0,
    forceField=force_field,
    componentName="Cu-BTC",
    simulationBox=SimulationBox(26.343, 26.343, 26.343),
    spaceGroupHallNumber=523,
    definedAtoms=[
        Atom(double3(0.2853, 0.2853, 0), 1.248, 1.0, 0, 0, 0, 0),
        Atom(double3(0.3166, 0.2431, 0.9478), -0.624, 1.0, 0, 1, 0, 0),
        Atom(double3(0.2968, 0.2032, 0.9313), 0.494, 1.0, 0, 2, 0, 0),
        Atom(double3(0.322, 0.178, 0.887), 0.130, 1.0, 0, 3, 0, 0),
        Atom(double3(0.3655, 0.1994, 0.8655), -0.156, 1.0, 0, 4, 0, 0),
        Atom(double3(0.3802, 0.228, 0.8802), 0.156, 1.0, 0, 5, 0, 0),
    ],
    numberOfUnitCells=int3(1, 1, 1),
)

move_probabilities = MCMoveProbabilities(
    translationProbability=0.5,
    rotationProbability=0.5,
    reinsertionCBMCProbability=0.5,
    swapProbability=swapProbability,
    swapCBMCProbability=swapCBMCProbability,
    swapCFCMCProbability=swapCFCMCProbability,
    swapCBCFCMCProbability=swapCBCFCMCProbability,
    widomProbability=widomProbability,
)

component = Component(
    componentId=0,
    forceField=force_field,
    componentName="CO2",
    criticalTemperature=304.1282,
    criticalPressure=7377300.0,
    acentricFactor=0.22394,
    definedAtoms=[
        Atom(double3(0.0, 0.0, 1.149), -0.3256, 1.0, 0, 7, 0, 0),
        Atom(double3(0.0, 0.0, 0.0), 0.6512, 1.0, 0, 6, 0, 0),
        Atom(double3(0.0, 0.0, -1.149), -0.3256, 1.0, 0, 7, 0, 0),
    ],
    numberOfBlocks=5,
    numberOfLambdaBins=21,
    particleProbabilities=move_probabilities,
    fugacityCoefficient=1.0,
    thermodynamicIntegration=True,
)

system_probabilities = MCMoveProbabilities()

system = System(
    systemId=0,
    forceField=force_field,
    simulationBox=None,
    externalTemperature=temperature,
    externalPressure=inputFugacity,
    heliumVoidFraction=0.774,
    frameworkComponents=framework,
    components=[component],
    initialNumberOfMolecules=[0],
    numberOfBlocks=5,
    systemProbabilities=system_probabilities,
    sampleMoviesEvery=None
)

mc = MonteCarlo(
    numberOfCycles=numberOfCycles,
    numberOfInitializationCycles=numberOfInitializationCycles,
    numberOfEquilibrationCycles=numberOfEquilibrationCycles,
    printEvery=printEvery,
    writeBinaryRestartEvery=5000,
    rescaleWangLandauEvery=2000,
    optimizeMCMovesEvery=2000,
    systems=[system],
    numberOfBlocks=5
)



def progress_call_back_initialization():
    progress_initialization.update(printEvery)
    total_progress.update(printEvery)
    sys.stdout.flush()

def progress_call_back_equilibration():
    progress_equilibration.update(printEvery)
    total_progress.update(printEvery)
    sys.stdout.flush()

def progress_call_back_production():
    progress_production.update(printEvery)
    total_progress.update(printEvery)
    sys.stdout.flush()

numberOfTotalCycles = numberOfCycles + numberOfInitializationCycles + numberOfEquilibrationCycles

with tqdm(total= numberOfTotalCycles, desc="Total", colour='black', position=3) as total_progress:

  progress_initialization = tqdm(total=numberOfInitializationCycles, desc="Initialization", colour='red', position=0)
  progress_equilibration = tqdm(total=numberOfEquilibrationCycles, desc=" Equilibration", colour='magenta', position=1)
  progress_production = tqdm(total=numberOfCycles, desc="    Production", colour='green', position=2)

  # Monte Carlo initialization step
  mc.initialize(call_back_function=progress_call_back_initialization)

  # Monte Carlo equilibration step (measuring bias-factors)
  mc.equilibrate(call_back_function=progress_call_back_equilibration)

  # Monte Carlo production step
  mc.production(call_back_function=progress_call_back_production)

  progress_initialization.close()
  progress_equilibration.close()
  progress_production.close()

pressure = mc.systems[0].inputPressure
print(f"The fugacity is: {pressure} Pa\n")
print(mc.systems[0].averageLoadings.writeAveragesStatistics(mc.systems[0].components, mc.systems[0].frameworkMass(), int3(1, 1, 1)))

print(mc.systems[0].writeMCMoveStatistics())
