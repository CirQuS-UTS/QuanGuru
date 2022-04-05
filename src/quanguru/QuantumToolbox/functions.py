r"""
    Contains functions to calculate some basic quantities, such as expectations, fidelities, entropy etc.

    .. currentmodule:: quanguru.QuantumToolbox.functions

    Functions
    ---------

    .. autosummary::
        expectation

    .. autosummary::
        fidelityPure
        traceDistance

    .. autosummary::
        entropy
        concurrence

    .. autosummary::
        sortedEigens

    .. autosummary::
        _expectationColArr

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `expectation`             |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `fidelityPure`            |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `_fidelityTest`           |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `entropy`                 |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `traceDistance`           |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `sortedEigens`            |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `concurrence`             |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `_expectationColArr`      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `standardDev`             |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `spectralNorm`            |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

""" #pylint:disable=too-many-lines

from typing import List, Tuple
from numpy import ndarray # type: ignore

import numpy as np # type: ignore
import scipy.linalg as lina # type: ignore
from scipy.sparse import spmatrix # type: ignore

from .linearAlgebra import hc, tensorProd, trace, innerProd, _matPower
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


def expectation(operator: Matrix, state: Matrix) -> float:
    r"""
    Calculates the expectation value
    :math:`\langle \hat{O}\rangle := \langle \psi | \hat{O} |\psi \rangle \equiv
    \textrm{Tr}(\hat{O}|\psi \rangle\langle \psi |)`
    of an `operator` :math:`\hat{O}`
    for a given `state` :math:`|\psi \rangle`.

    State can either be a `ket` or `density matrix`.
    State and operator can both be sparse or array or any combination of the two.

    Calculates the :func:`densityMatrix <quanguru.QuantumToolbox.states.densityMatrix>`, then uses
    :func:`trace <quanguru.QuantumToolbox.linearAlgebra.trace>`.

    Operator has to be the matrix (sparse or not), cannot pass a reference to operator function from the toolbox.

    Parameters
    ----------
    operator : Matrix
        an operator as a matrix
    state : Matrix
        a quantum state

    Returns
    -------
    float
        expectation value of the `operator` for the `state`

    Examples
    --------
    >>> ket = basis(dimension=2, state=1)
    >>> expectation(operator=sigmaz(), state=ket)
    -1
    >>> denMat = densityMatrix(ket)
    >>> expectation(sigmaz(), denMat)
    -1

    >>> ket1 = basis(dimension=2, state=0)
    >>> expectation(operator=sigmaz(), state=ket1)
    1
    >>> denMat1 = densityMatrix(ket1)
    >>> expectation(operator=sigmaz(), state=denMat1)
    1

    >>> ket2 = np.sqrt(0.5)*basis(dimension=2, state=1) + np.sqrt(0.5)*basis(dimension=2, state=0)
    >>> expectation(operator=sigmaz(), state=ket2)
    0
    >>> denMat2 = densityMatrix(ket2)
    >>> expectation(operator=sigmaz(), state=denMat2)
    0

    """

    if state.shape[0] != state.shape[1]:
        state = densityMatrix(state)
    expc = trace(operator @ state)
    return np.real(expc) if np.round(expc.imag, 12) == 0.0 else expc

def fidelityPure(state1: Matrix, state2: Matrix) -> float:
    r"""
    Calculates `fidelity`
    :math:`\mathcal{F}(\psi_{1}, \psi_{2}) := |\langle \psi_{2}|\psi_{1}\rangle|^{2} =
    Tr(|\psi_{1}\rangle\langle \psi_{1}|\psi_{2}\rangle|\psi_{2}\rangle)`
    between `two pure states`.

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
    >>> ket0 = basis(dimension=2, state=1)
    >>> ket1 = basis(dimension=2, state=0)
    >>> ket2 = np.sqrt(0.5)*basis(dimension=2, state=1) + np.sqrt(0.5)*basis(dimension=2, state=0)
    >>> fidelity(state1=ket0, state2=ket1)
    0.
    >>> fidelity(state1=ket0, state2=ket2)
    0.5
    >>> fidelity(state1=ket1, state2=ket2)
    0.5
    >>> denMat0 = densityMatrix(ket0)
    >>> denMat1 = densityMatrix(ket1)
    >>> denMat2 = densityMatrix(ket2)
    >>> fidelity(state1=denMat0, state2=denMat1)
    0
    >>> fidelity(state1=denMat0, state2=denMat2)
    0.5
    >>> fidelity(state1=denMat1, state2=denMat2)
    0.5

    """

    if ((state1.shape[0] != state1.shape[1]) and (state2.shape[0] != state2.shape[1])):
        fid = np.round(abs(innerProd(state1, state2)), 20)**2
    else:
        if state1.shape[0] != state1.shape[1]:
            state1 = densityMatrix(state1)

        if state2.shape[0] != state2.shape[1]:
            state2 = densityMatrix(state2)

        fid = np.real(trace(state1 @ state2))
    return fid

