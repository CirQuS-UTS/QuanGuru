import quanguru as qg
import random
import numpy as np

def Upauli(theta, vector):
    sigmaVec = [qg.sigmax(), qg.sigmay(), qg.sigmaz()]
    totalOp = sum([vector[i] * sigmaVec[i] for i in range(3)])
    return qg.identity(2)*np.cos(theta/2) - 1j*np.sin(theta/2)*totalOp

def test_qProtocolCreateUnitary():
    """
    Tests that the createUnitary property can be set for qProtocol instance on instantiation and after instantiation
    """
    fQ, fCav, cavDim = round(random.random()*5), round(random.random()*5), random.randint(5, 10)
    sys = qg.Qubit(frequency=fQ) + qg.Cavity(frequency=fCav, dimension=cavDim)

    unitary = unitary = np.random.rand(2*cavDim, 2*cavDim)
    func = lambda self, x: unitary

    #on instantiation
    qPro = qg.qProtocol(system=sys, createUnitary=func)
    assert np.array_equal(qPro.unitary(), unitary)

    #after instantiation
    del qPro
    qPro = qg.qProtocol(system=sys)
    qPro.createUnitary = func
    assert np.array_equal(qPro.unitary(), unitary)

def test_callUnitaryMethod():
    """
    Test that the proper unitary is returned when .unitary is called for each protocol class

    Note this is not testing open system superoperators at all
    """

    fQ, fCav, cavDim = round(random.random()*5), round(random.random()*5), random.randint(5, 10)
    qub = qg.Qubit(frequency=fQ)
    sys = qg.Qubit(frequency=fQ) + qg.Cavity(frequency=fCav, dimension=cavDim)

    unitary = np.random.rand(2*cavDim, 2*cavDim)
    func = lambda self, x: unitary

    sim = qg.Simulation()
    freeEvolsys = qg.freeEvolution(system=sys)
    freeEvolqub = qg.freeEvolution(system=qub)
    x = qg.xGate(system=qub, angle=np.pi/2)
    spin = qg.SpinRotation(system=qub, angle=np.pi, rotationAxis='y')
    qProtocol1 = qg.qProtocol(system=sys, createUnitary=func)
    qProtocol2 = qg.qProtocol(system=qub, createUnitary=func, steps=[x, freeEvolqub, spin])

    sim.stepSize = 1

    #Testing freeEvolution
    sim.addProtocol(freeEvolsys, sys)
    sim.addProtocol(freeEvolqub, qub)

    assert np.sum(np.abs(freeEvolqub.unitary()-Upauli(sim.stepSize*qub.frequency, [0, 0, 1]))) < 1e-9
    assert np.sum(np.abs(freeEvolsys.unitary()-qg.Unitary(sys.totalHamiltonian.A))) < 1e-9

    #testing x gate
    sim.addProtocol(x, qub)
    assert np.sum(np.abs(x.unitary()-Upauli(np.pi/2, [1, 0, 0]))) < 1e-9

    #testing spinRotation
    sim.addProtocol(spin, qub)
    assert np.sum(np.abs(spin.unitary()-Upauli(np.pi, [0, 1, 0]))) < 1e-9

    #testing qProtocols
    sim.addProtocol(qProtocol1, sys)
    sim.addProtocol(qProtocol2, qub)

    assert np.sum(np.abs(qProtocol1.unitary()-unitary)) < 1e-9 
    assert np.sum(np.abs(
        qProtocol2.unitary()
        - Upauli(np.pi, [0, 1, 0]) @ Upauli(sim.stepSize*qub.frequency, [0, 0, 1]) @ Upauli(np.pi/2, [1, 0, 0])
    )) < 1e-9

def test_reassignCreateUnitary():
    qub = qg.Qubit()
    pros = [qg.freeEvolution(system=qub), qg.xGate(system=qub), qg.SpinRotation(system=qub)]

    unitary = np.random.rand(2, 2)
    func = lambda self, x: unitary
    
    for pro in pros:
        pro._createUnitary = func
        assert np.array_equal(pro.unitary(), unitary)


    
