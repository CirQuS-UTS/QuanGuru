r"""
    Contains methods to functions to create and/or manipulate quantum operators

    .. currentmodule:: quanguru.QuantumToolbox.operators

    Functions
    ---------

    .. autosummary::
        identity

    .. autosummary::
        number
        destroy
        create

    .. autosummary::
        sigmaz
        sigmay
        sigmax
        sigmap
        sigmam

    .. autosummary::
        Jp
        Jm
        Jx
        Jy
        Jz
        Js

    .. autosummary::
        displacement
        squeeze

    .. autosummary::
        parityEXP
        paritySUM

    .. autosummary::
        compositeOp
        operatorPow

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `identity`                |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `number`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `destroy`                 |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `create`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `sigmaz`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `sigmay`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `sigmax`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `sigmap`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `sigmam`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `Jp`                      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `Jm`                      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `Jx`                      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `Jy`                      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `Jz`                      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `Js`                      |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `displacement`            |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |c|        |w| |w| |x|
       `squeeze`                 |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `parityEXP`               |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `paritySUM`               |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `compositeOp`             |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `operatorPow`             |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

""" #pylint:disable=too-many-lines

from typing import Callable

import scipy.sparse as sp # type: ignore
import scipy.linalg as linA # type: ignore
from scipy.sparse.linalg import expm # type: ignore
import numpy as np # type: ignore

from .linearAlgebra import tensorProd, _matPower

from .customTypes import Matrix #pylint: disable=relative-beyond-top-level


# do not delete these
# from typing import Callable, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


def number(dimension: int, sparse: bool = True) -> Matrix:
    r"""
    Creates the (bosonic) number :math:`\hat{n} := a^{\dagger}a` operator (in Fock basis).

    Parameters
    ----------
    dimension : int
        dimension of the Hilbert space
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        number operator

    Examples
    --------
    >>> number(dimension=3, sparse=False)
    [[0 0 0]
     [0 1 0]
     [0 0 2]]

    >>> print(number(3))
    (0, 0)	0
    (1, 1)	1
    (2, 2)	2
    """

    data = list(range(dimension))
    rows = range(0, dimension)
    columns = range(0, dimension)
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, dimension))
    return n if sparse else n.toarray()

def destroy(dimension: int, sparse: bool = True) -> Matrix:
    r"""
    Creates the bosonic `annihilation` :math:`\hat{a}` operator (in Fock basis).

    Parameters
    ----------
    dimension : int
        dimension of the Hilbert space
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        bosonic `annihilation` operator

    Examples
    --------
    >>> print(destroy(dimension=3))
    (0, 1)	1.0
    (1, 2)	1.4142135623730951

    >>> destroy(3, sparse=False)
    [[0.         1.         0.        ]
     [0.         0.         1.41421356]
     [0.         0.         0.        ]]
    """

    data = [np.sqrt(i+1) for i in range(dimension-1)]
    rows = range(0, dimension-1)
    columns = range(1, dimension)
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, dimension))
    return n if sparse else n.toarray()

def create(dimension: int, sparse: bool = True) -> Matrix:
    r"""
    Creates the bosonic `creation` :math:`\hat{a}^{\dagger}` operator (in Fock basis).

    Parameters
    ----------
    dimension : int
        dimension of the Hilbert space
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        bosonic `creation` operator

    Examples
    --------
    >>> print(create(3))
    (1, 0)	1.0
    (2, 1)	1.4142135623730951

    >>> create(3, sparse=False)
    [[0.         0.         0.        ]
     [1.         0.         0.        ]
     [0.         1.41421356 0.        ]]
    """

    data = [np.sqrt(i+1) for i in range(dimension-1)]
    rows = range(1, dimension)
    columns = range(0, dimension-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, dimension))
    return n if sparse else n.toarray()

def identity(dimension: int, sparse: bool = True) -> Matrix:
    r"""
    Creates the identity operator :math:`\mathbb{I}`.

    Parameters
    ----------
    dimension : int
        dimension of the Hilbert space
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        identity operator

    Examples
    --------
    >>> print(identity(3))
    (0, 0)	1.0
    (1, 1)	1.0
    (2, 2)	1.0

    >>> identity(3, sparse=False)
    [[1. 0. 0.]
     [0. 1. 0.]
     [0. 0. 1.]]
    """

    return sp.identity(dimension, format="csc") if sparse else np.identity(dimension)

