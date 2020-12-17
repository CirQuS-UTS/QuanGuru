r"""
    Contains functions to create some standard Hamiltonians.

    .. currentmodule:: qTools.QuantumToolbox.Hamiltonians

    Functions
    ---------

    .. autosummary::

        qubCavFreeHam
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
def qubCavFreeHam(qubFreq: float, cavFreq: float, cavDim: int) -> Tuple[Matrix, Matrix]:
    r"""
    Creates Qubit + Cavity Hamiltonian :math:`\frac{\omega_{q}}{2}\hat{\sigma}_{z} + \omega_{c}\hat{a}^{\dagger}\hat{a}`
    for
    given frequencies and truncated cavity dimension.

    Hilbert space ordering is :math:`Qubit\otimes Cavity`, i.e. qubit first.

    Parameters
    ----------
    qubFreq : float
        qubit frequency
    cavFreq : float
        cavity frequency
    cavDim : int
        (truncated) dimension for cavity

    Returns
    -------
    Matrix
        Qubit + Cavity Hamiltonian for given frequencies and truncated cavity dimension.

    Examples
    --------
    # TODO
    """

    cavHam = cavFreq * sp.kron(identity(2), number(cavDim), format='csc')
    qubHam = qubFreq * sp.kron(sigmaz(), identity(cavDim), format='csc')
    return cavHam, qubHam


def RabiHam(qubFreq: float, cavFreq: float, g: float, cavDim: int) -> Matrix:
    r"""
    Creates Rabi Hamiltonian :math:`\frac{\omega_{q}}{2}\hat{\sigma}_{z} + \omega_{c}\hat{a}^{\dagger}\hat{a}
    + g\hat{\sigma}_{x}(\hat{a}^{\dagger} + \hat{a})` for given frequencies, coupling strength, and truncated cavity
    dimension.

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

    cavHam, qubHam = qubCavFreeHam(qubFreq, cavFreq, cavDim)
    couplingRabi = g*(sp.kron(sigmax(), create(cavDim) + destroy(cavDim), format='csc'))

    rabiHam = cavHam + qubHam + couplingRabi
    return rabiHam


def JCHam(qubFreq: float, cavFreq: float, g: float, cavDim: int) -> Matrix:
    r"""
    Creates Jaynes-Cummings Hamiltonian :math:`\frac{\omega_{q}}{2}\hat{\sigma}_{z} + \omega_{c}\hat{a}^{\dagger}\hat{a}
    + g(\hat{\sigma}_{-}\hat{a}^{\dagger} + \hat{\sigma}_{+}\hat{a})` for given frequencies, coupling strength, and
    truncated
    cavity dimension.

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

    cavHam, qubHam = qubCavFreeHam(qubFreq, cavFreq, cavDim)
    couplingJC = g*(sp.kron(sigmam(), create(cavDim), format='csc') + sp.kron(sigmap(), destroy(cavDim), format='csc'))
    JCHamil = cavHam + qubHam + couplingJC
    return JCHamil


def aJCHam(qubFreq: float, cavFreq: float, g: float, cavDim: int) -> Matrix:
    r"""
    Creates anti-Jaynes-Cummings Hamiltonian :math:`\frac{\omega_{q}}{2}\hat{\sigma}_{z} +
    \omega_{c}\hat{a}^{\dagger}\hat{a}
    + g(\hat{\sigma}_{+}\hat{a}^{\dagger} + \hat{\sigma}_{-}\hat{a})` for given frequencies, coupling strength, and
    truncated
    cavity dimension.

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

    cavHam, qubHam = qubCavFreeHam(qubFreq, cavFreq, cavDim)
    couplingAJC = g*(sp.kron(sigmap(), create(cavDim), format='csc') + sp.kron(sigmam(), destroy(cavDim), format='csc'))
    AJCHamil = cavHam + qubHam + couplingAJC
    return AJCHamil
