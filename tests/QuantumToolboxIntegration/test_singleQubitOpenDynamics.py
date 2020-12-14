import random as rn
import numpy as np

decayRateSM = rn.random()

excitedPopulation = lambda t: 0.5*np.exp(-(0.00001*(decayRateSM+1)*2+1j)*50*t)
populations = {'excitedAnalytical':[], 'excitedNumerical':[]}

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
