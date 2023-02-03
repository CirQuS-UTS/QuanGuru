import quanguru as qg
import numpy as np

def test_unitaryGeneration():
    """
    Testing that the unitary is correctly generated from some given simulation object
    """
    
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

def test_paramBoundMatrix():
    """
    Test that when ._paramUpdated == True, the simulation is run to generate the unitary.
    Test that the unitary generated from uSim is correctly stored in qPulse._paramBoundBase__matrix.
    Test that when qPulse._paramUpdated == False, the unitary from qPulse._paramBoundBase is given.
    """
    unitary = np.random.rand(2, 2)
    pulse = qg.qPulse()
    qSim = qg.Simulation()
    qSys = qg.QuantumSystem(dimension=2, operator=qg.sigmax, frequency=1)
    qPro = qg.genericProtocol(system=qSys, createUnitary=lambda pro, a, b: unitary)
    qSim.addSubSys(qSys, qPro)
    pulse.uSim = qSim

    qSim.totalTime = 1
    qSim.stepCount = 1

    pulse._paramBoundBase__paramUpdated = True
    pulse._paramBoundBase__matrix = None
    pulse.unitary()

def test_systemAssignment():
    """
    Test that qPulse.system is correctly assigned to the subSys of uSim in the following cases:
        - assignment of uSim if the simulation object has a subSys in it
        - reassignment of the subSys in uSim
    """

def test_pulseParamSweeps():
    """
    Test that pulse parameters (pulse duration and amplitude in this example) can be swept inside of a larger simulation object.
    """

