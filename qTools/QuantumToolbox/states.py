"""
    Module of functions to create and/or normalise quantum states.

    Functions
    -------
    :basis : Creates a `ket` state for a given dimension with 1 at a given row
    :completeBasis : Creates a complete basis of `ket` states
    :basisBra : Creates a `bra` state for a given dimension with 1 at a given column
    :zeros : Creates a column matrix (ket) of zeros
    :superPos : Creates a `ket` superposition state

    :densityMatrix : Converts a `ket` state into ``density matrix``
    :completeBasisMat : Creates a complete basis of ``density matrices`` or convert a ``ket basis`` to ``density matrix``

    :normalise : Function to normalise `any` state (ket or density matrix)
    :normaliseKet : Function to normalise `ket` state
    :normaliseMat : Function to normalise a ``density matrix``

    :compositeState : Function to create ``composite ket`` states
    :tensorProd : ``missing docstring``
    :partialTrace : Calculates the partial trace of a `density matrix` of composite state

    :mat2Vec : Converts ``density matrix`` into ``density vector`` (used in super-operator representation)
    :vec2mat : Converts ``density vector`` into ``density matrix``
"""

from typing import Optional, List
from numpy import ndarray  # type: ignore

import scipy.sparse as sp
import numpy as np

from .customTypes import Matrix, intList, matrixList, supInp, ndOrList_int


"""from typing import Union, Dict, List, Optional, TypeVar
from numpy import ndarray
from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)
intList = List[int]                                 # Type for a list of integers
matrixList = List[Matrix]                           # Type for a list `Matrix` types
supInp = Union[Dict[int, float], intList, int]      # Type from the union of int, `intList`, and Dict[int:float]
ndOrList_int = Union[ndarray, intList]              # Type from the union of ndarray and intList with integer elements"""


def basis(dimension: int, state: int, sparse: bool = True) -> Matrix:
    """
    Creates a `ket` state for a given dimension with 1 at a given row

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param dimension : dimension of Hilbert space
    :param state : row to place 1, i.e. index for the populated state
    :param sparse : boolean for sparse or not (array)

    Returns
    -------
    :return : `ket` state with 1 at a given row

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


def completeBasis(dimension: int, sparse: bool = True) -> matrixList:
    """
    Creates a complete basis of `ket` states

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param dimension : dimension of Hilbert space
    :param sparse : boolean for sparse or not (array)

    Returns
    -------
    :return : a list (complete basis) of `ket` states

    Examples
    --------
    >>> completeBasis0 = completeBasis(2, sparse=False)
    >>> for state in completeBasis0:
    >>>    print(state)
    [[1]
    [0]]
    [[0]
    [1]]
    >>> completeBasis1 = completeBasis(2)
    >>> for state in completeBasis1:
    >>>    print(state)
    (0, 0)	1
    (1, 0)	1
    """

    compBasis = []
    for i in range(dimension):
        compBasis.append(basis(dimension, i, sparse))
    return compBasis

def basisBra(dimension: int, state: int, sparse: bool = True) -> Matrix:
    """
    Creates a `bra` state for a given dimension with 1 at a given column

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

    n = basis(dimension, state, sparse).T
    return n


def zeros(dimension: int, sparse: bool = True) -> Matrix:
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


def superPos(dimension: int, excitations: supInp, sparse: bool = True) -> Matrix:
    """
    Creates a `ket` superposition state

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
        sts = [basis(dimension, excitations, sparse)]
    else:
        for val in excitations:
            sts.append(basis(dimension, val, sparse))
    sta = normalise(sum(sts))
    return sta


def densityMatrix(ket: Matrix) -> Matrix:
    """
    Converts a `ket` state into ``density matrix``

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

    return ket @ (ket.conj().T)


