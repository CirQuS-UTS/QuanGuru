r"""
    Contains methods to calculate certain quantities used in thermal states, open systems, and quantum thermodynamics.
    TODO update docstring examples and write some tests after writing some tutorials

    .. currentmodule:: quanguru.QuantumToolbox.thermodynamics

    Functions
    ---------

    .. autosummary::

        nBarThermal
        qubitPolarisation
        HeatCurrent

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `nBarThermal`             |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `qubitPolarisation`       |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `HeatCurrent`             |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from numpy import exp, real # type: ignore
from .states import mat2Vec, vec2Mat
from .customTypes import Matrix

def nBarThermal(angFreq: float, temp: float, hbar: float = 1.0, kb: float = 1.0) -> float:
    r"""
    Calculates average excitation number :math:`\bar{n}(T) := 1/(e^{\hbar \omega / k_{b}T} - 1)` of a bosonic field with
    frequeny :math:`\omega` at a temperature T.
    Boltzmann and reduced Planck constants are by default :math:`\hbar = k_{B} = 1`.
    TODO Physical constants' default values should be connected to simUnits.

    Parameters
    ----------
    angFreq : float
        (angular) frequency of the bosonic field
    temp : float
        temperature
    hbar : float
        reduced Planck's constant
    kb : float
        Boltzmann constant

    Returns
    -------
    float
        Average excitation number

    Raises
    ------
    ValueError
        If average number is infinite.

    Examples
    --------
    # TODO
    """

    if temp == 0:
        return 0
    if exp((hbar*angFreq) / (temp*kb)) == 1:
        raise ValueError('?')
    return 1.0 / (exp((hbar*angFreq) / (temp*kb)) - 1)

def qubitPolarisation(freq: float, temp: float) -> float:
    r"""
    Returns the polarisation :math:`\langle\hat{\sigma}_{z}\rangle := P_{1} - P_{0}` of a qubit with frequency
    :math:`\omega`
    in a thermal state of temperature T. :math:`P_{1}` and :math:`P_{0}` are excited and ground state populations
    satisfying :math:`P_{1} + P_{0} = 1`, and thermal state populations also satisfy
    :math:`\frac{P_{1}}{P_{0}} := e^{\omega/T}`.

    Parameters
    ----------
    freq : float
        frequency of the qubit
    temp : float
        temperature of the qubit

    Returns
    -------
    float
        qubit polarisation, i.e. difference betwennn ground and excited state populations.

    Examples
    --------
    # TODO
    """

    populationRatio = exp(-freq/temp)
    groundPop = 1/(1+populationRatio)
    return 1 - (2*groundPop)

def HeatCurrent(Lindbladian: Matrix, Hamiltonian: Matrix, denMat: Matrix) -> float:
    r"""
    Calculates the heat current :math:`\mathcal{J}:=Tr(\dot{\rho}\hat{H})`, where
    :math:`\dot{\rho} := \hat{\mathcal{L}}\rho` is obtained using the given Lindbladian
    :math:`\hat{\mathcal{L}}`.
    Here, :math:`\hat{H}` is the system Hamiltonian, and the time derivative of density matrix is
    :math:`\dot{\rho}mathcal{L}`. It does not strictly speaking have to be
    a Lindbladian but any combination of terms from a Liouvillian. Disclaimer: physical meaning of those terms is not
    and cannot be interpreted by this function.
    TODO Write a bit of the theory here to better explain this function.

    Parameters
    ----------
    Lindbladian : Matrix
        a Lindbladian or any combination of terms from a Liouvillian
    Hamiltonian : Matrix
        Hamiltonian of the system
    denMat : Matrix
        Density matrix (state) of the system

    Returns
    -------
    float
        Heat current

    Examples
    --------
    # TODO
    """

    full = mat2Vec(Lindbladian * vec2Mat(denMat))
    heatCurrent = real((full * Hamiltonian).tr())
    return heatCurrent
