r"""
    Contains functions to create Unitary and open-system super-operators.

    .. currentmodule:: quanguru.QuantumToolbox.evolution

    Functions
    ---------

    .. autosummary::
        Unitary
        Liouvillian
        LiouvillianExp

        dissipator
        _preSO
        _postSO
        _prepostSO

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `Unitary`                 |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `Liouvillian`             |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `LiouvillianExp`          |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `dissipator`              |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `_preSO`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `_postSO`                 |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `_prepostSO`              |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from typing import Callable, List, Optional

import scipy.sparse as sp # type: ignore
import scipy.linalg as linA # type: ignore
import scipy.sparse.linalg as slinA # type: ignore

from .linearAlgebra import hc
from .functions import sortedEigens
from .states import densityMatrix, mat2Vec, vec2Mat, zerosMat

from .customTypes import Matrix


# do not delete these
# from typing import Optional, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


def Unitary(Hamiltonian: Matrix, timeStep: float = 1.0) -> Matrix:
    r"""
    Creates `Unitary` time evolution operator :math:`U(t) := e^{-i\hat{H}t}` for a given `Hamiltonian` :math:`\hat{H}`
    and `time step t`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    Hamiltonian : Matrix
        Hamiltonian of the system
    timeStep : float
        time used in the exponentiation (default=1.0)

    Returns
    -------
    Matrix
        Unitary time evolution operator

    Examples
    --------
    >>> Unitary(2*np.pi*sigmaz(), 1).A
    array([[1.+2.4492936e-16j, 0.+0.0000000e+00j],
           [0.+0.0000000e+00j, 1.-2.4492936e-16j]])

    """

    sparse = sp.issparse(Hamiltonian)
    if sparse is True:
        liouvillianEXP = slinA.expm(-1j * Hamiltonian * timeStep)
    else:
        liouvillianEXP = linA.expm(-1j * Hamiltonian * timeStep)
    return liouvillianEXP

def Liouvillian(Hamiltonian: Optional[Matrix] = None, collapseOperators: Optional[List] = None, # pylint: disable=dangerous-default-value,unsubscriptable-object
                decayRates: Optional[List] = None, _double: bool = False) -> Matrix:# pylint: disable=dangerous-default-value
    r"""
    TODO : I have generalised the functions, docs need to be updated.
    Creates `Liouvillian` super-operator
    :math:`\hat{\mathcal{L}} := -i(\hat{H}\otimes\mathbb{I} + \mathbb{I}\otimes\hat{H}) +
    \sum_{i}\kappa_{i}\hat{\mathcal{D}}(\hat{c}_{i})`
    for a `Hamiltonian` :math:`\hat{H}`
    and `collapse operators` :math:`\{\hat{c}_{i}\}` (with corresponding `decay rates` :math:`\{\kappa_{i}\}`).

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    Hamiltonian : Matrix or None
        Hamiltonian of the system
    collapseOperators : list (of Matrix)
        `list` of collapse operator for Lindblad dissipator terms
    decayRates` : list (of float)
        `list` of decay rates (if not given assumed to be 1)

    Returns
    -------
    Matrix
        Liouvillian super-operator

    Examples
    --------
    >>> Liouvillian(2*np.pi*sigmaz(), [2*np.pi*sigmaz()], [1]).A
    array([[  0.         +0.j        ,   0.         +0.j        ,
              0.         +0.j        ,   0.         +0.j        ],
           [  0.         +0.j        , -78.95683521+12.56637061j,
              0.         +0.j        ,   0.         +0.j        ],
           [  0.         +0.j        ,   0.         +0.j        ,
            -78.95683521-12.56637061j,   0.         +0.j        ],
           [  0.         +0.j        ,   0.         +0.j        ,
              0.         +0.j        ,   0.         +0.j        ]])

    """
    # TODO : Liouvillian docs need to be updated.
    #  functions are generalized.
    if Hamiltonian is not None:
        dimensionOfHilbertSpace = Hamiltonian.shape[0]
    else:
        if collapseOperators is not None:
            dimensionOfHilbertSpace = collapseOperators[0].shape[0]

    identity = sp.identity(dimensionOfHilbertSpace, format="csc")
    liouvillian = zerosMat(dimensionOfHilbertSpace**2)
    if Hamiltonian is not None:
        hamPart1 = _preSO(Hamiltonian, identity)
        hamPart2 = _postSO(Hamiltonian, identity)
        hamPart = -1j * (hamPart1 - hamPart2)
        liouvillian += hamPart

    if isinstance(collapseOperators, list):
        for idx, collapseOperator in enumerate(collapseOperators):
            if collapseOperator.shape[0] == dimensionOfHilbertSpace:
                collapsePart = dissipator(collapseOperator, identity=identity, _double=_double)
            elif collapseOperator.shape[0] == (dimensionOfHilbertSpace**2):
                collapsePart = collapseOperator
            elif isinstance(collapseOperator, tuple):
                collapsePart = dissipator(collapseOperator[0], collapseOperator[1], _double=_double)
            else:
                raise ValueError("Dimension mismatch")

            if decayRates is None:
                liouvillian += collapsePart
            elif len(decayRates) != 0:
                liouvillian += decayRates[idx]*collapsePart
    return liouvillian

def LiouvillianExp(Hamiltonian: Optional[Matrix] = None, timeStep: float = 1.0,# pylint: disable=dangerous-default-value,unsubscriptable-object # noqa: E501
                   collapseOperators: Optional[List] = None, decayRates: Optional[List] = None,
                   exp: bool = True, _double: bool = False) -> Matrix: # pylint: disable=dangerous-default-value
    r"""
    For a `time step t`, creates `Liouvillian` :math:`\hat{\mathcal{L}}` and exponentiate it, or unitary :math:`U(t)`
    for a `Hamiltonian` :math:`\hat{H}`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    Hamiltonian : Matrix or None
        Hamiltonian of the system
    timeStep : float
        time used in the exponentiation (default=1)
    collapseOperators : list (of Matrix)
        `list` of collapse operator for Lindblad dissipator terms
    decayRates : list (of float)
        `list` of decay rates (if not given assumed to be 1)
    exp : bool
        boolean to exponentiate the Liouvillian or not (=True by default)

    Returns
    -------
    Matrix
        (exponentiated) Liouvillian super-operator

    Examples
    --------
    >>> LiouvillianExp(2*np.pi*sigmaz(), 1, [], []).A
    array([[1.+2.4492936e-16j, 0.+0.0000000e+00j],
           [0.+0.0000000e+00j, 1.-2.4492936e-16j]])

    >>> LiouvillianExp(2*np.pi*sigmaz(), 1, [2*np.pi*sigmaz()], [1]).A
    array([[1.00000000e+00+0.00000000e+00j, 0.00000000e+00+0.00000000e+00j,
            0.00000000e+00+0.00000000e+00j, 0.00000000e+00+0.00000000e+00j],
           [0.00000000e+00+0.00000000e+00j, 5.12250228e-35-2.50930241e-50j,
            0.00000000e+00+0.00000000e+00j, 0.00000000e+00+0.00000000e+00j],
           [0.00000000e+00+0.00000000e+00j, 0.00000000e+00+0.00000000e+00j,
            5.12250228e-35+2.50930241e-50j, 0.00000000e+00+0.00000000e+00j],
           [0.00000000e+00+0.00000000e+00j, 0.00000000e+00+0.00000000e+00j,
            0.00000000e+00+0.00000000e+00j, 1.00000000e+00+0.00000000e+00j]])
    """

    if Hamiltonian is not None:
        sparse = sp.issparse(Hamiltonian)
    else:
        if collapseOperators is not None:
            sparse = sp.issparse(collapseOperators[0])

    if isinstance(collapseOperators, list):
        liouvillian = Liouvillian(Hamiltonian, collapseOperators, decayRates, _double=_double)
        if exp is True:
            if sparse is True:
                liouvillianEXP = slinA.expm(liouvillian * timeStep)
            elif sparse is False:
                liouvillianEXP = linA.expm(liouvillian * timeStep)
        else:
            liouvillianEXP = liouvillian
    else:
        liouvillianEXP = Unitary(Hamiltonian, timeStep)
    return liouvillianEXP

def dissipator(operatorA: Matrix, operatorB: Optional[Matrix] = None,
               identity: Optional[Matrix] = None, _double: bool = False) -> Matrix:#pylint:disable=unsubscriptable-object
    r"""
    TODO : I have generalised the functions, docs need to be updated.
    Creates the `Lindblad dissipator` super-operator
    :math:`\hat{\mathcal{D}}(\hat{c}) := (\hat{c}^{\dagger})^{T}\otimes\hat{c} -
    0.5(\mathbb{I}\otimes\hat{c}^{\dagger}\hat{c} + \hat{c}^{\dagger}\hat{c}\otimes\mathbb{I})`
    for a `collapse operator` :math:`\hat{c}`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    collapseOperator : Matrix
        a collapse operator
    identity : Matrix or None
        identity operator (exist for internal use and optimisation)

    Returns
    -------
    Matrix
        Lindblad dissipator

    Examples
    --------
    >>> dissipator(sigmaz()).A
    array([[ 0.,  0.,  0.,  0.],
           [ 0., -2.,  0.,  0.],
           [ 0.,  0., -2.,  0.],
           [ 0.,  0.,  0.,  0.]])

    >>> dissipator(sigmam()).A
    array([[-1. ,  0. ,  0. ,  0. ],
           [ 0. , -0.5,  0. ,  0. ],
           [ 0. ,  0. , -0.5,  0. ],
           [ 1. ,  0. ,  0. ,  0. ]])

    """
    if identity is None:
        identity = sp.identity(operatorA.shape[0], format="csc")

    if operatorB is None:
        operatorB = hc(operatorA)

    number = operatorB @ operatorA
    part1 = _prepostSO(operatorA, operatorB)
    part2 = _preSO(number, identity)
    part3 = _postSO(number, identity)
    return (1+int(_double))*(part1 - (0.5 * (part2 + part3)))

def _preSO(operator: Matrix, identity: Matrix = None) -> Matrix:
    r"""
    Creates `pre super-operator` :math:`\mathbb{I}\otimes\hat{O}` for an `operator` :math:`\hat{O}`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    operator : Matrix
        a collapse operator
    identity : Matrix or None
        identity operator (exist for internal use and optimisations)

    Returns
    -------
    Matrix
        `pre` super-operator

    Examples
    --------
    >>> evolution._preSO(sigmam()).A
    array([[0., 0., 0., 0.],
           [1., 0., 0., 0.],
           [0., 0., 0., 0.],
           [0., 0., 1., 0.]])

    """

    if identity is None:
        identity = sp.identity(operator.shape[0], format="csc")
    pre = sp.kron(identity, operator, format='csc')
    return pre if sp.issparse(operator) else pre.A

def _postSO(operator: Matrix, identity: Matrix = None) -> Matrix:
    r"""
    Creates `pos super-operator` :math:`\hat{O}^{T}\otimes\mathbb{I}` for an `operator` :math:`\hat{O}`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    operator : Matrix
        a collapse operator
    identity : Matrix or None
        identity operator (exist for internal use and optimisations)

    Returns
    -------
    Matrix
        `post` super-operator

    Examples
    --------
    >>> evolution._postSO(sigmam()).A
    array([[0., 0., 1., 0.],
           [0., 0., 0., 1.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.]])

    """

    if identity is None:
        identity = sp.identity(operator.shape[0], format="csc")
    pos = sp.kron(operator.transpose(), identity, format='csc')
    return pos if sp.issparse(operator) else pos.A

def _prepostSO(operatorA: Matrix, operatorB: Optional[Matrix] = None) -> Matrix:
    r"""
    TODO : I have generalised the functions, docs need to be updated.
    Creates `pre-pos super-operator` :math:`(\hat{B}^{\dagger})^{T}\otimes\hat{A}` for an operator :math:`\hat{O}`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    operatorA : Matrix
        collapse operator A
    operatorB : Matrix
        collapse operator B

    Returns
    -------
    Matrix
        `pre-post` super-operator

    Examples
    --------
    >>> evolution._prepostSO(sigmam()).A
    array([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [1, 0, 0, 0]], dtype=int64)

    """
    if operatorB is None:
        operatorB = operatorA
    prepost = sp.kron(operatorB.transpose(), operatorA, format='csc')
    return prepost if sp.issparse(operatorA) else prepost.A

def evolveOpen(initialState, totalTime, timeStep: float = 1.0, Hamiltonian: Optional[Matrix] = None,# pylint: disable=dangerous-default-value,unsubscriptable-object,too-many-arguments # noqa: E501
               collapseOperators: Optional[List] = None, decayRates: Optional[List] = None,
               calcFunc: Optional[Callable] = None, delStates: Optional[bool] = False, _double: bool = False) -> Matrix: # pylint: disable=dangerous-default-value
    # TODO : write docstrings
    LiouExp = LiouvillianExp(Hamiltonian, timeStep=timeStep, collapseOperators=collapseOperators, decayRates=decayRates,
                             _double = _double)
    rhoL = initialState
    if initialState.shape[0] != initialState.shape[1]:
        rhoL = densityMatrix(initialState)
    resultList = [rhoL]
    if calcFunc is not None:
        calcFunc(rhoL)
    rhoL = mat2Vec(rhoL)
    for _ in range(int(totalTime/timeStep)):
        rhoL = LiouExp @ rhoL
        denMat = vec2Mat(rhoL)
        if calcFunc is not None:
            calcFunc(denMat)

        if not delStates:
            resultList.append(denMat)
    return resultList

def steadyState(Hamiltonian: Optional[Matrix] = None, collapseOperators: Optional[List] = None,# pylint: disable=dangerous-default-value,unsubscriptable-object # noqa: E501
               decayRates: Optional[List] = None, _double: bool = False) -> Matrix: # pylint: disable=dangerous-default-value
    # TODO : write docstrings
    Liou = LiouvillianExp(Hamiltonian, timeStep=1, collapseOperators=collapseOperators, decayRates=decayRates,
                          _double=_double)
    vals, vecs = sortedEigens(Liou, mag=True)
    return vals, vecs
