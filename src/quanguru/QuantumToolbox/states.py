r"""
    Contains methods to create states, such as ket, bra, densityMatrix, superpositions, etc.

    .. currentmodule:: quanguru.QuantumToolbox.states

    Functions
    ---------

    .. autosummary::
        basis
        basisBra
        zerosKet
        zerosMat
        completeBasis

    .. autosummary::
        superPos
        densityMatrix
        normalise
        compositeState
        completeBasisMat
        weightedSum

    .. autosummary::
        mat2Vec
        vec2Mat

    .. autosummary::
        BellStates

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `basis`                   |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `basisBra`                |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `zerosKet`                |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `zerosMat`                |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `completeBasis`           |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `superPos`                |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `densityMatrix`           |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `normalise`               |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `compositeState`          |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `completeBasisMat`        |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `weightedSum`             |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `mat2Vec`                 |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `vec2Mat`                 |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `BellStates`              |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from typing import Optional, List, Iterable, Any

import scipy.sparse as sp # type: ignore
from scipy.sparse import spmatrix # type: ignore
import numpy as np # type: ignore

from .linearAlgebra import (norm as linAlNorm, outerProd as linAlOuterProd,
                            tensorProd as linAlTensorProd, trace as linAlTrace) #pylint: disable=relative-beyond-top-level

from .customTypes import Matrix, intList, matrixList, supInp, matrixOrMatrixList #pylint: disable=relative-beyond-top-level


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
    r"""
    Creates a `ket` state
    :math:`|n=\textrm{state}\rangle := \begin{bmatrix} 0 \\ \vdots \\ 1 \textrm{(nth element)} \\ \vdots \\ 0
    \end{bmatrix}_{\textrm{dimension}\times 1}`
    for a given dimension with 1 (unit population) at a given row.

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
    Matrix
        requested `ket` state

    Examples
    --------
    >>> print(basis(2, 0))
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
    r"""
    Creates a complete basis of ket states :math:`\{|n\rangle\}`,
    st :math:`\sum_n|n\rangle\langle n| = \hat{\mathbb{I}}`.

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    sparse : bool
         if True(False), the returned Matrix types will be sparse(array)

    Returns
    -------
    matrixList
        a list (complete basis) of `ket` states

    Examples
    --------
    >>> completeBasis(2, sparse=False)
    [array([[1],
            [0]], dtype=int64),
     array([[0],
            [1]], dtype=int64)]

    """

    return [basis(dimension, i, sparse) for i in range(dimension)]

def basisBra(dimension: int, state: int, sparse: bool = True) -> Matrix:
    r"""
    Creates a `bra` state :math:`\langle n| := |n\rangle^{T}` for a given dimension with 1 (unit population) at a
    given column. This function simply returns transpose of :func:`basis <quanguru.QuantumToolbox.linearAlgebra.basis>`.

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
    Matrix
        requested `bra` state

    Examples
    --------
    >>> print(basisBra(2, 0))
    (0, 0)	1

    >>> basisBra(2, 0, sparse=False)
    [[1 0]]
    """

    return basis(dimension, state, sparse).T

def zerosKet(dimension: int, sparse: bool = True) -> Matrix:
    r"""
    Creates a column matrix (ket) with all elements zero.

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    Matrix
        ket of zeros

    Examples
    --------
    >>> print(zerosKet(2))
    (0, 0)	0

    >>> zerosKet(2, sparse=False)
    [[0]
     [0]]
    """

    data = [0]
    rows = [0]
    columns = [0]
    Zeros = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return Zeros if sparse else Zeros.A

def zerosMat(dimension: int, sparse: bool = True) -> Matrix:
    r"""
    Creates a square matrix with all elements zero.

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    Matrix
        Square matrix of zeros

    Examples
    --------
    TODO
    """

    data = [0]
    rows = [0]
    columns = [0]
    Zeros = sp.csc_matrix((data, (rows, columns)), shape=(dimension, dimension))
    return Zeros if sparse else Zeros.A

