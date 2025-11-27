import pytest
from quanguru.classes.QSystem import *
from quanguru.QuantumToolbox.operators import sigmaz, sigmax, tensorProd, identity, number
from numpy import allclose


def test_quantumSystemObjectTimeDependencyExecution():
    """
    Test that QuantumSystem._timeDependency() and QuantumSystem.timeDependency() run the user defined function assigned QuantumSystem.timeDependency
    """
    qub = QuantumSystem(operator=sigmax, frequency=1, dimension=2)

    def driveAmplitude(t, A, tr): 
        return A if tr <= t else 0.0

    def qubFrequencyTimeDependency(qsys, ti):
        qsys.frequency = 1 + driveAmplitude(ti, 5, 2) 
    qub.timeDependency = qubFrequencyTimeDependency

    #QuantumSystem.timeDependency
    qub._timeDependency(time=0)
    assert qub.frequency == 1

    qub.timeDependency(qub, 3)
    assert qub.frequency == 6

    #QuantumSystem._timeDependency
    qub._timeDependency(time=0)
    assert qub.frequency == 1

    qub._timeDependency(time=3)
    assert qub.frequency == 6

def test_systemWithTermTimeDependencyExecution():
    """
    Test the execution of the user defined time dependency function for a QuantumSystem with a QTerm
    """
    qub = QuantumSystem(operator=sigmaz, frequency=1, dimension=2)
    term = qub.createTerm(
        operator=sigmax,
        frequency=2,
    )

    def qub_td(qsys, ti):
        qsys.frequency = 5 if ti > 3 else 0

    qub.timeDependency = qub_td

    def term_td(term, ti):
        term.frequency = 3 if ti < 3 else 0

    term.timeDependency = term_td

    qub._timeDependency(time=0)
    assert allclose(qub.totalHamiltonian.toarray(), 3*sigmax().toarray())

    qub._timeDependency(time=4)
    assert allclose(qub.totalHamiltonian.toarray(), 5*sigmaz().toarray())

def test_subSysTimeDependencyExecution():
    """
    Test the execution of the user defined time dependency function for a QuantumSystem in a subSys
    """
    qub = Qubit(frequency=1)
    cav = Cavity(frequency=6, dimension=5)

    totalSys = qub + cav

    def qub_td(qsys, ti):
        qsys.frequency = 5 if ti > 3 else 0

    qub.timeDependency = qub_td

    def cav_td(term, ti):
        term.frequency = 3 if ti < 3 else 0

    cav.timeDependency = cav_td

    totalSys._timeDependency(time=0)
    assert allclose(
        totalSys.totalHamiltonian.toarray(), 
        tensorProd(identity(2), number(5)*3).toarray()
    )

    totalSys._timeDependency(time=4)
    assert allclose(
        totalSys.totalHamiltonian.toarray(), 
        tensorProd(sigmaz()*5/2, identity(5)).toarray()
    )

def test_qubitObjectTimeDependencyWithSim():
    """
    Test the execution of the user defined time dependency function for a Qubit object during a simulation
    """
    qub = Qubit(frequency=1)
    qub.initialState = 0
    qub.simTotalTime = 5
    qub.simStepSize = 1

    def driveAmplitude(t, A, tr, tf): 
        # return A if tr <= t < tr + tf else 0.0
        return A*t**2

    def qubFrequencyTimeDependency(qsys, ti):
        qsys.frequency = 1 + driveAmplitude(ti, 5, 2, 2) 
    qub.timeDependency = qubFrequencyTimeDependency

    assert qub.frequency == 1

    qubitFreqList = []
    def compute(qsys, args):
        qubitFreqList.append(qsys.frequency)
    qub.compute = compute

    qub.run()

    assert qubitFreqList == [1, 1, 6, 21, 46, 81]