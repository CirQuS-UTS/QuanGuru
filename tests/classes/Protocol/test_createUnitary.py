import quanguru as qg
import random
import numpy as np

def Upauli(theta, vector):
    sigmaVec = [qg.sigmax(), qg.sigmay(), qg.sigmaz()]
    totalOp = sum([vector[i] * sigmaVec[i] for i in range(3)])
    return qg.identity(2)*np.cos(theta/2) - 1j*np.sin(theta/2)*totalOp

def test_assignCreateUnitary():
    """
    Tests that the createUnitary property can be set for qProtocol instance on and after instantiation
    """
    qub = qg.Qubit(frequency=round(random.random(), 2))
    unitary = unitary = np.random.rand(2, 2)
    func = lambda self, collapseOps, decayRate: unitary

    pros = [qg.genericProtocol, qg.freeEvolution, qg.qProtocol, qg.xGate, qg.SpinRotation]

    #on instantiation
    for pro in pros:
        qPro = pro(system=qub, createUnitary=func)
    assert np.array_equal(qPro.unitary(), unitary)

    #after instantiation
    for pro in pros:
        qPro = pro(system=qub)
        qPro.createUnitary = func
    assert np.array_equal(qPro.unitary(), unitary)

def test_callDefaultUnitaryMethod():
    """
    Test that the proper unitary is returned when .unitary is called for each protocol class

    Note this is not testing open system superoperators
    """

    fQ, fCav, cavDim = round(random.random()*5), round(random.random()*5), random.randint(5, 10)
    qub = qg.Qubit(frequency=fQ)
    sys = qg.Qubit(frequency=fQ) + qg.Cavity(frequency=fCav, dimension=cavDim)

    unitary = np.random.rand(2*cavDim, 2*cavDim)
    func = lambda self, collapseOps, decayRate: unitary

    sim = qg.Simulation()
    freeEvolsys = qg.freeEvolution(system=sys)
    freeEvolqub = qg.freeEvolution(system=qub)
    x = qg.xGate(system=qub, angle=np.pi/2)
    spin = qg.SpinRotation(system=qub, angle=np.pi, rotationAxis='y')
    qProtocol = qg.qProtocol(system=qub, steps=[x, freeEvolqub, spin])
    genProtocol = qg.genericProtocol(system=sys, createUnitary=func)

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
    sim.addProtocol(qProtocol, qub)
    assert np.sum(np.abs(
        qProtocol.unitary()
        - Upauli(np.pi, [0, 1, 0]) @ Upauli(sim.stepSize*qub.frequency, [0, 0, 1]) @ Upauli(np.pi/2, [1, 0, 0])
    )) < 1e-9

    #testing genericProtocol
    sim.addProtocol(genProtocol, sys)
    assert(np.sum(np.abs(genProtocol.unitary()-unitary)) < 1e-9)

def test_accessToObjOnCall():
    """
    Tests whether a custom createUnitary function assigned to a protocol has it's first argument equal as the protocol upon calling .unitary()
    """
    qub = qg.Qubit()
    unitary = np.random.rand(2, 2)
    func = lambda self, collapseOps, decayRate: self.auxDict['unitary']

    qPro = qg.genericProtocol(system=qub, createUnitary=func)
    qPro.auxDict['unitary'] = unitary

    assert(np.sum(np.abs(qPro.unitary()-unitary)) < 1e-9)