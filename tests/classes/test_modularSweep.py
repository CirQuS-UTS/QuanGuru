import numpy as np
import pytest
from quanguru import QuantumSystem, sigmam, Qubit, freeEvolution, Simulation, genericProtocol, QuantumToolbox

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

def test_doCompute():
    def preCompute(obj):
        obj.auxDict['pre'] += 1
    def compute(obj, state):
        obj.auxDict['comp'] += 1
    def postCompute(obj):
        obj.auxDict['post'] += 1

    qSim = Simulation(preCompute=preCompute, postCompute=postCompute, compute=compute)
    qSys = [QuantumSystem(dimension=2, preCompute=preCompute, postCompute=postCompute, compute=compute) for i in range(5)]
    qPro = [genericProtocol(system=qSys[i], preCompute=preCompute, postCompute=postCompute, compute=compute, createUnitary=lambda a, b, c: QuantumToolbox.identity(2)) for i in range(5)]
    qSim.auxDict['pre'] = 0
    qSim.auxDict['comp'] = 0
    qSim.auxDict['post'] = 0

    for sys, pro in zip(qSys, qPro): 
        qSim.addQSystems(sys, pro)
        sys.initialState = QuantumToolbox.basis(2, 0)
    
    qSim.totalTime = 5
    qSim.stepCount = 5

    qSim.run()
    assert qSim.auxDict['pre'] == 1 + len(qSys) + len(qPro)
    assert qSim.auxDict['comp'] == (1 + len(qSys) + len(qPro))*(qSim.stepCount+1)
    assert qSim.auxDict['post'] == 1 + len(qSys) + len(qPro)