###################################################### Rabi Model ######################################################
import QuantumToolbox.liouvillian as liou
import numpy as np
import datetime


def digitalRabi(obj,stepSize):
    HamJC = (2 * np.pi *
             (
                ((obj.resonatorFrequency / 2) * obj.HamiltonianCavity) +
                (obj.qubitFreqJC * obj.HamiltonianQubit) +
                (obj.g * obj.couplingJC)
             )
             )
    HamAJC = (2 * np.pi *
              (
                ((obj.resonatorFrequency / 2) * obj.HamiltonianCavity) +
                (obj.qubitFreqAJC * obj.HamiltonianQubit) +
                (obj.g * obj.couplingJC)
              )
              )

    UnitaryJC = liou.Liouvillian(HamJC, timeStep=(stepSize / 2))
    if obj.qubitFreqAJC == obj.qubitFreqJC:
        UnitaryAJC = UnitaryJC @ UnitaryJC
    else:
        UnitaryAJC = liou.Liouvillian(HamAJC, timeStep=stepSize)
    Unitary = UnitaryJC @ obj.sigmaX @ UnitaryAJC @ obj.sigmaX @ UnitaryJC
    return Unitary


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

def digitalRabiF(obj,stepSize):
    HamJC = (2 * np.pi *
             (
                ((obj.offset + (obj.resonatorFrequency / obj.ratio)) * obj.HamiltonianCavity) +
                ((obj.offset + obj.qubitFreqJC) * obj.HamiltonianQubit) +
                ((obj.offset + obj.g) * obj.couplingJC)
             )
             )
    HamAJC = (2 * np.pi *
              (
                ((obj.offset + (obj.resonatorFrequency / obj.ratio)) * obj.HamiltonianCavity) +
                ((obj.offset + obj.qubitFreqAJC) * obj.HamiltonianQubit) +
                ((obj.offset + obj.g) * obj.couplingJC)
              )
              )

    UnitaryJC = liou.Liouvillian(HamJC, timeStep=(stepSize / 2))
    if obj.qubitFreqAJC == obj.qubitFreqJC:
        UnitaryAJC = UnitaryJC @ UnitaryJC
    else:
        UnitaryAJC = liou.Liouvillian(HamAJC, timeStep=stepSize)

    if obj.offset == 0:
        Unitary = UnitaryJC @ obj.sigmaX @ UnitaryAJC @ obj.sigmaX @ UnitaryJC
    else:
        HamJC = (2 * np.pi *
                 (
                         ((obj.offset + (obj.resonatorFrequency / obj.ratio)) * obj.HamiltonianCavity) +
                         ((obj.offset + obj.g) * obj.couplingJC)
                 )
                 )
        half_flip = liou.Liouvillian(HamJC)
        UnitaryFlip = liou.Liouvillian(half_flip,timeStep=(obj.bitflipTime/2))
        Unitary = UnitaryJC @ UnitaryFlip @ obj.sigmaX @ UnitaryFlip @ UnitaryAJC @ UnitaryFlip @ obj.sigmaX @ UnitaryFlip @ UnitaryJC

    return Unitary