"""
    Module for some basic linear algebra.

    - trace ?
"""

from numpy import ndarray
import numpy as np # type: ignore
import scipy.sparse as sp # type: ignore

from .customTypes import Matrix, ndOrListInt #pylint: disable=relative-beyond-top-level


def hc(matrix: Matrix) -> Matrix:
    """
    Hermitian conjugate of a matrix

    Parameters
    ----------
    matrix : Matrix
        a matrix

    Returns
    -------
    Matrix
        Hermitian conjugate of the given matrix
    """
    return matrix.T.conj()


def innerProd(ket1: Matrix, ket2: Matrix = None) -> float:
    """
    Computes the inner product (bra(ket2) @ ket1) of a `ket` vector with itself or with another `ket`.

    Parameters
    ----------
    ket1 : Matrix
        1st ket state
    ket2 : Matrix
        2nd ket state

    Returns
    -------
    :return: float
        inner product

    Examples
    --------
    TODO
    """

    if ket2 is None:
        ket2 = ket1
    overlap = (hc(ket2) @ ket1).diagonal().sum()
    return overlap


def norm(ket: Matrix) -> float:
    """
    Norm of a ket state

    Parameters
    ----------
    ket : Matrix
        a ket state

    Returns
    -------
    float
        norm of the state
    """
    return np.sqrt(innerProd(ket))


def outerProd(ket1: Matrix, ket2: Matrix = None) -> Matrix:
    """
    Computes the outer product (ket @ bra) of a `ket` vector with itself or with another `ket`.

    Parameters
    ----------
    ket1 : Matrix
        1st ket state
    ket2 : Matrix
        2nd ket state

    Returns
    -------
    :return: Matrix
        operator in square matrix form resulting from the computed outer product

    Examples
    --------
    >>> ket = basis(2, 0)
    >>> mat = outerProd(ket)
    (0, 0)	1

    >>> ket = superPos(2, [0,1], sparse=False)
    >>> mat = outerProd(ket)
    [[0.5 0.5]
     [0.5 0.5]]

    >>> ket1 = superPos(2, [0,1], sparse=False)
    >>> ket2 = basis(2, 0)
    >>> mat = outerProd(ket1, ket2)
    [[0.70710678 0.]
     [0.70710678 0.]]
    """

    if ket2 is None:
        ket2 = ket1
    return ket1 @ hc(ket2)


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
    return sp.kron(totalProd, tensorProd(*args[1:]), format='csc') if len(args) > 1 else totalProd


def trace(matrix: Matrix) -> float:
    """
    Trace of a matrix.

    Parameters
    ----------
    matrix : Matrix
        a matrix

    Returns
    -------
    float
        trace of the given matrix
    """
    return matrix.diagonal().sum()


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
