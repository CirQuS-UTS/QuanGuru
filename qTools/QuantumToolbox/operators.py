"""
    Module of functions to create and/or manipulate quantum operators

    Methods
    -------
    :number : Creates the (bosonic) number operator
    :destroy : Creates the bosonic `annihilation` operator
    :create : Creates the bosonic `creation` operator

    :identity : Creates the identity operator

    :sigmaz : Creates the `Pauli` sigma z operator
    :sigmay : Creates the `Pauli` sigma y operator
    :sigmax : Creates the `Pauli` sigma x operator
    :sigmap : Creates the `Pauli` sigma + operator, i.e. 2D Fermionic creation operator
    :sigmam : Creates the `Pauli` sigma - operator, i.e. 2D Fermionic destruction operator

    :Jz : Creates the angular momentum (spin) `Z` operator for a given spin quantum number j
    :Jp : Creates the angular momentum (spin) `creation` operator for a given spin quantum number j
    :Jm : Creates the angular momentum (spin) `destruction` operator for a given spin quantum number j
    :Jx : Creates the angular momentum (spin) `X` operator for a given spin quantum number j
    :Jy : Creates the angular momentum (spin) `Y` operator for a given spin quantum number j
    :Js : Creates the total angular momentum (spin) operator for a given spin quantum number j

    :operatorPow : Creates a quantum operator for given function reference `op` and raises to a `power`

    :paritySUM : Creates the parity operator by explicity placing alternating +/- into a matrix
    :partiyEXP : Creates the parity operator by exponetiationg a given Hamiltonian

    :basis : Creates a `ket` state

    :displacement : Creates the displacement operator for a given displacement parameter alpha
    :squeeze : Creates the squeezing operator for a given squeezing parameter alpha

    :compositeOp : Creates a composite operator from a sub-sytem `operator`,
    i.e. tensor product with identities of dimensions dimB & dimA
""" # pylint: disable=W1401
from typing import Callable

import scipy.sparse as sp
import scipy.linalg as linA
from scipy.sparse.linalg import expm
import numpy as np

from .customTypes import Matrix


# from typing import Callable, TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


