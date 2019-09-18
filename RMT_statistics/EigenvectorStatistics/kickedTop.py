from QuantumToolbox.operators import Jz, Jy
import scipy.linalg as lina
import numpy as np
from QuantumToolbox.liouvillian import Liouvillian
from QuantumToolbox.states import genericBasis
from RMT_statistics.Modules.Distributions import EigenVectorDist

p = 1.7
j = 400
la = 6

jz = Jz(j)
jy = Jy(j)
jzs = jz@jz

h_0 = p*jy
V_1 = (la/(2*j))*(jzs)
V_1p = ((la+0.1)/(2*j))*(jzs)

U_0 = Liouvillian(h_0)
U_1 = Liouvillian(V_1)@U_0
U_2 = Liouvillian(V_1p)@U_0

vecs1 = lina.eig(U_1.toarray())[1]
basis1 = genericBasis(int((2*j)),sparse=False)
basis2 = lina.eig(U_2.toarray())[1]
basis = basis2

comps = []
for i in range(len(basis)):
    bra = np.transpose(np.conjugate(basis[i]))
    for j in range(len(vecs1)):
        overlap = bra@vecs1[j]
        comps.append(np.real(np.conjugate(overlap)*overlap))

import matplotlib.pyplot as plt
print(comps)
plt.hist(comps, bins=50, density=True)
x = np.arange(0.00001, 0.05, 0.00001)
COE = [EigenVectorDist(X, int(j), 1) for X in x]
CUE = [EigenVectorDist(X, int(j), 2) for X in x]
CSE = [EigenVectorDist(X, int(j), 4) for X in x]
plt.plot(x, COE, 'r-')
plt.plot(x, CUE, 'g-')
plt.plot(x, CSE, 'b-')
plt.show()