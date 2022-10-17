import numpy as np
import pytest
from quanguru import QuantumSystem, sigmam, Qubit, freeEvolution

# write a compute function for the qubit
def computeREF(qub, st):
    qub.qRes.singleResult = 'storedOnce', 1

def test_computeFunctionCallCount():
    # create a qubit
    qubit = Qubit(frequency=1)

    # create a second protocol for the system
    secondPro = freeEvolution(system=qubit)

    # add the second protocol to the simulation
    qubit.simulation.addSubSys(qubit, secondPro)
    qubit.simTotalTime = 2*np.pi
    qubit.simStepCount = 100
    qubit.simulation.initialState = [0, 1]

    qubit.compute = computeREF

    # run the simulation
    qubit.runSimulation()

    # length of results is not 101 but 202
    assert len(qubit.qRes.resultsDict['storedOnce']) == (qubit.simulation.stepCount+1)

def test_noInitialStateRequiredWhenNoTimeEvolution():
    # create a quantum system
    qsys = QuantumSystem()

    # turn off the time evolution
    qsys.simulation.evolFunc = None

    # run the simulation
    states = qsys.runSimulation()
    assert states == []

def test_noInitialStateRequiredWhenNoTimeEvolutionWithDimension():
    # create a quantum system
    qsys = QuantumSystem(dimension=1)

    # turn off the time evolution
    qsys.simulation.evolFunc = None

    # run the simulation
    states = qsys.runSimulation()
    assert states == []

def test_noInitialStateRequiredWhenNoTimeEvolutionWithOperator():
    # create a quantum system
    qsys = QuantumSystem(operator=sigmam)

    # turn off the time evolution
    qsys.simulation.evolFunc = None

    # run the simulation
    with pytest.raises(ValueError):
        states = qsys.runSimulation()


def test_noInitialStateRequiredWhenNoTimeEvolutionWithFrequency():
    # create a quantum system
    qsys = QuantumSystem(frequency=1)

    # turn off the time evolution
    qsys.simulation.evolFunc = None

    # run the simulation
    with pytest.raises(ValueError):
        states = qsys.runSimulation()

def test_noInitialStateRequiredWhenNoTimeEvolutionWithOrder():
    # create a quantum system
    qsys = QuantumSystem(order=3, dimension=2)

    # turn off the time evolution
    qsys.simulation.evolFunc = None

    # run the simulation
    with pytest.raises(TypeError):
        states = qsys.runSimulation()

### Tests related to issue #211
def test_runSingleSimulation():
    """
    Tests Backwards compatibility. Runs the simulation object of a single quantum system with a time dependent 
    drive term.
    """
    pass

def test_runNestedSimulationsOnMainSimulationClock():
    """
    Tests Backwards compatibility. Runs a simulation with multiple different systems and corresponding protocols, all
    on the same clock (share the same time parameters) as the main simulation.
    """
    pass

def test_runUniqueIndependentSimulationsNestedInSimulation():
    """
    Tests running multiple simulations with unique time dependencies, time parameters, and initial states under a 
    single simulation object which sweeps a single parameter. The nested simulations run independently of each other.
    """
    pass

def test_runUniqueSequentialSimulationsNestedInSimulation():
    """
    Tests running multiple simulations with unique time dependencies, time parameters, and initial states under a 
    single simulation object which sweeps a single parameter. The nested simulations run sequentially, that is, each
    simulation runs to completion and passes its final state to the next simulation to use as its initial state.
    """
    pass