def weightedSum(summands: Iterable, weights: Iterable = None) -> Any:
    r""" Weighted sum :math:`\sum_{x}w_{x}x` of given list of summands :math:`\{x\}` and weights :math:`\{w_{x}\}`.

    Parameters
    ----------
    summands : Iterable
        List of matrices
    weights : Iterable
        List of weights

    Returns
    -------
    Any
        weighted sum

    Examples
    --------
    # TODO
    """

    return sum([weight*val for weight, val in zip(weights, summands)]) if weights is not None else sum(summands)

def superPos(dimension: int, excitations: supInp, populations: bool = True, sparse: bool = True) -> Matrix:
    r"""
    Creates a superposition ket state in various ways.

    Given `excitations` is

        1. a `dictionary` : `keys = [k]` of the dictionary are the states ``basis(dimension, k)`` :math:`\forall k`,
        and the values are

            1. ``populations = True`` : `values =` :math:`[p_{k}]` are populations of the corresponding keys.
            They do not need to sum to 1. The state gets normalised, so these are relative populations.

            Output state

                :math:`|ket\rangle = \frac{1}{\sum p_{k}}\sum \sqrt{p_{k}}` ``basis(dimension, k)``

            2. ``populations = False`` : `values =` :math:`[c_{k}]` are the complex probability amplitudes. The output
            state gets normalised.

            Ouput state

                :math:`|ket\rangle = \frac{1}{\sum c_{k}^{2}}\sum c_{k}` ``basis(dimension, k)``

    2. a `list` [k] of N integers corresponding to states ``basis(dimension, k)`` :math:`\forall k` with equal weights

        Output state

            :math:`|ket\rangle = \frac{1}{\sqrt{N}}\sum` ``basis(dimension, k)``

    3. an `integer`, to create a basis state (equivalent to ``basis`` function)

    Parameters
    ----------
    dimension : int
        dimension of Hilbert space
    excitations : supInt (Union of int, list(int), dict(int:float))
        see above
    populations : bool
        If True (False) dictionary keys are the populations (complex probability amplitudes)

    Returns
    -------
    Matrix
        requested normalised `ket` state

    Examples
    --------
    >>> superPos(2, {0:0.2, 1:0.8}, sparse=False)
    [[0.4472136 ]
     [0.89442719]]

    >>> superPos(2, [0,1], sparse=False)
    [[0.70710678]
     [0.70710678]]

    >>> superPos(2, 1, sparse=False)
    [[0.]
     [1.]]
    """

    if isinstance(excitations, dict):
        sts = excitations
        if populations:
            sts = {k:np.sqrt(v) for (k, v) in sts.items()}  # noqa: E231
    elif isinstance(excitations, int):
        sts = {excitations:1}  # noqa: E231
    elif all(isinstance(item, int) for item in excitations):
        sts = {k: 1 for k in excitations}
    else:
        raise TypeError('Unsupported type for parameter excitations')

    return normalise(weightedSum([basis(dimension, excite, sparse) for excite in sts.keys()], list(sts.values())))

def densityMatrix(ket: matrixOrMatrixList, probability: Iterable[Any] = None) -> Matrix:
    r"""
    Computes the `density matrix` for both pure and mixed states.

    1. Given a pure `ket` :math:`|\psi\rangle` state

        Output state

            :math:`\rho = |\psi\rangle\langle\psi|`

    2. Given a list of kets states :math:`[|\psi_{i}\rangle]` and their associated probabilities :math:`[w_{i}]`

        Output mixed state

            :math:`\rho = \sum w_{i}|\psi_{i}\rangle\langle\psi_{i}|` from a list of kets

    Parameters
    ----------
    ket : matrixOrMatrixList
        single ket state or list of kets
    probability : floatList
        list of probabilities (0 to 1) associated with the corresponding list of kets

    Returns
    -------
    Matrix
        requested density matrix operator

    Examples
    --------
    >>> ket = basis(2, 0)
    >>> print(densityMatrix(ket))
    (0, 0)	1

    >>> ket = superPos(2, [0,1], sparse=False)
    >>> densityMatrix(ket)
    [[0.5 0.5]
     [0.5 0.5]]

    >>> ket1 = superPos(2, [0,1], sparse=False)
    >>> ket2 = basis(2, 0)
    >>> densityMatrix([ket1,ket2],[0.5, 0.5])
    [[0.75 0.5]
     [0.5 0.25]]
    """

    libool = isinstance(ket, list)
    return normalise(weightedSum([linAlOuterProd(k) for k in ket], probability)) if libool else linAlOuterProd(ket)

