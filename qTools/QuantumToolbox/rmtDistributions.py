from scipy.special import gammaln, factorial # pylint: disable=no-name-in-module
from numpy import sqrt, pi, e


def EigenVectorDist(x, dim, beta=1):
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

    if val == 0:
        val = 10**-30

    return val


def WignerDyson(x, beta=1):
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

    if val == 0:
        val = 10 ** -30

    return val


def Poissonian(x, lam):
    return ((lam**x)/(factorial(x)))*(e**(-lam))
