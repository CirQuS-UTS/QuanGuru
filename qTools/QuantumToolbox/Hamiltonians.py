"""
    Module of functions to create some standard Hamiltonians.
"""
import qTools.QuantumToolbox.operators as ops
import scipy.sparse as sp

from typing import Union, Tuple
from numpy import ndarray
from scipy.sparse import spmatrix


# TODO currently, there is no option for sparse or not
def cavQubFreeHam(cavFreq:float, qubFreq:float, cavDim:int) -> Tuple[Union[spmatrix, ndarray], Union[spmatrix, ndarray]]:
    """
    Creates Cavity + Qubit Hamiltonian for given frequencies and truncated cavity dimension.

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
    cavHam = cavFreq * sp.kron(ops.number(cavDim), ops.identity(2), format='csc')
    qubHam = qubFreq * sp.kron(ops.identity(cavDim), ops.sigmaz(), format='csc')
    return cavHam, qubHam


def RabiHam(cavFreq:float, qubFreq:float, g:float, cavDim:int) -> Tuple[Union[spmatrix, ndarray], Union[spmatrix, ndarray]]:
    """
    Creates Rabi Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension.

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
    couplingRabi = g*(sp.kron(ops.create(cavDim) + ops.destroy(cavDim), ops.sigmax(), format='csc'))

    rabiHam = cavHam + qubHam + couplingRabi
    return rabiHam


def JCHam(cavFreq:float, qubFreq:float, g:float, cavDim:int) -> Tuple[Union[spmatrix, ndarray], Union[spmatrix, ndarray]]:
    """
    Creates Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension.

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
    couplingJC = g * (sp.kron(ops.create(cavDim), ops.destroy(2), format='csc') + sp.kron(ops.destroy(cavDim), ops.create(2), format='csc'))
    JCHam = cavHam + qubHam + couplingJC
    return JCHam


def aJCHam(cavFreq:float, qubFreq:float, g:float, cavDim:int) -> Tuple[Union[spmatrix, ndarray], Union[spmatrix, ndarray]]:
    """
    Creates anti-Jaynes-Cummings Hamiltonian for given frequencies, coupling strength, and truncated cavity dimension.

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
    couplingAJC = g * (sp.kron(ops.create(cavDim), ops.create(2), format='csc') + sp.kron(ops.destroy(cavDim), ops.destroy(2), format='csc'))
    AJCHam = cavHam + qubHam + couplingAJC
    return AJCHam