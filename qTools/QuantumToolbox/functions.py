"""
    Module of functions to calculate expectations, fidelities, entropy etc. from quantum states

    The reason for having several methods for the same task is to improve performance
    For example, an if statement can be avoided using `expectationMat/expectationKet` for
    `density matrices/ket states`, or
    `expectationKetList/expectationMatList` is suitable in `multi-processing` of list of time-series of states

    Functions
    ---------
    | :func:`expectation` : Function to calculate the expectation value of an `operator` for a given `state`.
    | :func:`expectationMat` : Calculates the expectation value of an `operator` for a given `density matrix`.
    | :func:`expectationKet` : Calculates the expectation value of an `operator` for a given `ket`.
    | :func:`expectationKetList` : Calculates the expectation value of an `operator` for a given list of `ket` states.
    | :func:`expectationMatList` : Calculates the expectation value of an `operator` for a given list of
        `density matrices`.
    | :func:`expectationColArr` : Calculates the expectation values of an `operator` for a list/matrix of
        `ket (column) states` by matrix multiplication.

    | :func:`fidelity` : Calculates `fidelity` between `two states`.
    | :func:`fidelityKet` : Calculates `fidelity` between two `ket` states.
    | :func:`fidelityPureMat` : Calculates `fidelity` between two (pure) `density matrices`.
    | :func:`fidelityKetList` : Calculates `fidelity` between `a ket state` and `list of ket states`.
    | :func:`fidelityKetLists` : Created to be used in `multi-processing` calculations of two lists of kets states.

    | :func:`entropy` : Calculates the `entropy` of a given `density matrix` .
    | :func:`entropyKet` : Calculates the `entropy` of a given `ket` state.

    | :func:`iprKet` : Calculates the inverse participation ratio (a delocalisation measure) of a `ket` in a given
        basis.
    | :func:`iprKetList` : Calculates the inverse participation ratio (a delocalisation measure) of a `list of ket`
        states in a given basis.
    | :func:`iprKetNB` : Calculates the inverse participation ratio (a delocalisation measure) of a ket by assuming that
        the basis is of the free Hamiltonian.
    | :func:`iprKetNBList` : Calculates the inverse participation ratio (a delocalisation measure) of a list kets by
        assuming that the basis is of the free Hamiltonian.
    | :func:`iprKetNBmat` : Calculates the inverse participation ratio (a delocalisation measure) of `a matrix of ket
        states as the column`.
    | :func:`iprPureDenMat` : Calculates the inverse participation ratio (a delocalisation measure) of a
        `density matrix` in a given `basis`.

    | :func:`sortedEigens` : Calculates the `eigenvalues and eigenvectors` of a given Hamiltonian and `sorts` them.

    | :func:`eigVecStatKet` : Calculates components of a `ket` in a basis.
    | :func:`eigVecStatKetList` : Calculates components of a `list of ket states`.
    | :func:`eigVecStatKetNB` : Calculates the components of a ket by assuming that the basis is of the free Hamiltonian

    Types
    ^^^^^
    | :const:`Matrix <qTools.QuantumToolbox.customTypes.Matrix>` : Union of (scipy) sparse and (numpy) array
    | :const:`floatList <qTools.QuantumToolbox.customTypes.floatList>` : List of floats
    | :const:`matrixList <qTools.QuantumToolbox.customTypes.matrixList>` : List of Matrices

""" #pylint:disable=too-many-lines

from typing import List, Tuple, Any
from numpy import ndarray # type: ignore

import numpy as np # type: ignore
import scipy.linalg as lina # type: ignore
from scipy.sparse import spmatrix # type: ignore

from .states import tensorProd, densityMatrix, mat2Vec
from .operators import sigmay

from .customTypes import Matrix, floatList, matrixList


# do not delete these
# from numpy import ndarray
# from scipy.sparse import spmatrix
# from typing import List, Optional, TypeVar, Tuple, Any

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)
# floatList = List[float]                             # Type for a list of floats
# matrixList = List[Matrix]                           # Type for a list `Matrix` types

# TODO a possible improvement is to create decorator for similar functions to get function reference as input.
# Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.

