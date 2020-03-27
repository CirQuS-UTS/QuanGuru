"""
Functions to calculate expectations, fidelities, entorpy etc. from quantum states

The reason for having several functions for the same task is to improve performance
For example, an if statement can be avioded using ``expectationMat/expectationKet`` for
``density matrices/ket states``, or
``expectationKetList/expectationMatList`` is suitable in ``multi-processing`` of list of time-series of states
"""
import scipy as np
from typing import Union
import scipy.linalg as lina
from numpy import ndarray
from scipy.sparse import spmatrix

# TODO a possible improvement is to create decorator for similar functions to get function reference as input.
# Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.

# Functions for expectation value
def expectation(operator: Union[spmatrix, ndarray], state: Union[spmatrix, ndarray]) -> float:
    """
    Function to calculate the expectation value of an `operator` for a given `state`

    State can either be a `ket` or ``density matrix``.
    Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.
    State and operator can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param `operator` : matrix of a Hermitian operator
    :param `state` : a quantum state

    Returns
    -------
    :return: expectation value of the `operator` for the `state`

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    if state.shape[0] != state.shape[1]:
        state = state @ (state.conj().T)
    return expectationMat(operator, state)

def expectationMat(operator: Union[spmatrix, ndarray], denMat: Union[spmatrix, ndarray]) -> float:
    """
    Calculates the expectation value of an `operator` for a given ``density matrix``

    Works with both sparse and array.
    Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.
    State and operator can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param `operator` : matrix of a Hermitian operator
    :param `denMat` : density matrix

    Returns
    -------  
    :return: expectation value of the `operator` for the ``density matrix``

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    expc = ((operator @ denMat).diagonal()).sum()
    return np.real(expc)

def expectationKet(operator: Union[spmatrix, ndarray], ket: Union[spmatrix, ndarray]) -> float:
    """
    Calculates the expectation value of an `operator` for a given `ket`

    Calculates the density matrix and calls the expectationMat.
    Computationally the same as using (bra @ operator @ ket).
    Works with both sparse and array.
    Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.

    Parameters
    ----------
    :param `operator` : matrix of a Hermitian operator
    :param `ket` : ket state

    Returns
    -------
    :return: expectation value of the `operator` for the `ket` state

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    denMat = ket @ (ket.conj().T)
    return expectationMat(operator, denMat)

def expectationKetList(operator: Union[spmatrix, ndarray], kets: Union[list, ndarray]) -> list:
    """
    Calculates the expectation value of an `operator` for a given list of `ket` states

    Simply calls the `expectationKet` in a loop.
    This function exist for easy use in multi-processing.

    Parameters
    ----------
    :param `operator`: matrix of a Hermitian operator
    :param `kets` : list of ket states

    Returns
    -------
    :return: `list` of expectation values of the `operator` for the list of `ket` states

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    expectations = []
    for ket in kets:
        expectations.append(expectationKet(operator, ket))
    return expectations

def expectationMatList(operator: Union[spmatrix, ndarray], denMats: Union[list, ndarray]) -> list:
    """
    Calculates the expectation value of an `operator` for a given list of ``density matrices``

    Simply calls the `expectationMat` in a loop.
    This function exist for easy use in multi-processing.

    Parameters
    ----------
    :param `operator` : matrix of a Hermitian operator
    :param `denMats` : list of density matrices

    Returns
    -------
    :return: `list` of expectation values of the `operator` for the list of ``density matrices``

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    expectations = []
    for denMat in denMats:
        expectations.append(expectationMat(operator, denMat))
    return expectations

def expectationColList(operator: Union[spmatrix, ndarray], states: Union[list, ndarray]) -> list:
    """
    Calculates the expectation values of an `operator` for a list/matrix of ``ket (column) states`` by matrix multiplication.

    The `list` here is effectivly a matrix whose columns are `ket` states for which we want the expextation values.
    For example, the eigenstates obtained from eigenvalue calculations of numpy or scipy are this form.
    TODO introduced to be used with eigenvectors, needs to be tested for non-mutually orthogonal states.
    So, it relies on states being orthonormal, if not there will be off-diagonal elements in the resultant matrix,
    but still the diagonal elements are the expectation values, meaning it should work!

    Parameters
    ----------
    :param `operator` : matrix of a Hermitian operator
    :param `states` : ket states as the columns in the input matrix

    Returns
    -------
    :return: `list` of expectation values of the `operator` for a matrix of `ket` states

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    expMat = states.conj().T @ operator @ states
    return expMat.diagonal()

