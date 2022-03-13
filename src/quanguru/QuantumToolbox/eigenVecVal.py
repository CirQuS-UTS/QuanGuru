r"""
    Contains functions to calculate eigen-vector/value statistics in various cases.

    .. currentmodule:: quanguru.QuantumToolbox.eigenVecVal

    Functions
    ---------

    .. autosummary::

        _eigs
        _eigStat
        _eigStatEig
        _eigStatSymp
        _eigsStatEigSymp
        eigVecStatKet

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `_eigs`                   |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `_eigStat`                |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `_eigStatSymp`            |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `_eigStatEig`             |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `_eigsStatEigSymp`        |w| |w| |w| |c|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `eigVecStatKet`           |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from typing import Tuple
import numpy as np # type: ignore
import scipy.linalg as lina # type: ignore
from scipy.sparse import spmatrix # type: ignore

from .functions import fidelityPure
from .states import mat2Vec

from .customTypes import Matrix, floatList, matrixList


def _eigs(Mat: Matrix) -> tuple:
    r"""
    Calculates eigenvalues and eigenvectors of a given matrix (intended for internal use).

    Parameters
    ----------
    Mat : Matrix
        a matrix

    Returns
    -------
    tuple
        tuple containing (eigenvalues, eigenvectors)

    Examples
    --------
    # TODO
    """
    if isinstance(Mat, spmatrix):
        Mat = Mat.A
    return lina.eig(Mat)

def _eigStat(Mat: Matrix, symp: bool = False) -> floatList:
    r"""
    Calculates all the amplitudes :math:`|c_{i,k}|^{2}` of entries :math:`|k\rangle := \begin{bmatrix} c_{1,k}
    \\ \vdots \\
    c_{i,k}
    \\ \vdots \\c_{\mathcal{D},k}
    \end{bmatrix}_{\mathcal{D}\times 1}` for all the eigenvectors :math:`\{|k\rangle\}` of a given matrix.

    symp is used to calculate eigenvector statistics of systems with degeneracies, corresponding to symplectic class by
    summing every odd entry amplitude with the following even entry amplitude.

    Parameters
    ----------
    Mat : Matrix
        a matrix
    symp : bool, optional
        If True (False) sum every odd entry amplitude with the following even entry amplitude.

    Returns
    -------
    floatList
        list of entry amplitudes

    Examples
    --------
    # TODO
    """
    return (np.abs(_eigs(Mat)[1].flatten()))**2 if not symp else _eigStatSymp(Mat)

def _eigStatSymp(Mat: Matrix) -> floatList:
    r"""
    Intended for internal use, and used in eigenvector statistics calculation of symplectic class.

    Parameters
    ----------
    Mat : Matrix
        a matrix

    Returns
    -------
    floatList
        list of entry amplitudes

    Examples
    --------
    # TODO
    """
    vecsSymplectic = _eigs(Mat)[1]
    return _eigsStatEigSymp(vecsSymplectic)

def _eigStatEig(EigVecs: Matrix, symp=False) -> floatList:
    r"""
    Calculates all the amplitudes :math:`|c_{i,k}|^{2}` of entries :math:`|k\rangle := \begin{bmatrix} c_{1,k}
    \\ \vdots \\
    c_{i,k}
    \\ \vdots \\c_{\mathcal{D},k}
    \end{bmatrix}_{\mathcal{D}\times 1}` for a given list of eigenvectors :math:`\{|k\rangle\}`.

    symp is used to calculate eigenvectors statistics of systems with degeneracies, corresponding to symplectic class by
    summing every odd entry amplitude with the following even entry amplitude.

    Parameters
    ----------
    EigVecs : Matrix
        a list of ket vectors
    symp : bool, optional
        If True (False) sum every odd entry amplitude with the following even entry amplitude.

    Returns
    -------
    floatList
        list of entry amplitudes

    Examples
    --------
    # TODO
    """
    return list((np.abs(EigVecs.flatten()))**2) if not symp else _eigsStatEigSymp(EigVecs)

def _eigsStatEigSymp(EigVecs: Matrix) -> floatList:
    r"""
    Intended for internal use, and used in eigenvector statistics calculation of symplectic class.

    Parameters
    ----------
    EigVecs : Matrix
        a list of ket vectors

    Returns
    -------
    floatList
        list of entry amplitudes

    Examples
    --------
    # TODO
    """
    componentsSymplectic = []
    dims = EigVecs.shape[0]
    for ind in range(dims):
        elSymplectic = 0
        for _ in range(int(dims/2)):
            p1Symplectic = (np.abs(EigVecs[:, ind][elSymplectic]))**2
            p2Symplectic = (np.abs(EigVecs[:, ind][elSymplectic+1]))**2
            elSymplectic += 2
            componentsSymplectic.append(p1Symplectic+p2Symplectic)
    return componentsSymplectic

def eigVecStatKet(basis: matrixList, ket: Matrix, symp=True) -> Tuple:
    r"""
    Calculates component amplitudes :math:`|c_{i,k}|^{2}` of a `ket` :math:`|k\rangle := \sum_{i}c_{i,k}|i\rangle` in a
    basis :math:`\{|i\rangle\}`.

    Main use is in eigenvector statistics.

    Parameters
    ----------
    basis : matrixList
        a complete basis
    ket : Matrix
        the ket state

    Returns
    -------
    floatList
        `list` of component values in the basis

    Examples
    --------
    >>> ket = basis(2, 1)
    >>> completeBasis = completeBasis(dimension=2)
    >>> eigVecStatKet(basis=completeBasis, ket=ket)
    [0, 1]
    """
    regStat = [fidelityPure(mat2Vec(state), ket) for state in basis]
    symStat = []
    if symp:
        elSymplectic = 0
        for _ in range(int(len(regStat)/2)):
            symStat.append(regStat[elSymplectic+1] + regStat[elSymplectic])
            elSymplectic += 2
    return regStat, symStat
