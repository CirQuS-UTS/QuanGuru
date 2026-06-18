import random as rnd
import quanguru as qg

def test_canCreateTotalHamiltonianWithQuantumSystem():
    qsys = qg.QuantumSystem(dimension=rnd.randint(2, 10), frequency=rnd.random(), operator=qg.number)
    assert qsys._firstTerm._canCreateTotalHamiltonian()

    qsys = qg.QuantumSystem(frequency=rnd.random(), operator=qg.number)
    assert not qsys._firstTerm._canCreateTotalHamiltonian()

    qsys = qg.QuantumSystem(dimension=rnd.randint(2, 10), operator=qg.number)
    assert not qsys._firstTerm._canCreateTotalHamiltonian()

    qsys = qg.QuantumSystem(dimension=rnd.randint(2, 10), frequency=rnd.random())
    assert not qsys._firstTerm._canCreateTotalHamiltonian()