def completeBasisMat(dimension: Optional[int] = None, compKetBase: Optional[matrixList] = None, sparse: bool = True) -> matrixList:
    """
    Creates a complete basis of ``density matrices`` or convert a ket basis to density matrix for a given dimension.
    Note: This is not a complete basis for n-by-n matrices but for populations, i.e. diagonals.

    For a given basis, Keeps the sparse/array as sparse/array.
    For a given dimension, either as sparse (>>> sparse=True) or array (>>> sparse=False)

    If a complete basis is given, keeps the sparse/array as sparse/array

    Parameters
    ----------
    :param `dimension` : dimension of Hilbert space (or default None if a ket basis is given)
    :param `compKetBase`: a complete ket basis (or default None if dimension is given)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return : a list (complete basis) of ``density matrices``

    Raises
    ------
    :ValueError : raised if both complete ket basis and dimension are None (default). Dimension is used to create

    Examples
    --------
    >>> completeBasis0 = completeBasis(2, sparse=False)
    >>> completeBasis1 = completeBasis(2)
    >>> completeBasisMat0 = completeBasisMat(dimension=2, compKetBase=completeBasis0)
    >>> for state in completeBasisMat0:
    >>>    print(state)
    [[1 0]
    [0 0]]
    [[0 0]
    [0 1]]
    >>> completeBasisMat1 = completeBasisMat(dimension=2, compKetBase=completeBasis1)
    >>> for state in completeBasisMat1:
    >>>    print(state)
    (0, 0)	1
    (1, 1)	1
    >>> completeBasisMat01 = completeBasisMat(dimension=2, sparse=False)
    >>> for state in completeBasisMat01:
    >>>    print(state)
    [[1 0]
    [0 0]]
    [[0 0]
    [0 1]]
    >>> completeBasisMat11 = completeBasisMat(dimension=2)
    >>> for state in completeBasisMat11:
    >>>    print(state)
    (0, 0)	1
    (1, 1)	1
    """

    if compKetBase is None:
        if dimension is None:
            raise ValueError('err')
        compBase = completeBasis(dimension, sparse)
    else:
        compBase = compKetBase

    for i, state in enumerate(compBase):
        compBase[i] = densityMatrix(state)
    return compBase


def normalise(state: Matrix) -> Matrix:
    """
    Function to normalise `any` state (ket or density matrix)

    Keeps the sparse/array as sparse/array

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
        normalised = normaliseKet(state)
    else:
        normalised = normaliseMat(state)
    return normalised


def normaliseKet(ket: Matrix) -> Matrix:
    """
    Function to normalise `ket` state

    Keeps the sparse/array as sparse/array

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


def normaliseMat(denMat: Matrix) -> Matrix:
    """
    Function to normalise a ``density matrix``

    Keeps the sparse/array as sparse/array

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


def compositeState(dimensions: intList, excitations: List[supInp], sparse: bool = True) -> Matrix:
    """
    Function to create ``composite ket`` states

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


def tensorProd(*args: Matrix) -> Matrix:
    """
    Function to calculate tensor product of given states (in the given order).

    The matrices can be sparse/ndarray, but they all should be the same either sparse/ndarray not a mixture.

    Parameters
    ----------
    :param `*args` : state matrices (arbitary number of them)

    Returns
    -------
    :return: tensor product of given states (in the given order)

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    totalProd = args[0]
    if isinstance(totalProd, sp.spmatrix):
        kronProd = sp.kron
    else:
        kronProd = np.kron

    for ind in range(len(args)-1):
        totalProd = kronProd(totalProd, args[ind+1], format='csc')
    return totalProd


def partialTrace(keep: ndOrList_int, dims: ndOrList_int, state: Matrix) -> ndarray:
    """
    Calculates the partial trace of a `density matrix` of composite state.
    ρ_a = Tr_b(ρ)

    Found on: https://scicomp.stackexchange.com/questions/30052/calculate-partial-trace-of-an-outer-product-in-python

    Parameters
    ----------
    :param `keep` : An array of indices of the spaces to keep after being traced. For instance, if the space is
        A x B x C x D and we want to trace out B and D, keep = [0,2]
    dims : An array of the dimensions of each space. For instance, if the space is A x B x C x D,
        dims = [dim_A, dim_B, dim_C, dim_D]
    :param `state` : Matrix to trace

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


def mat2Vec(denMat: Matrix) -> Matrix:
    """
    Converts ``density matrix`` into ``density vector`` (used in super-operator respresentation)

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    :param `denMat`: density matrix to be converted

    Parameters
    ----------
    :return: density vector

    Examples
    --------
    >>> denMat = densityMatrix(ket=basis(dimension=2, state=1, sparse=True))
    >>> denVec = mat2Vec(denMat=denMat)
    [[0]
    [0]
    [0]
    [1]]
    """

    vec = denMat.T.reshape(np.prod(np.shape(denMat)), 1)
    return vec


def vec2mat(vec: Matrix) -> Matrix:
    """
    Converts ``density vector`` into ``density matrix``

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    :param `vec`: density vector to be converted

    Parameters
    ----------
    :return: density matrix

    Examples
    --------
    >>> denMat = densityMatrix(ket=basis(dimension=2, state=1, sparse=True))
    [[0 0]
    [0 1]]
    >>> denVec = mat2Vec(denMat=denMat)
    >>> denMatConverted = vec2mat(vec=denVec)
    [[0 0]
    [0 1]]
    """

    a = vec.shape
    n = int(np.sqrt(a[0]))
    mat = vec.reshape((n, n)).T
    return mat
