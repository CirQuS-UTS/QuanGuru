"""
    Module of functions to calculate expectations, fidelities, entorpy etc. from quantum states

    The reason for having several functions for the same task is to improve performance
    For example, an if statement can be avioded using ``expectationMat/expectationKet`` for
    ``density matrices/ket states``, or
    ``expectationKetList/expectationMatList`` is suitable in ``multi-processing`` of list of time-series of states
"""
import numpy as np
import scipy.linalg as lina

from typing import Union, Tuple, Any, List
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
    >>> ket = qStates.basis(dimension=2, state=1)
    >>> denMat = qStates.densityMatrix(ket)
    >>> sigmaz = qOperators.sigmaz()
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=ket)
    -1
    >>> expectMat = qFunctions.expectation(sigmaz, denMat)
    -1
    >>> import numpy as np
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=ket1)
    1
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=ket2)
    0
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=denMat1)
    1
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=denMat2)
    0
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
    >>> ket = qStates.basis(dimension=2, state=1)
    >>> denMat = qStates.densityMatrix(ket)
    >>> sigmaz = qOperators.sigmaz()
    >>> expectMat = qFunctions.expectation(sigmaz, denMat)
    -1
    >>> import numpy as np
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=denMat1)
    1
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=denMat2)
    0
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
    >>> ket = qStates.basis(dimension=2, state=1)
    >>> sigmaz = qOperators.sigmaz()
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=ket)
    -1
    >>> import numpy as np
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=ket1)
    1
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> expectKet = qFunctions.expectation(operator=sigmaz, state=ket2)
    0
    """
    denMat = ket @ (ket.conj().T)
    return expectationMat(operator, denMat)

def expectationKetList(operator: Union[spmatrix, ndarray], kets: List[Union[spmatrix, ndarray]]) -> List[float]:
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
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> ketList = [ket0, ket1, ket2]
    >>> expectKetList = qFunctions.expectationKetList(operator=sigmaz, kets=ketList)
    [-1, 1, 0.0]
    """
    expectations = []
    for ket in kets:
        expectations.append(expectationKet(operator, ket))
    return expectations

def expectationMatList(operator: Union[spmatrix, ndarray], denMats:  List[Union[spmatrix, ndarray]]) -> List[float]:
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
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> denMat0 = qStates.densityMatrix(ket0)
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> denMatList = [denMat0, denMat1, denMat2]
    >>> expectMatList = qFunctions.expectationMatList(sigmaz, denMats=denMatList)
    [-1, 1, 0.0]
    """
    expectations = []
    for denMat in denMats:
        expectations.append(expectationMat(operator, denMat))
    return expectations

def expectationColArr(operator: Union[spmatrix, ndarray], states: ndarray) -> List[float]:
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
    >>> ham = qOperators.sigmaz(sparse=False)
    >>> eigVals, eigVecs = np.linalg.eig(ham)
    >>> sz = qOperators.sigmaz()
    >>> sx = qOperators.sigmax()
    >>> expectZ = qFunctions.expectationColArr(sz, eigVecs)
    [ 1. -1.]
    >>>> expectX = qFunctions.expectationColArr(sx, eigVecs)
    [0. 0.]
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
    :param `state1`: `ket` state or ``density matrix``
    :param `state2` : `ket` state or ``density matrix``

    Returns
    -------
    :return: `fidelity` between any ``two states``

    Examples
    --------
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> denMat0 = qStates.densityMatrix(ket0)
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> fidelityKet01 = qFunctions.fidelity(state1=ket0, state2=ket1)
    0.
    >>> fidelityKet02 = qFunctions.fidelity(state1=ket0, state2=ket2)
    0.5
    >>> fidelityKet12 = qFunctions.fidelity(state1=ket1, state2=ket2)
    0.5
    >>> fidelityMat01 = qFunctions.fidelity(state1=denMat0, state2=denMat1)
    0
    >>> fidelityMat02 = qFunctions.fidelity(state1=denMat0, state2=denMat2)
    0.5
    >>> fidelityMat12 = qFunctions.fidelity(state1=denMat1, state2=denMat2)
    0.5
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
    :param `ket1` : ket state
    :param `ket2` : ket state

    Returns
    -------
    :return: `fidelity` between two ``ket states``

    Examples
    --------
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> fidelityKet01 = qFunctions.fidelityKet(state1=ket0, state2=ket1)
    0.
    >>> fidelityKet02 = qFunctions.fidelityKet(state1=ket0, state2=ket2)
    0.5
    >>> fidelityKet12 = qFunctions.fidelityKet(state1=ket1, state2=ket2)
    0.5
    """
    herm = ket1.conj().T
    fidelityA = ((herm @ ket2).diagonal()).sum()
    return np.real(fidelityA * np.conj(fidelityA))

