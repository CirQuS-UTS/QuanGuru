import QuantumToolbox.liouvillian as liou
import numpy as np
import scipy.linalg as lina
import matplotlib.pyplot as plt
################## Quantum Toolbox ################## 
import QuantumToolbox.operators as oper
################## scipy ################## 
import scipy.sparse as sp

def Rabi(dims):
    resonatorDimension = dims
    g = 1
    qubitFreq = 0
    gg = g
    qf = 1
    HamiltonianCavity = sp.kron(oper.number(resonatorDimension), oper.identity(2), format='csc')
    HamiltonianQubit = sp.kron(oper.identity(resonatorDimension), oper.number(2), format='csc')
    couplingJC = (sp.kron(oper.create(resonatorDimension), oper.sigmax(), format='csc')
                  + sp.kron(oper.destroy(resonatorDimension), oper.sigmax(), format='csc'))

    rescale = 1 / (resonatorDimension * gg * qf * 2)
    Num = int(1.5 * resonatorDimension)

    Ham = (rescale * (HamiltonianCavity + (qubitFreq * HamiltonianQubit) + (g * couplingJC))).tocsc()
    Unitary = (liou.Liouvillian(Ham)).toarray()
    fromUnitary = lina.eig(Unitary, right=False)
    fromHamiltonian = np.real(lina.eig(Ham.toarray(), right=False))

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

    analytic = []
    for n in range(resonatorDimension):
        en1 = rescale * (n - (g ** 2))
        analytic.append(en1)
        analytic.append(en1)

    fromHamiltonian.sort()
    analytic.sort()
    unitaryEigens.sort()
    return [fromHamiltonian,unitaryEigens,analytic]
"""print(Num)

    plt.plot(numbers[0:Num], unitaryEigens[0:Num], 'b.', markersize=8, label='From Unitary')
    plt.plot(numbers[0:Num], fromHamiltonian[0:Num], 'g.', markersize=6, label='From Hamiltonian')
    plt.plot(numbers[0:Num], analytic[0:Num], 'r.', markersize=4, label='Analytical')
    plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n}$', fontsize=14)
    plt.title('Rabi Hamiltonian', fontsize=16)
    plt.show()

    unitaryDif = [0]
    hamDif = [0]
    anDif = [0]
    print(len(unitaryEigens))
    for i in range(len(unitaryEigens) - 1):
        unitaryDif.append(unitaryEigens[i + 1] - unitaryEigens[i])
        hamDif.append(fromHamiltonian[i + 1] - fromHamiltonian[i])
        anDif.append(analytic[i + 1] - analytic[i])

    plt.plot(numbers[0:Num], unitaryDif[0:Num], 'b.', markersize=8, label='From Unitary')
    plt.plot(numbers[0:Num], hamDif[0:Num], 'g.', markersize=6, label='From Hamiltonian')
    plt.plot(numbers[0:Num], anDif[0:Num], 'r.', markersize=4, label='Analytical')
    plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n+1} - E_{n}$', fontsize=14)
    plt.title('Rabi Hamiltonian', fontsize=16)
    plt.show()

    fig, axs = plt.subplots()
    axs.hist(hamDif[0:Num], bins=100)
    fig2, axs2 = plt.subplots()
    axs2.hist(unitaryDif[0:Num], bins=100)
    fig3, axs3 = plt.subplots()
    axs3.hist(anDif, bins=100)
    plt.show()"""