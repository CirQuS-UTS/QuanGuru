import QuantumToolbox.operators as qOps
import scipy.linalg as lina
import numpy as np
import QuantumToolbox.liouvillian as liou
import QuantumToolbox.states as states
import RMT_statistics.Modules.Distributions as RMTdist
import Plotting.plottingSettings as pltSet
import matplotlib.pyplot as plt
import copy
import QuantumToolbox.functions as fncs
import SaveRead.saveH5 as sh5

jlist = np.arange(0.5,10.5,0.5)

for asdas in jlist:
    print(asdas)
    p = 0.1
    j = asdas
    la = 1

    tau = 10

    jz = qOps.Jz(j)
    jx = qOps.Jx(j)
    jzs = jz @ jz

    h_o = p * jx
    v_o = (la / (((2 * j) + 1))) * (jzs)

    U_ho = liou.Liouvillian(tau * h_o)
    U_o = liou.Liouvillian(tau * v_o) @ U_ho

    vecso = lina.eig(U_o.toarray())[1]
    basiso = states.genericBasisBra(int(((2 * j) + 1)), sparse=True)

    compso = []
    for i in range(len(vecso)):
        for k in range(int(len(basiso))):
            overlap1 = (basiso[k] @ (vecso[i]))[0]
            p1 = np.real(np.conjugate(overlap1) * overlap1)
            compso.append(p1)

    initialState = states.basis(int(2 * j + 1), 0)
    lecho = []
    times = np.arange(0.0, 1200 + tau, tau)
    state = copy.deepcopy(initialState)
    state1 = copy.deepcopy(initialState)
    for aswds in range(len(times)):
        lec0 = fncs.fidelityKet(initialState, state)
        state = U_o @ state
        # state1 = U_op @ state1
        lecho.append(lec0)

    print(np.mean(lecho))

    # listEx = [np.e**(-2.5*(((pp-p)*tau)**2)*t) for t in times]

    plt.plot(times, lecho)
    # plt.plot(times,listEx)
    plt.show()

    fig = plt.figure()
    ax = plt.subplot2grid((1, 1), (0, 0), colspan=1)
    pltSet.plottingSet(ax)
    plt.hist(compso, density=True)
    x = np.arange(0.00001, 0.5, 0.0001)
    COE = [RMTdist.EigenVectorDist(X, int(2 * j), 1) for X in x]
    CUE = [RMTdist.EigenVectorDist(X, int(2 * j), 2) for X in x]
    CSE = [RMTdist.EigenVectorDist(X, int(2 * j), 4) for X in x]
    plt.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
    plt.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
    plt.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
    ax.set_ylim([0, 2 * j])
    ax.set_xlim([0, 0.4])
    ax.set_yticks([0.0, j, 2 * j])
    ax.set_xticks([0.0, 0.2, 0.4])
    # fig.text(0.5, 0.01, r'$|c_n|^2$', ha='center', fontsize=17)
    pltSet.plottingSet(ax)
    # fig.text(0.005, 0.5, r'Prob($|c_n|^2$)', va='center', rotation='vertical', fontsize=17)
    plt.legend()
    plt.show()

    eigenvecs = {}
    eigenvecs[str(asdas)] = compso

sh5.saveData(eigenvecs)