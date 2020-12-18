r"""
    Contains functions to create qubit rotation operators.

    .. currentmodule:: qTools.QuantumToolbox.qubitRotations

    Functions
    ---------

    .. autosummary::

        qubRotation
        xRotation
        yRotation
        zRotation

"""

import numpy as np # type: ignore

from .operators import sigmaz, sigmax, sigmay, identity
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

    rotUnitary = round(np.cos(angle), 15)*identity(2, sparse) - 1j*round(np.sin(angle), 15)*sigmaz(sparse=sparse)
    return rotUnitary


def qubRotation(xyz: str, angle: float, sparse: bool = True) -> Matrix:
    r"""
    Creates the operator :math:`R_{i}(\theta)` for qubit rotation around the i = x/y/z-axis by `angle` :math:`\theta`.

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