def fidelityPureMat(denMat1: Union[spmatrix, ndarray], denMat2: Union[spmatrix, ndarray]) -> float:
    """
    Calculates `fidelity` between two (pure) ``density matrices``

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param `denMat1` : (pure) density matrix
    :param `denMat2` : (pure) density matrix

    Returns
    -------
    :return: `fidelity` between two (pure) ``density matrices``

    Examples
    --------
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> denMat0 = qStates.densityMatrix(ket0)
    >>> denMat1 = qStates.densityMatrix(ket1)
    >>> denMat2 = qStates.densityMatrix(ket2)
    >>> fidelityMat01 = qFunctions.fidelityPureMat(state1=denMat0, state2=denMat1)
    0
    >>> fidelityMat02 = qFunctions.fidelityPureMat(state1=denMat0, state2=denMat2)
    0.5
    >>> fidelityMat12 = qFunctions.fidelityPureMat(state1=denMat1, state2=denMat2)
    0.5
    """
    fidelityA = ((denMat1 @ denMat2).diagonal()).sum()
    return np.real(fidelityA)

def fidelityKetList(ket1: Union[spmatrix, ndarray], ketList: List[Union[spmatrix, ndarray]]) -> List[float]:
    """
    Calculates `fidelity` between ``a ket state`` and ``list of ket states``

    States can both be sparse or array or any combination of the two.

    Parameters
    ----------
    :param `ket1` : ket state
    :param `ketList` : `list` of ket states

    Returns
    -------
    :return: `list` of fidelities between ``a ket state`` and ``list of ket states``

    Examples
    --------
    >>> ket0 = qStates.basis(dimension=2, state=1)
    >>> ket1 = qStates.basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*qStates.basis(dimension=2, state=1) + np.sqrt(0.5)*qStates.basis(dimension=2, state=0)
    >>> ketList = [ket0, ket1, ket2]
    >>> fidelityList = qFunctions.fidelityKetList(ket0, ketList)
    [1, 0, 0.5000000000000001]
    """
    fidelities = []
    herm = ket1.conj().T
    for ket in ketList:
        fidelityA = ((herm @ ket).diagonal()).sum()
        fidelities.append(np.real(fidelityA * np.conj(fidelityA)))
    return fidelities

def fidelityKetLists(zippedStatesList: Any) -> List[float]:
    """
    Created to be used in ``multi-processing`` calculations of two lists of kets states

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
def entropy(densMat: Union[spmatrix, ndarray], base2:bool=False) -> float:
    """
    Calculates the `entropy` of a given ``density matrix``

    Input should be a density matrix by definition of entropy.
    Uses exponential basis as default.

    Parameters
    ----------
    :param `densMat`: a density matrix
    :param `base2`: option to calculate in base 2

    Returns
    -------
    :return: the `entropy` of the given ``density matrix``

    Examples
    --------
    >>> compositeStateKet = qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    >>> entropyKet = qFunctions.entropyKet(compositeStateKet)
    -0.0
    >>> compositeStateMat = qStates.densityMatrix(compositeStateKet)
    >>> entropyMat = qFunctions.entropy(compositeStateMat)
    -0.0
    >>> stateFirstSystem = qStates.partialTrace(keep=[0], dims=[2, 2], state=compositeStateKet)
    >>> entropy1 = qFunctions.entropy(stateFirstSystem)
    -0.0
    >>> stateSecondSystem = qStates.partialTrace(keep=[1], dims=[2, 2], state=compositeStateKet)
    >>> entropy2 = qFunctions.entropy(stateSecondSystem)
    -0.0
    >>> entangledKet = qStates.normalise(qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True) 
    + qStates.compositeState(dimensions=[2, 2], excitations=[1,0], sparse=True))
    >>> entropyKetEntangled = qFunctions.entropyKet(entangledKet)
    2.2204460492503126e-16
    >>> entangledMat = qStates.densityMatrix(entangledKet)
    >>> entropyMatEntangled = qFunctions.entropy(entangledMat)
    2.2204460492503126e-16
    >>> stateFirstSystemEntangled = qStates.partialTrace(keep=[0], dims=[2, 2], state=entangledKet)
    >>> entropy1Entangled = qFunctions.entropy(stateFirstSystemEntangled)
    0.6931471805599454
    >>> stateSecondSystemEntangled = qStates.partialTrace(keep=[1], dims=[2, 2], state=entangledMat)
    >>> entropy2Entangled = qFunctions.entropy(stateSecondSystemEntangled)
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