def number(dimension: int, sparse: bool = True) -> Matrix:
    """
    Creates the (bosonic) number operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param dimension : dimension of the Hilbert space
    :param sparse : boolean for sparse or not (array)

    Returns
    -------
    :return: number operator for dimension dimension

    Examples
    --------
    >>> numberArray = number(dimension=3, sparse=False)
    [[0 0 0]
    [0 1 0]
    [0 0 2]]
    >>> numberSparse = number(3)
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
    """
    Creates the bosonic `annihilation` operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `dimension` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: bosonic `annihilation` operator for dimension dimension

    Examples
    --------
    >>> annihilation = destroy(dimension=3)
    (0, 1)	1.0
    (1, 2)	1.4142135623730951
    >>> annihilation = destroy(3, sparse=False)
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
    """
    Creates the bosonic `creation` operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `dimension` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: bosonic `creation` operator for dimension dimension

    Examples
    --------
    >>> create = create(3)
    (1, 0)	1.0
    (2, 1)	1.4142135623730951
    >>> create = create(3, sparse=False)
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
    """
    Creates the identity operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `dimension` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: identity operator for dimension dimension

    Examples
    --------
    >>> identity = identity(3)
    (0, 0)	1.0
    (1, 1)	1.0
    (2, 2)	1.0
    >>> identity = identity(3, sparse=False)
    [[1. 0. 0.]
    [0. 1. 0.]
    [0. 0. 1.]]
    """

    return sp.identity(dimension, format="csc") if sparse else np.identity(dimension)

def sigmaz(sparse: bool = True) -> Matrix:
    """
    Creates the `Pauli` sigma z operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME dimension is meaningless, it is introduces to make objects more uniform, might remove later
    :param `dimension` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma z operator

    Examples
    --------
    >>> sz = sigmaz(sparse=False)
    [[ 1  0]
    [ 0 -1]]
    >>> sz = sigmaz()
    (0, 0)	1
    (1, 1)	-1
    """

    data = [1, -1]
    rows = [0, 1]
    columns = [0, 1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmay(sparse: bool = True) -> Matrix:
    """
    Creates the `Pauli` sigma y operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME dimension is meaningless, it is introduces to make objects more uniform, might remove later
    :param `dimension` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma y operator

    Examples
    --------
    >>> sy = sigmay(sparse=False)
    [[0.+0.j 0.-1.j]
    [0.+1.j 0.+0.j]]
    >>> sy = sigmay()
    (1, 0)	1j
    (0, 1)	(-0-1j)
    """

    data = [-1j, 1j]
    rows = [0, 1]
    columns = [1, 0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmax(sparse: bool = True) -> Matrix:
    """
    Creates the `Pauli` sigma x operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME dimension is meaningless, it is introduces to make objects more uniform, might remove later
    :param `dimension` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma x operator

    Examples
    --------
    >>> sx = sigmax(sparse=False)
    [[0 1]
    [1 0]]
    >>> sx = sigmax()
    (1, 0)	1
    (0, 1)	1
    """

    data = [1, 1]
    rows = [0, 1]
    columns = [1, 0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmap(sparse: bool = True) -> Matrix:
    """
    Creates the `Pauli` sigma + operator, i.e. 2D Fermionic creation operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME dimension is meaningless, it is introduces to make objects more uniform, might remove later
    :param `dimension` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma + operator

    Examples
    --------
    >>> sp = sigmap(sparse=False)
    [[0 1]
    [0 0]]
    >>> sp = sigmap()
    (0, 1)	1
    """

    data = [1]
    rows = [0]
    columns = [1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmam(sparse: bool = True) -> Matrix:
    """
    Creates the `Pauli` sigma - operator, i.e. 2D Fermionic destruction operator

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME dimension is meaningless, it is introduces to make objects more uniform, might remove later
    :param `dimension` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma - operator

    Examples
    --------
    >>> sm = sigmam(sparse=False)
    [[0 0]
    [1 0]]
    >>> sm = sigmam()
    (1, 0)	1
    """

    data = [1]
    rows = [1]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def Jz(j: float, sparse: bool = True, isDim: bool = True) -> Matrix:
    """
    Creates the angular momentum (spin) `Z` operator for a given spin quantum number j

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `j` : integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    :param `sparse` : boolean for sparse or not (array)
    :param isDim: boolean for whether j is spin quantum number of dimension

    Returns
    -------
    :return: Angular momentum (spin) Z operator

    Examples
    --------
    >>> jz0 = Jz(j=2, isDim=False, sparse=False)
    [[ 2  0  0  0  0]
    [ 0  1  0  0  0]
    [ 0  0  0  0  0]
    [ 0  0  0 -1  0]
    [ 0  0  0  0 -2]]
    >>> jz0 = Jz(j=2, isDim=False)
    (0, 0)	2
    (1, 1)	1
    (2, 2)	0
    (3, 3)	-1
    (4, 4)	-2
    >>> jz1 = Jz(j=5, sparse=False)
    [[ 2.  0.  0.  0.  0.]
    [ 0.  1.  0.  0.  0.]
    [ 0.  0.  0.  0.  0.]
    [ 0.  0.  0. -1.  0.]
    [ 0.  0.  0.  0. -2.]]
    >>> jz1 = Jz(j=5, isDim=True)
    (0, 0)	2.0
    (1, 1)	1.0
    (2, 2)	0.0
    (3, 3)	-1.0
    (4, 4)	-2.0
    """

    if not isDim:
        d = int((2*j) + 1)
    elif isDim:
        d = int(j)
        j = ((d-1)/2)
    data = [j-i for i in range(d)]
    rows = range(0, d)
    columns = range(0, d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jp(j: float, sparse: bool = True, isDim: bool = True) -> Matrix:
    """
    Creates the angular momentum (spin) `creation` operator for a given spin quantum number j

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `j` : integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    :param `sparse` : boolean for sparse or not (array)
    :param isDim: boolean for whether j is spin quantum number of dimension

    Returns
    -------
    :return: Angular momentum (spin) creation operator

    Examples
    --------
    >>> jp0 = Jp(j=2, isDim=False, sparse=False)
    [[0.         2.         0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.44948974 0.        ]
    [0.         0.         0.         0.         2.        ]
    [0.         0.         0.         0.         0.        ]]
    >>> jp0 = Jp(j=2, isDim=False)
    (0, 1)	2.0
    (1, 2)	2.449489742783178
    (2, 3)	2.449489742783178
    (3, 4)	2.0
    >>> jp1 = Jp(j=5, sparse=False)
    [[0.         2.         0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.44948974 0.        ]
    [0.         0.         0.         0.         2.        ]
    [0.         0.         0.         0.         0.        ]]
    >>> jp1 = Jp(j=5, isDim=True)
    (0, 1)	2.0
    (1, 2)	2.449489742783178
    (2, 3)	2.449489742783178
    (3, 4)	2.0
    """

    if not isDim:
        d = int((2*j) + 1)
    elif isDim:
        d = int(j)
        j = ((d-1)/2)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(0, d-1)
    columns = range(1, d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jm(j: float, sparse: bool = True, isDim: bool = True) -> Matrix:
    """
    Creates the angular momentum (spin) `destruction` operator for a given spin quantum number j

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `j` : integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    :param `sparse` : boolean for sparse or not (array)
    :param isDim: boolean for whether j is spin quantum number of dimension

    Returns
    -------
    :return: Angular momentum (spin) destruction operator

    Examples
    --------
    >>> jm0 = Jm(j=2, isDim=False, sparse=False)
    [[0.         0.         0.         0.         0.        ]
    [2.         0.         0.         0.         0.        ]
    [0.         2.44948974 0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.         0.        ]]
    >>> jm0 = Jm(j=2, isDim=False)
    (1, 0)	2.0
    (2, 1)	2.449489742783178
    (3, 2)	2.449489742783178
    (4, 3)	2.0
    >>> jm1 = Jm(j=5, sparse=False)
    [[0.         0.         0.         0.         0.        ]
    [2.         0.         0.         0.         0.        ]
    [0.         2.44948974 0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.         0.        ]]
    >>> jm1 = Jm(j=5, isDim=True)
    (1, 0)	2.0
    (2, 1)	2.449489742783178
    (3, 2)	2.449489742783178
    (4, 3)	2.0
    """

    if not isDim:
        d = int((2*j) + 1)
    elif isDim:
        d = int(j)
        j = ((d-1)/2)
    m = [j-i for i in range(d)]
    data = [np.sqrt((j+m[i])*(j-m[i]+1)) for i in range(len(m) - 1)]
    rows = range(1, d)
    columns = range(0, d-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jx(j: float, sparse: bool = True, isDim: bool = True) -> Matrix:
    """
    Creates the angular momentum (spin) `X` operator for a given spin quantum number j

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `j` : integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    :param `sparse` : boolean for sparse or not (array)
    :param isDim: boolean for whether j is spin quantum number of dimension

    Returns
    -------
    :return: Angular momentum (spin) X operator

    Examples
    --------
    >>> jx0 = Jx(j=2, isDim=False, sparse=False)
    [[0.         1.         0.         0.         0.        ]
    [1.         0.         1.22474487 0.         0.        ]
    [0.         1.22474487 0.         1.22474487 0.        ]
    [0.         0.         1.22474487 0.         1.        ]
    [0.         0.         0.         1.         0.        ]]
    >>> jx0 = Jx(j=2, isDim=False)
    (1, 0)	1.0
    (0, 1)	1.0
    (2, 1)	1.224744871391589
    (1, 2)	1.224744871391589
    (3, 2)	1.224744871391589
    (2, 3)	1.224744871391589
    (4, 3)	1.0
    (3, 4)	1.0
    >>> jx1 = Jx(j=5, sparse=False)
    [[0.         1.         0.         0.         0.        ]
    [1.         0.         1.22474487 0.         0.        ]
    [0.         1.22474487 0.         1.22474487 0.        ]
    [0.         0.         1.22474487 0.         1.        ]
    [0.         0.         0.         1.         0.        ]]
    >>> jx1 = Jx(j=5, isDim=True)
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

