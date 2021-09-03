r"""
    Contains functions to create some standard Hamiltonians.

    .. currentmodule:: quanguru.QuantumToolbox.Hamiltonians

    Functions
    ---------

    .. autosummary::

        qubCavFreeHam
        RabiHam
        JCHam
        aJCHam
        UJC

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `qubCavFreeHam`           |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `RabiHam`                 |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `JCHam`                   |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `aJCHam`                  |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `UJC`                     |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |c|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

#from quanguru.QuantumToolbox.operators import number, identity, sigmaz, create, destroy, sigmax, sigmam, sigmap

from typing import Tuple
import scipy.sparse as sp # type: ignore
import numpy as np # type: ignore

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

def UJC(wq: float, wc: float, g: float, t: float, dimC: int, sparse=False) -> Matrix: #pylint:disable=too-many-arguments
    """ Analytical implementation of the time independante Jaynes-Cummings Unitary evolution
        see Stenholm 1973 (https://doi.org/10.1016/0370-1573(73)90011-2)
        #TODO: explain the basis

    Args:
        wq (float):
            qubit frequency
        wc (float):
            cavity frequency
        g (float):
            coupling strength
        t (float):
            evolution time
        dimC (int):
            cavity dimention

    Returns:
        Matrix:
            Unitary matrix describing free evolution of the Jaynes-Cummings model

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    D = wq-wc
    n = np.arange(1, dimC)
    U = np.zeros((2*dimC, 2*dimC), dtype=np.complex128)

    U[2*n, 2*n] = np.cos((n*g**2+D**2/4)**0.5*t)+1j/2*D*np.sin((n*g**2+D**2/4)**0.5*t)/(n*g**2+D**2/4)**0.5
    U[2*n, 2*n] *= np.exp(-1j*wc*(n-0.5)*t)
    U[2*n-1, 2*n-1] = np.cos((n*g**2+D**2/4)**0.5*t)-1j/2*D*np.sin((n*g**2+D**2/4)**0.5*t)/(n*g**2+D**2/4)**0.5
    U[2*n-1, 2*n-1] *= np.exp(-1j*wc*(n-0.5)*t)
    U[2*n, 2*n-1] = -1j*n**0.5*g*np.sin((n*g**2+D**2/4)**0.5*t)/(n*g**2+D**2/4)**0.5*np.exp(-1j*wc*(n-0.5)*t)
    U[2*n-1, 2*n] = -1j*n**0.5*g*np.sin((n*g**2+D**2/4)**0.5*t)/(n*g**2+D**2/4)**0.5*np.exp(-1j*wc*(n-0.5)*t)
    U[0, 0] = (np.cos(D/2*t)+1j*np.sin(D/2*t))*np.exp(1j*wc*0.5*t)
    U[-1, -1] = (np.cos(D/2*t)-1j*np.sin(D/2*t))*np.exp(-1j*wc*(dimC-0.5)*t)

    return sp.csc_matrix(U) if sparse else U
