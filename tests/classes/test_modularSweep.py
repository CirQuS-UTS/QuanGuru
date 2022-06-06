import numpy as np
import pytest
from quanguru import QuantumSystem, sigmam, Qubit, freeEvolution

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

    # write a compute function for the qubit
    def compute(qub, st):
        qub.qRes.result = 'storedOnce', 1
    qubit.compute = compute

    # run the simulation
    qubit.runSimulation()

    # length of results is not 101 but 202
    assert len(qubit.qRes.results['storedOnce']) == (qubit.simulation.stepCount+1)

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
