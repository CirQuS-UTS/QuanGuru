r"""
    Contains probability density functions (PDF) from Random Matrix Theory (RMT).

    .. currentmodule:: quanguru.QuantumToolbox.rmtDistributions

    Functions
    ---------

    .. autosummary::
        EigenVectorDist

    .. autosummary::
        WignerDyson
        WignerSurmise
        Poissonian

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `EigenVectorDist`         |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `WignerDyson`             |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `WignerSurmise`           |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `Poissonian`              |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from scipy.special import gammaln # type: ignore # pylint: disable=no-name-in-module
import numpy as np # type: ignore


def EigenVectorDist(x: float, dim: int, beta: int = 1) -> float:
    r"""
    Computes PDF :math:`P(x)` of eigenvector statistics at x for three universality classes
    (COE (beta=1), CUE (beta=2), and CSE (beta=4)) of dimension :math:`dim`.

    `Read here more details and derivations. <https://iopscience.iop.org/article/10.1088/0305-4470/21/22/006>`__

    Parameters
    ----------
    x : float
        component amplitude
    dim : int
        dimension of the matrix
    beta : int
        Dyson parameter of universality class

    Returns
    -------
    float
        Eigenvector statistics PDF at x

    Examples
    --------
    # TODO
    """

    if beta == 1:
        coef = np.e**(gammaln(dim/2) - gammaln((dim-1)/2))
        dist = ((1 - x)**((dim-3)/2))/(np.sqrt(np.pi*x))
    elif beta == 2:
        coef = (dim - 1)
        dist = (1 - x)**(dim - 2)
    elif beta == 4:
        coef = (dim - 1)*(dim - 2)
        dist = x*((1-x)**(dim - 1))
    val = coef*dist
    if val > 10**30:
        val = 10**30

    if val < 10**-30:
        val = 10**-30

    return val if val != 0 else 10**-30


def WignerDyson(x: float, beta: int = 1) -> float:
    r"""
    Calculate Wigner Surmise (Wigner-Dyson) PDF at x for three universality classes
    (COE (beta=1), CUE (beta=2), and CSE (beta=4)). Used in nearest-neighbour eigen-value/phase spacing statistics.

    `For these definitions and more details. <https://doi.org/10.1080/00018732.2016.1198134>`__

    Parameters
    ----------
    x : float
        a float greater or equal to zero
    beta : int, optional
        Dyson parameter of universality class, by default 1

    Returns
    -------
    float
        Wigner Surmise (Wigner-Dyson) PDF at x

    Examples
    --------
    # TODO
    """

    if beta == 1:
        val = (np.pi/2)*(x**beta)*np.exp(-np.pi*(x**2)*0.25)
    elif beta == 2:
        val = ((x**beta)*(32/(np.pi**2)))*np.exp(-4*(x**2)/(np.pi))
    elif beta == 4:
        val = ((x**beta)*((2**18)/((3**6)*(np.pi**3))))*np.exp(-64*(x**2)/(9*np.pi))
    elif beta == 0:
        val = np.exp(-x)
    return val

WignerSurmise = WignerDyson

def Poissonian(x: float, lam: float) -> float:
    r"""
    Poisson PDF at x.

    Parameters
    ----------
    x : float
        a float larger than zero
    lam : float
        Poisson parameter :math:`\lambda`

    Returns
    -------
    float
         Poisson PDF at x.

    Examples
    --------
    # TODO
    """
    return ((np.e**(-gammaln(x+1)))*(lam**x))*(np.e**(-lam))
