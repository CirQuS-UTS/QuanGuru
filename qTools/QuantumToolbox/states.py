import scipy.sparse as sp
import numpy as np
from typing import Union
from numpy import ndarray
from scipy.sparse import spmatrix


def basis(dimension:int, state:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates a `ket` state either as sparse (sparse=True) or array (sparse=False) 

    Parameters
    ----------
    dimension: int 
        dimension of Hilbert space
    :param state: index number for the populated state
    :param sparse: boolean for sparse or not (array)

    Returns
    -------
    :return: ket state

    Examples
    --------
    >>> basis(2, 1)
    (0, 0)	1
    >>> basis(2, 1, sparse=False)
    [[1]
    [0]]
    """
    data = [1]
    rows = [state]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return n if sparse else n.A

def basisBra(dimension:int, state:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates a bra state either as sparse (sparse=True) or array (sparse=False) 

    Parameters
    ----------
    :param dimension: dimension of Hilbert space
    :param state: index number for the populated state
    :param sparse: boolean for sparse or not (array)

    Returns
    -------
    :return: bra state

    Examples
    --------
    >>> basisBra(2, 1)
    (0, 0)	1
    >>> basisBra(2, 1, sparse=False)
    [[1 0]]
    """
    n = basis(dimension,state,sparse).T
    return n

def zeros(dimension:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates a column matrix of zeros, either as sparse (sparse=True) or array (sparse=False) 

    :param dimension: dimension of Hilbert space
    :return: bra state
    """
    data = [0]
    rows = [0]
    columns = [0]
    Zeros = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return Zeros if sparse else Zeros.A

def densityMatrix(ket:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Converts a ket state into density matrix \\
    Keeps the sparse/array as sparse/array

    :param ket: ket state
    :return: density Matrix
    """
    return (ket @ (ket.conj().T))

def mat2Vec(densityMatrix:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Converts density matrix into density vector (used in super-operator respresentation)

    :param densityMatrix: density matrix to be converted
    :return: density vector
    """
    vec = densityMatrix.T.reshape(np.prod(np.shape(densityMatrix)), 1)
    return vec

def vec2mat(vec:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Converts density vector into density matrix

    :param vec: density vector to be converted
    :return: density matrix
    """
    a = vec.shape
    n = int(np.sqrt(a[0]))
    mat = vec.reshape((n, n)).T
    return mat

def normalise(state:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Function to normalise any state (ket or density matrix)

    :param state: state to be normalised
    :return: normalised state
    """
    if state.shape[0] != state.shape[1]:
        return normaliseKet(state)
    else:
        return normaliseMat(state)

def normaliseKet(ket:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Function to normalise ket state

    :param state: ket state to be normalised
    :return: normalised ket state
    """
    mag = 1 / np.sqrt((((ket.conj().T) @ ket).diagonal()).sum())
    ketn = mag * ket
    return ketn

def normaliseMat(denMat:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Function to normalise a density matrix

    :param state: density matrix to be normalised
    :return: normalised density matrix
    """
    mag = 1 / (denMat.diagonal()).sum()
    denMatn = mag * denMat
    return denMatn

def superPos(dimension:int, excitations:Union[dict, list, int], sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Function to create a superposition KET state from a given dictionary or list, \\
    or ket state from a given integer (in this case, it is equivalent to basis function)

    :param dimension: dimension of Hilbert space
    :excitations: There are 3 possible uses of this \\
        1) a dictionary with state:population (key:value), e.g. {0:0.2, 1:0.4, 2:0.4} \\
        2) a list (e.g. [0,1,2]) for equally populated super-position \\
        3) an integer, which is equivalent to basis function
    :return: a superposition KET state
    """
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

def compositeState(dimensions:list, excitations:list, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Function to create composite ket states

    :param dimensions: list of dimensions for each sub-system of the composite quantum system
    :param excitations: list of state information for sub-systems \\
        This list can have mixture of dict, list, and int values, 
        which are used to create a superposition state for the corresponding sub-system
    :param sparse: boolean for sparse or not (array)
    :return: composite ket state 
    """
    if isinstance(excitations[0], int):
        st = basis(dimensions[0], excitations[0], sparse)
    else:
        st = superPos(dimensions[0], excitations[0], sparse)

    for ind in range(len(dimensions)-1):
        if isinstance(excitations[ind+1], int):
            st = sp.kron(st, basis(dimensions[ind+1], excitations[ind+1], sparse), format='csc')
        else:
            st = sp.kron(st, superPos(dimensions[ind+1], excitations[ind+1], sparse), format='csc')
    return st if sparse else st.A