def Jy(j: float, sparse: bool = True, isDim: bool = True) -> Matrix:
    """
    Creates the angular momentum (spin) `Y` operator for a given spin quantum number j

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `j` : integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    :param `sparse` : boolean for sparse or not (array)
    :param isDim: boolean for whether j is spin quantum number of dimension

    Returns
    -------
    :return: Angular momentum (spin) Y operator

    Examples
    --------
    >>> jy0 = Jy(j=2, isDim=False, sparse=False)
    [[0.+0.j         0.-1.j         0.+0.j         0.+0.j                0.+0.j        ]
    [0.+1.j         0.+0.j         0.-1.22474487j 0.+0.j                0.+0.j        ]
    [0.+0.j         0.+1.22474487j 0.+0.j         0.-1.22474487j        0.+0.j        ]
    [0.+0.j         0.+0.j         0.+1.22474487j 0.+0.j                0.-1.j        ]
    [0.+0.j         0.+0.j         0.+0.j         0.+1.j                0.+0.j        ]]
    >>> jy0 = Jy(j=2, isDim=False)
    (1, 0)	1j
    (0, 1)	-1j
    (2, 1)	1.224744871391589j
    (1, 2)	-1.224744871391589j
    (3, 2)	1.224744871391589j
    (2, 3)	-1.224744871391589j
    (4, 3)	1j
    (3, 4)	-1j
    >>> jy1 = Jy(j=5, sparse=False)
    [[0.+0.j         0.-1.j         0.+0.j         0.+0.j                0.+0.j        ]
    [0.+1.j         0.+0.j         0.-1.22474487j 0.+0.j                0.+0.j        ]
    [0.+0.j         0.+1.22474487j 0.+0.j         0.-1.22474487j        0.+0.j        ]
    [0.+0.j         0.+0.j         0.+1.22474487j 0.+0.j                0.-1.j        ]
    [0.+0.j         0.+0.j         0.+0.j         0.+1.j                0.+0.j        ]]
    >>> jy1 = Jy(j=5, isDim=True)
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

def Js(j: float, sparse: bool = True, isDim: bool = True) -> Matrix:
    """
    Creates the total angular momentum (spin) operator for a given spin quantum number j

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `j` : integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    :param `sparse` : boolean for sparse or not (array)
    :param isDim: boolean for whether j is spin quantum number of dimension

    Returns
    -------
    :return: Total angular momentum (spin) operator

    Examples
    --------
    >>> js0 = Js(j=2, isDim=False, sparse=False)
    [[6.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 6.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 6.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 6.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 0.+0.j 6.+0.j]]
    >>> js0 = Js(j=2, isDim=False)
    (0, 0)	(6+0j)
    (1, 1)	(6+0j)
    (2, 2)	(5.999999999999999+0j)
    (3, 3)	(6+0j)
    (4, 4)	(6+0j)
    >>> js1 = Js(j=5, sparse=False)
    [[6.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 6.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 6.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 6.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 0.+0.j 6.+0.j]]
    >>> js1 = Js(j=5, isDim=True)
    (0, 0)	(6+0j)
    (1, 1)	(6+0j)
    (2, 2)	(5.999999999999999+0j)
    (3, 3)	(6+0j)
    (4, 4)	(6+0j)
    """

    n = (Jx(j, isDim=isDim)@Jx(j, isDim=isDim)) + (Jy(j, isDim=isDim)@Jy(j, isDim=isDim)) + (Jz(j, isDim=isDim)@Jz(j, isDim=isDim))
    return n if sparse else n.toarray()

def operatorPow(op: Callable, dim: int, power: int, sparse: bool = True) -> Matrix:
    """
    Creates a quantum operator for given function reference `op` and raises to a `power`

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `op` : reference to the function (in here) for the operator
    :param `dim` : dimension of the Hilbert space
    :param `power` : power that the operator to be raised
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: an operator raised to a power

    Examples
    --------
    >>> squareSigmaX = operatorPow(op=sigmax, dim=2, power=2, sparse=False)
    [[1 0]
    [0 1]]
    >>> squareSigmaX = operatorPow(op=sigmax, dim=2, power=2)
    (0, 0)	1
    (1, 1)	1
    >>> cubedSigmaX = operatorPow(op=sigmax, dim=2, power=3, sparse=False)
    [[0 1]
    [1 0]]
    >>> cubedSigmaX = operatorPow(op=sigmax, dim=2, power=3)
    (1, 0)	1
    (0, 1)	1
    """

    return op(dim, sparse)**power

def paritySUM(dimension: int, sparse: bool = True) -> Matrix:
    """
    Creates the parity operator by explicity placing alternating +/- into a matrix

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `dimension` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Parity operator

    Examples
    --------
    >>> paritySum = paritySUM(dimension=5, sparse=False)
    [[ 1.  0.  0.  0.  0.]
    [ 0. -1.  0.  0.  0.]
    [ 0.  0.  1.  0.  0.]
    [ 0.  0.  0. -1.  0.]
    [ 0.  0.  0.  0.  1.]]
    >>> paritySum = paritySUM(dimension=5)
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


