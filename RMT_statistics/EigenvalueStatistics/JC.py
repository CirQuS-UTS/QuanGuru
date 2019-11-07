import QuantumToolbox.liouvillian as liou
import scipy.linalg as lina
################## Quantum Toolbox ################## 
import QuantumToolbox.operators as oper
################## scipy ################## 
import scipy.sparse as sp
import numpy as np
import matplotlib.pyplot as plt

def JC(dims):
    resonatorDimension = dims
    g = 1
    qubitFreq = 0
    gg = 1
    qf = 1
    HamiltonianCavity = sp.kron(oper.number(resonatorDimension), oper.identity(2), format='csc')
    HamiltonianQubit = sp.kron(oper.identity(resonatorDimension), oper.sigmaz(), format='csc')
    couplingJC = (sp.kron(oper.create(resonatorDimension), oper.destroy(2), format='csc') +
                  sp.kron(oper.destroy(resonatorDimension),oper.create(2), format='csc'))
    rescale = 1 / (resonatorDimension * gg * qf)
    Num = int(1.75 * resonatorDimension)

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

    analytic = [0]
    for n in range(resonatorDimension):
        en1 = rescale * (n + 0.5 + 0.5 * np.sqrt(1 + 4 * (g ** 2) * (n + 1)))
        en2 = rescale * (n + 0.5 - 0.5 * np.sqrt(1 + 4 * ((g ** 2) * (n + 1))))
        analytic.append(en2)
        analytic.append(en1)

    fromHamiltonian.sort()
    analytic.sort()
    unitaryEigens.sort()
    return [fromHamiltonian,unitaryEigens,analytic]
"""print(Num)

    plt.plot(numbers, unitaryEigens, 'b.', markersize=8, label='From Unitary')
    plt.plot(numbers, fromHamiltonian, 'g.', markersize=6, label='From Hamiltonian')
    plt.plot(numbers, analytic[0:len(analytic) - 1], 'r.', markersize=4, label='Analytical')
    plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n}$', fontsize=14)
    plt.title('Jaynes-Cummings Hamiltonian', fontsize=16)
    plt.show()

    unitaryDif = []
    hamDif = []
    anDif = []
    nums = []
    for i in range(len(unitaryEigens) - 1):
        unitaryDif.append(unitaryEigens[i + 1] - unitaryEigens[i])
        hamDif.append(fromHamiltonian[i + 1] - fromHamiltonian[i])
        anDif.append(analytic[i + 1] - analytic[i])
        nums.append(i)

    plt.plot(nums, unitaryDif, 'b.', markersize=8, label='From Unitary')
    plt.plot(nums, hamDif, 'g.', markersize=6, label='From Hamiltonian')
    plt.plot(nums, anDif, 'r.', markersize=4, label='Analytical')
    plt.legend()
    plt.xlabel(r'$n_{th}$ level', fontsize=14)
    plt.ylabel(r'$E_{n+1} - E_{n}$', fontsize=14)
    plt.title('Jaynes-Cummings Hamiltonian', fontsize=16)
    plt.show()

    fig, axs = plt.subplots()
    axs.hist(hamDif, bins=100)
    fig2, axs2 = plt.subplots()
    axs2.hist(unitaryDif, bins=100)
    fig3, axs3 = plt.subplots()
    axs3.hist(anDif, bins=100)
    plt.show()"""