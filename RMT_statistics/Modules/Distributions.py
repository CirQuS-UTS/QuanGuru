from scipy.special import gammaln, factorial
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
    return val if val != 0 else 10**-30


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
    return val if val != 0 else 10**-30


def Poissonian(x, lam):
    return ((lam**x)/(factorial(x)))*(e**(-lam))


"""import matplotlib.pyplot as plt
from numpy import arange

x = arange(0, 0.5, 0.001)
prbx1 = [EigenVectorDist(X, 10, 1) for X in x]
prbx2 = [EigenVectorDist(X, 10, 2) for X in x]
prbx3 = [EigenVectorDist(X, 10, 4) for X in x]
#prbx4 = [WignerDyson(X, 4) for X in x]
#prbx5 = [Poissonian(X, 4) for X in x]
plt.plot(x, prbx1, 'r-')
plt.plot(x, prbx2, 'b-')
plt.plot(x, prbx3, 'g-')
#plt.plot(x, prbx4, 'k-')
#plt.plot(x, prbx5, 'c-')
plt.show()"""