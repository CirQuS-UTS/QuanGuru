from quanguru.QuantumToolbox import Hamiltonians as hams
import quanguru.QuantumToolbox.operators as ops
import scipy.linalg as lin
import numpy as np
from numpy.testing import assert_almost_equal

# TODO randomize these parameters
wq = 2
wc = 2
g = 2
t = 4
dimC = 3

H = - 0.5 * wq * np.kron(np.eye(dimC), ops.sigmaz(sparse=False))
H = H+wc*np.kron(ops.number(dimC, sparse=False), np.eye(2))
H = H+g*np.kron(ops.destroy(dimC, sparse=False), ops.create(2, sparse=False))
H = H+g*np.kron(ops.create(dimC, sparse=False), ops.destroy(2, sparse=False))

UJC_exp = UJC_exp = lin.expm(-1j*H*t)
UJC_analytical = hams.UJC(wq, wc, g, t, dimC, sparse=False)

def test_analytical_JC():
    assert_almost_equal(UJC_exp, UJC_analytical, 6)

def test_analytical_JC_is_unitary():
    identity = UJC_analytical @ UJC_analytical.conj().T
    assert_almost_equal(identity, np.eye(2*dimC, dtype=np.complex128), 6)
    
def test_analytical_JC_absolute_values():
    assert_almost_equal(np.abs(UJC_exp), np.abs(UJC_analytical), 6)
