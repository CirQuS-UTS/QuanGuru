"""
Testing QuantumToolbox by comparing it with Qutip
"""

import qutip as qtp
import QuantumToolbox.states as qt
import scipy.sparse as sp
import numpy as np

############################################################################################################
dimension = 4

###################################
"""n = qt.basis(dimension,2)
ns = qt.basis(dimension,2, sparse=False)
nq = (qtp.basis(dimension,2).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""n = qt.zeros(dimension)
ns = qt.zeros(dimension, sparse=False)

print(sp.isspmatrix(n), sp.isspmatrix(ns))
print(ns)
print(n)
print(ns)"""

###################################
"""k = qt.basis(dimension,2)
ks = qt.basis(dimension,2,sparse=False)
kq = qtp.basis(dimension,2)
n = qt.densityMatrix(k)
ns = qt.densityMatrix(ks)
nq = ((kq * kq.dag()).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(ns)
print(n - nq)
print(ns - nq)"""

###################################
"""k = qt.basis(dimension,2)
ks = qt.basis(dimension,2,sparse=False)
kq = qtp.basis(dimension,2)
m = qt.densityMatrix(k)
ms = qt.densityMatrix(ks)
mq = ((kq * kq.dag()).data)
n = qt.mat2Vec(m)
ns = qt.mat2Vec(ms)
print(mq.toarray())
print(sp.isspmatrix(mq))
nq = (qtp.mat2vec(mq))

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n)
print(ns)
print(nq)
print(n - nq)
print(ns - nq)"""

###################################
"""k = qt.basis(dimension,2)
ks = qt.basis(dimension,2,sparse=False)
kq = qtp.basis(dimension,2)
m = qt.densityMatrix(k)
ms = qt.densityMatrix(ks)
mq = ((kq * kq.dag()).data)
v = qt.mat2Vec(m)
vs = qt.mat2Vec(ms)
vq = (qtp.mat2vec(mq))
n = qt.vec2mat(v)
ns = qt.vec2mat(vs)
nq = (qtp.vec2mat(vq.toarray()))

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(n)
print(ns)
print(nq)
print(n - nq)
print(ns - nq)"""

###################################
"""s = 2*qt.basis(dimension,2)
ss = 2*qt.basis(dimension,2, sparse=False)
n = qt.normalize(s)
ns = qt.normalize(ss)
nq = (qtp.basis(dimension,2).data)

print(sp.isspmatrix(n), sp.isspmatrix(ns), sp.isspmatrix(nq))
print(ns)
print(n - nq)
print(ns - nq)"""