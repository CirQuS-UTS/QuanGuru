# Rabi Model #
import QuantumToolbox.liouvillian as liou
import numpy as np
# import datetime

def idealRabi(obj, stepSize):
    HamRabi = 2 * np.pi * (obj.systemParameters.resonatorFrequency * obj.HamiltonianCavity + obj.systemParameters.qubitFreq * obj.HamiltonianQubit
                           + obj.systemParameters.g * obj.couplingHamiltonian)
    Unitary = liou.Liouvillian(HamRabi, timeStep=stepSize)
    return Unitary


def digitalRabi(obj, stepSize):
    HamJC = 2 * np.pi * (((obj.systemParameters.offset + obj.systemParameters.resonatorFrequency/obj.systemParameters.ratio) * obj.HamiltonianCavity) +
                         ((obj.systemParameters.offset + obj.systemParameters.qubitFreqJC) * obj.HamiltonianQubit) + (obj.systemParameters.g * obj.couplingJC))
    UnitaryJC = liou.Liouvillian(HamJC, timeStep=(stepSize / 2))

    if obj.systemParameters.qubitFreqAJC == obj.systemParameters.qubitFreqJC:
        UnitaryAJC = (UnitaryJC @ UnitaryJC)
    else:
        HamAJC = 2 * np.pi * ((obj.systemParameters.offset + obj.systemParameters.resonatorFrequency / obj.systemParameters.ratio) * obj.HamiltonianCavity
                              + (obj.systemParameters.offset + obj.systemParameters.qubitFreqAJC) * obj.HamiltonianQubit + obj.systemParameters.g * obj.couplingJC)
        UnitaryAJC = liou.Liouvillian(HamAJC, timeStep=stepSize)

    if obj.systemParameters.offset == 0:
        Unitary = UnitaryJC @ obj.sigmaX @ UnitaryAJC @ obj.sigmaX @ UnitaryJC
    else:
        half_flip = 2 * np.pi * ((obj.systemParameters.offset + obj.systemParameters.resonatorFrequency / obj.ratio) * obj.HamiltonianCavity +
                                 obj.systemParameters.g * obj.couplingJC)
        UnitaryFlip = liou.Liouvillian(half_flip, timeStep=(obj.bitflipTime/2))
        Unitary = UnitaryJC @ UnitaryFlip @ obj.sigmaX @ UnitaryFlip @ UnitaryAJC @ UnitaryFlip @ obj.sigmaX @ UnitaryFlip @ UnitaryJC

    return Unitary