def entropyKet(ket: Union[spmatrix, ndarray], base2:bool=False) -> float:
    """
    Calculates the `entropy` of a given `ket` state

    This function should not exist at all, ket is always a pure state.

    Input should be a density matrix by definition of entropy.
    Uses exponential basis as default.

    Parameters
    ----------
    :param `ket` : a ket state
    :param `base2` : option to calculate in base 2

    Returns
    -------
    :return: the `entropy` of the given ``density matrix``

    Examples
    --------
    >>> compositeStateKet = qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    >>> entropyKet = qFunctions.entropyKet(compositeStateKet)
    -0.0
    >>> entangledKet = qStates.normalise(qStates.compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True) 
    + qStates.compositeState(dimensions=[2, 2], excitations=[1,0], sparse=True))
    >>> entropyKetEntangled = qFunctions.entropyKet(entangledKet)
    2.2204460492503126e-16
    """
    denMat = ket @ (ket.conj().T)
    S = entropy(denMat, base2)
    return S

# Delocalisation measures for various cases
def iprKet(basis: List[Union[spmatrix, ndarray]], ket: Union[spmatrix, ndarray]) -> float:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a `ket` in a given basis.

    Parameters
    ----------
    :param `ket` : a ket state
    :param `basis` : a complete basis

    Returns
    -------
    :return: inverse participation ratio

    Examples
    --------
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> ipr0 = qFunctions.iprKet(completeBasis, state0)
    1.1245136186770428
    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> ipr1 = qFunctions.iprKet(completeBasis, state1)
    2.000000000000001
    >>> state2 = qStates.basis(2,1)
    >>> ipr2 = qFunctions.iprKet(completeBasis, state2)
    1.0
    """
    npc = 0.0
    for basKet in basis:
        fid = fidelityKet(basKet, ket)
        npc += (fid**2)
    return 1/npc

def iprKetList(basis: List[Union[spmatrix, ndarray]], kets: List[Union[spmatrix, ndarray]]) -> List[float]:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a ``list of ket`` states in a given basis.

    Simply calls iprKet in a loop.

    Parameters
    ----------
    :param `kets` : a `list` of ket states
    :param `basis` : a complete basis

    Returns
    -------
    :return: a `list` of inverse participation ratios for the given list of ket states

    Examples
    --------
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> state2 = qStates.basis(2,1)
    >>> state3 = qStates.basis(2,0)
    >>> stateList = [state0, state1, state2, state3]
    >>> iprList = qFunctions.iprKetList(completeBasis, stateList)
    [1.1245136186770428, 2.000000000000001, 1.0, 1.0]
    """
    npcs = []
    for ket in kets:
        npcs.append(iprKet(basis, ket))
    return npcs

def iprKetNB(ket: Union[spmatrix, ndarray]) -> float:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a ket by assuming that 
    the basis is of the free Hamiltonian.

    Parameters
    ----------
    :param `ket` : a ket state

    Returns
    -------
    :return: inverse participation ratio

    Examples
    --------
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> ipr0 = qFunctions.iprKetNB(state0)
    1.1245136186770428
    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> ipr1 = qFunctions.iprKetNB(state1)
    2.000000000000001
    >>> state2 = qStates.basis(2,1)
    >>> ipr2 = qFunctions.iprKetNB(state2)
    1.0
    >>> state3 = qStates.basis(2,0)
    >>> ipr3 = qFunctions.iprKetNB(state3)
    1.0
    """
    if isinstance(ket, spmatrix):
        ket = ket.A
    return 1/np.sum(np.power((np.abs(ket.flatten())),4))

def iprKetNBList(kets: List[Union[spmatrix, ndarray]]) -> List[float]:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a list kets by assuming that 
    the basis is of the free Hamiltonian.

    Simply calls iprKetNB in a loop.

    Parameters
    ----------
    :param kets: a `list` of ket states

    Returns
    -------
    :return: a `list` of inverse participation ratios

    Examples
    --------
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> state2 = qStates.basis(2,1)
    >>> state3 = qStates.basis(2,0)
    >>> stateList = [state0, state1, state2, state3]
    >>> iprList = qFunctions.iprKetNBList(stateList)
    [1.1245136186770428, 2.000000000000001, 1.0, 1.0]
    """
    IPRatio = []
    for ket in kets:
        IPRatio.append(iprKetNB(ket))
    return IPRatio

