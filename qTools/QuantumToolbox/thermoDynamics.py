from numpy import exp, real # type: ignore
from .states import mat2Vec, vec2Mat
from .customTypes import Matrix

def nBarThermal(angFreq: float, temp: float, hbar: float = 1.0, kb: float = 1.0) -> float:
    r"""
    Calculates the average excitation number for a Harmonic oscillator with frequeny `freq` at a temperature `temp`.
    Boltzmann and reduced Planck constants are by default :math:`\\hbar = k_{B} = 1`.
    TODO Physical constants' default values should be connected to simUnits.

    Parameters
    ----------
    angFreq : float
        (angular) frequency of the Harmonic oscillator
    temp : float
        temperature of the Harmonic oscillator
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
    """

    if exp((hbar*angFreq) / (temp*kb)) == 1:
        raise ValueError('?')
    return 1.0 / (exp((hbar*angFreq) / (temp*kb)))


def HeatCurrent(Lindbladian: Matrix, Hamiltonian: Matrix, denMat: Matrix) -> float:
    r"""
    Calculates the heat current from a quantum system due to a Lindbladian term. It does not strictly speaing have to be
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
    """

    full = mat2Vec(Lindbladian * vec2Mat(denMat))
    heatCurrent = real((full * Hamiltonian).tr())
    return heatCurrent


def qubitPolarisation(freq: float, temp: float) -> float:
    r"""
    Returns the qubit polarisation for a given frequency and temperature.

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
    """

    populationRatio = exp(-freq/temp)
    groundPop = 1/(1+populationRatio)
    return 1 - (2*groundPop)
