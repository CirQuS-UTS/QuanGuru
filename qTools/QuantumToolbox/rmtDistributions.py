from scipy.special import gammaln # type: ignore # pylint: disable=no-name-in-module
from numpy import sqrt, pi, e # type: ignore


def EigenVectorDist(x: float, dim: int, beta: int = 1) -> float:
    if beta == 1:
        coef = e**(gammaln(dim/2) - gammaln((dim-1)/2))
        dist = ((1 - x)**((dim-3)/2))/(sqrt(pi*x))
    elif beta == 2:
        coef = (dim - 1)
        dist = (1 - x)**(dim - 2)
    elif beta == 4:
        coef = (dim - 1)*(dim - 2)
        dist = x*((1-x)**(dim - 1))
    val = coef*dist
    return val if val != 0 else 10**-30


def WignerDyson(x: float, beta: int = 1) -> float:
    """[summary]

    Parameters
    ----------
    x : float
        [description]
    beta : int, optional
        [description], by default 1

    Returns
    -------
    float
        [description]
    """
    if beta == 1:
        coef = pi/2
        dist = (x ** beta) * (e ** (-(pi * (x ** 2)) / 4))
    elif beta == 2:
        coef = 32/(pi**2)
        dist = (x ** beta) * (e ** (-(4 * (x ** 2)) / pi))
    elif beta == 4:
        coef = (2**18)/((3**6)*(pi**3))
        dist = (x ** beta) * (e ** (-(64 * (x ** 2)) / (9*pi)))
    val = coef*dist
    return val if val != 0 else 10**-30


def Poissonian(x: float, lam: float) -> float:
    return ((e**(-gammaln(x+1)))*(lam**x))*(e**(-lam))
