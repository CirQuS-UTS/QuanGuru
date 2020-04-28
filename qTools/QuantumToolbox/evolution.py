"""
    Module of functions to create Unitary operator and open-system super-operators.

    Methods
    -------
    :Unitary : Creates Unitary time evolution operator for a given Hamiltonian and time step
    :Liouvillian : Creates Liovillian super-operator for a given Hamiltonian, time step,
                    and a `list` of collapse operators (with correcponding `list` of decay rates)
    :LiouvillianExp : Creates Liovillian super-operator (and exponentiates) for a given Hamiltonian, time step,
                    and a `list` of collapse operators (with correcponding `list` of decay rates)
    :dissipator : Creates the Lindblad dissipator super-operator for a collapse operator
    :_preSO : Creates `pre` super-operator for an operator
    :_posSO : Creates `pos` super-operator for an operator
    :_preposSO : Creates `pre-pos` super-operator for an operator
"""

from typing import Optional

import scipy.sparse as sp
import scipy.linalg as linA
import scipy.sparse.linalg as slinA
import numpy as np

from .customTypes import Matrix

# from typing import Optional, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)'''


def Unitary(Hamiltonian: Matrix, timeStep: float = 1.0) -> Matrix:
    """
    Creates Unitary time evolution operator for a given Hamiltonian and time step

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `Hamiltonian` : Hamiltonian of the system
    :param `timeStep` : time used in the exponentiation (default=1)

    Returns
    -------
    :return: Unitary time evolution operator

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


def Liouvillian(Hamiltonian: Optional[Matrix] = None,
                collapseOperators: Optional[list] = list, decayRates: Optional[list] = list) -> Matrix:
    """
    Creates Liovillian super-operator for a given Hamiltonian, time step,
    and a `list` of collapse operators (with correcponding `list` of decay rates)

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `Hamiltonian` : Hamiltonian of the system
    :param `timeStep` : time used in the exponentiation (default=1)
    :param `collapseOperators` : `list` of collapse operator for Lindblad dissipator terms
    :param `decayRates` : `list` of decay rates (if not given assumed to be 1)

    Returns
    -------
    :return: Liovillian super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    if Hamiltonian is not None:
        sparse = sp.issparse(Hamiltonian)
    else:
        sparse = sp.issparse(collapseOperators[0])

    dimensionOfHilbertSpace = Hamiltonian.shape[0]
    if sparse is False:
        identity = np.identity(dimensionOfHilbertSpace)
    elif sparse is True:
        identity = sp.identity(dimensionOfHilbertSpace, format="csc")
    hamPart1 = _preSO(Hamiltonian, identity, sparse)
    hamPart2 = _posSO(Hamiltonian, identity, sparse)
    hamPart = -1j * (hamPart1 - hamPart2)
    liouvillian = hamPart
    for idx, collapseOperator in enumerate(collapseOperators):
        collapsePart = dissipator(collapseOperator, identity)
        if len(decayRates) != 0:
            liouvillian += decayRates[idx]*collapsePart
        else:
            liouvillian += collapsePart
    return liouvillian


def LiouvillianExp(Hamiltonian: Optional[Matrix] = None, timeStep: float = 1.0,
                   collapseOperators: Optional[list] = list, decayRates: Optional[list] = list, exp: bool = True) -> Matrix:
    """
    Creates Liovillian super-operator for a given Hamiltonian, time step,
    and a `list` of collapse operators (with correcponding `list` of decay rates)

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `Hamiltonian` : Hamiltonian of the system
    :param `timeStep` : time used in the exponentiation (default=1)
    :param `collapseOperators` : `list` of collapse operator for Lindblad dissipator terms
    :param `decayRates` : `list` of decay rates (if not given assumed to be 1)
    :param `exp` : boolean to exponentiate the Liouvillian or not (=True by default)

    Returns
    -------
    :return: (exponentiated) Liovillian super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    if Hamiltonian is not None:
        sparse = sp.issparse(Hamiltonian)
    else:
        sparse = sp.issparse(collapseOperators[0])

    if isinstance(collapseOperators, list):
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
    Creates the Lindblad dissipator super-operator for a collapse operator

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `collapseOperator` : a collapse operator
    :param `identity` : identity operator (exist for internal use and optimisation)

    Returns
    -------
    :return: Lindblad dissipator

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
    part1 = _preposSO(collapseOperator, sparse)
    part2 = _preSO(number, identity, sparse)
    part3 = _posSO(number, identity, sparse)
    return part1 - (0.5 * (part2 + part3))


def _preSO(operator: Matrix, identity: Matrix, sparse: bool) -> Matrix:
    """
    Creates `pre` super-operator for an operator

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `operator` : a collapse operator
    :param `identity` : identity operator (exist for internal use and optimisations)

    Returns
    -------
    :return: `pre` super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    if sparse is True:
        pre = sp.kron(identity, operator, format='csc')
    else:
        pre = np.kron(identity, operator)
    return pre


def _posSO(operator: Matrix, identity: Matrix, sparse: bool) -> Matrix:
    """
    Creates `pos` super-operator for an operator

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `operator` : a collapse operator
    :param `identity` : identity operator (exist for internal use and optimisations)

    Returns
    -------
    :return: `pos` super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    if sparse is True:
        pos = sp.kron(operator.transpose(), identity, format='csc')
    else:
        pos = np.kron(np.transpose(operator), identity)
    return pos


def _preposSO(operator: Matrix, sparse: bool) -> Matrix:
    """
    Creates `pre-pos` super-operator for an operator

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `operator` : a collapse operator

    Returns
    -------
    :return: `pre-pos` super-operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    if sparse is True:
        prepos = sp.kron(operator.conj(), operator, format='csc')
    else:
        prepos = np.kron(np.conjugate(operator), operator)
    return prepos
