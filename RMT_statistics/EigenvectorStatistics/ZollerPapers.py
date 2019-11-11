import QuantumToolbox.operators as qOps
import scipy.linalg as lina
import numpy as np
import QuantumToolbox.liouvillian as liou
import QuantumToolbox.states as states
import RMT_statistics.Modules.Distributions as RMTdist
import Plotting.plottingSettings as pltSet
import matplotlib.pyplot as plt

p = 0.1
j = 4
la = 1

tau = 20

jz = qOps.Jz(j)
jx = qOps.Jx(j)
jzs = jz@jz

h_o = tau*p*jx
v_o = tau*(la/(((2*j) + 1)))*(jzs)

U_ho = liou.Liouvillian(h_o)
U_o = liou.Liouvillian(v_o)@U_ho

vecso = lina.eig(U_o.toarray())[1]
basiso = states.genericBasisBra(int(((2*j) + 1)),sparse=True)

compso = []
for i in range(len(vecso)):
    for k in range(int(len(basiso))):
        overlap1 = (basiso[k]@(vecso[i]))[0]
        p1 = np.real(np.conjugate(overlap1)*overlap1)
        compso.append(p1)
fig = plt.figure()
ax = plt.subplot2grid((1, 1), (0, 0), colspan=1)
pltSet.plottingSet(ax)
plt.hist(compso, bins=int(1.5*j), density=True)
x = np.arange(0.00001, 0.5, 0.0001)
COE = [RMTdist.EigenVectorDist(X, int(2*j), 1) for X in x]
CUE = [RMTdist.EigenVectorDist(X, int(2*j), 2) for X in x]
CSE = [RMTdist.EigenVectorDist(X, int(2*j), 4) for X in x]
plt.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
plt.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
plt.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
ax.set_ylim([0, 2*j])
#ax.set_xlim([0, 0.02])
ax.set_yticks([0.0, j, 2*j])
#ax.set_xticks([0.0,0.01,0.02])
#fig.text(0.5, 0.01, r'$|c_n|^2$', ha='center', fontsize=17)
pltSet.plottingSet(ax)
#fig.text(0.005, 0.5, r'Prob($|c_n|^2$)', va='center', rotation='vertical', fontsize=17)
plt.legend()
plt.show()


eigenvecs = {}
eigenvecs['Orthogonal'] = compso
#saveData(eigenvecs)