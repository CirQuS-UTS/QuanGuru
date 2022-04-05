r"""
    Contains some basic linear algebra methods for scipy.sparse and np.ndarray types.

    .. currentmodule:: quanguru.QuantumToolbox.linearAlgebra

    Functions
    ---------

    .. autosummary::
        hc
        innerProd
        norm
        outerProd
        tensorProd
        trace
        partialTrace
        _matMulInputs
        _matPower

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `hc`                      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `innerProd`               |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `norm`                    |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |c|        |w| |w| |x|
       `outerProd`               |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `tensorProd`              |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `trace`                   |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `partialTrace`            |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `_matMulInputs`           |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `_matPower`               |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |c|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from numpy import ndarray # type: ignore
import numpy as np # type: ignore
import scipy.sparse as sp # type: ignore

from .customTypes import Matrix, ndOrListInt, matrixOrMatrixList # pylint: disable=relative-beyond-top-level


def hc(matrix: Matrix) -> Matrix:
    r"""
    Hermitian conjugate :math:`M^{\dagger} := (M^{*})^{T}` of a matrix :math:`M`, where * is complex conjugation, and
    T is transposition.

    Parameters
    ----------
    matrix : Matrix
        a matrix

    Returns
    -------
    Matrix
        Hermitian conjugate of the given matrix

    Examples
    --------
    >>> operEx1 = np.array([[1+1j, 2+2j],
    >>>                     [3+3j, 4+4j]])
    >>> hc(operEx1)
    array([[1.-1.j, 3.-3.j],
           [2.-2.j, 4.-4.j]])

    >>> operEx2 = np.array([[0, 1],
    >>>                    [1, 0]])
    >>> hc(operEx2)
    array([[0, 1],
           [1, 0]])

    >>> operEx3 = np.array([[1, 0, 0],
    >>>                     [0, 1, 0],
    >>>                     [1j, 0, 1]])
    >>> hc(operEx3)
    array([[1, 0, -1j],
           [0, 1, 0],
           [0, 0, 1]])

    """

    return matrix.T.conj()

def innerProd(ket1: Matrix, ket2: Matrix = None) -> float:
    r"""
    Computes the inner product :math:`\langle ket2 | ket1 \rangle` of a ket vector with itself or with another,
    where :math:`\langle ket2| := |ket2 \rangle^{\dagger}`.

    Parameters
    ----------
    ket1 : Matrix
        1st ket state
    ket2 : Matrix
        2nd ket state

    Returns
    -------
    float
        inner product

    Examples
    --------
    >>> cMatEx1 = np.array([[1],
    >>>                     [0]])
    >>> innerProd(cMatEx1)
    1

    >>> cMatEx2 = np.array([[0],
    >>>                     [1]])
    >>> innerProd(cMatEx2)
    1

    >>> cMatEx3 = (1/5)*np.array([[3],
    >>>                           [4j]])
    >>> innerProd(cMatEx3)
    1

    >>> cMatEx4 = np.array([[1],
    >>>                     [1j]])
    >>> innerProd(cMatEx4)
    2

    """

    if ket2 is None:
        ket2 = ket1
    overlap = (hc(ket2) @ ket1).diagonal().sum()
    return overlap

def norm(ket: Matrix) -> float:
    r"""
    Norm :math:`\sqrt{\langle ket | ket \rangle}` of a ket state :math:`|ket \rangle`,
    where :math:`\langle ket| := |ket \rangle^{\dagger}`.
    This function simply returns the square root of :func:`innerProd <quanguru.QuantumToolbox.linearAlgebra.innerProd>`

    Parameters
    ----------
    ket : Matrix
        a ket state

    Returns
    -------
    float
        norm of the state

    Examples
    --------
    # TODO
    """

    return np.sqrt(innerProd(ket))

def outerProd(ket1: Matrix, ket2: Matrix = None) -> Matrix:
    r"""
    Computes the outer product :math:`|ket2 \rangle\langle ket1|` of a ket vector with itself or with another,
    where :math:`\langle ket2| := |ket2 \rangle^{\dagger}`.

    Parameters
    ----------
    ket1 : Matrix
        1st ket state
    ket2 : Matrix
        2nd ket state

    Returns
    -------
    Matrix
        operator in square matrix form resulting from the computed outer product

    Examples
    --------
    >>> cMatEx1 = np.array([[1],
    >>>                     [0]])
    >>> outerProd(cMatEx1)
    array([[1, 0],
           [0, 0]])

    >>> cMatEx2 = np.array([[0],
    >>>                     [1]])
    >>> outerProd(cMatEx2)
    array([[0, 0],
           [0, 1]])

    >>> cMatEx3 = (1/5)*np.array([[3],
    >>>                           [4j]])
    >>> outerProd(cMatEx3)
    array([[0.36+0.j  , 0.  -0.48j],
           [0.  +0.48j, 0.64+0.j  ]])

    >>> cMatEx4 = np.array([[1],
    >>>                     [1j]])
    >>> outerProd(cMatEx4)
    array([[1+0.j , 0. -1j],
           [0. +1j, 1+0.j ]])


    """

    if ket2 is None:
        ket2 = ket1
    return ket1 @ hc(ket2)

def tensorProd(*args: Matrix) -> Matrix:
    r"""
    Function to calculate tensor product :math:`\otimes_{i} M_{i}` of given (any number i of)
    states (:math:`\{M_{i}\}` in the given order).

    Parameters
    ----------
    *args : Matrix
        state matrices (arbitrary number of them)

    Returns
    -------
    Matrix
        tensor product of given states (in the given order)

    Examples
    --------
    >>> cMatEx1 = np.array([[1],
    >>>                     [0]])
    >>> cMatEx2 = np.array([[0],
    >>>                     [1]])
    >>> tensorProd(cMatEx1, cMatEx2)
    array([[0],
           [1],
           [0],
           [0]], dtype=int64)
    >>> tensorProd(cMatEx2, cMatEx1)
    array([[0],
           [0],
           [1],
           [0]], dtype=int64)

    >>> operEx1 = np.array([[0, 1],
    >>>                    [1, 0]])
    >>> operEx2 = np.array([[1, 0, 0],
    >>>                     [0, 1, 0],
    >>>                     [1j, 0, 1]])
    >>> tensorProd(operEx1, operEx2)
    array([[0, 0, 0, 1, 0, 0],
           [0, 0, 0, 0, 1, 0],
           [0, 0, 0, 0, 0, 1],
           [1, 0, 0, 0, 0, 0],
           [0, 1, 0, 0, 0, 0],
           [0, 0, 1, 0, 0, 0]], dtype=int64)
    >>> tensorProd(operEx2, operEx1)
    array([[0, 1, 0, 0, 0, 0],
           [1, 0, 0, 0, 0, 0],
           [0, 0, 0, 1, 0, 0],
           [0, 0, 1, 0, 0, 0],
           [0, 0, 0, 0, 0, 1],
           [0, 0, 0, 0, 1, 0]], dtype=int64)
    """

    totalProd = args[0]
    if isinstance(totalProd, int):
        totalProd = sp.identity(totalProd, format="csc")
    return sp.kron(totalProd, tensorProd(*args[1:]), format='csc') if len(args) > 1 else totalProd

def trace(matrix: Matrix) -> float:
    r"""
    Trace :math:`Tr(M) := \sum_{i} M_{ii}` of a matrix `M`.

    Parameters
    ----------
    matrix : Matrix
        a matrix

    Returns
    -------
    float
        trace of the given matrix

    Examples
    --------
    >>> cMatEx1 = np.array([[1],
    >>>                     [0]])
    >>> trace(outerProd(cMatEx1))
    1

    >>> cMatEx2 = np.array([[0],
    >>>                     [1]])
    >>> trace(outerProd(cMatEx2))
    1

    """

    return matrix.diagonal().sum()

def partialTrace(keep: ndOrListInt, dims: ndOrListInt, state: Matrix) -> ndarray:
    r"""
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
    Matrix
        Traced matrix

    Examples
    --------
    >>> cMatEx1 = np.array([[1],
    >>>                     [0]])
    >>> cMatEx2 = np.array([[0],
    >>>                     [1]])
    >>> partialTrace([0], [2, 2], outerProd(tensorProd(cMatEx1, cMatEx2)))
    array([[1, 0],
           [0, 0]], dtype=int64)
    >>> partialTrace([1], [2, 2], outerProd(tensorProd(cMatEx1, cMatEx2)))
    array([[0, 0],
           [0, 1]], dtype=int64)
    >>> partialTrace([0], [2, 2], outerProd(tensorProd(cMatEx2, cMatEx1)))
    array([[0, 0],
           [0, 1]], dtype=int64)
    >>> partialTrace([1], [2, 2], outerProd(tensorProd(cMatEx2, cMatEx1)))
    array([[1, 0],
           [0, 0]], dtype=int64)
    """

    if not isinstance(state, np.ndarray):
        state = state.toarray()

    rho = state
    if rho.shape[0] != rho.shape[1]:
        rho = (rho @ hc(rho))

    keep = np.asarray(keep)
    dims = np.asarray(dims)
    Ndim = dims.size
    Nkeep = np.prod(dims[keep])

    idx1 = list(range(Ndim))
    idx2 = [Ndim+i if i in keep else i for i in range(Ndim)]
    rhoA = rho.reshape(np.tile(dims, 2))
    rhoA = np.einsum(rhoA, idx1+idx2, optimize=False)
    return rhoA.reshape(Nkeep, Nkeep)

def _matMulInputs(*args: matrixOrMatrixList) -> Matrix:
    r"""
    Calculates the matrix multiplication of the given arbitrary number of inputs in the given order.
    It does not check the correctness of the shapes until the matrix multiplication operator (@) itself gives an error.
    """
    totalMul = args[0]
    return (totalMul @ _matMulInputs(*args[1:])) if len(args) > 1 else totalMul

def _matPower(matrix: Matrix, power: int) -> Matrix:
    r"""
    A recursive function to raise the given matrix to a power,
    ie for given matrix :math:`M` and power :math:`n`,
    this returns :math:`\overbrace{M @ M @ \cdots @ M}^{n times}`,
    where :math:`@` is the matrix multiplication.

    Parameters
    ----------
    matrix : Matrix
        The matrix to raise to a power
    power : int
        Power to raise

    Returns
    -------
    Matrix
        Given matrix raised to given power

    Examples
    --------
    """
    assert power > 0, "power has to be larger than 0"
    matPow = matrix
    return (matPow @ _matPower(matrix, power-1)) if power > 1 else matPow
