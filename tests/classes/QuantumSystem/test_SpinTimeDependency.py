import pytest
from quanguru.classes.QSystem import Spin, Qubit

def test_spinObjectTimeDependency():
    qub = Spin(frequency=1)

    def driveAmplitude(t, A, tr, tf): 
        return A if tr <= t < tr + tf else 0.0

    def qubFrequencyTimeDependency(qsys, ti):
        qsys.frequency = 1 + driveAmplitude(ti, 5, 2, 5) 
    qub.timeDependency = qubFrequencyTimeDependency

    assert qub.frequency == 1

    qub.timeDependency(qub, 3)
    assert qub.frequency == 6

    qub.timeDependency(qub, 8)
    assert qub.frequency == 1

def test_qubitObjectTimeDependency():
    qub = Qubit(frequency=1)

    def driveAmplitude(t, A, tr, tf): 
        return A if tr <= t < tr + tf else 0.0

    def qubFrequencyTimeDependency(qsys, ti):
        qsys.frequency = 1 + driveAmplitude(ti, 5, 2, 5) 
    qub.timeDependency = qubFrequencyTimeDependency

    assert qub.frequency == 1

    qub.timeDependency(qub, 3)
    assert qub.frequency == 6

    qub.timeDependency(qub, 8)
    assert qub.frequency == 1

def test_qubitObjectTimeDependencyWithSim():
    qub = Qubit(frequency=1)
    qub.initialState = 0
    qub.simTotalTime = 5
    qub.simStepSize = 1

    def driveAmplitude(t, A, tr, tf): 
        return A if tr <= t < tr + tf else 0.0

    def qubFrequencyTimeDependency(qsys, ti):
        qsys.frequency = 1 + driveAmplitude(ti, 5, 2, 2) 
    qub.timeDependency = qubFrequencyTimeDependency

    assert qub.frequency == 1
    qubitFreqList = []
    def compute(qsys, args):
        qubitFreqList.append(qsys.frequency)

    qub.compute = compute

    qub.run()

    assert qubitFreqList == [1, 1, 6, 6, 1, 1]


test_spinObjectTimeDependency()
test_qubitObjectTimeDependency()
test_qubitObjectTimeDependencyWithSim()