# Functions for expectation value
def expectation(operator: Matrix, state: Matrix) -> float:
    """
    Function to calculate the expectation value of an `operator` for a given `state`.

    State can either be a `ket` or `density matrix`.
    Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.
    State and operator can both be sparse or array or any combination of the two.

    Parameters
    ----------
    operator : Matrix
        matrix of a Hermitian operator
    state : Matrix
        a quantum state

    Returns
    -------
    :return: float
        expectation value of the `operator` for the `state`

    Examples
    --------
    >>> import numpy as np
    >>> import qTools.QuantumToolbox.states as qStates
    >>> import qTools.QuantumToolbox.operators as qOperators
    >>> sigmaz = qOperators.sigmaz()

    >>> ket = qStates.basis(dimension=2, state=1)
    >>> expectKet = expectation(operator=sigmaz, state=ket)
    -1

    >>> denMat = qStates.densityMatrix(ket)
    >>> expectMat = expectation(sigmaz, denMat)
    -1

    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> expectKet = expectation(operator=sigmaz, state=ket1)
    1

    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> expectKet = expectation(operator=sigmaz, state=ket2)
    0

    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> expectKet = expectation(operator=sigmaz, state=denMat1)
    1

    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> expectKet = expectation(operator=sigmaz, state=denMat2)
    0
    """

    if state.shape[0] != state.shape[1]:
        state = state @ (state.conj().T)
    return expectationMat(operator, state)


def expectationMat(operator: Matrix, denMat: Matrix) -> float:
    """
    Calculates the expectation value of an `operator` for a given `density matrix`.

    Works with both sparse and array.
    Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.
    State and operator can both be sparse or array or any combination of the two.

    Parameters
    ----------
    operator : Matrix
        matrix of a Hermitian operator
    denMat : Matrix
        density matrix

    Returns
    -------
    :return: float
        expectation value of the `operator` for the `density matrix`

    Examples
    --------
    >>> import numpy as np
    >>> import qTools.QuantumToolbox.states as qStates
    >>> import qTools.QuantumToolbox.operators as qOperators
    >>> sigmaz = qOperators.sigmaz()

    >>> ket = qStates.basis(dimension=2, state=1)
    >>> denMat = qStates.densityMatrix(ket)
    >>> expectMat = expectation(sigmaz, denMat)
    -1

    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> expectKet = expectation(operator=sigmaz, state=denMat1)
    1

    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> expectKet = expectation(operator=sigmaz, state=denMat2)
    0
    """

    expc = ((operator @ denMat).diagonal()).sum()
    return np.real(expc)


def expectationKet(operator: Matrix, ket: Matrix) -> float:
    """
    Calculates the expectation value of an `operator` for a given `ket`.

    Calculates the density matrix and calls the expectationMat.
    Computationally the same as using (``bra @ operator @ ket``).
    Works with both sparse and array.
    Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.

    Parameters
    ----------
    operator : Matrix
        matrix of a Hermitian operator
    ket : Matrix
        ket state

    Returns
    -------
    :return: float
        expectation value of the `operator` for the `ket` state

    Examples
    --------
    >>> import numpy as np
    >>> import qTools.QuantumToolbox.states as qStates
    >>> import qTools.QuantumToolbox.operators as qOperators
    >>> sigmaz = qOperators.sigmaz()

    >>> ket = qStates.basis(dimension=2, state=1)
    >>> expectKet = expectation(operator=sigmaz, state=ket)
    -1

    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> expectKet = expectation(operator=sigmaz, state=ket1)
    1

    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> expectKet = expectation(operator=sigmaz, state=ket2)
    0
    """

    denMat = ket @ (ket.conj().T)
    return expectationMat(operator, denMat)


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
    :return: floatList
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
        expectations.append(expectationKet(operator, ket))
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
    :return: floatList
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
        expectations.append(expectationMat(operator, denMat))
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
    :return: floatList
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

    expMat = states.conj().T @ operator @ states
    return expMat.diagonal()


# Functions for fidelity (currently only for pure states)
def fidelity(state1: Matrix, state2: Matrix) -> float:
    """
    Calculates `fidelity` between `two states`.

    States can either be a `ket` or `density matrix`,
    and they can both be sparse or array or any combination of the two.

    Parameters
    ----------
    state1 : Matrix
        `ket` state or `density matrix`
    state2 : Matrix
        `ket` state or `density matrix`

    Returns
    -------
    :return: float
        `fidelity` between any `two states`

    Examples
    --------
    >>> import numpy as np
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> fidelityKet01 = fidelity(state1=ket0, state2=ket1)
    0.

    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> fidelityKet02 = fidelity(state1=ket0, state2=ket2)
    0.5

    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> fidelityKet12 = fidelity(state1=ket1, state2=ket2)
    0.5

    >>> denMat0 = qStates.densityMatrix(ket0)
    >>> fidelityMat01 = fidelity(state1=denMat0, state2=denMat1)
    0

    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> fidelityMat02 = fidelity(state1=denMat0, state2=denMat2)
    0.5

    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> fidelityMat12 = fidelity(state1=denMat1, state2=denMat2)
    0.5
    """

    if state1.shape[0] != state1.shape[1]:
        if state2.shape[0] != state2.shape[1]:
            fid = fidelityKet(state1, state2)
        else:
            state1 = (state1 @ (state1.conj().T))
            fid = fidelityPureMat(state1, state2)
    else:
        if state2.shape[0] != state2.shape[1]:
            state2 = (state2 @ (state2.conj().T))
            fid = fidelityPureMat(state1, state2)
        else:
            state1 = (state1 @ (state1.conj().T))
            fid = fidelityPureMat(state1, state2)
    return fid


