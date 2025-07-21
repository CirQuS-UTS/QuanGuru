import quanguru as qg
import random
from quanguru.QuantumToolbox.IPR import iprMatrix

def test_iprMatrix():
    qub = qg.Qubit(frequency=round(random.random(), 2))
    qub.simulation.totalTime = 1
    qub.simulation.stepSize = 1
    hamiltonian = qub.totalHamiltonian.toarray()
    unitary = qub._freeEvol._defGetUnitary().toarray()
    assert round(iprMatrix(hamiltonian, hamiltonian),7) == round(1/qub.dimension,7)
    assert round(iprMatrix(unitary, unitary),7) == round(1/qub.dimension,7)
    assert round(iprMatrix(qg.sigmaz(), qg.sigmax()),7) == round(1,7)