from ast import operator
import pytest
from quanguru import QuantumSystem, sigmam

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