# Functions for fidelity (currently only for pure states)
def fidelity(state1: Union[spmatrix, ndarray], state2: Union[spmatrix, ndarray]) -> float:
    """
    Calculates `fidelity` between ``two states``

    States can either be a `ket` or ``density matrix``,
    and they can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param state1: `ket` state or ``density matrix``
    :param state2: `ket` state or ``density matrix``

    Returns
    -------
    :return: `fidelity` between any ``two states``

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    if state1.shape[0] != state1.shape[1]:
        if state2.shape[0] != state2.shape[1]:
            return fidelityKet(state1, state2)
        else:
            state1 = (state1 @ (state1.conj().T))
            return fidelityPureMat(state1, state2)
    else:
        if state2.shape[0] != state2.shape[1]:
            state2 = (state2 @ (state2.conj().T))
            return fidelityPureMat(state1, state2)
        else:
            state1 = (state1 @ (state1.conj().T))
            return fidelityPureMat(state1, state2)

def fidelityKet(ket1: Union[spmatrix, ndarray], ket2: Union[spmatrix, ndarray]) -> float:
    """
    Calculates `fidelity` between two `ket` states

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param ket1: `ket` state
    :param ket2: `ket` state

    Returns
    -------
    :return: `fidelity` between two ``ket states``

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    herm = ket1.conj().T
    fidelityA = ((herm @ ket2).diagonal()).sum()
    return np.real(fidelityA * np.conj(fidelityA))

def fidelityKetList(ket1: Union[spmatrix, ndarray], ketList: Union[list, ndarray]) -> list:
    """
    Calculates `fidelity` between ``a ket state`` and ``list of ket states``

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param ket1: `ket` state
    :param ketList: `list` of ket states

    Returns
    -------
    :return: `list` of fidelities between ``a ket state`` and ``list of ket states``

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    fidelities = []
    herm = ket1.conj().T
    for ket in ketList:
        fidelityA = ((herm @ ket).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))
    return fidelities

def fidelityPureMat(denMat1, denMat2):
    """
    Calculates `fidelity` between two (pure) ``density matrices``

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param denMat1: (pure) ``density matrix``
    :param denMat2: (pure) ``density matrix``

    Returns
    -------
    :return: `fidelity` between two (pure) ``density matrices``

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    fidelityA = ((denMat1 @ denMat2).diagonal()).sum()
    return np.real(fidelityA)

def fidelityKetLists(zippedStatesList):
    """
    Created to be used in ``multi-processing`` calculations

    
    FIXME too specific, requires zipping
    """
    fidelities = []
    for ind in range(len(zippedStatesList[0])):
        herm = zippedStatesList[0][ind].conj().T
        fidelityA = ((herm @ zippedStatesList[1][ind]).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))
    return fidelities

# Entropy function
def entropy(densMat, base2=False):
    """
    Calculates the entropy of a given state
    Input should be a density matrix by definition of entropy
    Uses exponential basis as default

    :param densMat: a density matrix
    :param base2: option to calculate in base 2
    :return: the entropy of the given density matrix
    """

    # converts sparse into array (and has to)
    if not isinstance(densMat, np.ndarray):
        densMat = densMat.A

    vals = lina.eig(densMat)[0]
    nzvals = vals[vals != 0]

    if not base2:
        logvals = np.log(nzvals)
    else:
        logvals = np.log2(nzvals)

    S = float(np.real(-sum(nzvals * logvals)))
    return S