def fidelityKet(ket1: Matrix, ket2: Matrix) -> float:
    """
    Calculates `fidelity` between two `ket` states.

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    ket1 : Matrix
        ket state
    ket2 : Matrix
        ket state

    Returns
    -------
    :return: float
        `fidelity` between two `ket states`

    Examples
    --------
    >>> import numpy as np
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> fidelityKet01 = fidelityKet(state1=ket0, state2=ket1)
    0.

    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> fidelityKet02 = fidelityKet(state1=ket0, state2=ket2)
    0.5

    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> fidelityKet12 = fidelityKet(state1=ket1, state2=ket2)
    0.5
    """

    herm = ket1.conj().T
    fidelityA = ((herm @ ket2).diagonal()).sum()
    return np.real(fidelityA * np.conj(fidelityA))


def fidelityPureMat(denMat1: Matrix, denMat2: Matrix) -> float:
    """
    Calculates `fidelity` between two (pure) `density matrices`.

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    denMat1 : Matrix
        (pure) density matrix
    denMat2 : Matrix
        (pure) density matrix

    Returns
    -------
    :return: float
        `fidelity` between two (pure) `density matrices`

    Examples
    --------
    >>> import numpy as np
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> denMat0 = qStates.densityMatrix(ket0)
    >>> fidelityMat01 = fidelityPureMat(state1=denMat0, state2=denMat1)
    0

    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> fidelityMat02 = fidelityPureMat(state1=denMat0, state2=denMat2)
    0.5

    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> fidelityMat12 = fidelityPureMat(state1=denMat1, state2=denMat2)
    0.5
    """

    fidelityA = ((denMat1 @ denMat2).diagonal()).sum()
    return np.real(fidelityA)


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
    :return: floatList
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
    herm = ket1.conj().T
    for ket in ketList:
        fidelityA = ((herm @ ket).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))
    return fidelities


def fidelityKetLists(zippedStatesList: Any) -> floatList:
    """
    Created to be used in `multi-processing` calculations of two lists of kets states.

    FIXME too specific, requires zipping
    """

    fidelities = []
    for ind in range(len(zippedStatesList[0])):
        herm = zippedStatesList[0][ind].conj().T
        fidelityA = ((herm @ zippedStatesList[1][ind]).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))
    return fidelities