def parityEXP(HamiltonianCavity: Matrix) -> Matrix:
    """
    Creates the parity operator by exponetiationg a given Hamiltonian

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `HamiltonianCavity` : dimension of the Hilbert space

    Returns
    -------
    :return: Parity operator

    Examples
    --------
    >>> ham = number(dimension=5, sparse=False)
    >>> parityEXP = parityEXP(HamiltonianCavity=ham) # returns an array since ham is an array
    [[ 1.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j]
    [ 0.+0.0000000e+00j -1.+1.2246468e-16j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j]
    [ 0.+0.0000000e+00j  0.+0.0000000e+00j  1.-2.4492936e-16j  0.+0.0000000e+00j  0.+0.0000000e+00j]
    [ 0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  -1.+3.6739404e-16j  0.+0.0000000e+00j]
    [ 0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  0.+0.0000000e+00j  1.-4.8985872e-16j]]
    >>> ham = number(dimension=5)
    >>> parityEXP = parityEXP(HamiltonianCavity=ham) # returns a sparse since ham is a sparse
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


def basis(dimension: int, state: int, sparse: bool = True) -> Matrix:
    """
    Creates a `ket` state

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `dimension` : dimension of Hilbert space
    :param `state` : index number for the populated state
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return : `ket` state

    Examples
    --------
    >>> basis(2, 1)
    (0, 0)	1
    >>> basis(2, 1, sparse=False)
    [[1]
    [0]]
    """

    data = [1]
    rows = [state]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(dimension, 1))
    return n if sparse else n.A

def displacement(alpha: complex, dim: int, sparse: bool = True) -> Matrix:
    """
    Creates the displacement operator for a given displacement parameter alpha

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `alpha` : complex number, the displacement parameter
    :param dim: dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Displacement operator

    Examples
    --------
    >>> disp = displacement(alpha=1j, dim=4, sparse=False)
    [[ 0.60605894+0.j          0.        +0.6100857j  -0.41242505+0.j       0.        -0.30065525j]
    [ 0.        +0.6100857j   0.02280184+0.j          0.        +0.34204129j        -0.71434114+0.j]
    [-0.41242505+0.j          0.        +0.34204129j -0.56045527+0.j        0.        +0.63150869j]
    [ 0.        -0.30065525j -0.71434114+0.j          0.        +0.63150869j        0.02280184+0.j]]
    >>> disp = displacement(alpha=1j, dim=4)
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
    n = linA.expm(oper.toarray())
    return sp.csc_matrix(n) if sparse else n

