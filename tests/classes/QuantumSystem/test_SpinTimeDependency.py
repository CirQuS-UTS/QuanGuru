import pytest
from quanguru.classes.QSystem import *
from quanguru.QuantumToolbox.operators import sigmax


def test_quantumSystemObjectTimeDependency():
    qub = QuantumSystem(operator=sigmax, frequency=1, dimension=2)

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


def test_compositeSystemObjectTimeDependencyWithSim():
    qub = Qubit(frequency=1)
    cav = Cavity(frequency=2, dimension=5)
    totalSys = qub + cav

    totalSys.initialState = [0, 1]
    totalSys.simTotalTime = 8
    totalSys.simStepSize = 1

    def driveCavFreq(t, A, tr, tf): 
        return A if tr <= t < tr + tf else 0.0

    def cavFrequencyTimeDependency(qsys, ti):
        qsys.frequency = 2 + driveCavFreq(ti, 4, 2, 3) 
    totalSys.getByNameOrAlias(cav).timeDependency = cavFrequencyTimeDependency

    assert cav.frequency == 2

    cavFreqList = []
    def compute(qsys, args):
        cavFreqList.append(qsys.getByNameOrAlias(cav).frequency)
    totalSys.compute = compute

    totalSys.run()

    assert cavFreqList == [2, 2, 6, 6, 6, 2, 2, 2, 2]
