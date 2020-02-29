import scipy.sparse as sp
import numpy as np


def basis(dimension, state, sparse=True):
    data = [1]
    rows = [state]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return n if sparse == True else n.A

def basisBra(dimension, state, sparse=True):
    n = basis(dimension,state,sparse).T
    return n

def zeros(dimension, sparse=True):
    data = [0]
    rows = [0]
    columns = [0]
    Zeros = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return Zeros if sparse == True else Zeros.A

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

def normalise(psi):
    mag = (((psi.conj().T) @ psi).diagonal()).sum()
    psin = (1 / np.sqrt(mag)) * psi
    return psin


def superPos(dimension, excitations, sparse=True):
    # TODO write this better to handle int cases
    sts = []
    if isinstance(excitations, dict):
        for key, val in excitations.items():
            sts.append(np.sqrt(val)*basis(dimension, key, sparse))
    elif isinstance(excitations, int):
        sts = [basis(dimension, excitations)]
    else:
        for val in excitations:
            sts.append(basis(dimension, val, sparse))
    sta = normalise(sum(sts))
    return sta


def compositeState(dimensions, excitations, sparse=True):
    if isinstance(excitations[0], int):
        st = basis(dimensions[0], excitations[0], True)
    else:
        st = superPos(dimensions[0], excitations[0], True)

    for ind in range(len(dimensions)-1):
        if isinstance(excitations[ind+1], int):
            st = sp.kron(st, basis(dimensions[ind+1], excitations[ind+1], True), format='csc')
        else:
            st = sp.kron(st, superPos(dimensions[ind+1], excitations[ind+1], True), format='csc')
    return st if sparse == True else st.A
