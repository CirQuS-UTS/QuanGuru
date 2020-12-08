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

from typing import Optional, List, Iterable, Any

import scipy.sparse as sp # type: ignore
import numpy as np # type: ignore

from .linearAlgebra import norm, outerProd, tensorProd, trace #pylint: disable=relative-beyond-top-level

from .customTypes import Matrix, intList, floatList, matrixList, supInp, matrixOrMatrixList #pylint: disable=relative-beyond-top-level


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
    Creates a `ket` state :math:`|n\\rangle` for a given dimension with 1 (unit population) at a given row.

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    state : int
        row to place 1, i.e. index for the populated state
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    :return : Matrix
        requested `ket` state

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
    Creates a complete basis of `ket` states :math:`\\sum_n|n\\rangle = \\hat{\\mathbb{I}}`.

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    sparse : bool
         if True(False), the returned Matrix types will be sparse(array)

    Returns
    -------
    :return : matrixList
        a list (complete basis) of `ket` states

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

    return [basis(dimension, i, sparse) for i in range(dimension)]


def basisBra(dimension: int, state: int, sparse: bool = True) -> Matrix:
    """
    Creates a `bra` state :math:`\\langle n|` for a given dimension with 1 (unit population) at a given column.

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    state : int
        column to place 1, i.e. index number for the populated state
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    :return : Matrix
        requested `bra` state

    Examples
    --------
    >>> basisBra(2, 0)
    (0, 0)	1

    >>> basisBra(2, 0, sparse=False)
    [[1 0]]
    """

    return basis(dimension, state, sparse).T


def zeros(dimension: int, sparse: bool = True) -> Matrix:
    """
    Creates a column matrix (ket) with all elements zero.

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


def weightedSum(summands: Iterable, weights: Iterable = None) -> Any:
    """ Weighted sum of given list of summands and weights

    Parameters
    ----------
    summands : Iterable
        List of matrices
    weights : Iterable
        List of weights

    Returns
    -------
    :return: Any
        weighted sum
    """

    return sum([weight*val for weight, val in zip(weights, summands)]) if weights is not None else sum(summands)


def superPos(dimension: int, excitations: supInp, populations: bool = True, sparse: bool = True) -> Matrix:
    """
    Create a `ket` state with complex probability amplitudes given as a `dictionary` or `list`.

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    excitations : supInt (Union of int, list(int), dict(int:float))

            1. a `dictionary` with state:population (key:value). The generated state will be normalised.
            2. a `list` of integers corresponding to states to be populated in equal super-position
            3. an `integer`, to create a basis state (equivalent to `basis` function)

    Returns
    -------
    :return: Matrix
        requested normalised `ket` state

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

    if isinstance(excitations, dict):
        sts = excitations
        if populations:
            sts = {k:np.sqrt(v) for (k, v) in sts.items()}
    elif isinstance(excitations, int):
        sts = {excitations:1}
    elif all(isinstance(item, int) for item in excitations):
        sts = {k: 1 for k in excitations}
    else:
        raise TypeError('Unsupported type for parameter excitations')

    return normalise(weightedSum([basis(dimension, excite, sparse) for excite in sts.keys()], list(sts.values())))


def densityMatrix(ket: matrixOrMatrixList, probability: Iterable[Any] = None) -> Matrix:
    """
    Computes the `density matrix` of a pure `ket` state or a mixed state from a list of kets and their associated
    probabilities.

    Parameters
    ----------
    ket : matrixOrMatrixList
        single ket state or list of kets
    probability : floatList
        list of probabilities (0 to 1) associated with the corresponding list of kets

    Returns
    -------
    :return: Matrix
        requested density matrix operator

    Examples
    --------
    >>> ket = basis(2, 0)
    >>> mat = densityMatrix(ket)
    (0, 0)	1

    >>> ket = superPos(2, [0,1], sparse=False)
    >>> mat = densityMatrix(ket)
    [[0.5 0.5]
    [0.5 0.5]]

    >>> ket1 = superPos(2, [0,1], sparse=False)
    >>> ket2 = basis(2, 0)
    >>> mat = densityMatrix([ket1,ket2],[0.5, 0.5])
    [[0.75 0.5]
    [0.5 0.25]]
    """

    return normalise(weightedSum([outerProd(k) for k in ket], probability)) if isinstance(ket, list) else outerProd(ket)


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
        mag = 1 / norm(state)
    else:
        mag = 1 / trace(state)
    return mag * state


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

    st = tensorProd(*[superPos(dim, exs) for (dim, exs) in zip(dimensions, excitations)])
    return st if sparse else st.A


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

    return denMat.T.reshape(np.prod(np.shape(denMat)), 1)


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
