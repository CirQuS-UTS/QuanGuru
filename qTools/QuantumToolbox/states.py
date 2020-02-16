import scipy.sparse as sp
import numpy as np


def basis(dimension, state, sparse=True):
    data = [1]
    rows = [state]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return n if sparse == True else n.toarray()

def basisBra(dimension, state, sparse=True):
    data = [1]
    rows = [0]
    columns = [state]
    n = sp.csc_matrix((data, (rows, columns)), shape=(1,dimension))
    return n if sparse == True else n.toarray()

def zeros(dimension, sparse=True):
    data = [0]
    rows = [0]
    columns = [0]
    Zeros = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return Zeros if sparse == True else Zeros.toarray()

def densityMatrix(ket):
    return (ket @ (ket.conj().T))

def mat2Vec(densityMatrix):
    vec = densityMatrix.T.reshape(np.prod(np.shape(densityMatrix)), 1)
    return vec

def vec2mat(vec):
    a = vec.shape
    n = int(np.sqrt(a[0]))
    mat = vec.reshape((n, n)).T
    return mat

def normalize(psi):
    mag = (((psi.conj().T) @ psi).diagonal()).sum()
    psin = (1 / np.sqrt(mag)) * psi
    return psin