# Entropy function
# TODO may create a function specifically for sparse input
def entropy(densMat: Matrix, base2: bool = False) -> float:
    """
    Calculates the `entropy` of a given `density matrix`.

    Input should be a density matrix by definition of entropy.
    Uses exponential basis as default.

    Parameters
    ----------
    densMat : Matrix
        a density matrix
    base2 : bool
        option to calculate in base 2

    Returns
    -------
    :return: float
        the `entropy` of the given `density matrix`

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> compositeStateKet = qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    >>> entropyKet = entropyKet(compositeStateKet)
    -0.0

    >>> compositeStateMat = qStates.densityMatrix(compositeStateKet)
    >>> entropyMat = entropy(compositeStateMat)
    -0.0

    >>> stateFirstSystem = qStates.partialTrace(keep=[0], dims=[2, 2], state=compositeStateKet)
    >>> entropy1 = entropy(stateFirstSystem)
    -0.0

    >>> stateSecondSystem = qStates.partialTrace(keep=[1], dims=[2, 2], state=compositeStateKet)
    >>> entropy2 = entropy(stateSecondSystem)
    -0.0

    >>> entangledKet = qStates.normalise(qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    + qStates.compositeState(dimensions=[2, 2], excitations=[1,0], sparse=True))
    >>> entropyKetEntangled = entropyKet(entangledKet)
    2.2204460492503126e-16

    >>> entangledMat = qStates.densityMatrix(entangledKet)
    >>> entropyMatEntangled = entropy(entangledMat)
    2.2204460492503126e-16

    >>> stateFirstSystemEntangled = qStates.partialTrace(keep=[0], dims=[2, 2], state=entangledKet)
    >>> entropy1Entangled = entropy(stateFirstSystemEntangled)
    0.6931471805599454

    >>> stateSecondSystemEntangled = qStates.partialTrace(keep=[1], dims=[2, 2], state=entangledMat)
    >>> entropy2Entangled = entropy(stateSecondSystemEntangled)
    0.6931471805599454
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


def entropyKet(ket: Matrix, base2: bool = False) -> float:
    """
    Calculates the `entropy` of a given `ket` state.

    This function should not exist at all, ket is always a pure state.

    Input should be a density matrix by definition of entropy.
    Uses exponential basis as default.

    Parameters
    ----------
    ket : Matrix
        a ket state
    base2 : bool
        option to calculate in base 2

    Returns
    -------
    :return: float
        the `entropy` of the given `density matrix`

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> compositeStateKet = qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    >>> entropyKet = entropyKet(compositeStateKet)
    -0.0

    >>> entangledKet = qStates.normalise(qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    + qStates.compositeState(dimensions=[2, 2], excitations=[1,0], sparse=True))
    >>> entropyKetEntangled = entropyKet(entangledKet)
    2.2204460492503126e-16
    """

    denMat = ket @ (ket.conj().T)
    S = entropy(denMat, base2)
    return S


# Delocalisation measures for various cases
def iprKet(basis: matrixList, ket: Matrix) -> float:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a `ket` in a given basis.

    Parameters
    ----------
    ket : matrixList
        a ket state
    basis : Matrix
        a complete basis

    Returns
    -------
    :return: float
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
        fid = fidelityKet(basKet, ket)
        npc += (fid**2)
    return 1/npc


def iprKetList(basis: matrixList, kets: matrixList) -> floatList:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a `list of ket` states in a given basis.

    Simply calls iprKet in a loop.

    Parameters
    ----------
    kets : matrixList
        a `list` of ket states
    basis : matrixList
        a complete basis

    Returns
    -------
    :return: floatList
        a `list` of inverse participation ratios for the given list of ket states

    Examples
    --------
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> state2 = qStates.basis(2,1)
    >>> state3 = qStates.basis(2,0)
    >>> stateList = [state0, state1, state2, state3]
    >>> iprList = iprKetList(completeBasis, stateList)
    [1.1245136186770428, 2.000000000000001, 1.0, 1.0]
    """

    npcs = []
    for ket in kets:
        npcs.append(iprKet(basis, ket))
    return npcs


def iprKetNB(ket: Matrix) -> float:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a ket
    by assuming that the basis is of the free Hamiltonian.

    Parameters
    ----------
    ket : Matrix
        a ket state

    Returns
    -------
    :return: float
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


def iprKetNBList(kets: matrixList) -> floatList:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a list kets
    by assuming that the basis is of the free Hamiltonian.

    Simply calls iprKetNB in a loop.

    Parameters
    ----------
    kets: matrixList
        a `list` of ket states

    Returns
    -------
    :return: floatList
        a `list` of inverse participation ratios

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> state2 = qStates.basis(2,1)
    >>> state3 = qStates.basis(2,0)
    >>> stateList = [state0, state1, state2, state3]
    >>> iprList = iprKetNBList(stateList)
    [1.1245136186770428, 2.000000000000001, 1.0, 1.0]
    """

    IPRatio = []
    for ket in kets:
        IPRatio.append(iprKetNB(ket))
    return IPRatio


def iprKetNBmat(kets: ndarray) -> floatList:
    """
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
    :return: floatList
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
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a `density matrix` in a given `basis`.

    Parameters
    ----------
    denMat : matrixList
        a density matrix
    basis : Matrix
        a complete basis

    Returns
    -------
    :return: float
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
        fid = fidelityPureMat(basKet, denMat)
        npc += (fid**2)
    return 1/npc


