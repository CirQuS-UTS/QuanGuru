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
    UnitaryAJC = UnitaryJC @ UnitaryJC
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