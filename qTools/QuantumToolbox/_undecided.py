from numpy import ndarray # type: ignore

from .linearAlgebra import hc

from .customTypes import Matrix, floatList


def expectationColArr(operator: Matrix, states: ndarray) -> floatList:
    """
    Calculates the expectation values of an `operator` for a list/matrix of `ket (column) states`.
     by matrix multiplication.

    The `list` here is effectively a matrix whose columns are `ket` states for which we want the expectation values.
    For example, the eigenstates obtained from eigenvalue calculations of numpy or scipy are this form.
    TODO introduced to be used with eigenvectors, needs to be tested for non-mutually orthogonal states.
    So, it relies on states being orthonormal, if not there will be off-diagonal elements in the resultant matrix,
    but still the diagonal elements are the expectation values, meaning it should work!

    Parameters
    ----------
    operator : Matrix
        matrix of a Hermitian operator
    states : ndarray
        ket states as the columns in the input matrix

    Returns
    -------
    floatList
        `list` of expectation values of the `operator` for a matrix of `ket` states

    Examples
    --------
    >>> import qTools.QuantumToolbox.operators as qOperators
    >>> ham = qOperators.sigmaz(sparse=False)
    >>> eigVals, eigVecs = np.linalg.eig(ham)

    >>> sz = qOperators.sigmaz()
    >>> expectZ = expectationColArr(sz, eigVecs)
    [ 1. -1.]

    >>> sx = qOperators.sigmax()
    >>> expectX = expectationColArr(sx, eigVecs)
    [0. 0.]
    """

    expMat = hc(states) @ operator @ states
    return expMat.diagonal()