# Eigenvector statistics
def sortedEigens(Ham: Matrix, mag=False) -> Tuple[floatList, List[ndarray]]:
    """
    Calculates the `eigenvalues and eigenvectors` of a given Hamiltonian and `sorts` them.
    If `mag is True`, sort is accordingly with the magnitude of the eigenvalues.
    TODO update docstrings, change Ham to Matrix, since this can be used also for any matrix.

    Parameters
    ----------
    Ham : Matrix
        the Hamiltonian

    Returns
    -------
    :return: Tuple[floatList, List[ndarray]]
        `sorted` eigenvalues and eigenvectors

    Examples
    --------
    >>> import qTools.QuantumToolbox.operators as qOperators
    >>> ham = qOperators.Jx(j=6)
    >>> eigVals, eigVecs = sortedEigens(ham)

    >>> print(eigVals)
    [-2.5+0.j -1.5+0.j -0.5+0.j  0.5+0.j  1.5+0.j  2.5+0.j]

    >>> print(eigVecs)
    [[ 0.1767767   0.39528471  0.55901699  0.55901699 -0.39528471 -0.1767767 ]
    [-0.39528471 -0.53033009 -0.25        0.25       -0.53033009 -0.39528471]
    [ 0.55901699  0.25       -0.35355339 -0.35355339 -0.25       -0.55901699]
    [-0.55901699  0.25        0.35355339 -0.35355339  0.25       -0.55901699]
    [ 0.39528471 -0.53033009  0.25        0.25        0.53033009 -0.39528471]
    [-0.1767767   0.39528471 -0.55901699  0.55901699  0.39528471 -0.1767767 ]]
    """

    if not isinstance(Ham, np.ndarray):
        Ham = Ham.A

    eigVals, eigVecs = lina.eig(Ham)
    if mag:
        mags = np.abs(eigVals)
        idx = mags.argsort()
    else:
        idx = eigVals.argsort()
    sortedVals = eigVals[idx]
    sortedVecs = eigVecs[:, idx]
    sortedVecsMat = []
    for ind in range(len(sortedVecs)):
        sortedVecsMat.append(mat2Vec(sortedVecs[:, ind]))
    return sortedVals, sortedVecsMat


# TODO create the function for the result of eigenvec calculation
def eigVecStatKet(basis: matrixList, ket: Matrix) -> floatList:
    """
    Calculates components of a `ket` in a basis.

    Main use is in eigenvector statistics.

    Parameters
    ----------
    basis : matrixList
        a complete basis
    ket : Matrix
        the ket state

    Returns
    -------
    :return: floatList
        `list` of component values in the basis

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket = qStates.basis(2, 1)
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> components = eigVecStatKet(basis=completeBasis, ket=ket)
    [0, 1]
    """

    comps = []
    for basKet in basis:
        comps.append(fidelityKet(basKet, ket))
    return comps


def eigVecStatKetList(basis: matrixList, kets: matrixList) -> List[floatList]:
    """
    Calculates components of a `list of ket states`
    Main use is in eigenvector statistics.

    Parameters
    ----------
    basis : matrixList
        a complete basis
    kets : matrixList
        `list` of ket states

    Returns
    -------
    :return: List[floatList]
        `list` of component values in the basis

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(2, 0)
    >>> ket1 = qStates.basis(2, 1)
    >>> ketList = [ket0, ket1]
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> components = eigVecStatKetList(basis=completeBasis, kets=ketList)
    [[1, 0], [0, 1]]
    """

    compsList = []
    for ket in kets:
        compsList.append(eigVecStatKet(basis, ket))
    return compsList


def eigVecStatKetNB(ket: Matrix) -> float:
    """
    Calculates the components of a ket by assuming that the basis is of the free Hamiltonian.

    Parameters
    ----------
    ket : Matrix
        a ket state or list of ket states

    Returns
    -------
    return: float
        list of components

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket = qStates.basis(2, 1)
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> components = eigVecStatKetNB(ket=ket)
    [0 1]
    """

    # TODO Find a way around this
    if isinstance(ket, spmatrix):
        ket = ket.A
    return np.real(ket.flatten())

def concurrence(state: Matrix) -> float:
    """
    TODO docstrings
    sqrtState = lina.sqrtm(state)
    SySy = tensorProd(sigmay(), sigmay())
    magicConj = SySy @ state.conj() @ SySy
    R = sqrtState @ magicConj @ sqrtState
    eigVals, _ = sortedEigens(lina.sqrtm(R))
    eigVals = np.real(eigVals)
    print(eigVals)
    """

    if not isinstance(state, np.ndarray):
        state = state.A

    if state.shape[0] != state.shape[1]:
        state = densityMatrix(state)
    SySy = tensorProd(sigmay(), sigmay())
    magicConj = SySy @ state.conj() @ SySy
    R = state @ magicConj
    eigVals, _ = sortedEigens(R)
    eigVals = np.real(np.sqrt(eigVals))
    return max([0, np.round(eigVals[3] - eigVals[2] - eigVals[1] - eigVals[0], 15)])