def completeBasisMat(dimension: Optional[int] = None, compKetBase: Optional[matrixList] = None, #pylint:disable=unsubscriptable-object
                     sparse: bool = True) -> matrixList:
    r"""
    Creates a set of `density matrices` :math:`\{|n\rangle\langle n|\}` st
    :math:`\sum_n|n\rangle\langle n| = \hat{\mathbb{I}}` for a given dimension or
    convert a `ket basis` :math:`\{|n\rangle\}` to `density matrix`.

    NOTE: This is not a complete basis for n-by-n matrices but for populations, i.e. diagonals.

    For a given basis, this keeps the sparse/array as sparse/array.

    Parameters
    ----------
    dimension : int or None
        dimension of Hilbert space (or default None if a ket basis is given)
    compKetBase : matrixList or None
        a complete ket basis (or default None if dimension is given)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    matrixList
        a list (complete basis) of `density matrices`

    :raises ValueError : raised if both complete ket basis and dimension are None (default). Dimension is used to create

    Examples
    --------
    >>> completeBasisMat(dimension=2, sparse=False)
    [array([[1, 0],
            [0, 0]], dtype=int64),
     array([[0, 0],
            [0, 1]], dtype=int64)]

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
    r"""
    Function to normalise `any` state (ket or density matrix).

    For ket states :math:`|\psi\rangle`

        :math:`\frac{1}{norm(|\psi\rangle)}|\psi\rangle`

    For density matrices :math:`\rho``

        :math:`\frac{1}{trace(\rho)}\rho`

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    state : Matrix
        state to be normalised

    Returns
    -------
    Matrix
        normalised state

    Examples
    --------
    >>> import numpy as np
    >>> nonNormalisedKet = np.sqrt(0.2)*basis(2,1) + np.sqrt(0.8)*basis(2,0)
    >>> normalise(nonNormalisedKet)
    [[0.89442719]
    [0.4472136 ]]

    >>> nonNormalisedMat = densityMatrix(nonNormalisedKet)
    >>> normalise(nonNormalisedMat)
    [[0.8 0.4]
    [0.4 0.2]]
    """

    if state.shape[0] != state.shape[1]:
        mag = 1 / linAlNorm(state)
    else:
        mag = 1 / linAlTrace(state)
    return mag * state

def compositeState(dimensions: intList, excitations: List[supInp], sparse: bool = True) -> Matrix:
    r"""
    Function to create `composite ket` states. Uses :func:`superPos <quanguru.QuantumToolbox.states.superPos>` to create
    individual states and :func:`tensorProd <quanguru.QuantumToolbox.linearAlgebra.tensorProd>` to calculate their
    tensor product.

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
    Matrix
        composite ket state

    Examples
    --------
    >>> compositeState(dimensions=[2, 2], excitations=[0,1], sparse=False)
    [[0]
     [1]
     [0]
     [0]]

    >>> compositeState(dimensions=[2, 2], excitations=[[0,1],1], sparse=False)
    [[0.        ]
     [0.70710678]
     [0.        ]
     s[0.70710678]]

    >>> compositeState(dimensions=[2, 2], excitations=[0,{0:0.2, 1:0.8}], sparse=False)
    [[0.4472136 ]
     [0.89442719]
     [0.        ]
     [0.        ]]
    """

    st = linAlTensorProd(*[superPos(dim, exs) for (dim, exs) in zip(dimensions, excitations)])
    return st.A if ( (not sparse) and (isinstance(st, spmatrix))) else st

def mat2Vec(denMat: Matrix) -> Matrix: # pylint: disable=invalid-name
    r"""
    Converts `density matrix` into `density vector` (used in super-operator representation).

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    denMat : Matrix
        density matrix to be converted

    Returns
    -------
    Matrix
        density vector

    Examples
    --------
    >>> denMat = densityMatrix(ket=basis(dimension=2, state=1, sparse=True))
    >>> mat2Vec(denMat=denMat).A
    [[0]
     [0]
     [0]
     [1]]
    """

    return denMat.T.reshape(np.prod(np.shape(denMat)), 1)

def vec2Mat(vec: Matrix) -> Matrix: # pylint: disable=invalid-name
    r"""
    Converts `density vector` into `density matrix`.

    Keeps the sparse/array as sparse/array

    Parameters
    ----------
    vec : Matrix
        density vector to be converted

    Parameters
    ----------
    Matrix
        density matrix

    Examples
    --------
    >>> denMat = densityMatrix(ket=basis(dimension=2, state=1, sparse=True))
    >>> print(denMat.A)
    [[0 0]
     [0 1]]

    >>> denVec = mat2Vec(denMat=denMat)
    >>> vec2mat(vec=denVec).A
    [[0 0]
     [0 1]]
    """

    a = vec.shape
    n = int(np.sqrt(a[0]))
    mat = vec.reshape((n, n)).T
    return mat

def BellStates(bs: str = 'Phi+', sparse: bool = True) -> Matrix:
    r"""
    Creates a Bell state
    :math:`\begin{cases} |\Phi^{+}\rangle := \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)
    \\ |\Phi^{+}\rangle := \frac{1}{\sqrt{2}}(|00\rangle - |11\rangle)
    \\ |\Psi^{-}\rangle := \frac{1}{\sqrt{2}}(|01\rangle + |10\rangle)
    \\ |\Psi^{+}\rangle := \frac{1}{\sqrt{2}}(|01\rangle - |10\rangle)
    \\ \end{cases}`, where :math:`|ab\rangle := |a\rangle\otimes|b\rangle`.

    Parameters
    ----------
    bs : str, optional
        String for different Bell states, by default 'Phi+'. Options are
        ['Phi+' or '00', 'Phi-' or '01', 'Psi+' or '10', 'Psi-' or '11']
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Bell state

    Examples
    --------
    >>> BellStates('Phi+').A
    array([[0.70710678],
           [0.        ],
           [0.        ],
           [0.70710678]])
    >>> BellStates('Phi-').A
    array([[ 0.70710678],
           [ 0.        ],
           [ 0.        ],
           [-0.70710678]])
    >>> BellStates('Psi+').A
    array([[0.        ],
           [0.70710678],
           [0.70710678],
           [0.        ]])
    >>> BellStates('Psi-').A
    array([[ 0.        ],
           [ 0.70710678],
           [-0.70710678],
           [ 0.        ]]
    """

    BellState = 0
    if bs in ['Phi+', '00']:
        BellState = (1/np.sqrt(2))*np.array([[1], [0], [0], [1]])
    elif bs in ['Phi-', '01']:
        BellState = (1/np.sqrt(2))*np.array([[1], [0], [0], [-1]])
    elif bs in ['Psi+', '10']:
        BellState = (1/np.sqrt(2))*np.array([[0], [1], [1], [0]])
    elif bs in ['Psi-', '11']:
        BellState = (1/np.sqrt(2))*np.array([[0], [1], [-1], [0]])
    return sp.csr_matrix(BellState) if sparse else BellState

def purity(denMat: Matrix) -> float:
    r"""
    Calculates the purity :math:`Tr(\rho^{2})` of a given density matrix :math:`\rho`

    Parameters
    ----------
    denMat : Matrix
        Density matrix

    Returns
    -------
    float
        the purity of given density matrix.
    """
    return linAlTrace(denMat@denMat)
