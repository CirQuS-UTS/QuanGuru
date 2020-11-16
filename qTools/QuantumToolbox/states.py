"""
    This module contains the functions to create, manipulate, convert, and/or normalise quantum states.

    .. currentmodule:: qTools.QuantumToolbox


    Functions
    ---------

    .. autosummary::
        basis
        completeBasis
        basisBra
        zeros
        superPos

        densityMatrix
        completeBasisMat

        normalise
        normaliseKet
        normaliseMat

        compositeState
        tensorProd
        partialTrace

        mat2Vec
        vec2Mat

    Types
    ^^^^^
    | :const:`Matrix <qTools.QuantumToolbox.customTypes.Matrix>` : Union of (scipy) sparse and (numpy) array
    | :const:`intList <qTools.QuantumToolbox.customTypes.intList>` : List of integers
    | :const:`matrixList <qTools.QuantumToolbox.customTypes.matrixList>` : List of Matrices
    | :const:`supInt <qTools.QuantumToolbox.customTypes.supInt>` : Union of the types: int, `intList`,
        and dict[int:float] (used in super-position creations)
    | :const:`ndOrListInt <qTools.QuantumToolbox.customTypes.ndOrListInt>` : Union of ndarray and intList
"""

from typing import Optional, List
from numpy import ndarray  # type: ignore

import scipy.sparse as sp # type: ignore
import numpy as np # type: ignore

from .customTypes import Matrix, intList, matrixList, supInp, ndOrListInt


# do not delete these
# from typing import Union, Dict, List, Optional, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)  # Type which is either spmatrix or nparray (created using TypeVar)
# intList = List[int]                            # Type for a list of integers
# matrixList = List[Matrix]                      # Type for a list `Matrix` types
# supInp = Union[Dict[int, float], intList, int] # Type from the union of int, `intList`, and Dict[int:float]
# ndOrListInt = Union[ndarray, intList]         # Type from the union of ndarray and intList with integer elements


def basis(dimension: int, state: int, sparse: bool = True) -> Matrix:
    """
    Creates a `ket` state for a given dimension with 1 (unit population) at a given row (state).

    Either as sparse (``sparse=True``) or array (``sparse=False``)

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    state : int
        row to place 1, i.e. index for the populated state
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return : Matrix
        `ket` state as ``sparse if sparse=True else array``

    Examples
    --------
    >>> basis(2, 0)
    (0, 0)	1

    >>> basis(2, 0, sparse=False)
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
    Creates a complete basis of `ket` states.

    Either as sparse (``sparse=True``) or array (``sparse=False``)

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return : matrixList
        a list (complete basis) of `ket` states as ``sparse if sparse=True else array``

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
    Creates a `bra` state for a given dimension with 1 (unit population) at a given column (state).

    Either as sparse (``sparse=True``) or array (``sparse=False``)

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    state : int
        column to place 1, i.e. index number for the populated state
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return : Matrix
        `bra` state as ``sparse if sparse=True else array``

    Examples
    --------
    >>> basisBra(2, 0)
    (0, 0)	1

    >>> basisBra(2, 0, sparse=False)
    [[1 0]]
    """

    n = basis(dimension, state, sparse).T
    return n


