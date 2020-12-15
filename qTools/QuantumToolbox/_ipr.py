r"""
    Functions to calculate delocalisation measure (Inverse participation ratio) in for various cases.

"""
from numpy import ndarray # type: ignore

import numpy as np # type: ignore
from scipy.sparse import spmatrix # type: ignore

from .functions import fidelityPure

from .customTypes import Matrix, floatList, matrixList


def iprKet(basis: matrixList, ket: Matrix) -> float:
    r"""
    Calculate inverse participation ratio (a delocalisation measure) of a `ket` in a given basis.

    Parameters
    ----------
    ket : matrixList
        a ket state
    basis : Matrix
        a complete basis

    Returns
    -------
    float
        inverse participation ratio

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> ipr0 = iprKet(completeBasis, state0)
    1.1245136186770428

    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> ipr1 = iprKet(completeBasis, state1)
    2.000000000000001

    >>> state2 = qStates.basis(2,1)
    >>> ipr2 = iprKet(completeBasis, state2)
    1.0
    """

    npc = 0.0
    for basKet in basis:
        fid = fidelityPure(basKet, ket)
        npc += (fid**2)
    return 1/npc


def iprKetNB(ket: Matrix) -> float:
    r"""
    Calculates the inverse participation ratio (a delocalisation measure) of a ket
    by assuming that the basis is of the free Hamiltonian.

    Parameters
    ----------
    ket : Matrix
        a ket state

    Returns
    -------
    float
        inverse participation ratio

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> ipr0 = iprKetNB(state0)
    1.1245136186770428

    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> ipr1 = iprKetNB(state1)
    2.000000000000001

    >>> state2 = qStates.basis(2,1)
    >>> ipr2 = iprKetNB(state2)
    1.0

    >>> state3 = qStates.basis(2,0)
    >>> ipr3 = iprKetNB(state3)
    1.0
    """

    # TODO Find a way around this
    if isinstance(ket, spmatrix):
        ket = ket.A
    return 1/np.sum(np.power((np.abs(ket.flatten())), 4))


def iprKetNBmat(kets: ndarray) -> floatList:
    r"""
    Calculates the inverse participation ratio (a delocalisation measure) of `a matrix of ket states as the column`.

    For example the eigenstates obtained from eigenvalue calculations of numpy or scipy are this form.
    TODO use if you know what you are doing.
    This assumes the basis is of the free Hamiltonian.

    Parameters
    ----------
    ket : ndarray
        a density matrix

    Returns
    -------
    floatList
        a `list` of inverse participation ratios

    Examples
    --------
    >>> import qTools.QuantumToolbox.operators as qOperators
    >>> ham = qOperators.sigmaz()
    >>> eigValsHam, eigVecsHams = np.linalg.eig(ham.A)
    >>> iprHam = iprKetNBmat(eigVecsHams)
    [1.0, 1.0]

    >>> unitary = sp.sparse.linalg.expm(ham)
    >>> eigValsUni, eigVecsUni = np.linalg.eig(unitary.A)
    >>> iprUni = iprKetNBmat(eigVecsUni)
    [1.0, 1.0]
    """

    IPRatio = []
    for ind in range(len(kets)):
        IPRatio.append(iprKetNB(kets[:, ind]))
    return IPRatio


def iprPureDenMat(basis: matrixList, denMat: Matrix) -> float:
    r"""
    Calculates the inverse participation ratio (a delocalisation measure) of a `density matrix` in a given `basis`.

    Parameters
    ----------
    denMat : matrixList
        a density matrix
    basis : Matrix
        a complete basis

    Returns
    -------
    float
        inverse participation ratio

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> completeBasis = qStates.completeBasisMat(dimension=2)
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> denMat0 = qStates.densityMatrix(state0)
    >>> ipr0 = iprPureDenMat(completeBasis, denMat0)
    1.1245136186770428

    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> denMat1 = qStates.densityMatrix(state1)
    >>> ipr1 = iprPureDenMat(completeBasis, denMat1)
    2.000000000000001

    >>> state2 = qStates.basis(2,1)
    >>> denMat2 = qStates.densityMatrix(state2)
    >>> ipr2 = iprPureDenMat(completeBasis, denMat2)
    1.0
    """

    npc = 0.0
    for basKet in basis:
        fid = fidelityPure(basKet, denMat)
        npc += (fid**2)
    return 1/npc
