"""
    Module of functions to create quantum operations (such as rotations).
"""
from qTools.QuantumToolbox.operators import sigmaz, sigmax, sigmay, identity
from numpy import cos, sin

from typing import Union, Tuple, Any, Literal, List
from numpy import ndarray
from scipy.sparse import spmatrix


def xRotation(angle:float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the operator for Qubit ``X rotation``.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ----------
    :param `angle` : angle of rotation around `X`
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Qubit X rotation operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmax(sparse=sparse)))
    return rotUnitary

def yRotation(angle:float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the operator for Qubit ``Y rotation``.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ----------
    :param `angle` : angle of rotation around `Y`
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Qubit Y rotation operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmay(sparse=sparse)))
    return rotUnitary

def zRotation(angle:float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the operator for Qubit ``Z rotation``.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ----------
    :param `angle` : angle of rotation around `Z`
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Qubit Z rotation operator

    Examples
    --------
    # TODO Create some examples both in here and the demo script
    """
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmaz(sparse=sparse)))
    return rotUnitary

def qubRotation(xyz=str, angle=float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    """
    Creates the operator for Qubit rotation around given X/Y/Z.

    Either as sparse (>>> sparse=True) or array (>>> sparse=False) 

    Parameters
    ----------
    :param `xyz` : string for rotation direction
    :param `angle` : angle of rotation around `x`
    :param `sparse` : boolean for sparse or not (array)

    Returns
    -------
    :return: Qubit X/Y/Z rotation operator

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