def _fidelityTest(state1: Matrix, state2: Matrix) -> float:
    r"""
    Calculates `fidelity`
    """
    if isinstance(state1, spmatrix):
        state1 = state1.A

    if isinstance(state2, spmatrix):
        state2 = state2.A
    matsqrt = lina.sqrtm(state1)
    fid = trace(lina.sqrtm(matsqrt @ state2  @ matsqrt))
    return np.real(fid**2)

def entropy(densMat: Matrix, base2: bool = False) -> float:
    r"""
    Calculates the `entropy` :math:`\mathcal{S}(\rho) := -Tr(\rho\ln\rho)`  of a given `density matrix` :math`\rho`.

    Input has to be a density matrix by definition, but works with a given ket state as well.
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
    >>> compositeStateKet = compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    >>> entropyKet(compositeStateKet)
    -0.0
    >>> compositeStateMat = densityMatrix(compositeStateKet)
    >>> entropy(compositeStateMat)
    -0.0
    >>> stateFirstSystem = partialTrace(keep=[0], dims=[2, 2], state=compositeStateKet)
    >>> entropy(stateFirstSystem)
    -0.0
    >>> stateSecondSystem = partialTrace(keep=[1], dims=[2, 2], state=compositeStateKet)
    >>> entropy(stateSecondSystem)
    -0.0

    >>> entangledKet = normalise(compositeState(dimensions=[2, 2], excitations=[0,1], sparse=True)
    + compositeState(dimensions=[2, 2], excitations=[1,0], sparse=True))
    >>> entropyKet(entangledKet)
    2.2204460492503126e-16
    >>> entangledMat = densityMatrix(entangledKet)
    >>> entropy(entangledMat)
    2.2204460492503126e-16
    >>> stateFirstSystemEntangled = partialTrace(keep=[0], dims=[2, 2], state=entangledKet)
    >>> entropy(stateFirstSystemEntangled)
    0.6931471805599454
    >>> stateSecondSystemEntangled = partialTrace(keep=[1], dims=[2, 2], state=entangledMat)
    >>> entropy(stateSecondSystemEntangled)
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

def traceDistance(A: Matrix, B: Matrix) -> float:
    r"""
    Calculates the trace distance :math:`\mathcal{T}(A, B) := \frac{1}{2}||A-B||_{1} =
    \frac{1}{2}Tr\left[\sqrt{(A-B)^{\dagger}(A-B)} \right]` between two matrices.

    # TODO implement a method for trace norm

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
    >>> PhiPlus = qt.densityMatrix(qt.BellStates('Phi+'))
    >>> qt.traceDistance(PhiPlus, PhiPlus)
    0.0
    >>> PhiMinus = qt.densityMatrix(qt.BellStates('Phi-'))
    >>> qt.traceDistance(PhiPlus, PhiMinus)
    1.0
    >>> fourZero = qt.densityMatrix(qt.basis(4, 0))
    >>> qt.traceDistance(PhiPlus, fourOne)
    0.7071067811865475

    """

    diff = A-B

    diff = hc(diff) @ diff
    if hasattr(diff, 'A'):
        diff = diff.A
    vals = lina.eig(diff)[0]
    return np.real(0.5 * np.sum(np.sqrt(np.abs(vals))))

def sortedEigens(Mat: Matrix, mag: bool = False) -> Tuple[floatList, List[ndarray]]:
    r"""
    Calculates `eigenvalues and eigenvectors` of a given matrix and `sorts` them.

    If `mag is True`, sort is accordingly with the magnitude of the eigenvalues.

    Parameters
    ----------
    Mat : Matrix
        a Matrix

    Returns
    -------
    Tuple[floatList, List[ndarray]]
        `sorted` eigenvalues and eigenvectors

    Examples
    --------
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

    if not isinstance(Mat, np.ndarray):
        Mat = Mat.A

    eigVals, eigVecs = lina.eig(Mat)
    if mag:
        mags = np.abs(eigVals)
        idx = mags.argsort()
    else:
        idx = eigVals.argsort()
    sortedVals = eigVals[idx]
    sortedVecs = eigVecs[:, idx]
    sortedVecsMat = [mat2Vec(sortedVecs[:, ind]) for ind in range(len(sortedVecs))]
    return sortedVals, sortedVecsMat

