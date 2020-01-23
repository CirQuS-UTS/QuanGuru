import QuantumToolbox.operators as qOps
import scipy.linalg as lina
import numpy as np
import QuantumToolbox.liouvillian as liou
import QuantumToolbox.states as states
import RMT_statistics.Modules.Distributions as RMTdist
import Plotting.plottingSettings as pltSet
import matplotlib.pyplot as plt

p = 1.7
j = 100
la = 6

jz = qOps.Jz(j)
jy = qOps.Jy(j)
jzs = jz@jz

h_o = p*jy
v_o = (la/(2*j))*(jzs)
v_op = ((la+(la/10))/(2*j))*(jzs)

U_ho = liou.Liouvillian(h_o)
U_o = liou.Liouvillian(v_o)@U_ho
U_op = liou.Liouvillian(v_op)@U_ho

vecso = lina.eig(U_o.toarray())[1]
#basiso = lina.eig(U_op.toarray())[1]
basiso = states.genericBasis(int((2*j + 1)))
print(basiso[0])

compso = []
for i in range(len(vecso)):
    bra = np.transpose(np.conjugate(vecso[i]))
    print(i)
    for k in range(int(len(basiso))):
        overlap1 = (bra@(basiso[k]))
        p1 = np.real(np.conjugate(overlap1)*overlap1)
        compso.append(p1)
fig = plt.figure()
ax = plt.subplot2grid((1, 1), (0, 0), colspan=1)
pltSet.plottingSet(ax)
plt.hist(compso, bins=50, density=True)
x = np.arange(0.00001, 0.05, 0.00001)
COE = [RMTdist.EigenVectorDist(X, int(2*j) + 1, 1) for X in x]
CUE = [RMTdist.EigenVectorDist(X, int(2*j) + 1, 2) for X in x]
CSE = [RMTdist.EigenVectorDist(X, int(2*j) + 1, 4) for X in x]
plt.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
plt.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
plt.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
ax.set_ylim([0, 2*j])
ax.set_xlim([0, 0.02])
ax.set_yticks([0.0, j, 2*j])
ax.set_xticks([0.0,0.01,0.02])
#fig.text(0.5, 0.01, r'$|c_n|^2$', ha='center', fontsize=17)
pltSet.plottingSet(ax)
#fig.text(0.005, 0.5, r'Prob($|c_n|^2$)', va='center', rotation='vertical', fontsize=17)
plt.legend()
plt.show()


p1 = 2.5
j1 = 49.5
k = 2.5
kp = 2
kpp = 3

jz_1 = qOps.Jz(j1)
jy_1 = qOps.Jy(j1)
jx_1 = qOps.Jx(j1)
jzs_1 = jz_1@jz_1
h_s = (p1/j1)*jzs_1
v_s = (k/j1)*(jzs_1 + kp*(jx_1@jz_1 + jz_1@jx_1) + kpp*(jx_1@jy_1 + jy_1@jx_1))
v_sp = ((k+(k/10))/j1)*(jzs_1 + kp*(jx_1@jz_1 + jz_1@jx_1) + kpp*(jx_1@jy_1 + jy_1@jx_1))

U_hs = liou.Liouvillian(h_s)
U_s = liou.Liouvillian(v_s)@U_hs
U_sp = liou.Liouvillian(v_sp)@U_hs

vecss = lina.eig(U_s.toarray())[1]
basiss = lina.eig(U_sp.toarray())[1]
#basiss = states.genericBasis(int((2*j1)),sparse=False)

compss = []
for i in range(len(vecss)):
    bra = np.transpose(np.conjugate(vecss[i]))
    el = 0
    for k in range(int(len(basiss)/2)-2):
        el += 2
        overlap1 = bra@(basiss[k])
        p1 = np.real(np.conjugate(overlap1)*overlap1)
        overlap2 = bra @ (basiss[el+1])
        p2 = np.real(np.conjugate(overlap2) * overlap2)
        compss.append(p1+p2)
fig = plt.figure()
ax = plt.subplot2grid((1, 1), (0, 0), colspan=1)
pltSet.plottingSet(ax)
plt.hist(compss, bins=50, density=True)
x = np.arange(0.00001, 0.05, 0.00001)
COE = [RMTdist.EigenVectorDist(X, int(2*j1), 1) for X in x]
CUE = [RMTdist.EigenVectorDist(X, int(2*j1), 2) for X in x]
CSE = [RMTdist.EigenVectorDist(X, int(2*j1), 4) for X in x]
plt.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
plt.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
plt.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
ax.set_ylim([0, j1 + 0.5])
ax.set_xlim([0, 0.02])
ax.set_yticks([0.0, int((j1 + 0.5)/2), j1 + 0.5])
ax.set_xticks([0.0,0.02,0.04])
#fig.text(0.5, 0.01, r'$|c_n|^2$', ha='center', fontsize=17)
pltSet.plottingSet(ax)
#fig.text(0.005, 0.5, r'Prob($|c_n|^2$)', va='center', rotation='vertical', fontsize=17)
plt.legend()
plt.show()


pu = 1.7
ju = 100
ku = 6
kpu = 0.5

jzu = qOps.Jz(ju)
jxu = qOps.Jx(ju)
jyu = qOps.Jy(ju)
jzsu = jzu@jzu
jxsu = jxu@jxu

h_u = pu*jy
v_u1 = (ku/(2*j))*(jzsu)
v_u2 = (kpu/(2*j))*(jxsu)
v_u2p = ((kpu+(kpu/10))/(2*j))*(jxsu)

U_hu = liou.Liouvillian(h_u)
U_u1 = liou.Liouvillian(v_u1)@U_hu
U_u = liou.Liouvillian(v_u2)@U_u1
U_up = liou.Liouvillian(v_u2p)@U_u1

vecsu = lina.eig(U_u.toarray())[1]
basisu = lina.eig(U_up.toarray())[1]
#basisu = states.genericBasis(int((2*ju)),sparse=False)

compsu = []
for i in range(len(vecsu)):
    bra = np.transpose(np.conjugate(vecsu[i]))
    for k in range(int(len(basisu))):
        overlap1 = bra@(basisu[k])
        p1 = np.real(np.conjugate(overlap1)*overlap1)
        compsu.append(p1)


x = np.arange(0.00001, 0.05, 0.00001)
fig = plt.figure()
ax = plt.subplot2grid((1, 1), (0, 0), colspan=1)
plt.hist(compsu, bins=50, density=True)
COE = [RMTdist.EigenVectorDist(X, int(2*ju), 1) for X in x]
CUE = [RMTdist.EigenVectorDist(X, int(2*ju), 2) for X in x]
CSE = [RMTdist.EigenVectorDist(X, int(2*ju), 4) for X in x]
plt.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
plt.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
plt.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
ax.set_ylim([0, 2*ju])
ax.set_xlim([0, 0.02])
ax.set_yticks([0.0, ju, 2*ju])
ax.set_xticks([0.0,0.01,0.02])
#fig.text(0.5, 0.01, r'$|c_n|^2$', ha='center', fontsize=17)
pltSet.plottingSet(ax)
#fig.text(0.005, 0.5, r'Prob($|c_n|^2$)', va='center', rotation='vertical', fontsize=17)
plt.legend()
plt.show()



eigenvecs = {}
eigenvecs['Orthogonal'] = compso
eigenvecs['Unitary'] = compsu
eigenvecs['Symplectic'] = compss
#saveData(eigenvecs)