def zeros(dimension: int, sparse: bool = True) -> Matrix:
    """
    Creates a column matrix (ket) with all elements zero.

    Either as sparse (``sparse=True``) or array (``sparse=False``)

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return: Matrix
        ket of zeros

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
    Function to create a `superposition ket` state from a given `dictionary` or `list`,
    or `ket` state from a given `integer` (in this case, it is equivalent to basis function)

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    excitations : supInt (Union of int, list(int), dict(int:float))
        There are 3 possible uses of this

            1. a `dictionary` with state:population (key:value), e.g. {0:0.2, 1:0.4, 2:0.4}
            2. a `list` (e.g. [0,1,2]) for equally populated super-position
            3. an `integer`, which is equivalent to basis function

    Returns
    -------
    :return: Matrix
        a superposition `ket` state

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
    Converts a `ket` state into a `density matrix`.

    Keeps the sparse/array as sparse/array.

    Parameters
    ----------
    ket : Matrix
        ket state

    Returns
    -------
    :return: Matrix
        density Matrix

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


def completeBasisMat(dimension: Optional[int] = None, compKetBase: Optional[matrixList] = None,
                     sparse: bool = True) -> matrixList:
    """
    Creates a complete basis of `density matrices` for a given dimension or convert a `ket basis` to `density matrix`.

    NOTE: This is not a complete basis for n-by-n matrices but for populations, i.e. diagonals.

    For a given basis, this keeps the sparse/array as sparse/array.
    For a given dimension, either as sparse (``sparse=True``) or array (``sparse=False``)

    Parameters
    ----------
    dimension : int or None
        dimension of Hilbert space (or default None if a ket basis is given)
    compKetBase : matrixList or None
        a complete ket basis (or default None if dimension is given)
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return : matrixList
        a list (complete basis) of `density matrices`

    :raises ValueError : raised if both complete ket basis and dimension are None (default). Dimension is used to create


    Examples
    --------

    .. testcode::

        from qTools import completeBasis, completeBasisMat
        completeBasisMat1 = completeBasisMat(dimension=2, compKetBase=completeBasis1)
        print('s')

    .. testoutput::
        :options: -ELLIPSIS, +NORMALIZE_WHITESPACE

        (0, 1)	1
        (1, 1)	1


    .. doctest::

        >>> print('x')
        x

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
    Function to normalise `any` state (ket or density matrix).

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    state : Matrix
        state to be normalised

    Returns
    -------
    :return: Matrix
        normalised state

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
    Function to normalise a `ket` state.

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    state : Matrix
        ket state to be normalised

    Returns
    -------
    :return: Matrix
        normalised `ket` state

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
    Function to normalise a `density matrix`.

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    state : Matrix
        `density matrix` to be normalised

    Returns
    -------
    :return: Matrix
        normalised `density matrix`

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
    Function to create `composite ket` states.

    Parameters
    ----------
    dimensions : intList
        list of dimensions for each sub-system of the composite quantum system
    excitations : List[supInp]
        list of state information for sub-systems.
        This list can have mixture of dict, list, and int values,
        which are used to create a superposition state for the corresponding sub-system
        See: `superPos` function
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return: Matrix
        composite ket state

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

    st = superPos(dimensions[0], excitations[0], sparse)

    for ind in range(len(dimensions)-1):
        st = sp.kron(st, superPos(dimensions[ind+1], excitations[ind+1], sparse), format='csc')
    return st if sparse else st.A


def tensorProd(*args: Matrix) -> Matrix:
    """
    Function to calculate tensor product of given (any number of) states (in the given order).
    TODO test with ndarrays. sp.kron documentation says that it works with dense, not sure what if it means any array.
    The matrices can be sparse/ndarray, but they all should be the same either sparse/ndarray not a mixture.

    Parameters
    ----------
    *args : Matrix
        state matrices (arbitrary number of them)

    Returns
    -------
    :return: Matrix
        tensor product of given states (in the given order)

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    totalProd = args[0]
    if isinstance(totalProd, int):
        totalProd = sp.identity(totalProd, format="csc")

    for ind in range(len(args)-1):
        mat = args[ind+1]
        if isinstance(args[ind+1], int):
            mat = sp.identity(mat, format='csc')
        totalProd = sp.kron(totalProd, mat, format='csc')
    return totalProd


def partialTrace(keep: ndOrListInt, dims: ndOrListInt, state: Matrix) -> ndarray:
    """
    Calculates the partial trace of a `density matrix` of composite state.

    Parameters
    ----------
    keep : ndOrListInt
        An array of indices of the spaces to keep after being traced. For instance, if the space is
        A x B x C x D and we want to trace out B and D, keep = [0,2]
    dims : ndOrListInt
        An array of the dimensions of each space. For instance, if the space is A x B x C x D,
        dims = [dim_A, dim_B, dim_C, dim_D]
    state : Matrix
        Matrix to trace

    Returns
    -------
    :return : Matrix
        Traced matrix

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

    idx1 = list(range(Ndim))
    idx2 = [Ndim+i if i in keep else i for i in range(Ndim)]
    rhoA = rho.reshape(np.tile(dims, 2))
    rhoA = np.einsum(rhoA, idx1+idx2, optimize=False)
    return rhoA.reshape(Nkeep, Nkeep)


def mat2Vec(denMat: Matrix) -> Matrix: # pylint: disable=invalid-name
    """
    Converts `density matrix` into `density vector` (used in super-operator representation).

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    denMat : Matrix
        density matrix to be converted

    Returns
    -------
    :return: Matrix
        density vector

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


def vec2Mat(vec: Matrix) -> Matrix: # pylint: disable=invalid-name
    """
    Converts `density vector` into `density matrix`.

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    vec : Matrix
        density vector to be converted

    Parameters
    ----------
    :return: Matrix
        density matrix

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
