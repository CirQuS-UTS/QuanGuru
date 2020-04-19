"""
    Module of functions to create some standard Hamiltonians.

    Methods
    -------
    :cavQubFreeHam : Creates Cavity + Qubit Hamiltonian for given frequencies and truncated cavity dimension
    :RabiHam : Creates Rabi Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension
    :JCHam : Creates Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension
    :aJCHam : Creates anti-Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension
"""

from qTools.QuantumToolbox.operators import number, identity, sigmaz, create, destroy, sigmax, sigmam, sigmap
import scipy.sparse as sp

#from .operators import number, identity, sigmaz, create, destroy, sigmax, sigmam, sigmap
#from .customTypes import Matrix
#from typing import Tuple

from typing import Tuple, TypeVar
from numpy import ndarray
from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


# TODO currently, there is no option for sparse or not
def cavQubFreeHam(cavFreq:float, qubFreq:float, cavDim:int) -> Tuple[Matrix, Matrix]:
    """
    Creates Cavity + Qubit Hamiltonian for given frequencies and truncated cavity dimension

    Parameters
    ----------
    :param `cavFreq` : cavity frequency
    :param `qubFreq` : qubit frequency
    :param `cavDim` : (truncated) dimension for cavity

    Returns
    -------
    :return: Cavity + Qubit Hamitlonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    cavHam = cavFreq * sp.kron(number(cavDim), identity(2), format='csc')
    qubHam = qubFreq * sp.kron(identity(cavDim), sigmaz(), format='csc')
    return cavHam, qubHam


def RabiHam(cavFreq:float, qubFreq:float, g:float, cavDim:int) -> Matrix:
    """
    Creates Rabi Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension

    Parameters
    ----------
    :param `cavFreq` : cavity frequency
    :param `qubFreq` : qubit frequency
    :param `g` : coupling strength
    :param `cavDim` : (truncated) dimension for cavity

    Returns
    -------
    :return: Rabi Hamitlonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    cavHam, qubHam = cavQubFreeHam(cavFreq,qubFreq,cavDim)
    couplingRabi = g*(sp.kron(create(cavDim) + destroy(cavDim), sigmax(), format='csc'))

    rabiHam = cavHam + qubHam + couplingRabi
    return rabiHam


def JCHam(cavFreq:float, qubFreq:float, g:float, cavDim:int) -> Matrix:
    """
    Creates Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension

    Parameters
    ----------
    :param `cavFreq` : cavity frequency
    :param `qubFreq` : qubit frequency
    :param `g` : coupling strength
    :param `cavDim` : (truncated) dimension for cavity

    Returns
    -------
    :return: Jaynes-Cummings Hamitlonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    cavHam, qubHam = cavQubFreeHam(cavFreq, qubFreq, cavDim)
    couplingJC = g * (sp.kron(create(cavDim), destroy(2), format='csc') + sp.kron(destroy(cavDim), create(2), format='csc'))
    JCHam = cavHam + qubHam + couplingJC
    return JCHam


def aJCHam(cavFreq:float, qubFreq:float, g:float, cavDim:int) -> Matrix:
    """
    Creates anti-Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension

    Parameters
    ----------
    :param `cavFreq` : cavity frequency
    :param `qubFreq` : qubit frequency
    :param `g` : coupling strength
    :param `cavDim` : (truncated) dimension for cavity

    Returns
    -------
    :return: anti-Jaynes-Cummings Hamitlonian for given frequencies

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    
    cavHam, qubHam = cavQubFreeHam(cavFreq,qubFreq,cavDim)
    couplingAJC = g * (sp.kron(create(cavDim), create(2), format='csc') + sp.kron(destroy(cavDim), destroy(2), format='csc'))
    AJCHam = cavHam + qubHam + couplingAJC
    return AJCHam