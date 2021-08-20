import random as rn
import numpy as np

# open system dynamics of a qubit and compare numerical results with the analytical calculations
# NOTE these are also TUTORIALS of the library, so see the Tutorials for what these are doing and analytical
# calculations.

# currently includes 2 cases: (i) decay only, and (ii) unitary evolution by calling Liouville method without giving
# any collapse operators. For now, only looks at excited state populations

# TODO this is an unfinished test. below two tests are the same and it actually is not testing open system dynamics.

decayRateSM = rn.random()

excitedPopulation = lambda t: 0.5*np.exp(-(0.00001*(decayRateSM+1)*2+1j)*50*t)
populations = {'excitedAnalytical':[], 'excitedNumerical':[]}

# this is used as the calculate attribute of the qubit, and the singleQubit fixture evolve method calls this at every
# step of the evolution. It stores both numerical and analytical excited state populations into the dictionary above.
def singleQubitDecayCalculate(qub, state, i):
    populations['excitedAnalytical'].append(excitedPopulation(i*qub.stepSize))
    populations['excitedNumerical'].append(state[0, 0])

def test_qubitUnitaryEvolutionFromLiouville(singleQubit):
    for k in populations:
        populations[k] = []
    singleQubit.evolutionMethod = singleQubit.openEvolution
    singleQubit.calculate = singleQubitDecayCalculate
    singleQubit.evolve()
    assert singleQubit.stepCount == len(populations['excitedNumerical'])

def test_qubitDecay(singleQubit):
    for k in populations:
        populations[k] = []
    singleQubit.evolutionMethod = singleQubit.openEvolution
    singleQubit.calculate = singleQubitDecayCalculate
    singleQubit.evolve()
    assert singleQubit.stepCount == len(populations['excitedNumerical'])
