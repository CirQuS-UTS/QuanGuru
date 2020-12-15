r"""
    Module of functions to create some standard Hamiltonians.

    . currentmodule:: qTools.QuantumToolbox.Hamiltonians

    Functions
    ---------

    .. autosummary::

        cavQubFreeHam
        RabiHam
        JCHam
        aJCHam
"""

#from qTools.QuantumToolbox.operators import number, identity, sigmaz, create, destroy, sigmax, sigmam, sigmap

from typing import Tuple
import scipy.sparse as sp # type: ignore

from .operators import number, identity, sigmaz, create, destroy, sigmax, sigmam, sigmap
from .customTypes import Matrix


# do not delete these
# from typing import Tuple, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


# TODO currently, there is no option for sparse or not
def cavQubFreeHam(cavFreq: float, qubFreq: float, cavDim: int) -> Tuple[Matrix, Matrix]:
    r"""
    Creates Cavity + Qubit Hamiltonian for given frequencies and truncated cavity dimension.

    Parameters
    ----------
    cavFreq : float
        cavity frequency
    qubFreq : float
        qubit frequency
    cavDim : int
        (truncated) dimension for cavity

    Returns
    -------
    Matrix
        Cavity + Qubit Hamiltonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    cavHam = cavFreq * sp.kron(number(cavDim), identity(2), format='csc')
    qubHam = qubFreq * sp.kron(identity(cavDim), sigmaz(), format='csc')
    return cavHam, qubHam


def RabiHam(cavFreq: float, qubFreq: float, g: float, cavDim: int) -> Matrix:
    r"""
    Creates Rabi Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension.

    Parameters
    ----------
    cavFreq : float
        cavity frequency
    qubFreq : float
        qubit frequency
    g : float
        coupling strength
    cavDim : int
        (truncated) dimension for cavity

    Returns
    -------
    Matrix
        Rabi Hamiltonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    cavHam, qubHam = cavQubFreeHam(cavFreq, qubFreq, cavDim)
    couplingRabi = g*(sp.kron(create(cavDim) + destroy(cavDim), sigmax(), format='csc'))

    rabiHam = cavHam + qubHam + couplingRabi
    return rabiHam


def JCHam(cavFreq: float, qubFreq: float, g: float, cavDim: int) -> Matrix:
    r"""
    Creates Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension.

    Parameters
    ----------
    cavFreq : float
        cavity frequency
    qubFreq : float
        qubit frequency
    g : float
        coupling strength
    cavDim : int
        (truncated) dimension for cavity

    Returns
    -------
    Matrix
        Jaynes-Cummings Hamiltonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    cavHam, qubHam = cavQubFreeHam(cavFreq, qubFreq, cavDim)
    couplingJC = g * (sp.kron(create(cavDim), sigmam(), format='csc') + sp.kron(destroy(cavDim), sigmap(),
                                                                                format='csc'))
    JCHamil = cavHam + qubHam + couplingJC
    return JCHamil


def aJCHam(cavFreq: float, qubFreq: float, g: float, cavDim: int) -> Matrix:
    r"""
    Creates anti-Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension.

    Parameters
    ----------
    cavFreq : float
        cavity frequency
    qubFreq : float
        qubit frequency
    g : float
        coupling strength
    cavDim : int
        (truncated) dimension for cavity

    Returns
    -------
    Matrix
        anti-Jaynes-Cummings Hamiltonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    cavHam, qubHam = cavQubFreeHam(cavFreq, qubFreq, cavDim)
    couplingAJC = g * (sp.kron(create(cavDim), sigmap(), format='csc') + sp.kron(destroy(cavDim), sigmam(),
                                                                                 format='csc'))
    AJCHamil = cavHam + qubHam + couplingAJC
    return AJCHamil
