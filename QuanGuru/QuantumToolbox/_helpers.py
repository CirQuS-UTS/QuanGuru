r"""
    Contains some helper functions.

    .. currentmodule:: QuanGuru.QuantumToolbox._helpers

    Functions
    ---------

    .. autosummary::

        loopIt


"""

from typing import Callable, Iterable, List


def loopIt(func: Callable, *inps: Iterable) -> List:
    r"""
    Loop over given iterable/s of inputs for a (multivariate) function.

    Parameters
    ----------
    func : Callable
        a callable function
    inps : Iterable
        iterable/s of inputs

    Returns
    -------
    List
        Given function calculated at each input point

    Examples
    --------
    >>> def mulT(a, b, c):
    >>>     return a*b*c
    >>> al = range(10)
    >>> loopIt(mulT, al, al, al)
    [0, 1, 8, 27, 64, 125, 216, 343, 512, 729]
    >>> bl = [2*i for i in range(10)]
    >>> cl = [3*i for i in range(10)]
    >>> loopIt(mulT, al, bl, cl)
    [0, 6, 48, 162, 384, 750, 1296, 2058, 3072, 4374]

    """

    return [func(*inp) for inp in zip(*inps)]
