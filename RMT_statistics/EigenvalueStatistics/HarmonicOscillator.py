################## Quantum Toolbox ################## 
import QuantumToolbox.operators as oper
from QuantumToolbox.liouvillian import Liouvillian
################## scipy ################## 
import scipy.sparse as sp
import scipy.linalg as lina
import numpy as np
import matplotlib.pyplot as plt
################# Hamiltonian & Initial State #################

def HO(dim):
    resonatorDimension = dim
    rescale = 1 / resonatorDimension

    HamiltonianCavity = rescale * oper.number(resonatorDimension)
    Unitary = Liouvillian(HamiltonianCavity)

    unitaryEig = lina.eig(Unitary.toarray(), right=False)
    hamEigens = np.real(lina.eig(HamiltonianCavity.toarray(), right=False))
    numbers = []
    unitaryEigens = []
    for i in range(len(unitaryEig)):
        c = unitaryEig[i].real
        s = unitaryEig[i].imag
        if (s > np.pi / 2) or (s < -np.pi):
            print('here')
            break
        unitaryEigens.append(np.arcsin(-s))
        numbers.append(i)

    """hamEigens.sort()
    unitaryEigens.sort()"""
    #plt.plot(numbers, unitaryEigens, 'b.', markersize=8, label='From Unitary')
    """plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n}$', fontsize=14)
    plt.title('Harmonic Oscillator', fontsize=16)
    plt.show()"""
    """plt.plot(numbers, hamEigens, 'r.', markersize=5, label='From Hamiltonian')
    plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n}$', fontsize=14)
    plt.title('Harmonic Oscillator', fontsize=16)
    plt.show()"""
    return [hamEigens, unitaryEigens]