def concurrence(state: Matrix) -> float:
    r"""
    Calculates the `concurrence` :math:`\mathcal{C}(\rho) := \max(0, \lambda_{1}-\lambda_{2}-\lambda_{3}-\lambda_{4})`
    of two qubit state :math:`\rho`, where :math:`\lambda_{i}` are sorted eigenvalues
    :math:`R = \sqrt{\sqrt{\rho}\tilde{\rho}\sqrt{\rho}}` with
    :math:`\tilde{\rho} = (\sigma_{y}\otimes\sigma_{y})\rho^{*}(\sigma_{y}\otimes\sigma_{y})`.

    Works both with ket states and density matrices.

    Parameters
    ----------
    state : Matrix
        two qubit state

    Returns
    -------
    float
        concurrence of the state

    Examples
    --------
    >>> PhiPlus = qt.densityMatrix(qt.BellStates('Phi+'))
    >>> qt.concurrence(PhiPlus)
    1.0
    >>> PhiMinus = qt.densityMatrix(qt.BellStates('Phi-'))
    >>> qt.concurrence(PhiMinus)
    1.0
    >>> fourZero = qt.densityMatrix(qt.basis(4, 0))
    >>> qt.concurrence(fourZero)
    0.0

    """

    # sqrtState = lina.sqrtm(state)
    # SySy = tensorProd(sigmay(), sigmay())
    # magicConj = SySy @ state.conj() @ SySy
    # R = sqrtState @ magicConj @ sqrtState
    # eigVals, _ = sortedEigens(lina.sqrtm(R))
    # eigVals = np.real(eigVals)
    # print(eigVals)

    if state.shape[0] != state.shape[1]:
        state = densityMatrix(state)

    if not isinstance(state, np.ndarray):
        state = state.A

    SySy = tensorProd(sigmay(), sigmay())
    magicConj = SySy @ state.conj() @ SySy
    R = state @ magicConj
    eigValList, _ = sortedEigens(R)
    eigVals = np.real(np.sqrt(eigValList))
    return max([0, np.round(eigVals[3] - eigVals[2] - eigVals[1] - eigVals[0], 15)])

def _expectationColArr(operator: Matrix, states: ndarray) -> floatList:
    r"""
    Calculates expectation values of an `operator` for a list/matrix of `ket (column) states` by matrix multiplication.

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
    >>> import quanguru.QuantumToolbox.operators as qOperators
    >>> ham = qOperators.sigmaz(sparse=False)
    >>> eigVals, eigVecs = np.linalg.eig(ham)
    >>> sz = qOperators.sigmaz()
    >>> expectationColArr(sz, eigVecs)
    [ 1. -1.]

    >>> sx = qOperators.sigmax()
    >>> expectationColArr(sx, eigVecs)
    [0. 0.]
    """

    expMat = hc(states) @ operator @ states
    return expMat.diagonal()

def standardDev(operator: Matrix, state: Matrix, expect: bool = False) -> float:
    expSq = (expectation(operator, state))
    SqExp = expectation(_matPower(operator, 2), state)
    return np.sqrt(SqExp - (expSq**2)) if not expect else (np.sqrt(SqExp - (expSq**2)), expSq)

def spectralNorm(operator: Matrix) -> Tuple:
    vals, _ = sortedEigens(hc(operator)@operator)
    return (np.sqrt(np.real(max(vals))), vals)
