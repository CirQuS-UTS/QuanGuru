"""Copied from Qutip"""

import numpy as np
import scipy.sparse as sp
from scipy import (zeros, array, arange, exp, real, conj, pi,copy, sqrt, meshgrid, size, polyval, fliplr, conjugate)
from scipy.special import factorial
import scipy.linalg as la
import QuantumToolbox.states as states

def Wigner(xvec, rho, g=np.sqrt(2)):
    """
        Using an iterative method to evaluate the wigner functions for the Fock
        state :math:`|m><n|`.

        The Wigner function is calculated as
        :math:`W = \sum_{mn} \\rho_{mn} W_{mn}` where :math:`W_{mn}` is the Wigner
        function for the density matrix :math:`|m><n|`.

        In this implementation, for each row m, Wlist contains the Wigner functions
        Wlist = [0, ..., W_mm, ..., W_mN]. As soon as one W_mn Wigner function is
        calculated, the corresponding contribution is added to the total Wigner
        function, weighted by the corresponding element in the density matrix
        :math:`rho_{mn}`.
        """

    if not isinstance(rho, np.ndarray):
        rho = rho.toarray()

    if rho.shape[0] != rho.shape[1]:
        rho = states.densityMatrix(rho)

    M = np.prod(rho.shape[0])
    X, Y = meshgrid(xvec, xvec)
    A = 0.5 * g * (X + 1.0j * Y)
    Wlist = array([zeros(np.shape(A), dtype=complex) for k in range(M)])
    Wlist[0] = exp(-2.0 * abs(A) ** 2) / pi
    W = real(rho[0, 0]) * real(Wlist[0])
    for n in range(1, M):
        Wlist[n] = (2.0 * A * Wlist[n - 1]) / sqrt(n)
        W += 2 * real(rho[0, n] * Wlist[n])
    for m in range(1, M):
        temp = copy(Wlist[m])
        Wlist[m] = (2 * conj(A) * temp - sqrt(m) * Wlist[m - 1]) / sqrt(m)
        # Wlist[m] = Wigner function for |m><m|
        W += real(rho[m, m] * Wlist[m])
        for n in range(m + 1, M):
            temp2 = (2 * A * Wlist[n - 1] - sqrt(m) * temp) / sqrt(n)
            temp = copy(Wlist[n])
            Wlist[n] = temp2
            # Wlist[n] = Wigner function for |m><n|
            W += 2 * real(rho[m, n] * Wlist[n])
    return W * g ** 2

def HusimiQ(state, xvec, g=sqrt(2)):
    """Q-function of a given state vector or density matrix
    at points `xvec + i * yvec`.

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

    if not isinstance(state,np.ndarray):
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

def _qfunc_pure(psi, alpha_mat):
    """
    Calculate the Q-function for a pure state.
    """
    n = np.prod(psi.shape)
    psi = psi.T

    qmat = abs(polyval(fliplr([psi / sqrt(factorial(arange(n)))])[0],conjugate(alpha_mat))) ** 2

    return real(qmat) * exp(-abs(alpha_mat) ** 2) / pi