import numpy as np
import scipy.sparse as sp

def CNOT(sparse=True):
    data = [1, 1, 1, 1]
    rows = [0, 1, 2, 3]
    columns = [0, 1, 3, 2]
    n = sp.csc_matrix((data, (rows, columns)), shape=(4, 4))
    return n if sparse else n.toarray()

def CPHASE(phase, sparse=True):
    data = [1, 1, 1, np.exp(1j*phase)]
    rows = [0, 1, 2, 3]
    columns = [0, 1, 2, 3]
    n = sp.csc_matrix((data, (rows, columns)), shape=(4, 4))
    return n if sparse else n.toarray()

def Hadamard(sparse=True):
    data = [1/np.sqrt(2), 1/np.sqrt(2), 1/np.sqrt(2), -1/np.sqrt(2)]
    rows = [0, 0, 1, 1]
    columns = [0, 1, 0, 1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()
