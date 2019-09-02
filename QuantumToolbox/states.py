import scipy.sparse as sp
import numpy as np

def genericBasis(n,sparse=True):
    basisStates = []
    for i in range(n):
        b = basis(n,i,sparse)
        basisStates.append(b)
    return basisStates

def basis(dimension, state, sparse=True):
    data = [1]
    rows = [state]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return n if sparse == True else n.toarray()

def zeros(dimension, sparse=True):
    data = [0]
    rows = [0]
    columns = [0]
    Zeros = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return Zeros if sparse == True else Zeros.toarray()

def densityMatrix(ket):
    sparse = sp.isspmatrix(ket)
    if sparse == True:
        return (ket @ (ket.getH()))
    else:
        herm = np.transpose(np.conjugate(ket))
        return (ket @ herm)

def mat2Vec(densityMatrix):
    sparse = sp.isspmatrix(densityMatrix)
    if sparse == False:
        densityMatrixS = sp.csc_matrix(densityMatrix)
    else:
        densityMatrixS = densityMatrix
    vec = densityMatrixS.T.reshape(np.prod(np.shape(densityMatrixS)), 1)
    return vec if sparse == True else vec.toarray()

def vec2mat(vec):
    sparse = sp.isspmatrix(vec)
    if sparse == False:
        vecS = sp.csc_matrix(vec)
    else:
        vecS = vec
    a = vecS.get_shape()
    n = int(np.sqrt(a[0]))
    mat = vecS.reshape((n, n)).T
    return mat if sparse == True else mat.toarray()

def normalize(psi):
    sparse = sp.isspmatrix(psi)
    if sparse == True:
        mag = (psi.getH() @ psi)[0, 0]
        psin = (1 / np.sqrt(mag)) * psi
        return psin
    elif sparse == False:
        mag = ((np.transpose(np.conjugate(psi))) @ psi)
        psin = (1 / np.sqrt(mag)) * psi
        return psin