"""
    Module of functions to create and/or manipulate quantum operators
"""
import scipy.sparse as sp
import scipy.linalg as linA
import numpy as np

from typing import Union, Callable
from numpy import ndarray
from scipy.sparse import spmatrix

def number(N:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the (bosonic) number operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ----------
    :param `N` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: number operator for dimension N

    Examples
    --------
    >>> numberArray = qOperators.number(N=3, sparse=False)
    [[0 0 0]
    [0 1 0]
    [0 0 2]]
    >>> numberSparse = qOperators.number(3)
    (0, 0)	0
    (1, 1)	1
    (2, 2)	2
    """
    data = [i for i in range(N)]
    rows = range(0, N)
    columns = range(0, N)
    n = sp.csc_matrix((data, (rows, columns)), shape=(N, N))
    return n if sparse else n.toarray()

def destroy(N: int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the bosonic `annihilation` operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `N` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: bosonic `annihilation` operator for dimension N

    Examples
    --------
    >>> annihilation = qOperators.destroy(N=3)
    (0, 1)	1.0
    (1, 2)	1.4142135623730951
    >>> annihilation = qOperators.destroy(3, sparse=False)
    [[0.         1.         0.        ]
    [0.         0.         1.41421356]
    [0.         0.         0.        ]]
    """
    data = [np.sqrt(i+1) for i in range(N-1)]
    rows = range(0,N-1)
    columns = range(1,N)
    n = sp.csc_matrix((data, (rows, columns)), shape=(N, N))
    return n if sparse else n.toarray()

def create(N: int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the bosonic `creation` operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `N` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: bosonic `creation` operator for dimension N

    Examples
    --------
    >>> create = qOperators.create(3)
    (1, 0)	1.0
    (2, 1)	1.4142135623730951
    >>> create = qOperators.create(3, sparse=False)
    [[0.         0.         0.        ]
    [1.         0.         0.        ]
    [0.         1.41421356 0.        ]]
    """
    data = [np.sqrt(i+1) for i in range(N-1)]
    rows = range(1,N)
    columns = range(0,N-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(N, N))
    return n if sparse else n.toarray()

def identity(N: int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the identity operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `N` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: identity operator for dimension N

    Examples
    --------
    >>> identity = qOperators.identity(3)
    (0, 0)	1.0
    (1, 1)	1.0
    (2, 2)	1.0
    >>> identity = qOperators.identity(3, sparse=False)
    [[1. 0. 0.]
    [0. 1. 0.]
    [0. 0. 1.]]
    """
    return sp.identity(N, format="csc") if sparse else np.identity(N)

def sigmaz(N:int=2, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the `Pauli` sigma z operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME N is meaningles, it is introduces to make objects more uniform, might remove later
    :param `N` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma z operator

    Examples
    --------
    >>> sz = qOperators.sigmaz(sparse=False)
    [[ 1  0]
    [ 0 -1]]
    >>> sz = qOperators.sigmaz()
    (0, 0)	1
    (1, 1)	-1
    """
    data = [1, -1]
    rows = [0, 1]
    columns = [0, 1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmay(N:int=2, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the `Pauli` sigma y operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME N is meaningles, it is introduces to make objects more uniform, might remove later
    :param `N` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma y operator

    Examples
    --------
    >>> sy = qOperators.sigmay(sparse=False)
    [[0.+0.j 0.-1.j]
    [0.+1.j 0.+0.j]]
    >>> sy = qOperators.sigmay()
    (1, 0)	1j
    (0, 1)	(-0-1j)
    """
    data = [-1j, 1j]
    rows = [0, 1]
    columns = [1, 0]
    n =  sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmax(N:int=2, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the `Pauli` sigma x operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME N is meaningles, it is introduces to make objects more uniform, might remove later
    :param `N` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma x operator

    Examples
    --------
    >>> sx = qOperators.sigmax(sparse=False)
    [[0 1]
    [1 0]]
    >>> sx = qOperators.sigmax()
    (1, 0)	1
    (0, 1)	1
    """
    data = [1, 1]
    rows = [0, 1]
    columns = [1, 0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmap(N:int=2, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the `Pauli` sigma + operator, i.e. 2D Fermionic creation operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME N is meaningles, it is introduces to make objects more uniform, might remove later
    :param `N` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma + operator

    Examples
    --------
    >>> sp = qOperators.sigmap(sparse=False)
    [[0 1]
    [0 0]]
    >>> sp = qOperators.sigmap()
    (0, 1)	1
    """
    data = [1]
    rows = [0]
    columns = [1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def sigmam(N:int=2, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the `Pauli` sigma - operator, i.e. 2D Fermionic destruction operator.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    # FIXME N is meaningles, it is introduces to make objects more uniform, might remove later
    :param `N` : dimension of the Hilbert space (2 by default)
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: `Pauli` sigma - operator

    Examples
    --------
    >>> sm = qOperators.sigmam(sparse=False)
    [[0 0]
    [1 0]]
    >>> sm = qOperators.sigmam()
    (1, 0)	1
    """
    data = [1]
    rows = [1]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

def Jz(j:float, sparse:bool=True, isDim:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the angular momentum (spin) `Z` operator for a given spin quantum number j.

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
    >>> jz0 = qOperators.Jz(j=2, isDim=False, sparse=False)
    [[ 2  0  0  0  0]
    [ 0  1  0  0  0]
    [ 0  0  0  0  0]
    [ 0  0  0 -1  0]
    [ 0  0  0  0 -2]]
    >>> jz0 = qOperators.Jz(j=2, isDim=False)
    (0, 0)	2
    (1, 1)	1
    (2, 2)	0
    (3, 3)	-1
    (4, 4)	-2
    >>> jz1 = qOperators.Jz(j=5, sparse=False)
    [[ 2.  0.  0.  0.  0.]
    [ 0.  1.  0.  0.  0.]
    [ 0.  0.  0.  0.  0.]
    [ 0.  0.  0. -1.  0.]
    [ 0.  0.  0.  0. -2.]]
    >>> jz1 = qOperators.Jz(j=5, isDim=True)
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
    rows = range(0,d)
    columns = range(0,d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jp(j:float, sparse:bool=True, isDim:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the angular momentum (spin) `creation` operator for a given spin quantum number j.

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
    >>> jp0 = qOperators.Jp(j=2, isDim=False, sparse=False)
    [[0.         2.         0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.44948974 0.        ]
    [0.         0.         0.         0.         2.        ]
    [0.         0.         0.         0.         0.        ]]
    >>> jp0 = qOperators.Jp(j=2, isDim=False)
    (0, 1)	2.0
    (1, 2)	2.449489742783178
    (2, 3)	2.449489742783178
    (3, 4)	2.0
    >>> jp1 = qOperators.Jp(j=5, sparse=False)
    [[0.         2.         0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.44948974 0.        ]
    [0.         0.         0.         0.         2.        ]
    [0.         0.         0.         0.         0.        ]]
    >>> jp1 = qOperators.Jp(j=5, isDim=True)
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
    rows = range(0,d-1)
    columns = range(1,d)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jm(j:float, sparse:bool=True, isDim:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the angular momentum (spin) `destruction` operator for a given spin quantum number j.

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
    >>> jm0 = qOperators.Jm(j=2, isDim=False, sparse=False)
    [[0.         0.         0.         0.         0.        ]
    [2.         0.         0.         0.         0.        ]
    [0.         2.44948974 0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.         0.        ]]
    >>> jm0 = qOperators.Jm(j=2, isDim=False)
    (1, 0)	2.0
    (2, 1)	2.449489742783178
    (3, 2)	2.449489742783178
    (4, 3)	2.0
    >>> jm1 = qOperators.Jm(j=5, sparse=False)
    [[0.         0.         0.         0.         0.        ]
    [2.         0.         0.         0.         0.        ]
    [0.         2.44948974 0.         0.         0.        ]
    [0.         0.         2.44948974 0.         0.        ]
    [0.         0.         0.         2.         0.        ]]
    >>> jm1 = qOperators.Jm(j=5, isDim=True)
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
    rows = range(1,d)
    columns = range(0,d-1)
    n = sp.csc_matrix((data, (rows, columns)), shape=(d, d))
    return n if sparse else n.toarray()

def Jx(j:float, sparse:bool=True, isDim:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the angular momentum (spin) `X` operator for a given spin quantum number j.

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
    >>> jx0 = qOperators.Jx(j=2, isDim=False, sparse=False)
    [[0.         1.         0.         0.         0.        ]
    [1.         0.         1.22474487 0.         0.        ]
    [0.         1.22474487 0.         1.22474487 0.        ]
    [0.         0.         1.22474487 0.         1.        ]
    [0.         0.         0.         1.         0.        ]]
    >>> jx0 = qOperators.Jx(j=2, isDim=False)
    (1, 0)	1.0
    (0, 1)	1.0
    (2, 1)	1.224744871391589
    (1, 2)	1.224744871391589
    (3, 2)	1.224744871391589
    (2, 3)	1.224744871391589
    (4, 3)	1.0
    (3, 4)	1.0
    >>> jx1 = qOperators.Jx(j=5, sparse=False)
    [[0.         1.         0.         0.         0.        ]
    [1.         0.         1.22474487 0.         0.        ]
    [0.         1.22474487 0.         1.22474487 0.        ]
    [0.         0.         1.22474487 0.         1.        ]
    [0.         0.         0.         1.         0.        ]]
    >>> jx1 = qOperators.Jx(j=5, isDim=True)
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

def Jy(j, sparse=True, isDim=True) -> Union[spmatrix, ndarray]:
    """
    Creates the angular momentum (spin) `Y` operator for a given spin quantum number j.

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
    >>> jy0 = qOperators.Jy(j=2, isDim=False, sparse=False)
    [[0.+0.j         0.-1.j         0.+0.j         0.+0.j                0.+0.j        ]
    [0.+1.j         0.+0.j         0.-1.22474487j 0.+0.j                0.+0.j        ]
    [0.+0.j         0.+1.22474487j 0.+0.j         0.-1.22474487j        0.+0.j        ]
    [0.+0.j         0.+0.j         0.+1.22474487j 0.+0.j                0.-1.j        ]
    [0.+0.j         0.+0.j         0.+0.j         0.+1.j                0.+0.j        ]]
    >>> jy0 = qOperators.Jy(j=2, isDim=False)
    (1, 0)	1j
    (0, 1)	-1j
    (2, 1)	1.224744871391589j
    (1, 2)	-1.224744871391589j
    (3, 2)	1.224744871391589j
    (2, 3)	-1.224744871391589j
    (4, 3)	1j
    (3, 4)	-1j
    >>> jy1 = qOperators.Jy(j=5, sparse=False)
    [[0.+0.j         0.-1.j         0.+0.j         0.+0.j                0.+0.j        ]
    [0.+1.j         0.+0.j         0.-1.22474487j 0.+0.j                0.+0.j        ]
    [0.+0.j         0.+1.22474487j 0.+0.j         0.-1.22474487j        0.+0.j        ]
    [0.+0.j         0.+0.j         0.+1.22474487j 0.+0.j                0.-1.j        ]
    [0.+0.j         0.+0.j         0.+0.j         0.+1.j                0.+0.j        ]]
    >>> jy1 = qOperators.Jy(j=5, isDim=True)
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

def Js(j:float, sparse:bool=True, isDim:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the total angular momentum (spin) operator for a given spin quantum number j.

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
    >>> js0 = qOperators.Js(j=2, isDim=False, sparse=False)
    [[6.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 6.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 6.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 6.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 0.+0.j 6.+0.j]]
    >>> js0 = qOperators.Js(j=2, isDim=False)
    (0, 0)	(6+0j)
    (1, 1)	(6+0j)
    (2, 2)	(5.999999999999999+0j)
    (3, 3)	(6+0j)
    (4, 4)	(6+0j)
    >>> js1 = qOperators.Js(j=5, sparse=False)
    [[6.+0.j 0.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 6.+0.j 0.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 6.+0.j 0.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 6.+0.j 0.+0.j]
    [0.+0.j 0.+0.j 0.+0.j 0.+0.j 6.+0.j]]
    >>> js1 = qOperators.Js(j=5, isDim=True)
    (0, 0)	(6+0j)
    (1, 1)	(6+0j)
    (2, 2)	(5.999999999999999+0j)
    (3, 3)	(6+0j)
    (4, 4)	(6+0j)
    """
    n = (Jx(j, isDim=isDim)@Jx(j, isDim=isDim)) + (Jy(j, isDim=isDim)@Jy(j, isDim=isDim)) + (Jz(j, isDim=isDim)@Jz(j, isDim=isDim))
    return n if sparse else n.toarray()

def operatorPow(op: Callable, dim:int, power:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates a quantum operator for given function reference `op` and raises to a `power`.

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
    # TODO Create some examples both in here and the demo script
    """
    return op(dim, sparse)**power


def paritySUM(N:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the parity operator by explicity placing alternating +/- into a matrix.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    :param `N` : dimension of the Hilbert space
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Parity operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    a = np.empty((N,))
    a[::2] = 1
    a[1::2] = -1
    data = a
    rows = range(0,N)
    columns = range(0,N)
    n = sp.csc_matrix((data,(rows,columns)), shape=(N,N))
    return n if sparse else n.toarray()

def parityEXP(HamiltonianCavity: Union[spmatrix, ndarray]) -> Union[spmatrix, ndarray]:
    """
    Creates the parity operator by exponetiationg a given Hamiltonian.

    Keeps sparse/array as sparse/array.

    Parameters
    ----------
    :param `HamiltonianCavity` : dimension of the Hilbert space

    Returns
    -------
    :return: Parity operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    sparse = sp.isspmatrix(HamiltonianCavity)
    parEX = ((1j * np.pi) * HamiltonianCavity.toarray())
    n = linA.expm(parEX)
    return sp.csc_matrix(n) if sparse else n

def basis(dimension:int, state:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
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

def displacement(alpha:complex, dim:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the displacement operator for a given displacement parameter alpha.

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
    # TODO Create some examples both in here and the demo script
    """
    oper = (alpha * create(dim)) - (np.conj(alpha) * destroy(dim))
    n = linA.expm(oper.toarray())
    return sp.csc_matrix(n) if sparse else n

def squeeze(alpha:complex, dim:int, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the squeezing operator for a given squeezing parameter alpha.

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
    # TODO Create some examples both in here and the demo script
    """
    oper = -(alpha * (create(dim)@create(dim))) + (np.conj(alpha) * (destroy(dim)@destroy(dim)))
    n = linA.expm(0.5*(oper.toarray()))
    return sp.csc_matrix(n) if sparse else n

# TODO Does this really work with ndarray ?
def compositeOp(operator: Union[spmatrix, ndarray], dimB:int, dimA:int) -> Union[spmatrix, ndarray]:
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
    # TODO Create some examples both in here and the demo script
    """
    if (dimB <= 1) and (dimA > 1):
        return sp.kron(operator,sp.identity(dimA), format='csc')
    elif (dimB > 1) and (dimA <= 1):
        return sp.kron(sp.identity(dimB), operator, format='csc')
    elif (dimB > 1) and (dimA > 1):
        return sp.kron(sp.kron(sp.identity(dimB), operator, format='csc'), sp.identity(dimA), format='csc')
    else:
        return operator