def sigmaz(sparse: bool = True) -> Matrix:
    r"""
    Creates the `Pauli` (sigma z) :math:`\hat{\sigma}_{z} := \begin{bmatrix} 1, \ \ 0 \\ 0, -1 \end{bmatrix}` operator.

    Parameters
    ----------
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        `Pauli` sigma z operator

    Examples
    --------
    >>> sigmaz(sparse=False)
    [[ 1  0]
     [ 0 -1]]

    >>> print(sigmaz())
    (0, 0)	1
    (1, 1)	-1
    """

    data = [1, -1]
    rows = [0, 1]
    columns = [0, 1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmay(sparse: bool = True) -> Matrix:
    r"""
    Creates the `Pauli` (sigma y) :math:`\hat{\sigma}_{y} := \begin{bmatrix} 0, -i \\ i,\ \ 0 \end{bmatrix}` operator.

    Parameters
    ----------
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        `Pauli` sigma y operator

    Examples
    --------
    >>> sigmay(sparse=False)
    [[0.+0.j 0.-1.j]
     [0.+1.j 0.+0.j]]

    >>> print(sigmay())
    (1, 0)	1j
    (0, 1)	(-0-1j)
    """

    data = [-1j, 1j]
    rows = [0, 1]
    columns = [1, 0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmax(sparse: bool = True) -> Matrix:
    r"""
    Creates the `Pauli` (sigma x) :math:`\hat{\sigma}_{x} := \begin{bmatrix} 0, 1 \\ 1, 0 \end{bmatrix}` operator.

    Parameters
    ----------
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        `Pauli` sigma x operator

    Examples
    --------
    >>> sigmax(sparse=False)
    [[0 1]
     [1 0]]

    >>> print(sigmax())
    (1, 0)	1
    (0, 1)	1
    """

    data = [1, 1]
    rows = [0, 1]
    columns = [1, 0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmap(sparse: bool = True) -> Matrix:
    r"""
    Creates the `Pauli` (sigma +) :math:`\hat{\sigma}_{+} := \frac{1}{2}(\hat{\sigma}_{x} +i\hat{\sigma}_{y}) =
    \begin{bmatrix} 0, 1 \\ 0, 0 \end{bmatrix}` operator.

    Parameters
    ----------
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        `Pauli` sigma + operator

    Examples
    --------
    >>> sigmap(sparse=False)
    [[0 1]
     [0 0]]

    >>> print(sigmap())
    (0, 1)	1
    """

    data = [1]
    rows = [0]
    columns = [1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmam(sparse: bool = True) -> Matrix:
    r"""
    Creates the `Pauli` (sigma -) :math:`\hat{\sigma}_{-} := \frac{1}{2}(\hat{\sigma}_{x} - i\hat{\sigma}_{y}) =
    \begin{bmatrix} 0, 0 \\ 1, 0 \end{bmatrix}` operator.

    Parameters
    ----------
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        `Pauli` sigma - operator

    Examples
    --------
    >>> sigmam(sparse=False)
    [[0 0]
     [1 0]]

    >>> print(sigmam())
    (1, 0)	1
    """

    data = [1]
    rows = [1]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def Jp(j: float, sparse: bool = True, isDim: bool = False) -> Matrix:
    r"""
    Creates the angular momentum (spin) `raising` operator
    :math:`\hat{J}_{+} := \frac{1}{2}(\hat{J}_{x}+i\hat{J}_{y})` for a given spin quantum number j.

    NOTE This is a direct matrix construction, i.e. it does not use the Jx and Jy functions, and this function is used
    in Jx and Jy implementations

    Parameters
    ----------
    j : int or float
        integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)
    isDim : bool
        boolean for whether j is spin quantum number of dimension

    Returns
    -------
    Matrix
        Angular momentum (spin) raising operator

    Examples
    --------
    >>> Jp(j=2, sparse=False)
    [[0.         2.         0.         0.         0.        ]
     [0.         0.         2.44948974 0.         0.        ]
     [0.         0.         0.         2.44948974 0.        ]
     [0.         0.         0.         0.         2.        ]
     [0.         0.         0.         0.         0.        ]]

    >>> print(Jp(j=2))
    (0, 1)	2.0
    (1, 2)	2.449489742783178
    (2, 3)	2.449489742783178
    (3, 4)	2.0

    >>> Jp(j=5, sparse=False, isDim=True)
    [[0.         2.         0.         0.         0.        ]
     [0.         0.         2.44948974 0.         0.        ]
     [0.         0.         0.         2.44948974 0.        ]
     [0.         0.         0.         0.         2.        ]
     [0.         0.         0.         0.         0.        ]]

    >>> print(Jp(j=5, isDim=True))
    (0, 1)	2.0
    (1, 2)	2.449489742783178
    (2, 3)	2.449489742783178
    (3, 4)	2.0
    """

    d = int((2*j) + 1)
    if isDim:
        d = int(j)
        j = round((d-1)/2, 1)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(0, d-1)
    columns = range(1, d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jm(j: float, sparse: bool = True, isDim: bool = False) -> Matrix:
    r"""
    Creates the angular momentum (spin) `lowering` operator
    :math:`\hat{J}_{-} := \frac{1}{2}(\hat{J}_{x}-i\hat{J}_{y})` for a given spin quantum number j.

    NOTE This is a direct matrix construction, i.e. it does not use the Jx and Jy functions, and this function is used
    in Jx and Jy implementations

    Parameters
    ----------
    j : int or float
        integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)
    isDim : bool
        boolean for whether j is spin quantum number of dimension

    Returns
    -------
    Matrix
        Angular momentum (spin) lowering operator

    Examples
    --------
    >>> Jm(j=2, isDim=False, sparse=False)
    [[0.         0.         0.         0.         0.        ]
     [2.         0.         0.         0.         0.        ]
     [0.         2.44948974 0.         0.         0.        ]
     [0.         0.         2.44948974 0.         0.        ]
     [0.         0.         0.         2.         0.        ]]

    >>> print(Jm(j=2, isDim=False))
    (1, 0)	2.0
    (2, 1)	2.449489742783178
    (3, 2)	2.449489742783178
    (4, 3)	2.0

    >>> Jm(j=5, sparse=False, isDim=True)
    [[0.         0.         0.         0.         0.        ]
     [2.         0.         0.         0.         0.        ]
     [0.         2.44948974 0.         0.         0.        ]
     [0.         0.         2.44948974 0.         0.        ]
     [0.         0.         0.         2.         0.        ]]

    >>> print(Jm(j=5, isDim=True))
    (1, 0)	2.0
    (2, 1)	2.449489742783178
    (3, 2)	2.449489742783178
    (4, 3)	2.0
    """

    d = int((2*j) + 1)
    if isDim:
        d = int(j)
        j = round((d-1)/2, 1)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(1, d)
    columns = range(0, d-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jx(j: float, sparse: bool = True, isDim: bool = False) -> Matrix:
    r"""
    Creates the angular momentum (spin) `X` operator :math:`\hat{J}_{x}` for a given spin quantum number j.

    NOTE This function uses the definition :math:`\hat{J}_{x} =\frac{1}{2}(\hat{J}_{p}+\hat{J}_{m})` and calls Jp and Jm
    There are no test for this method, it rely on Jp and Jm

    Parameters
    ----------
    j : int or float
        integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)
    isDim : bool
        boolean for whether j is spin quantum number of dimension

    Returns
    -------
    Matrix
        Angular momentum (spin) X operator

    Examples
    --------
    >>> Jx(j=2, isDim=False, sparse=False)
    [[0.         1.         0.         0.         0.        ]
     [1.         0.         1.22474487 0.         0.        ]
     [0.         1.22474487 0.         1.22474487 0.        ]
     [0.         0.         1.22474487 0.         1.        ]
     [0.         0.         0.         1.         0.        ]]

    >>> print(Jx(j=2, isDim=False))
    (1, 0)	1.0
    (0, 1)	1.0
    (2, 1)	1.224744871391589
    (1, 2)	1.224744871391589
    (3, 2)	1.224744871391589
    (2, 3)	1.224744871391589
    (4, 3)	1.0
    (3, 4)	1.0

    >>> Jx(j=5, sparse=False, isDim=True)
    [[0.         1.         0.         0.         0.        ]
     [1.         0.         1.22474487 0.         0.        ]
     [0.         1.22474487 0.         1.22474487 0.        ]
     [0.         0.         1.22474487 0.         1.        ]
     [0.         0.         0.         1.         0.        ]]

    >>> print(Jx(j=5, isDim=True))
    (1, 0)	1.0
    (0, 1)	1.0
    (2, 1)	1.224744871391589
    (1, 2)	1.224744871391589
    (3, 2)	1.224744871391589
    (2, 3)	1.224744871391589
    (4, 3)	1.0
    (3, 4)	1.0
    """

    n = 0.5*(Jp(j, isDim=isDim) + Jm(j, isDim=isDim))
    return n if sparse else n.toarray()

def Jy(j: float, sparse: bool = True, isDim: bool = False) -> Matrix:
    r"""
    Creates the angular momentum (spin) `Y` operator :math:`\hat{J}_{y}` for a given spin quantum number j.

    NOTE This function uses the definition :math:`\hat{J}_{y}=\frac{1}{2j}(\hat{J}_{p}-\hat{J}_{m})` and calls Jp and Jm
    There are no test for this method, it rely on Jp and Jm

    Parameters
    ----------
    j : int or float
        integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)
    isDim : bool
        boolean for whether j is spin quantum number of dimension

    Returns
    -------
    Matrix
        Angular momentum (spin) Y operator

    Examples
    --------
    >>> Jy(j=2, isDim=False, sparse=False)
    [[0.+0.j         0.-1.j         0.+0.j         0.+0.j                0.+0.j        ]
     [0.+1.j         0.+0.j         0.-1.22474487j 0.+0.j                0.+0.j        ]
     [0.+0.j         0.+1.22474487j 0.+0.j         0.-1.22474487j        0.+0.j        ]
     [0.+0.j         0.+0.j         0.+1.22474487j 0.+0.j                0.-1.j        ]
     [0.+0.j         0.+0.j         0.+0.j         0.+1.j                0.+0.j        ]]

    >>> print(Jy(j=2, isDim=False))
    (1, 0)	1j
    (0, 1)	-1j
    (2, 1)	1.224744871391589j
    (1, 2)	-1.224744871391589j
    (3, 2)	1.224744871391589j
    (2, 3)	-1.224744871391589j
    (4, 3)	1j
    (3, 4)	-1j

    >>> Jy(j=5, sparse=False, isDim=True)
    [[0.+0.j         0.-1.j         0.+0.j         0.+0.j                0.+0.j        ]
     [0.+1.j         0.+0.j         0.-1.22474487j 0.+0.j                0.+0.j        ]
     [0.+0.j         0.+1.22474487j 0.+0.j         0.-1.22474487j        0.+0.j        ]
     [0.+0.j         0.+0.j         0.+1.22474487j 0.+0.j                0.-1.j        ]
     [0.+0.j         0.+0.j         0.+0.j         0.+1.j                0.+0.j        ]]

    >>> print(Jy(j=5, isDim=True))
    (1, 0)	1j
    (0, 1)	-1j
    (2, 1)	1.224744871391589j
    (1, 2)	-1.224744871391589j
    (3, 2)	1.224744871391589j
    (2, 3)	-1.224744871391589j
    (4, 3)	1j
    (3, 4)	-1j
    """

    n = (1/(2j))*(Jp(j, isDim=isDim) - Jm(j, isDim=isDim))
    return n if sparse else n.toarray()

def Jz(j: float, sparse: bool = True, isDim: bool = False) -> Matrix:
    r"""
    Creates the angular momentum (spin) `Z` operator :math:`\hat{J}_{z}` for a given spin quantum number j.

    Parameters
    ----------
    j : int or float
        integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)
    isDim : bool
        boolean for whether j is spin quantum number of dimension

    Returns
    -------
    Matrix
        Angular momentum (spin) Z operator

    Examples
    --------
    >>> Jz(j=2, isDim=False, sparse=False)
    [[ 2  0  0  0  0]
     [ 0  1  0  0  0]
     [ 0  0  0  0  0]
     [ 0  0  0 -1  0]
     [ 0  0  0  0 -2]]

    >>> print(Jz(j=2, isDim=False))
    (0, 0)	2
    (1, 1)	1
    (2, 2)	0
    (3, 3)	-1
    (4, 4)	-2

    >>> Jz(j=5, sparse=False, isDim=True)
    [[ 2.  0.  0.  0.  0.]
     [ 0.  1.  0.  0.  0.]
     [ 0.  0.  0.  0.  0.]
     [ 0.  0.  0. -1.  0.]
     [ 0.  0.  0.  0. -2.]]

    >>> print(Jz(j=5, isDim=True))
    (0, 0)	2.0
    (1, 1)	1.0
    (2, 2)	0.0
    (3, 3)	-1.0
    (4, 4)	-2.0
    """

    d = int((2*j) + 1)
    if isDim:
        d = int(j)
        j = round((d-1)/2, 1)
    data = [j-i for i in range(d)]
    rows = range(0, d)
    columns = range(0, d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Js(j: float, sparse: bool = True, isDim: bool = False) -> Matrix:
    r"""
    Creates the total angular momentum (spin) operator
    :math:`\hat{J}_{s} := \hat{J}_{x}^{2} + \hat{J}_{y}^{2}+ \hat{J}_{z}^{2}` for a given spin quantum number j.

     NOTE This function is direct implementation of the defition, meaning it uses Jx, Jy, and Jz functions

    Parameters
    ----------
    j : int or float
        integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)
    isDim : bool
        boolean for whether j is spin quantum number of dimension

    Returns
    -------
    Total angular momentum (spin) operator

    Examples
    --------
    >>> Js(j=2, isDim=False, sparse=False)
    [[6.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j]
     [0.+0.j 6.+0.j 0.+0.j 0.+0.j 0.+0.j]
     [0.+0.j 0.+0.j 6.+0.j 0.+0.j 0.+0.j]
     [0.+0.j 0.+0.j 0.+0.j 6.+0.j 0.+0.j]
     [0.+0.j 0.+0.j 0.+0.j 0.+0.j 6.+0.j]]

    >>> print(Js(j=2, isDim=False))
    (0, 0)	(6+0j)
    (1, 1)	(6+0j)
    (2, 2)	(5.999999999999999+0j)
    (3, 3)	(6+0j)
    (4, 4)	(6+0j)

    >>> Js(j=5, sparse=False, isDim=True)
    [[6.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j]
     [0.+0.j 6.+0.j 0.+0.j 0.+0.j 0.+0.j]
     [0.+0.j 0.+0.j 6.+0.j 0.+0.j 0.+0.j]
     [0.+0.j 0.+0.j 0.+0.j 6.+0.j 0.+0.j]
     [0.+0.j 0.+0.j 0.+0.j 0.+0.j 6.+0.j]]

    >>> print(Js(j=5, isDim=True))
    (0, 0)	(6+0j)
    (1, 1)	(6+0j)
    (2, 2)	(5.999999999999999+0j)
    (3, 3)	(6+0j)
    (4, 4)	(6+0j)
    """

    n = (Jx(j, isDim=isDim)@Jx(j, isDim=isDim)) + (Jy(j, isDim=isDim)@Jy(j, isDim=isDim))\
        + (Jz(j, isDim=isDim)@Jz(j, isDim=isDim))
    return n if sparse else n.toarray()

def displacement(alpha: complex, dim: int, sparse: bool = True) -> Matrix:
    r"""
    Creates the displacement operator :math:`\hat{D}(\alpha) := e^{\alpha a^{\dagger} - \alpha^{*}a}`
    for a given displacement parameter :math:`\alpha`.

    NOTE can be implemented without matrix exponentiation

    Parameters
    ----------
    alpha : complex
        complex number, the displacement parameter
    dim : int
        dimension of the Hilbert space
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Displacement operator

    Examples
    --------
    >>> displacement(alpha=1j, dim=4, sparse=False)
    [[ 0.60605894+0.j          0.        +0.6100857j  -0.41242505+0.j       0.        -0.30065525j]
     [ 0.        +0.6100857j   0.02280184+0.j          0.        +0.34204129j        -0.71434114+0.j]
     [-0.41242505+0.j          0.        +0.34204129j -0.56045527+0.j        0.        +0.63150869j]
     [ 0.        -0.30065525j -0.71434114+0.j          0.        +0.63150869j        0.02280184+0.j]]

    >>> print(displacement(alpha=1j, dim=4))
    (0, 0)	(0.6060589372864117+0j)
    (1, 0)	0.610085698426889j
    (2, 0)	(-0.41242505189886125+0j)
    (3, 0)	(-0-0.3006552538647247j)
    (0, 1)	0.610085698426889j
    (1, 1)	(0.02280183542861441+0j)
    (2, 1)	0.3420412936689465j
    (3, 1)	(-0.7143411442030587+0j)
    (0, 2)	(-0.4124250518988613+0j)
    (1, 2)	0.34204129366894637j
    (2, 2)	(-0.5604552664291825+0j)
    (3, 2)	0.6315086890322961j
    (0, 3)	-0.3006552538647247j
    (1, 3)	(-0.7143411442030586+0j)
    (2, 3)	0.6315086890322962j
    (3, 3)	(0.02280183542861464+0j)
    """

    oper = (alpha * create(dim)) - (np.conj(alpha) * destroy(dim))
    n = expm(oper)
    return n if sparse else n.A

def squeeze(alpha: complex, dim: int, sparse: bool = True) -> Matrix:
    r"""
    Creates the squeezing operator :math:`\hat{S}(\alpha) := e^{\frac{1}{2}(\alpha^{*}a^{2} - \alpha a^{\dagger 2})}`
    for a given squeezing parameter :math:`\alpha`.

    NOTE can be implemented without matrix exponentiation

    Parameters
    ----------
    alpha : complex
        complex number, the squeezing parameter
    dim : int
        dimension of the Hilbert space
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Squeezing operator

    Examples
    --------
    >>> squeeze(alpha=1j, dim=4, sparse=False)
    [[0.7602446 +0.j         0.        +0.j         0.        -0.64963694j      0.        +0.j        ]
     [0.        +0.j         0.33918599+0.j         0.        +0.j               0.        -0.94071933j]
     [0.        -0.64963694j 0.        +0.j         0.7602446 +0.j               0.        +0.j        ]
     [0.        +0.j         0.        -0.94071933j 0.        +0.j               0.33918599+0.j        ]]

    >>> print(squeeze(alpha=1j, dim=4))
    (0, 0)	(0.7602445970756301+0j)
    (2, 0)	-0.6496369390800625j
    (1, 1)	(0.3391859889869473+0j)
    (3, 1)	-0.940719333741444j
    (0, 2)	-0.6496369390800625j
    (2, 2)	(0.7602445970756302+0j)
    (1, 3)	-0.9407193337414442j
    (3, 3)	(0.33918598898694713+0j)
    """

    oper = -(alpha * (create(dim)@create(dim))) + (np.conj(alpha) * (destroy(dim)@destroy(dim)))
    n = expm(0.5*oper)
    return n if sparse else n.A

def parityEXP(HamiltonianCavity: Matrix) -> Matrix:
    r"""
    Creates a parity operator :math:`\hat{P}(\hat{H}) := e^{i\pi\hat{H}}` by exponenting a given Hamiltonian
    :math:`\hat{H}`.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    HamiltonianCavity : Matrix
        dimension of the Hilbert space

    Returns
    -------
    Matrix
        Parity operator

    Examples
    --------
    >>> ham = number(dimension=5, sparse=False)
    >>> parityEXP(HamiltonianCavity=ham) # returns an array since ham is an array
    [[ 1.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j]
     [ 0.+0.0000000e+00j -1.+1.2246468e-16j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j]
     [ 0.+0.0000000e+00j  0.+0.0000000e+00j  1.-2.4492936e-16j  0.+0.0000000e+00j  0.+0.0000000e+00j]
     [ 0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  -1.+3.6739404e-16j  0.+0.0000000e+00j]
     [ 0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  1.-4.8985872e-16j]]

    >>> ham = number(dimension=5)
    >>> print(parityEXP(HamiltonianCavity=ham)) # returns a sparse since ham is a sparse
    (0, 0)	(1+0j)
    (0, 1)	0j
    (1, 1)	(-1+1.2246467991473532e-16j)
    (1, 2)	-0j
    (2, 2)	(1-2.4492935982947064e-16j)
    (2, 3)	0j
    (3, 3)	(-1+3.6739403974420594e-16j)
    (3, 4)	-0j
    (4, 4)	(1-4.898587196589413e-16j)
    """

    sparse = sp.isspmatrix(HamiltonianCavity)
    parEX = ((1j * np.pi) * HamiltonianCavity)
    return expm(parEX) if sparse else linA.expm(parEX)

def paritySUM(dimension: int, sparse: bool = True) -> Matrix:
    r"""
    Creates a parity operator by explicitly placing alternating +/- into a matrix.

    Parameters
    ----------
    dimension : int
        dimension of the Hilbert space
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Parity operator

    Examples
    --------
    >>> paritySUM(dimension=5, sparse=False)
    [[ 1.  0.  0.  0.  0.]
     [ 0. -1.  0.  0.  0.]
     [ 0.  0.  1.  0.  0.]
     [ 0.  0.  0. -1.  0.]
     [ 0.  0.  0.  0.  1.]]

    >>> print(paritySUM(dimension=5))
    (0, 0)	1.0
    (1, 1)	-1.0
    (2, 2)	1.0
    (3, 3)	-1.0
    (4, 4)	1.0
    """

    a = np.empty((dimension,))
    a[::2] = 1
    a[1::2] = -1
    data = a
    rows = range(0, dimension)
    columns = range(0, dimension)
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, dimension))
    return n if sparse else n.toarray()

def compositeOp(operator: Matrix, dimB: int = 1, dimA: int = 1) -> Matrix:
    r"""
    Creates a composite operator
    :math:`\hat{O}_{comp} = \mathbb{I}_{dimB\times dimB}\otimes\hat{O}_{single}\otimes\mathbb{I}_{dimA\times dimA}`
    ,ie tensor product with identities of dimensions before dimB and after dimA

    NOTE simply calls and returns :func:`tensorProd <quanguru.QuantumToolbox.linearAlgebra.tensorProd>`

    Parameters
    ----------
    operator : Matrix
        operator of a sub-system
    dimB : int
        (total) dimension of the systems that appear `before` in the tensor product order
    dimA : int
        (total) dimension of the systems that appear `after` in the tensor product order

    Returns
    -------
    Matrix
        sub-system operator in the extended Hilbert space

    Examples
    --------
    >>> compositeOp(operator=sigmaz(), dimB=0, dimA=2).A
    [[ 1.  0.  0.  0.]
     [ 0.  1.  0.  0.]
     [ 0.  0. -1.  0.]
     [ 0.  0.  0. -1.]]

    >>> compositeOp(operator=sigmaz(), dimB=2, dimA=0).A
    [[ 1.  0.  0.  0.]
     [ 0. -1.  0.  0.]
     [ 0.  0.  1.  0.]
     [ 0.  0.  0. -1.]]

    """

    return tensorProd(*[a for a in [dimB, operator, dimA] if ((not isinstance(a, int)) or (a > 1))])

def operatorPow(op: Callable, dim: int, power: int, sparse: bool = True) -> Matrix:
    r"""
    Creates a quantum operator for given function reference `op` and raises to a `power`.

    Parameters
    ----------
    op : Callable
        reference to the function (in here) for the operator
    dim : int
        dimension of the Hilbert space
    power : int
        power that the operator to be raised
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        an operator raised to a power

    Examples
    --------
    >>> operatorPow(op=sigmax, dim=2, power=2, sparse=False)
    [[1 0]
     [0 1]]

    >>> print(operatorPow(op=sigmax, dim=2, power=2))
    (0, 0)	1
    (1, 1)	1

    >>> operatorPow(op=sigmax, dim=2, power=3, sparse=False)
    [[0 1]
     [1 0]]

    >>> print(operatorPow(op=sigmax, dim=2, power=3))
    (1, 0)	1
    (0, 1)	1
    """

    try:
        opPow = _matPower(op(dim, sparse), power)
    except: # pylint: disable=bare-except # noqa: E722
        opPow = _matPower(op(sparse), power)
    return opPow