def squeeze(alpha: complex, dim: int, sparse: bool = True) -> Matrix:
    """
    Creates the squeezing operator for a given squeezing parameter alpha

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `alpha` : complex number, the squeezing parameter
    :param dim: dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Squeezing operator

    Examples
    --------
    >>> squeeze = squeeze(alpha=1j, dim=4, sparse=False)
    [[0.7602446 +0.j         0.        +0.j         0.        -0.64963694j      0.        +0.j        ]
    [0.        +0.j         0.33918599+0.j         0.        +0.j               0.        -0.94071933j]
    [0.        -0.64963694j 0.        +0.j         0.7602446 +0.j               0.        +0.j        ]
    [0.        +0.j         0.        -0.94071933j 0.        +0.j               0.33918599+0.j        ]]
    >>> squeeze = squeeze(alpha=1j, dim=4)
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
    n = linA.expm(0.5*(oper.toarray()))
    return sp.csc_matrix(n) if sparse else n

# TODO Does this really work with ndarray ?
def compositeOp(operator: Matrix, dimB: int, dimA: int) -> Matrix:
    """
    Creates a composite operator from a sub-sytem `operator`, i.e. tensor product with identities of dimensions dimB & dimA

    Parameters
    ----------
    :param `operator` : operator of a sub-system
    :param `dimB` : (total) dimension of the systems that appear `before` in the tensor product order
    :param `dimA` : (total) dimension of the systems that appear `after` in the tensor product order

    Returns:
    :return: sub-system operator in the extended Hilbert space

    Examples
    --------
    TODO Update these
    >>> szQ1 = compositeOp(operator=sigmaz(), dimB=0, dimA=2)
    >>> szQ2 = compositeOp(operator=sigmaz(), dimB=2, dimA=0)
    >>> print(szQ1.A)
    [[ 1.  0.  0.  0.]
    [ 0.  1.  0.  0.]
    [ 0.  0. -1.  0.]
    [ 0.  0.  0. -1.]]
    >>> print(szQ2.A)
    [[ 1.  0.  0.  0.]
    [ 0. -1.  0.  0.]
    [ 0.  0.  1.  0.]
    [ 0.  0.  0. -1.]]
    """

    if (dimB <= 1) and (dimA > 1): # pylint: disable=R1716
        oper = sp.kron(operator, sp.identity(dimA), format='csc')
    elif (dimB > 1) and (dimA <= 1): # pylint: disable=R1716
        oper = sp.kron(sp.identity(dimB), operator, format='csc')
    elif (dimB > 1) and (dimA > 1):
        oper = sp.kron(sp.kron(sp.identity(dimB), operator, format='csc'), sp.identity(dimA), format='csc')
    else:
        oper = operator
    return oper
