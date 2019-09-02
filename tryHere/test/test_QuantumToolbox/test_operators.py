"""
Testing QuantumToolbox by comparing it with Qutip
"""

import qutip as qtp
import QuantumToolbox.operators as qt
import scipy.sparse as sp
import numpy as np

############################################################################################################
dimension = 4

###################################
"""n = qt.number(dimension)
ns = qt.number(dimension, sparse=False)
nq = (qtp.num(dimension).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n)
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.destroy(dimension)
ns = qt.destroy(dimension, sparse=False)
nq = (qtp.destroy(dimension).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(np.sqrt(2),np.sqrt(3))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.create(dimension)
ns = qt.create(dimension, sparse=False)
nq = (qtp.create(dimension).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(np.sqrt(2),np.sqrt(3))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.sigmay()
ns = qt.sigmay(sparse=False)
nq = (qtp.sigmay().data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.sigmax()
ns = qt.sigmax(sparse=False)
nq = (qtp.sigmax().data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.sigmaz()
ns = qt.sigmaz(sparse=False)
nq = (qtp.sigmaz().data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""a = np.empty((dimension,))
a[::2] = 1
print(a)
a[1::2] = -1
print(a)
ps = qt.paritySUM(dimension)
pe = qt.parityEXP(qt.number(dimension))
print(ps - pe)"""

###################################
"""n = qt.basis(dimension,2)
ns = qt.basis(dimension,2,sparse=False)
nq = (qtp.basis(dimension,2).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.displacement(2,dimension)
ns = qt.displacement(2,dimension,sparse=False)
nq = (qtp.displace(dimension,2).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.squeeze(2,dimension)
ns = qt.squeeze(2,dimension,sparse=False)
nq = (qtp.squeeze(dimension,2).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.Jz(dimension)
ns = qt.Jz(dimension,sparse=False)
nq = (qtp.jmat(dimension,'z').data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.Jp(dimension)
ns = qt.Jp(dimension,sparse=False)
nq = (qtp.jmat(dimension,'+').data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.Jm(dimension)
ns = qt.Jm(dimension,sparse=False)
nq = (qtp.jmat(dimension,'-').data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.Jx(dimension)
ns = qt.Jx(dimension,sparse=False)
nq = (qtp.jmat(dimension,'x').data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.Jy(dimension)
ns = qt.Jy(dimension,sparse=False)
nq = (qtp.jmat(dimension,'y').data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.Js(dimension)
ns = qt.Js(dimension,sparse=False)
nq = (qtp.jmat(dimension,'x').data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n - nq)
print(ns - nq)"""