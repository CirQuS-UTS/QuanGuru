"""
    Module of functions to create quantum operations (such as rotations).

    Functions
    ---------
    | **xRotation** : Creates the operator for Qubit `X rotation`
    | **yRotation** : Creates the operator for Qubit `Y rotation`
    | **zRotation** : Creates the operator for Qubit `Z rotation`
    | **qubRotation** : Creates the operator for Qubit rotation around given X/Y/Z

    Types
    ^^^^^
    | **Matrix** : Union of (scipy) sparse and (numpy) array
"""

#from qTools.QuantumToolbox.operators import sigmaz, sigmax, sigmay, identity
from numpy import cos, sin # type: ignore

from .operators import sigmaz, sigmax, sigmay, identity
from .customTypes import Matrix

# from typing import TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


def xRotation(angle: float, sparse: bool = True) -> Matrix:
    """
    Creates the operator for Qubit `X rotation`.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    angle : float
        angle of rotation around `X`
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return: Matrix
        Qubit X rotation operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmax(sparse=sparse)))
    return rotUnitary


def yRotation(angle: float, sparse: bool = True) -> Matrix:
    """
    Creates the operator for Qubit `Y rotation`.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    angle : float
        angle of rotation around `Y`
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return: Matrix
        Qubit Y rotation operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmay(sparse=sparse)))
    return rotUnitary


def zRotation(angle: float, sparse: bool = True) -> Matrix:
    """
    Creates the operator for Qubit `Z rotation`.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    angle : float
        angle of rotation around `Z`
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return: Matrix
        Qubit Z rotation operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmaz(sparse=sparse)))
    return rotUnitary


def qubRotation(xyz: str, angle: float, sparse: bool = True) -> Matrix:
    """
    Creates the operator for Qubit rotation around given X/Y/Z.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False)

    Parameters
    ----------
    xyz : str
        string for rotation direction
    angle : float
        angle of rotation around `x`
    sparse : bool
        boolean for sparse or not (array)

    Returns
    -------
    :return: Matrix
        Qubit X/Y/Z rotation operator.

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """

    if xyz.lower() == 'x':
        rotUnitary = xRotation(angle, sparse)
    elif xyz.lower() == 'y':
        rotUnitary = yRotation(angle, sparse)
    elif xyz.lower() == 'z':
        rotUnitary = zRotation(angle, sparse)
    else:
        print(xyz + ' is not supported')
    return rotUnitary
