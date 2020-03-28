"""
    Module of functions to create quantum operations (such as rotations).
"""
from qTools.QuantumToolbox.operators import sigmaz, sigmax, sigmay, identity
from numpy import cos, sin

from typing import Union, Tuple, Any, Literal, List
from numpy import ndarray
from scipy.sparse import spmatrix


def xRotation(angle:float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmax(sparse=sparse)))
    return rotUnitary

def yRotation(angle:float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmay(sparse=sparse)))
    return rotUnitary

def zRotation(angle:float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    rotUnitary = ((cos(angle)*identity(2, sparse))+(sin(angle)*sigmaz(sparse=sparse)))
    return rotUnitary

def qubRotation(xyz=str, angle=float, sparse:bool=True) -> Union[spmatrix, ndarray]:
    if xyz.lower() == 'x':
        rotUnitary = xRotation(angle, sparse)
    elif xyz.lower() == 'y':
        rotUnitary = yRotation(angle, sparse)
    elif xyz.lower() == 'z':
        rotUnitary = zRotation(angle, sparse)
    else:
        print(xyz + ' is not supported')
    return rotUnitary

