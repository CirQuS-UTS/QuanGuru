from numpy import exp

def nBarThermal(angFreq: float, temp: float, hbar: float = 1.0, kb: float = 1.0) -> float:
    """
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
    :return: float
        Average excitation number

    Raises
    ------
    ValueError
        If average number is infinite.
    """
    if exp((hbar*angFreq) / (temp*kb)) == 1:
        raise ValueError('?')
    return 1.0 / (exp((hbar*angFreq) / (temp*kb)))
