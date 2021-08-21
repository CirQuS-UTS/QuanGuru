r"""
    Contains functions to calculate quasi-probability distributions (adapted from qutip).

    .. currentmodule:: quanguru.QuantumToolbox.quasiProbabilities

    Functions
    ---------

    .. autosummary::
        Wigner
        HusimiQ
        _qfuncPure

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `Wigner`                  |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `HusimiQ`                 |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `_qfuncPure`              |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from numpy import ndarray # type: ignore
import numpy as np # type: ignore
from numpy import (zeros, array, arange, exp, real, conj, pi,
                   copy, meshgrid, size, polyval, fliplr, conjugate) # type: ignore
from scipy.special import factorial # type: ignore
import scipy.linalg as la # type: ignore
#from quanguru.QuantumToolbox.states as densityMatrix

from .states import densityMatrix
from .customTypes import Matrix, ndOrList


# do not delete these
# from typing import Union, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)
# ndOrList = Union[ndarray, list]                     # Type from union of ndarray and list

def Wigner(rho: Matrix, vec: ndOrList, g: float = np.sqrt(2)) -> ndarray:
    r"""
    An iterative method to evaluate the Wigner functions for the states :math:`|m \rangle \langle n|` and use them in
    a weighted sum to calculate Wigner function of any arbitrary state.

    The Wigner function is calculated as
    :math:`W = \sum_{mn} \rho_{mn} W_{mn}` where :math:`W_{mn}` is the Wigner
    function for the density matrix :math:`|m \rangle \langle n|`.

    In this implementation, for each row m, Wlist contains the Wigner functions
    Wlist = :math:`[0, ..., W_{mm} , ..., W_{mN} ]`. As soon as one :math:`W_{mn}` Wigner function is
    calculated, the corresponding contribution is added to the total Wigner
    function, weighted by the corresponding element in the density matrix
    :math:`\\rho_{mn}`.

    Parameters
    ----------
    rho : Matrix
        Density matrix or ket state.
    vec : ndOrList
        An array (or list) to define the (coarse-grained) Phase space.
        This creates a square grid of the phase space.
    g : float
        Scaling factor for `a = 0.5 * g * (x + iy)`, default `g = sqrt(2)`.

    Returns
    -------
    ndarray
        Values representing the Wigner-function calculated over the specified range [vec, vec].

    Examples
    --------
    # TODO
    """

    if not isinstance(rho, np.ndarray):
        rho = rho.toarray()

    if rho.shape[0] != rho.shape[1]:
        rho = densityMatrix(rho)

    M = np.prod(rho.shape[0])
    X, Y = meshgrid(vec, vec)
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
        W += real(rho[m, m] * Wlist[m])
        for n in range(m + 1, M):
            temp2 = (2 * A * Wlist[n - 1] - np.sqrt(m) * temp) / np.sqrt(n)
            temp = copy(Wlist[n])
            Wlist[n] = temp2
            W += 2 * real(rho[m, n] * Wlist[n])
    return W * g ** 2


def HusimiQ(state: Matrix, vec: ndOrList, g: float = np.sqrt(2)) -> ndarray:
    r"""
    Q-function of a given state vector or density matrix at points `vec + i * vec`

    Parameters
    ----------
    rho : Matrix
        density matrix or ket state
    vec : ndOrList
        An array (or list) to define the (coarse-grained) Phase space.
        This creates a square grid of the phase space.
    g : float
        Scaling factor for `a = 0.5 * g * (x + iy)`, default `g = sqrt(2)`.

    Returns
    --------
    array
        Values representing the Q-function calculated over the specified range [vec, vec].

    Examples
    --------
    # TODO
    """

    X, Y = meshgrid(vec, vec)
    amat = 0.5 * g * (X + Y * 1j)
    qmat = zeros(size(amat))

    if not isinstance(state, np.ndarray):
        state = state.toarray()

    if state.shape[0] != state.shape[1]:
        qmat = _qfuncPure(state, amat)
    else:
        d, v = la.eig(state.full())
        # d[i]   = eigenvalue i
        # v[:,i] = eigenvector i

        qmat = zeros(np.shape(amat))
        for k in arange(0, len(d)):
            qmat1 = _qfuncPure(v[:, k], amat)
            qmat += real(d[k] * qmat1)
    qmat = 0.25 * qmat * g ** 2
    return qmat


def _qfuncPure(psi: Matrix, alphaMat: ndarray) -> ndarray:
    r"""
    Calculates the Q-function for a pure state.

    Parameters
    ----------
    psi : Matrix
        a pure state
    vec : ndOrList
        an array (or list) to define the (coarse-grained) Phase space.
        This creates a square grid of the phase space.
    g : float
        Scaling factor for `a = 0.5 * g * (x + iy)`, default `g = sqrt(2)`.

    Returns
    --------
    array
        Values representing the Q-function calculated over the specified range [vec, vec].

    Examples
    --------
    # TODO
    """

    n = np.prod(psi.shape)
    psi = psi.T

    qmat = abs(polyval(fliplr([psi / np.sqrt(factorial(arange(n)))])[0], conjugate(alphaMat))) ** 2

    return real(qmat) * exp(-abs(alphaMat) ** 2) / pi
