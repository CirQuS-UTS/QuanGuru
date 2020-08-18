"""
    Module of functions to create Unitary operator and open-system super-operators.

    Functions
    ---------
    | :func:`Unitary`: Creates `Unitary` time evolution operator for a given `Hamiltonian` and `time step`.
    | :func:`Liouvillian`: Creates `Liouvillian super-operator` for a given `Hamiltonian`, `time step`,
        and a `list of collapse operators` (with the correcponding `list` of `decay rates`).
    | :func:`LiouvillianExp`: Creates `Liouvillian super-operator` (and exponentiates) for a given `Hamiltonian`,
        `time step`,
        and a `list of collapse operators` (with the correcponding `list` of `decay rates`).
    | :func:`dissipator`: Creates the `Lindblad dissipator` super-operator for a `collapse operator`.
    | :func:`_preSO`: Creates `pre super-operator` for an `operator`.
    | :func:`_posSO`: Creates `pos super-operator` for an `operator`.
    | :func:`_preposSO`: Creates `pre-pos super-operator` for an `operator`.

    Types
    -----
    | :const:`Matrix <qTools.QuantumToolbox.customTypes.Matrix>`: Union of (scipy) sparse and (numpy) array
"""

from typing import Optional

import scipy.sparse as sp # type: ignore
import scipy.linalg as linA # type: ignore
import scipy.sparse.linalg as slinA # type: ignore
import numpy as np # type: ignore

from .customTypes import Matrix


# do not delete these
# from typing import Optional, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


def Unitary(Hamiltonian: Matrix, timeStep: float = 1.0) -> Matrix:
    """
    Creates `Unitary` time evolution operator for a given `Hamiltonian` and `time step`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    Hamiltonian : Matrix
        Hamiltonian of the system
    timeStep : float
        time used in the exponentiation (default=1.0)

    Returns
    -------
    :return : Matrix
        Unitary time evolution operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    sparse = sp.issparse(Hamiltonian)
    if sparse is True:
        liouvillianEXP = slinA.expm(-1j * Hamiltonian * timeStep)
    else:
        liouvillianEXP = linA.expm(-1j * Hamiltonian * timeStep)
    return liouvillianEXP


def Liouvillian(Hamiltonian: Optional[Matrix] = None, # pylint: disable=dangerous-default-value
                collapseOperators: list = [], decayRates: list = []) -> Matrix:# pylint: disable=dangerous-default-value
    """
    Creates `Liouvillian` super-operator for a given `Hamiltonian`, `time step`,
    and a `list of collapse operators` (with the correcponding `list` of `decay rates`).

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
    :return : Matrix
        Liouvillian super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    if Hamiltonian is not None:
        sparse = sp.issparse(Hamiltonian)
        dimensionOfHilbertSpace = Hamiltonian.shape[0]
    else:
        sparse = sp.issparse(collapseOperators[0])
        dimensionOfHilbertSpace = collapseOperators[0].shape[0]

    if sparse is False:
        identity = np.identity(dimensionOfHilbertSpace)
    elif sparse is True:
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


def LiouvillianExp(Hamiltonian: Optional[Matrix] = None, timeStep: float = 1.0,# pylint: disable=dangerous-default-value
                   collapseOperators: list = [], decayRates: list = [],
                   exp: bool = True) -> Matrix: # pylint: disable=dangerous-default-value
    """
    Creates `Liovillian` super-operator for a given `Hamiltonian`, `time step`,
    and a `list of collapse operators` (with the correcponding `list` of `decay rates`).

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
    :return : Matrix
        (exponentiated) Liouvillian super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
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


def dissipator(collapseOperator: Matrix, identity: Optional[Matrix] = None) -> Matrix:
    """
    Creates the `Lindblad dissipator` super-operator for a `collapse operator`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    collapseOperator : Matrix
        a collapse operator
    identity : Matrix or None
        identity operator (exist for internal use and optimisation)

    Returns
    -------
    :return : Matrix
        Lindblad dissipator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    sparse = sp.issparse(collapseOperator)
    if identity is None:
        dimension = collapseOperator.shape[0]
        if sparse is True:
            identity = sp.identity(dimension, format="csc")
        else:
            identity = np.identity(dimension)

    dagger = collapseOperator.conj().T

    number = dagger @ collapseOperator
    part1 = _preposSO(collapseOperator)
    part2 = _preSO(number, identity)
    part3 = _posSO(number, identity)
    return part1 - (0.5 * (part2 + part3))


def _preSO(operator: Matrix, identity: Matrix = None) -> Matrix:
    """
    Creates `pre super-operator` for an `operator`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    operator : Matrix
        a collapse operator
    identity : Matrix or None
        identity operator (exist for internal use and optimisations)

    Returns
    -------
    :return : Matrix
        `pre` super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    sparse = sp.issparse(operator)
    if identity is None:
        dimension = operator.shape[0]
        if sparse is True:
            identity = sp.identity(dimension, format="csc")
        else:
            identity = np.identity(dimension)

    if sparse is True:
        pre = sp.kron(identity, operator, format='csc')
    else:
        pre = np.kron(identity, operator)
    return pre


def _posSO(operator: Matrix, identity: Matrix = None) -> Matrix:
    """
    Creates `pos` super-operator for an operator.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    operator : Matrix
        a collapse operator
    identity : Matrix or None
        identity operator (exist for internal use and optimisations)

    Returns
    -------
    :return : Matrix
        `pos` super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    sparse = sp.issparse(operator)
    if identity is None:
        dimension = operator.shape[0]
        if sparse is True:
            identity = sp.identity(dimension, format="csc")
        else:
            identity = np.identity(dimension)

    if sparse is True:
        pos = sp.kron(operator.transpose(), identity, format='csc')
    else:
        pos = np.kron(np.transpose(operator), identity)
    return pos


def _preposSO(operator: Matrix) -> Matrix:
    """
    Creates `pre-pos super-operator` for an operator.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    operator : Matrix
        a collapse operator
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return: Matrix
        `pre-pos` super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    sparse = sp.issparse(operator)

    if sparse is True:
        prepos = sp.kron(operator.conj(), operator, format='csc')
    else:
        prepos = np.kron(np.conjugate(operator), operator)
    return prepos
