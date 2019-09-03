###################################################### Rabi Model ######################################################
import QuantumToolbox.liouvillian as liou
import numpy as np
import datetime


def idealRabi(obj,stepSize):
    HamRabi = (2 * np.pi *
               (
                (obj.resonatorFrequency * obj.HamiltonianCavity)
                + (obj.qubitFreqJC * obj.HamiltonianQubit)
                + (obj.g * obj.couplingHamiltonian)
               )
               )


    Unitary = liou.Liouvillian(HamRabi, timeStep=stepSize)
    return Unitary

def digitalRabi(obj,stepSize):
    HamJC = (2 * np.pi *
             (
                ((obj.offset + (obj.resonatorFrequency / obj.ratio)) * obj.HamiltonianCavity) +
                ((obj.offset + obj.qubitFreqJC) * obj.HamiltonianQubit) +
                (obj.g * obj.couplingJC)
             )
             )

    UnitaryJC = liou.Liouvillian(HamJC, timeStep=(stepSize / 2))
    if obj.qubitFreqAJC == obj.qubitFreqJC:
        UnitaryAJC = UnitaryJC @ UnitaryJC
    else:
        HamAJC = (2 * np.pi *
                  (
                          ((obj.offset + (obj.resonatorFrequency / obj.ratio)) * obj.HamiltonianCavity) +
                          ((obj.offset + obj.qubitFreqAJC) * obj.HamiltonianQubit) +
                          (obj.g * obj.couplingJC)
                  )
                  )
        UnitaryAJC = liou.Liouvillian(HamAJC, timeStep=stepSize)

    if obj.offset == 0:
        Unitary = UnitaryJC @ obj.sigmaX @ UnitaryAJC @ obj.sigmaX @ UnitaryJC
    else:
        half_flip = (2 * np.pi *
                 (
                         ((obj.offset + (obj.resonatorFrequency / obj.ratio)) * obj.HamiltonianCavity) +
                         (obj.g * obj.couplingJC)
                 )
                 )
        UnitaryFlip = liou.Liouvillian(half_flip,timeStep=(obj.bitflipTime/2))
        Unitary = UnitaryJC @ UnitaryFlip @ obj.sigmaX @ UnitaryFlip @ UnitaryAJC @ UnitaryFlip @ obj.sigmaX @ UnitaryFlip @ UnitaryJC

    return Unitary