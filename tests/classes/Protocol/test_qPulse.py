import quanguru as qg
import pytest
import numpy as np

def test_unitaryGeneration():
    """
    Testing that the unitary is correctly generated from some given simulation object

    Also test that:
        - when ._paramUpdated == True, the simulation is run to generate the unitary and is stored in qPulse._paramBoundBase__matrix
        - when ._paramUpdated == False, the unitary from qPulse._paramBoundBase__matrix is given.
    """
    unitary = np.random.rand(2, 2)
    pulse = qg.qPulse()
    qSim = qg.Simulation()
    qSys = qg.QuantumSystem(dimension=2, operator=qg.sigmax, frequency=1)
    qPro = qg.genericProtocol(system=qSys, createUnitary=lambda pro, a, b: unitary)
    qSim.addSubSys(qSys, qPro)
    pulse.uSim = qSim

    qSim.totalTime = 1
    qSim.stepCount = np.random.randint(1, 10)

    pulse._paramBoundBase__paramUpdated = False
    assert pulse._paramBoundBase__matrix is None

    pulse._paramBoundBase__paramUpdated = True
    pulse._paramBoundBase__matrix = None
    pulse.unitary()
    assert np.allclose(pulse._paramBoundBase__matrix, np.linalg.matrix_power(unitary, qSim.stepCount))

def test_paramUpdating():
    """
    Test that the ._paramUpdated if switched to True on:
        - assignment of uSim
        - reassignment of the systems and protocols inside uSim
        - any changes to
            - uSim time parameters
            - the protocols and systems inside uSim that switches their paramUpdated to True

    Test that removing a uSim removes the paramBound links between the qPulse and simulation
    """
    pulse = qg.qPulse()
    qSim = qg.Simulation()
    qSys = qg.QuantumSystem()
    qPro = qg.genericProtocol(system=qSys)

    #Assignment of uSim
    pulse._paramBoundBase__paramUpdated = False
    pulse.uSim = qSim
    assert pulse._paramBoundBase__paramUpdated

    #Assignment of uSim.subSys
    pulse._paramBoundBase__paramUpdated = False
    qSim.addSubSys(qSys, qPro)
    assert pulse._paramBoundBase__paramUpdated

    #Reassignment of uSim.subSys
    pulse._paramBoundBase__paramUpdated = False
    qSim.removeProtocol(qPro)
    qSim.addSubSys(qSys, qPro)
    assert pulse._paramBoundBase__paramUpdated

    #Changing time parameters of uSim
    pulse._paramBoundBase__paramUpdated = False
    pulse.uSim.totalTime = 5
    assert pulse._paramBoundBase__paramUpdated

    #Turning on ._paramUpdated of simulation
    pulse._paramBoundBase__paramUpdated = False
    qSim._paramUpdated = True
    assert pulse._paramBoundBase__paramUpdated

    #Turning on ._paramUpdated of system
    pulse._paramBoundBase__paramUpdated = False
    qSys._paramUpdated = True
    assert pulse._paramBoundBase__paramUpdated

    #Turning on ._paramUpdated of protocol
    pulse._paramBoundBase__paramUpdated = False
    qPro._paramUpdated = True
    assert pulse._paramBoundBase__paramUpdated

    #Removing the uSim
    pulse.uSim = None
    pulse._paramBoundBase__paramUpdated = False
    qSim._paramUpdated = True
    qSys._paramUpdated = True
    qPro._paramUpdated = True
    assert not pulse._paramBoundBase__paramUpdated

def test_systemAssignment():
    """
    Test that qPulse.system is correctly assigned to the subSys of uSim in the following cases:
        - assignment of uSim if the simulation object has a subSys in it
        - reassignment of the subSys in uSim
    """
    pulse = qg.qPulse()
    qSim = qg.Simulation()
    qSys = qg.QuantumSystem()
    qPro = qg.genericProtocol(system=qSys)

    pulse.uSim = qSim
    assert pulse.system is None
    
    qSim.addSubSys(qSys, qPro)
    assert pulse.system is qSys

@pytest.mark.parametrize('simType', ['pulse.simulation', 'independent'])
def test_pulseParamSweeps(simType):
    """
    Test that pulse parameters can be swept inside of a larger time dependent simulation object.
    """
    #Instantiation of system
    unitary = np.random.rand(2, 2)
    pulse = qg.qPulse(alias='pulse')
    qSim = qg.Simulation()
    qSys = qg.QuantumSystem(dimension=2, operator=qg.sigmax, frequency=1)
    # qPro = qg.genericProtocol(system=qSys, createUnitary=lambda pro, a, b: pro.system.frequency * pro.getByNameOrAlias('pulse').coeff * unitary, alias='qPro')
    qPro = qg.genericProtocol(system=qSys, createUnitary=lambda pro, a, b: pro.system.frequency * unitary, alias='qPro')
    qSim.addSubSys(qSys, qPro)

    pulse.coeff = 1

    #Time Parameters
    qSim.totalTime = 1
    qSim.stepCount = 5

    #Time dependency
    def omega_t(sweep):
        val = (sweep.index+1)*sweep.getByNameOrAlias('pulse').coeff
        sweep._runUpdate(val)

    omegaSweep = qSim.timeDependency.createSweep(
        system=qSys,
        sweepKey='frequency',
        sweepFunction=omega_t,
        sweepList = qSys.simulation.timeList[:-1]
    )

    pulse.uSim = qSim

    if simType == 'pulse.simulation':
        sim = pulse.simulation
    elif simType == 'independent':
        sim = qg.Simulation()
        sim.addQSystems(qSys, pulse)

    sim.totalTime = 1
    sim.stepCount = 1
    sim.delStates = True

    qSys.initialState = qg.basis(2, 0)

    sList = np.random.uniform(-10, 10, 10)
    sw = sim.Sweep.createSweep(system=pulse, sweepKey='coeff', sweepList=sList)

    def postCompute(sim):
        sim.qRes.singleResult = 'finalState', sim.getByNameOrAlias('pulse').currentState

    sim.postCompute = postCompute

    sim.run()

    n = qSim.stepCount
    assert np.all(
        [
            np.allclose(
                np.math.factorial(n)*(val**n)*np.linalg.matrix_power(unitary, n)@qg.basis(2, 0), 
                sim.resultsDict['finalState'][i]
            ) for i, val in enumerate(sList)
        ]
    )

    del pulse, qSim, qSys, qPro, sim, omegaSweep, sw
    qg.qBase._resetAll()