from typing import List

import numpy as np # type: ignore
import scipy.linalg as lina # type: ignore
from scipy.sparse import spmatrix # type: ignore

from .functions import fidelity

from .customTypes import Matrix, floatList, matrixList



# Eigenvector statistics
def _eigs(Mat: Matrix) -> matrixList:
    if isinstance(Mat, spmatrix):
        Mat = Mat.A
    return lina.eig(Mat)

def _eigStat(Mat: Matrix, symp: bool = False) -> floatList:
    return (np.abs(_eigs(Mat)[1].flatten()))**2 if not symp else _eigStatSymp(Mat)

def _eigStatSymp(Mat: Matrix) -> floatList:
    vecsSymplectic = _eigs(Mat)[1]
    return _eigsStatEigSymp(vecsSymplectic)

def _eigStatEig(EigVecs: Matrix, symp=False) -> floatList:
    return (np.abs(EigVecs.flatten()))**2 if not symp else _eigsStatEigSymp(EigVecs)

def _eigsStatEigSymp(EigVecs: Matrix) -> floatList:
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

# TODO create the function for the result of eigenvec calculation
def eigVecStatKet(basis: matrixList, ket: Matrix) -> floatList:
    """
    Calculates components of a `ket` in a basis.

    Main use is in eigenvector statistics.

    Parameters
    ----------
    basis : matrixList
        a complete basis
    ket : Matrix
        the ket state

    Returns
    -------
    :return: floatList
        `list` of component values in the basis

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket = qStates.basis(2, 1)
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> components = eigVecStatKet(basis=completeBasis, ket=ket)
    [0, 1]
    """

    comps = []
    for basKet in basis:
        comps.append(fidelity(basKet, ket))
    return comps


def eigVecStatKetList(basis: matrixList, kets: matrixList) -> List[floatList]:
    """
    Calculates components of a `list of ket states`
    Main use is in eigenvector statistics.

    Parameters
    ----------
    basis : matrixList
        a complete basis
    kets : matrixList
        `list` of ket states

    Returns
    -------
    :return: List[floatList]
        `list` of component values in the basis

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket0 = qStates.basis(2, 0)
    >>> ket1 = qStates.basis(2, 1)
    >>> ketList = [ket0, ket1]
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> components = eigVecStatKetList(basis=completeBasis, kets=ketList)
    [[1, 0], [0, 1]]
    """

    compsList = []
    for ket in kets:
        compsList.append(eigVecStatKet(basis, ket))
    return compsList


def eigVecStatKetNB(ket: Matrix) -> float:
    """
    Calculates the components of a ket by assuming that the basis is of the free Hamiltonian.

    Parameters
    ----------
    ket : Matrix
        a ket state or list of ket states

    Returns
    -------
    return: float
        list of components

    Examples
    --------
    >>> import qTools.QuantumToolbox.states as qStates
    >>> ket = qStates.basis(2, 1)
    >>> completeBasis = qStates.completeBasis(dimension=2)
    >>> components = eigVecStatKetNB(ket=ket)
    [0 1]
    """

    # TODO Find a way around this
    if isinstance(ket, spmatrix):
        ket = ket.A
    return np.real(ket.flatten())
