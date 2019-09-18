import QuantumToolbox.liouvillian as liou
import numpy as np
import scipy.linalg as lina
import matplotlib.pyplot as plt
################## Quantum Toolbox ################## 
import QuantumToolbox.operators as oper
################## scipy ################## 
import scipy.sparse as sp

def DRabi(dims):
    resonatorDimension = dims
    resonatorFrequency = 1
    StepSize = 1
    g = 1
    qubitFreq = 0
    gg = g
    qf = 1

    HamiltonianCavity = sp.kron(oper.number(resonatorDimension), oper.identity(2), format='csc')
    HamiltonianQubit = sp.kron(oper.identity(resonatorDimension), oper.sigmaz(), format='csc')
    couplingJC = (sp.kron(oper.create(resonatorDimension), oper.destroy(2), format='csc')
                  + sp.kron(oper.destroy(resonatorDimension), oper.create(2), format='csc'))
    sigmaX = sp.kron(oper.identity(resonatorDimension), oper.sigmax(), format='csc')

    rescale = 1 / (resonatorDimension * gg * qf)
    Num = int(1.5 * resonatorDimension)

    HamJC = rescale * ((0.5 * HamiltonianCavity) + (g * couplingJC)).tocsc()
    HamAJC = rescale * ((0.5 * HamiltonianCavity) + (g * couplingJC)).tocsc()
    UnitaryJC = liou.Liouvillian(HamJC, timeStep=(StepSize / 2))
    UnitaryAJC = (UnitaryJC @ UnitaryJC)
    Unitary = (UnitaryJC @ sigmaX @ UnitaryAJC @ sigmaX @ UnitaryJC).toarray()
    fromUnitary = lina.eig(Unitary, right=False)

    unitaryEigens = []
    numbers = []

    for i in range(len(fromUnitary)):
        c = fromUnitary[i].real
        s = fromUnitary[i].imag
        if (s > np.pi / 2) or (s < -np.pi):
            print('here')
            break
        unitaryEigens.append(np.arcsin(-s))
        numbers.append(i)

    unitaryEigens.sort()
    return unitaryEigens

"""plt.plot(numbers[0:Num], unitaryEigens[0:Num], 'b.', markersize=8, label='From Unitary')
    plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n}$', fontsize=14)
    plt.title('Floquet Hamiltonian', fontsize=16)
    plt.show()

    unitaryDif = []
    for i in range(len(unitaryEigens) - 1):
        unitaryDif.append(unitaryEigens[i + 1] - unitaryEigens[i])

    plt.plot(numbers[0:Num], unitaryDif[0:Num], 'b.', markersize=8, label='From Unitary')
    plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n+1} - E_{n}$', fontsize=14)
    plt.title('Floquet Hamiltonian', fontsize=16)
    plt.show()

    fig2, axs2 = plt.subplots()
    axs2.hist(unitaryDif[1000:Num], bins=100)
    plt.show()"""