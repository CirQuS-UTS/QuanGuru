from QuantumToolbox.operators import Jz, Jy, Jx
import scipy.linalg as lina
import numpy as np
from QuantumToolbox.liouvillian import Liouvillian
from QuantumToolbox.states import genericBasis
from RMT_statistics.Modules.Distributions import EigenVectorDist

p = 1.7
j = 100
la = 6

jz = Jz(j)
jy = Jy(j)
jzs = jz@jz


h_0 = p*jy
V_1 = (la/(2*j))*(jzs)
V_1p = ((la+0.1)/(2*j))*(jzs)

p1 = 2.5
j1 = 49.5
k = 2.5
kp = 2
kpp = 3

jz_1 = Jz(j1)
jy_1 = Jy(j1)
jx_1 = Jx(j1)
jzs_1 = jz_1@jz_1
H_0 = (p1/j1)*jzs_1
v_1 = (k/j1)*(jzs_1 + kp*(jx_1@jz_1 + jz_1@jx_1) + kpp*(jx_1@jy_1 + jy_1@jx_1))

U_0 = Liouvillian(H_0)
U_1 = Liouvillian(v_1)@U_0
#U_2 = Liouvillian(V_1p)@U_0
basisdim = j1
vecs1 = lina.eig(U_1.toarray())[1]
basis1 = genericBasis(int((2*basisdim)),sparse=False)
#basis2 = lina.eig(U_2.toarray())[1]
basis = basis1

comps = []
for i in range(len(vecs1)):
    bra = np.transpose(np.conjugate(vecs1[i]))
    el = 0
    for k in range(int(len(basis)/2)-1):
        el += 2
        overlap1 = bra@(basis[el])
        p1 = np.real(np.conjugate(overlap1)*overlap1)[0]
        overlap2 = bra @ (basis[el+1])
        p2 = np.real(np.conjugate(overlap2) * overlap2)[0]
        comps.append(p1+p2)

import matplotlib.pyplot as plt
print(comps)
plt.hist(comps, bins=50, density=True)
x = np.arange(0.00001, 0.05, 0.00001)
COE = [EigenVectorDist(X, int(2*basisdim), 1) for X in x]
CUE = [EigenVectorDist(X, int(2*basisdim), 2) for X in x]
CSE = [EigenVectorDist(X, int(2*basisdim), 4) for X in x]
plt.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
plt.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
plt.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
plt.legend()
plt.show()