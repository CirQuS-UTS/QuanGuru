"""
    A module of functions to create and/or manipulate quantum operators
"""
import scipy.sparse as sp
import scipy.linalg as linA
import numpy as np

from typing import Union, Callable
from numpy import ndarray
from scipy.sparse import spmatrix

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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
    """
    return sp.identity(N, format="csc") if sparse else np.identity(N)

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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
    """
    data = [1, 1]
    rows = [0, 1]
    columns = [1, 0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

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
    # TODO Create some examples both in here and the demo script
    """
    data = [1, -1]
    rows = [0, 1]
    columns = [0, 1]
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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
    """
    data = [1]
    rows = [1]
    columns = [0]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()

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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
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
    # TODO Create some examples both in here and the demo script
    """
    n = 0.5*(Jp(j, isDim=isDim) + Jm(j, isDim=isDim))
    return n if sparse else n.toarray()

def Jy(k,sparse=True, isDim=True) -> Union[spmatrix, ndarray]:
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
    # TODO Create some examples both in here and the demo script
    """
    n = (1/(2j))*(Jp(k, isDim=isDim) - Jm(k, isDim=isDim))
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
    # TODO Create some examples both in here and the demo script
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
