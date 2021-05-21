r"""
    Contains functions to create Unitary and open-system super-operators.

    .. currentmodule:: QuanGuru.QuantumToolbox.evolution

    Functions
    ---------

    .. autosummary::
        Unitary
        Liouvillian
        LiouvillianExp

        dissipator
        _preSO
        _posSO
        _preposSO
"""

from typing import Optional

import scipy.sparse as sp # type: ignore
import scipy.linalg as linA # type: ignore
import scipy.sparse.linalg as slinA # type: ignore

from .linearAlgebra import hc

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


def Liouvillian(Hamiltonian: Optional[Matrix] = None, # pylint: disable=dangerous-default-value,unsubscriptable-object
                collapseOperators: list = [], decayRates: list = []) -> Matrix:# pylint: disable=dangerous-default-value
    r"""
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

    if Hamiltonian is not None:
        dimensionOfHilbertSpace = Hamiltonian.shape[0]
    else:
        dimensionOfHilbertSpace = collapseOperators[0].shape[0]

    identity = sp.identity(dimensionOfHilbertSpace, format="csc")
    hamPart1 = _preSO(Hamiltonian, identity)
    hamPart2 = _posSO(Hamiltonian, identity)
    hamPart = -1j * (hamPart1 - hamPart2)
    liouvillian = hamPart
    for idx, collapseOperator in enumerate(collapseOperators):
        collapsePart = dissipator(collapseOperator, identity)
        if len(decayRates) != 0:
            liouvillian += decayRates[idx]*collapsePart
        else:
            liouvillian += collapsePart
    return liouvillian


def LiouvillianExp(Hamiltonian: Optional[Matrix] = None, timeStep: float = 1.0,# pylint: disable=dangerous-default-value,unsubscriptable-object # noqa: E501
                   collapseOperators: list = [], decayRates: list = [],
                   exp: bool = True) -> Matrix: # pylint: disable=dangerous-default-value
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
        sparse = sp.issparse(collapseOperators[0])

    if len(collapseOperators) > 0:
        liouvillian = Liouvillian(Hamiltonian, collapseOperators, decayRates)
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


def dissipator(collapseOperator: Matrix, identity: Optional[Matrix] = None) -> Matrix:#pylint:disable=unsubscriptable-object
    r"""
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
        identity = sp.identity(collapseOperator.shape[0], format="csc")

    dagger = hc(collapseOperator)

    number = dagger @ collapseOperator
    part1 = _preposSO(collapseOperator)
    part2 = _preSO(number, identity)
    part3 = _posSO(number, identity)
    return part1 - (0.5 * (part2 + part3))


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


def _posSO(operator: Matrix, identity: Matrix = None) -> Matrix:
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
        `pos` super-operator

    Examples
    --------
    >>> evolution._posSO(sigmam()).A
    array([[0., 0., 1., 0.],
           [0., 0., 0., 1.],
           [0., 0., 0., 0.],
           [0., 0., 0., 0.]])

    """

    if identity is None:
        identity = sp.identity(operator.shape[0], format="csc")
    pos = sp.kron(operator.transpose(), identity, format='csc')
    return pos if sp.issparse(operator) else pos.A


def _preposSO(operator: Matrix) -> Matrix:
    r"""
    Creates `pre-pos super-operator` :math:`(\hat{O}^{\dagger})^{T}\otimes\hat{O}` for an operator :math:`\hat{O}`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    operator : Matrix
        a collapse operator
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    Matrix
        `pre-pos` super-operator

    Examples
    --------
    >>> evolution._preposSO(sigmam()).A
    array([[0, 0, 0, 0],
           [0, 0, 0, 0],
           [0, 0, 0, 0],
           [1, 0, 0, 0]], dtype=int64)

    """

    prepos = sp.kron(operator.conj(), operator, format='csc')
    return prepos if sp.issparse(operator) else prepos.A
