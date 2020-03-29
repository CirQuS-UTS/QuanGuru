"""
    Module of functions to create and/or normalise quantum states
"""
import scipy.sparse as sp
import numpy as np

from typing import Union, Dict, List
from numpy import ndarray
from scipy.sparse import spmatrix


def basis(dimension:int, state:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates a `ket` state 
    
    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ----------
    :param `dimension` : dimension of Hilbert space
    :param `state` : index number for the populated state
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return : `ket` state

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
    Creates a `bra` state

    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ----------
    :param `dimension` : dimension of Hilbert space
    :param `state` : index number for the populated state
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `bra` state

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
    Creates a column matrix of zeros

    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ---------- 
    :param `dimension` : dimension of Hilbert space

    Returns
    -------
    :return: ket of zeros

    Examples
    --------
    >>> zeros(2)
    (0, 0)	0
    >>> zeros(2, sparse=False)
    [[0]
    [0]]
    """
    data = [0]
    rows = [0]
    columns = [0]
    Zeros = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return Zeros if sparse else Zeros.A

def superPos(dimension:int, excitations:Union[Dict[int, float], List[int], int], sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates a `ket` state

    Function to create a ``superposition ket`` state from a given `dictionary` or `list`, \\
    or `ket` state from a given `integer` (in this case, it is equivalent to basis function)

    Parameters
    ----------
    :param `dimension`: dimension of Hilbert space
    :param `excitations`: There are 3 possible uses of this \\
        1) a `dictionary` with state:population (key:value), e.g. {0:0.2, 1:0.4, 2:0.4} \\
        2) a `list` (e.g. [0,1,2]) for equally populated super-position \\
        3) an `integer`, which is equivalent to basis function

    Returns
    -------
    :return: a superposition `ket` state

    Examples
    --------
    >>> ket = superPos(2, {0:0.2, 1:0.8}, sparse=False)
    [[0.4472136 ]
    [0.89442719]]
    >>> ket = superPos(2, [0,1], sparse=False)
    [[0.70710678]
    [0.70710678]]
    >>> ket = superPos(2, 1, sparse=False)
    [[0.]
    [1.]]
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

def densityMatrix(ket:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Converts a ket state into density matrix 

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    :param `ket` : ket state

    Returns
    -------
    :return: density Matrix

    Examples
    --------
    >>> ket = basis(2, 0)
    >>> mat = densityMatrix(ket)
    (0, 0)	1
    >>> ket = basis(2, 0, False)
    >>> mat = densityMatrix(ket)
    [[1 0]
    [0 0]]
    >>> ket = superPos(2, [0,1], sparse=False)
    >>> mat = densityMatrix(ket)
    [[0.5 0.5]
    [0.5 0.5]]
    >>> ket = superPos(2, {0:0.2, 1:0.8}, sparse=False)
    >>> mat = densityMatrix(ket)
    [[0.2 0.4]
    [0.4 0.8]]
    """
    return (ket @ (ket.conj().T))

def normalise(state:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Function to normalise `any` state (ket or density matrix)

    Parameters
    ----------
    :param `state` : state to be normalised

    Returns
    -------
    :return: normalised state

    Examples
    --------
    >>> import numpy as np
    >>> nonNormalisedKet = np.sqrt(0.2)*basis(2,1) + np.sqrt(0.8)*basis(2,0)
    >>> normalisedKet = normalise(nonNormalisedKet)
    [[0.89442719]
    [0.4472136 ]]
    >>> nonNormalisedMat = densityMatrix(nonNormalisedKet)
    >>> normalisedMat = normalise(nonNormalisedMat)
    [[0.8 0.4]
    [0.4 0.2]]
    """
    if state.shape[0] != state.shape[1]:
        return normaliseKet(state)
    else:
        return normaliseMat(state)

def normaliseKet(ket:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Function to normalise `ket` state

    Parameters
    ----------
    :param `state` : ket state to be normalised

    Returns
    -------
    :return: normalised `ket` state

    Examples
    --------
    >>> import numpy as np
    >>> nonNormalisedKet = np.sqrt(0.2)*basis(2,1) + np.sqrt(0.8)*basis(2,0)
    >>> normalisedKet = normaliseKet(nonNormalisedKet)
    [[0.89442719]
    [0.4472136 ]]
    """
    mag = 1 / np.sqrt((((ket.conj().T) @ ket).diagonal()).sum())
    ketn = mag * ket
    return ketn

def normaliseMat(denMat:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Function to normalise a ``density matrix``

    Parameters
    ----------
    :param `state` : ``density matrix`` to be normalised

    Returns
    -------
    :return: normalised ``density matrix``

    Examples
    --------
    >>> import numpy as np
    >>> nonNormalisedMat = densityMatrix(nonNormalisedKet)
    >>> normalisedMat = normalise(nonNormalisedMat)
    [[0.8 0.4]
    [0.4 0.2]]
    """
    mag = 1 / (denMat.diagonal()).sum()
    denMatn = mag * denMat
    return denMatn

def compositeState(dimensions:List[int], excitations:List[Union[Dict[int, float], List[int], int]], sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Function to create composite ket states

    Parameters
    ----------
    :param `dimensions` : list of dimensions for each sub-system of the composite quantum system
    :param `excitations` : list of state information for sub-systems \\
        This list can have mixture of dict, list, and int values, 
        which are used to create a superposition state for the corresponding sub-system \\
        See: `superPos` function
    :param `sparse`: boolean for sparse or not (array)

    Returns
    -------
    :return: composite ket state

    Examples
    --------
    >>> compositeState0 = compositeState(dimensions=[2, 2], excitations=[0,1], sparse=False)
    [[0]
    [1]
    [0]
    [0]]
    >>> compositeState1 = compositeState(dimensions=[2, 2], excitations=[[0,1],1], sparse=False)
    [[0.        ]
    [0.70710678]
    [0.        ]
    [0.70710678]]
    >>> compositeState2 = compositeState(dimensions=[2, 2], excitations=[0,{0:0.2, 1:0.8}], sparse=False)
    [[0.4472136 ]
    [0.89442719]
    [0.        ]
    [0.        ]]
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

def partialTrace(keep:Union[ndarray, List[int]], dims:Union[ndarray, List[int]], state:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Calculates the partial trace of a `density matrix` of composite state.
    ρ_a = Tr_b(ρ)

    Found on: https://scicomp.stackexchange.com/questions/30052/calculate-partial-trace-of-an-outer-product-in-python

    Parameters
    ----------
    :param `ρ` : Matrix to trace
    :param `keep` : An array of indices of the spaces to keep after being traced. For instance, if the space is
        A x B x C x D and we want to trace out B and D, keep = [0,2]
    dims : An array of the dimensions of each space. For instance, if the space is A x B x C x D,
        dims = [dim_A, dim_B, dim_C, dim_D]

    Returns
    -------
    ρ_a : Traced matrix

    Examples
    --------
    >>> compositeState0 = compositeState(dimensions=[2, 2], excitations=[0,1], sparse=False)
    >>> stateFirstSystem0 = partialTrace(keep=[0], dims=[2, 2], state=compositeState0)
    [[1 0]
    [0 0]]
    >>> stateSecondSystem0 = partialTrace(keep=[1], dims=[2, 2], state=compositeState0)
    [[0 0]
    [0 1]]
    >>> compositeState1 = compositeState(dimensions=[2, 2], excitations=[[0,1],1], sparse=False)
    [[0. 0.]
    [0. 1.]]
    >>> stateFirstSystem1 = partialTrace(keep=[0], dims=[2, 2], state=compositeState1)
    [[0.5 0.5]
    [0.5 0.5]]
    >>> stateSecondSystem1 = partialTrace(keep=[1], dims=[2, 2], state=compositeState1)
    >>> compositeState2 = compositeState(dimensions=[2, 2], excitations=[0,{0:0.2, 1:0.8}], sparse=False)
    >>> stateFirstSystem2 = partialTrace(keep=[0], dims=[2, 2], state=compositeState2)
    [[1. 0.]
    [0. 0.]]
    >>> stateSecondSystem2 = partialTrace(keep=[1], dims=[2, 2], state=compositeState2)
    [[0.2 0.4]
    [0.4 0.8]]
    """
    if not isinstance(state, np.ndarray):
        state = state.toarray()

    rho = state
    if rho.shape[0] != rho.shape[1]:
        rho = (rho @ (rho.conj().T))

    keep = np.asarray(keep)
    dims = np.asarray(dims)
    Ndim = dims.size
    Nkeep = np.prod(dims[keep])

    idx1 = [i for i in range(Ndim)]
    idx2 = [Ndim+i if i in keep else i for i in range(Ndim)]
    rho_a = rho.reshape(np.tile(dims, 2))
    rho_a = np.einsum(rho_a, idx1+idx2, optimize=False)
    return rho_a.reshape(Nkeep, Nkeep)

def mat2Vec(densityMatrix:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Converts density matrix into density vector (used in super-operator respresentation)

    Parameters
    ----------
    :param `densityMatrix`: density matrix to be converted

    Parameters
    ----------
    :return: density vector

    Examples
    --------
    >>> denMat = qStates.densityMatrix(ket=qStates.basis(dimension=2, state=1, sparse=True))
    >>> denVec = qStates.mat2Vec(densityMatrix=denMat)
    [[0]
    [0]
    [0]
    [1]]
    """
    vec = densityMatrix.T.reshape(np.prod(np.shape(densityMatrix)), 1)
    return vec

def vec2mat(vec:Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Converts density vector into density matrix

    Parameters
    ----------
    :param `vec`: density vector to be converted

    Parameters
    ----------
    :return: density matrix

    Examples
    --------
    >>> denMat = qStates.densityMatrix(ket=qStates.basis(dimension=2, state=1, sparse=True))
    [[0 0]
    [0 1]]
    >>> denVec = qStates.mat2Vec(densityMatrix=denMat)
    >>> denMatConverted = qStates.vec2mat(vec=denVec)
    [[0 0]
    [0 1]]
    """
    a = vec.shape
    n = int(np.sqrt(a[0]))
    mat = vec.reshape((n, n)).T
    return mat