def entropyKet(ket, base2=False):
    """
    Calculates the entropy of a given ket state

    This function should not exist at all, ket is always a pure state

    Input should be a density matrix by definition of entropy
    Uses exponential basis as default

    :param ket: a ket state
    :param base2: option to calculate in base 2
    :return: the entropy of the given density matrix
    """
    denMat = ket @ (ket.conj().T)
    S = entropy(denMat, base2)
    return S


# Delocalisation measure for various cases
def iprKet(basis, ket):
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a ket in a given basis

    :param ket: a ket state
    :param basis: a complete basis
    :return: inverse participation ratio
    """
    npc = 0
    for basKet in basis:
        fid = fidelityKet(basKet, ket)
        npc += (fid**2)
    return 1/npc


def iprKetList(basis, kets):
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a list kets in a given basis
    Simply calls iprKet in a loop

    :param kets: a list of ket states
    :param basis: a complete basis
    :return: a list of inverse participation ratios
    """
    npcs = []
    for ket in kets:
        npcs.append(iprKet(basis, ket))
    return npcs


def iprKetNB(ket):
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a ket
    This assumes the basis is of the free Hamiltonian

    :param ket: a ket state
    :return: inverse participation ratio
    """
    return 1/np.sum(np.power((np.abs(ket.A.flatten())),4))


def iprKetNBList(kets):
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a list kets in a given basis
    This assumes the basis is of the free Hamiltonian
    Simply calls iprKetNB in a loop

    :param kets: a list of ket states
    :return: a list of inverse participation ratios
    """
    IPRatio = []
    for ket in kets:
        IPRatio.append(iprKetNB(ket))
    return IPRatio


def iprKetNBmat(kets):
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a matrix of ket states as the column
    For example the eigenstates obtained from eigenvalue calculations of numpy or scipy are this form
    TODO use if you know what you are doing
    This assumes the basis is of the free Hamiltonian

    :param ket: a density matrix
    :return: inverse participation ratio
    """
    IPRatio = []
    for ind in range(len(kets)):
        IPRatio.append(iprKetNB(kets[:,ind]))
    return IPRatio


def iprPureDenMat(basis, denMat):
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a density matrix in a given basis

    :param denMat: a density matrix
    :param basis: a complete basis
    :return: inverse participation ratio
    """
    npc = 0
    for basKet in basis:
        fid = fidelityPureMat(basKet, denMat)
        npc += (fid**2)
    return 1/npc


# Eigenvector statistics
def sortedEigens(Ham):
    """
    Calculates the eigenvalues and eigenvectors of a given Hamiltonian and sorts them

    :param Ham: the Hamiltoniam
    :return: sorted eigenvalues and eigenvectors
    """
    if not isinstance(Ham, np.ndarray):
        Ham = Ham.A

    eigVals, eigVecs = lina.eig(Ham)
    idx = eigVals.argsort()
    sortedVals = eigVals[idx]
    sortedVecs = eigVecs[:,idx]
    return sortedVals, sortedVecs


def eigVecStatKet(basis, ket):
    """
    Calculates the list of components of a ket in a basis
    Mainly useful in eigenvector statistics

    :param basis: a complete basis
    :param ket: the ket state
    :return: list of component values in the basis
    """
    comps = []
    for basKet in basis:
        comps.append(fidelityKet(basKet, ket))
    return comps


def eigVecStatKetList(basis, kets):
    """
    Calculates the list components of a list of ket states
    Mainly useful in eigenvector statistics

    :param basis: a complete basis
    :param ket: list of ket states
    :return: list of component values in the basis
    """
    compsList = []
    for ket in kets:
        compsList.append(eigVecStatKet(basis, ket))
    return compsList


def eigVecStatKetNB(ket):
    """
    Calculates the components of a ket
    Assumes the basis is of the free Hamiltonian

    :param ket: a ket state or list of ket states
    return: list of components
    """
    return 1/np.sum(np.power((np.abs(ket.A.flatten())),2))