def iprKetNBmat(kets: ndarray) -> List[float]:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of ``a matrix of ket states as the column``

    For example the eigenstates obtained from eigenvalue calculations of numpy or scipy are this form.
    TODO use if you know what you are doing.
    This assumes the basis is of the free Hamiltonian.

    Parameters
    ----------
    :param ket: a density matrix

    Returns
    -------
    :return: a `list` of inverse participation ratios

    Examples
    --------
    >>> ham = qOperators.sigmaz()
    >>> eigValsHam, eigVecsHams = np.linalg.eig(ham.A)
    >>> iprHam = qFunctions.iprKetNBmat(eigVecsHams)
    [1.0, 1.0]
    >>> unitary = sp.sparse.linalg.expm(ham) 
    >>> eigValsUni, eigVecsUni = np.linalg.eig(unitary.A)
    >>> iprUni = qFunctions.iprKetNBmat(eigVecsUni)
    [1.0, 1.0]
    """
    IPRatio = []
    for ind in range(len(kets)):
        IPRatio.append(iprKetNB(kets[:,ind]))
    return IPRatio

def iprPureDenMat(basis: List[Union[spmatrix, ndarray]], denMat: Union[spmatrix, ndarray]) -> float:
    """
    Calculates the inverse participation ratio (a delocalisation measure) of a ``density matrix`` in a given `basis`

    Parameters
    ----------
    :param `denMat` : a density matrix
    :param `basis` : a complete basis

    Returns
    -------
    :return: inverse participation ratio

    Examples
    --------
    >>> completeBasis = qStates.completeBasisMat(dimension=2)
    >>> state0 = qStates.normalise(0.2*qStates.basis(2, 0) + 0.8*qStates.basis(2,1))
    >>> denMat0 = qStates.densityMatrix(state0)
    >>> ipr0 = qFunctions.iprPureDenMat(completeBasis, denMat0)
    1.1245136186770428
    >>> state1 = qStates.normalise(0.5*qStates.basis(2, 0) + 0.5*qStates.basis(2,1))
    >>> denMat1 = qStates.densityMatrix(state1)
    >>> ipr1 = qFunctions.iprPureDenMat(completeBasis, denMat1)
    2.000000000000001
    >>> state2 = qStates.basis(2,1)
    >>> denMat2 = qStates.densityMatrix(state2)
    >>> ipr2 = qFunctions.iprPureDenMat(completeBasis, denMat2)
    1.0
    """
    npc = 0.0
    for basKet in basis:
        fid = fidelityPureMat(basKet, denMat)
        npc += (fid**2)
    return 1/npc

# Eigenvector statistics
def sortedEigens(Ham: Union[spmatrix, ndarray]) -> Tuple[List[float], List[ndarray]]:
    """
    Calculates the ``eigenvalues and eigenvectors`` of a given Hamiltonian and `sorts` them

    Parameters
    ----------
    :param `Ham` : the Hamiltoniam

    Returns
    -------
    :return: `sorted` eigenvalues and eigenvectors

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    if not isinstance(Ham, np.ndarray):
        Ham = Ham.A

    eigVals, eigVecs = lina.eig(Ham)
    idx = eigVals.argsort()
    sortedVals = eigVals[idx]
    sortedVecs = eigVecs[:,idx]
    return sortedVals, sortedVecs

def eigVecStatKet(basis: List[Union[spmatrix, ndarray]], ket: Union[spmatrix, ndarray]) -> List[float]:
    """
    Calculates components of a `ket` in a basis.
    Main use is in eigenvector statistics.

    Parameters
    ----------
    :param `basis` : a complete basis
    :param `ket` : the ket state

    Returns
    -------
    :return: `list` of component values in the basis

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    comps = []
    for basKet in basis:
        comps.append(fidelityKet(basKet, ket))
    return comps

def eigVecStatKetList(basis: List[Union[spmatrix, ndarray]], kets: List[Union[spmatrix, ndarray]]) -> List[List[float]]:
    """
    Calculates components of a ``list of ket states``.
    Main use is in eigenvector statistics.

    Parameters
    ----------
    :param `basis` : a complete basis
    :param `kets` : `list` of ket states

    Returns
    -------
    :return: `list` of component values in the basis

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    compsList = []
    for ket in kets:
        compsList.append(eigVecStatKet(basis, ket))
    return compsList

def eigVecStatKetNB(ket: Union[spmatrix, ndarray]) -> float:
    """
    Calculates the components of a ket by
    assuming that the basis is of the free Hamiltonian.

    Parameters
    ----------
    :param `ket`: a ket state or list of ket states

    Returns
    -------
    return: list of components

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    return 1/np.sum(np.power((np.abs(ket.A.flatten())),2))
