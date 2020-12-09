from typing import Any
from numpy import ndarray # type: ignore

import numpy as np # type: ignore

from .linearAlgebra import hc
from .functions import expectation

from .customTypes import Matrix, floatList, matrixList

def expectationKetList(operator: Matrix, kets: matrixList) -> floatList:
    """
    Calculates the expectation value of an `operator` for a given list of `ket` states.

    Simply calls the `expectationKet` in a loop.
    This function exist for easy use in multi-processing.

    Parameters
    ----------
    operator : Matrix
        matrix of a Hermitian operator
    kets : Matrix
        list of ket states

    Returns
    -------
    floatList
        `list` of expectation values of the `operator` for the list of `ket` states

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> ketList = [ket0, ket1, ket2]
    >>> expectKetList = expectationKetList(operator=sigmaz, kets=ketList)
    [-1, 1, 0.0]
    """

    expectations = []
    for ket in kets:
        expectations.append(expectation(operator, ket))
    return expectations


def expectationMatList(operator: Matrix, denMats: matrixList) -> floatList:
    """
    Calculates the expectation value of an `operator` for a given list of `density matrices`.

    Simply calls the `expectationMat` in a loop.
    This function exist for easy use in multi-processing.

    Parameters
    ----------
    operator : Matrix
        matrix of a Hermitian operator
    denMats : Matrix
        list of density matrices

    Returns
    -------
    floatList
        `list` of expectation values of the `operator` for the list of `density matrices`

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> denMat0 = qStates.densityMatrix(ket0)
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> denMatList = [denMat0, denMat1, denMat2]
    >>> expectMatList = expectationMatList(sigmaz, denMats=denMatList)
    [-1, 1, 0.0]
    """

    expectations = []
    for denMat in denMats:
        expectations.append(expectation(operator, denMat))
    return expectations


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


def fidelityKetList(ket1: Matrix, ketList: matrixList) -> floatList:
    """
    Calculates `fidelity` between `a ket state` and `list of ket states`.

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    ket1 : Matrix
        ket state
    ketList : matrixList
        `list` of ket states

    Returns
    -------
    floatList
        `list` of fidelities between `a ket state` and `list of ket states`

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> ketList = [ket0, ket1, ket2]
    >>> fidelityList = fidelityKetList(ket0, ketList)
    [1, 0, 0.5000000000000001]
    """

    fidelities = []
    for ket in ketList:
        fidelityA = ((hc(ket1) @ ket).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))
    return fidelities


def fidelityKetLists(zippedStatesList: Any) -> floatList:
    """
    Created to be used in `multi-processing` calculations of two lists of kets states.

    FIXME too specific, requires zipping
    """

    fidelities = []
    for ind in range(len(zippedStatesList[0])):
        herm = hc(zippedStatesList[0][ind])
        fidelityA = ((herm @ zippedStatesList[1][ind]).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))

    return fidelities
