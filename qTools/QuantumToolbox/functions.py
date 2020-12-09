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

from typing import List, Tuple
from numpy import ndarray # type: ignore

import numpy as np # type: ignore
import scipy.linalg as lina # type: ignore

from .linearAlgebra import hc, tensorProd, trace, innerProd
from .states import densityMatrix, mat2Vec
from .operators import sigmay

from .customTypes import Matrix, floatList


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
    float
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
        state = densityMatrix(state)
    expc = trace(operator @ state)
    return np.real(expc) if np.imag(round(expc, 15)) == 0.0 else expc


# Functions for fidelity (currently only for pure states)
def fidelity(state1: Matrix, state2: Matrix) -> float:
    """
    TODO USE INNER PRODUCT
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
    float
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

    if ((state1.shape[0] != state1.shape[1]) and (state2.shape[0] != state2.shape[1])):
        fid = abs(innerProd(state1, state2))**2
    else:
        if state1.shape[0] != state1.shape[1]:
            state1 = densityMatrix(state1)

        if state2.shape[0] != state2.shape[1]:
            state2 = densityMatrix(state2)

        fid = np.real(trace(state1 @ state2))
    return fid


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
    float
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

    if densMat.shape[0] != densMat.shape[1]:
        densMat = densityMatrix(densMat)

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


def traceDistance(A: Matrix, B: Matrix) ->float:
    """
    Calculates the trace distance between two matrices.

    Parameters
    ----------
    A: Matrix
        density matrix

    B: Matrix
        density matrix

    Returns
    -------
    return: float
        Trace distance between A and B

    Examples
    --------
    # TODO
    """
    diff = A-B

    diff = hc(diff) @ diff
    vals = lina.eig(diff)[0]
    return float(np.real(0.5 * np.sum(np.sqrt(np.abs(vals)))))


def sortedEigens(Ham: Matrix, mag: bool = False) -> Tuple[floatList, List[ndarray]]:
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
    Tuple[floatList, List[ndarray]]
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

    if state.shape[0] != state.shape[1]:
        state = densityMatrix(state)

    if not isinstance(state, np.ndarray):
        state = state.A

    SySy = tensorProd(sigmay(), sigmay())
    magicConj = SySy @ state.conj() @ SySy
    R = state @ magicConj
    eigVals, _ = sortedEigens(R)
    eigVals = np.real(np.sqrt(eigVals))
    return max([0, np.round(eigVals[3] - eigVals[2] - eigVals[1] - eigVals[0], 15)])
