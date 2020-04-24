"""
    Module of functions to calculate quasi-probablity distributions (adapted from qutip).

    Methods
    -------
    :Wigner : An iterative method to evaluate the Wigner functions for the Fock state :math:`|m><n|`.
    :HusimiQ : Q-function of a given state vector or density matrix at points `xvec + i * yvec`.
    :_qfunc_pure : Calculate the Q-function for a pure state.
"""

from numpy import ndarray
import numpy as np
from numpy import (zeros, array, arange, exp, real, conj, pi, copy, meshgrid, size, polyval, fliplr, conjugate)
from scipy.special import factorial
import scipy.linalg as la
#from qTools.QuantumToolbox.states as densityMatrix

from .states import densityMatrix
from .customTypes import Matrix, ndOrList


# from typing import Union, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)
# ndOrList = Union[ndarray, list]                     # Type from union of ndarray and list

def Wigner(rho: Matrix, xvec: ndOrList, g: float = np.sqrt(2)) -> ndarray:
    """
    An iterative method to evaluate the Wigner functions for the Fock state :math:`|m><n|`

    The Wigner function is calculated as
    :math:`W = \\sum_{mn} \\rho_{mn} W_{mn}` where :math:`W_{mn}` is the Wigner
    function for the density matrix :math:`|m><n|`.

    In this implementation, for each row m, Wlist contains the Wigner functions
    Wlist = [0, ..., W_mm, ..., W_mN]. As soon as one W_mn Wigner function is
    calculated, the corresponding contribution is added to the total Wigner
    function, weighted by the corresponding element in the density matrix
    :math:`rho_{mn}`.

    Parameters
    ----------
    :param `rho` : density matrix or ket state
    :param `xvec` : multi-dimensional array for the (coarse-grained) Phase space
    """

    if not isinstance(rho, np.ndarray):
        rho = rho.toarray()

    if rho.shape[0] != rho.shape[1]:
        rho = densityMatrix(rho)

    M = np.prod(rho.shape[0])
    X, Y = meshgrid(xvec, xvec)
    A = 0.5 * g * (X + 1.0j * Y)
    Wlist = array([zeros(np.shape(A), dtype=complex) for k in range(M)])
    Wlist[0] = exp(-2.0 * abs(A) ** 2) / pi
    W = real(rho[0, 0]) * real(Wlist[0])
    for n in range(1, M):
        Wlist[n] = (2.0 * A * Wlist[n - 1]) / np.sqrt(n)
        W += 2 * real(rho[0, n] * Wlist[n])
    for m in range(1, M):
        temp = copy(Wlist[m])
        Wlist[m] = (2 * conj(A) * temp - np.sqrt(m) * Wlist[m - 1]) / np.sqrt(m)
        # Wlist[m] = Wigner function for |m><m|
        W += real(rho[m, m] * Wlist[m])
        for n in range(m + 1, M):
            temp2 = (2 * A * Wlist[n - 1] - np.sqrt(m) * temp) / np.sqrt(n)
            temp = copy(Wlist[n])
            Wlist[n] = temp2
            # Wlist[n] = Wigner function for |m><n|
            W += 2 * real(rho[m, n] * Wlist[n])
    return W * g ** 2


def HusimiQ(state: Matrix, xvec: ndOrList, g: float = np.sqrt(2)) -> ndarray:
    """
    Q-function of a given state vector or density matrix at points `xvec + i * yvec`

    Parameters
    ----------
    state : qobj
        A state vector or density matrix.

    xvec : array_like
        x-coordinates at which to calculate the Wigner function.

    yvec : array_like
        y-coordinates at which to calculate the Wigner function.

    g : float
        Scaling factor for `a = 0.5 * g * (x + iy)`, default `g = sqrt(2)`.

    Returns
    --------
    Q : array
        Values representing the Q-function calculated over the specified range
        [xvec,yvec].

    """

    X, Y = meshgrid(xvec, xvec)
    amat = 0.5 * g * (X + Y * 1j)
    qmat = zeros(size(amat))

    if not isinstance(state, np.ndarray):
        state = state.toarray()

    if state.shape[0] != state.shape[1]:
        qmat = _qfunc_pure(state, amat)
    else:
        d, v = la.eig(state.full())
        # d[i]   = eigenvalue i
        # v[:,i] = eigenvector i

        qmat = zeros(np.shape(amat))
        for k in arange(0, len(d)):
            qmat1 = _qfunc_pure(v[:, k], amat)
            qmat += real(d[k] * qmat1)
    qmat = 0.25 * qmat * g ** 2
    return qmat


def _qfunc_pure(psi: Matrix, alpha_mat: ndarray) -> ndarray:
    """
    Calculate the Q-function for a pure state
    """

    n = np.prod(psi.shape)
    psi = psi.T

    qmat = abs(polyval(fliplr([psi / np.sqrt(factorial(arange(n)))])[0], conjugate(alpha_mat))) ** 2

    return real(qmat) * exp(-abs(alpha_mat) ** 2) / pi
