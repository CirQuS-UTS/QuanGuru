r"""
    Contains functions to create qubit rotation operators.

    .. currentmodule:: quanguru.QuantumToolbox.spinRotations

    Functions
    ---------

    .. autosummary::

        qubRotation
        spinRotation
        xRotation
        yRotation
        zRotation

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `qubRotation`             |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `spinRotation`            |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `xRotation`               |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `yRotation`               |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `zRotation`               |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

import numpy as np # type: ignore

from .operators import sigmaz, sigmax, sigmay, identity, Jz, Jx, Jy
from .evolution import Unitary
from .customTypes import Matrix


# do not delete these
# from typing import TypeVar
# from numpy import ndarray
# from scipy.sparse import spmatrix

# These type aliases are used in type hinting of below methods
# Matrix = TypeVar('Matrix', spmatrix, ndarray)       # Type which is either spmatrix or nparray (created using TypeVar)


def xRotation(angle: float, sparse: bool = True) -> Matrix:
    r"""
    Creates the operator :math:`R_{x}(\theta)` for qubit rotation around the x-axis by `angle` :math:`\theta`.

    Parameters
    ----------
    angle : float
        angle of rotation around `x`
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Qubit X rotation operator :math:`R_{x}(\theta)`

    Examples
    --------
    # TODO
    """
    angle = angle/2
    rotUnitary = round(np.cos(angle), 15)*identity(2, sparse) - 1j*round(np.sin(angle), 15)*sigmax(sparse=sparse)
    return rotUnitary

def yRotation(angle: float, sparse: bool = True) -> Matrix:
    r"""
    Creates the operator :math:`R_{y}(\theta)` for qubit rotation around the y-axis by `angle` :math:`\theta`.

    Parameters
    ----------
    angle : float
        angle of rotation around `y`
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Qubit Y rotation operator :math:`R_{y}(\theta)`

    Examples
    --------
    # TODO
    """
    angle = angle/2
    rotUnitary = round(np.cos(angle), 15)*identity(2, sparse) - 1j*round(np.sin(angle), 15)*sigmay(sparse=sparse)
    return rotUnitary

def zRotation(angle: float, sparse: bool = True) -> Matrix:
    r"""
    Creates the operator :math:`R_{z}(\theta)` for qubit rotation around the z-axis by `angle` :math:`\theta`.

    Parameters
    ----------
    angle : float
        angle of rotation around `z`
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Qubit Z rotation operator :math:`R_{z}(\theta)`

    Examples
    --------
    # TODO
    """
    angle = angle/2
    rotUnitary = round(np.cos(angle), 15)*identity(2, sparse) - 1j*round(np.sin(angle), 15)*sigmaz(sparse=sparse)
    return rotUnitary

def qubRotation(xyz: str, angle: float, sparse: bool = True) -> Matrix:
    r"""
    Creates the operator :math:`R_{i}(\theta) := e^{-i\sigma_{i}\theta/2}` for qubit rotation around the i = x/y/z-axis
    by `angle` :math:`\theta`.

    Parameters
    ----------
    xyz : str
        string for rotation direction x, y, or z
    angle : float
        angle of rotation
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)

    Returns
    -------
    Matrix
        Qubit x/y/z rotation operator.

    Examples
    --------
    # TODO
    """

    if xyz.lower() == 'x':
        rotUnitary = xRotation(angle, sparse)
    elif xyz.lower() == 'y':
        rotUnitary = yRotation(angle, sparse)
    elif xyz.lower() == 'z':
        rotUnitary = zRotation(angle, sparse)
    else:
        raise ValueError(xyz + ' is not supported')
    return rotUnitary

def spinRotation(xyz: str, angle: float, j: float, sparse: bool = True, isDim: bool = False) -> Matrix:
    r"""
    Creates the operator :math:`R_{i}(\theta) := e^{-iJ_{i}\theta}` for a spin value j rotation around i = x/y/z-axis
    by `angle` :math:`\theta`.

    Parameters
    ----------
    xyz : str
        string for rotation direction x, y, or z
    angle : float
        angle of rotation
    j : int or float
        integer or half-integer spin quantum number, or the dimension (then spin quantum number = (d-1)/2)
    sparse : bool
        if True(False), the returned Matrix type will be sparse(array)
    isDim : bool
        boolean for whether j is spin quantum number of dimension

    Returns
    -------
    Matrix
        Spin x/y/z rotation operator.

    Examples
    --------
    # TODO
    """
    if xyz.lower() == 'x':
        rotOp = Jx
    elif xyz.lower() == 'y':
        rotOp = Jy
    elif xyz.lower() == 'z':
        rotOp = Jz
    else:
        raise ValueError(xyz + ' is not supported')
    rotOpMat = rotOp(j, isDim=isDim, sparse=sparse)
    rotUnitary = Unitary(angle*rotOpMat)
    return rotUnitary
