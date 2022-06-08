import numpy as np
import quanguru as qg

def test_HermitianConjugateCopyStep():
    spinSys = qg.QuantumSystem(frequency=1, operator=qg.sigmaz, dimension=2)

    freeEvolution = qg.freeEvolution(system=spinSys)
    ry = qg.SpinRotation(system=spinSys, angle=np.pi/2, rotationAxis = 'y')
    ProtocolY = qg.qProtocol(system=spinSys, steps=[ry.hc, freeEvolution, ry])

    spinSys.simulation.addSubSys(spinSys, ProtocolY)
    spinSys.simTotalTime = 1
    spinSys.simStepSize = 1

    assert np.allclose(ProtocolY.unitary().A, (ry.unitary() @ spinSys.unitary() @ qg.hc(ry.unitary()) ).A)
