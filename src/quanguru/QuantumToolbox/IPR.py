r"""
    Contains functions to calculate delocalisation measure (Inverse participation ratio, shortly IPR) in various cases.

    .. currentmodule:: quanguru.QuantumToolbox.IPR

    Functions
    ---------

    .. autosummary::

        iprKet
        iprKetNB

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `iprKet`                  |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
       `iprKetNB`                |w| |w| |w| |c|      |w| |w| |c|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

import numpy as np # type: ignore
from scipy.sparse import spmatrix # type: ignore

from .functions import fidelityPure, sortedEigens

from .customTypes import Matrix, matrixList


def iprKet(basis: matrixList, ket: Matrix) -> float:
    r"""
    Calculates inverse participation ratio :math:`1/(\sum_{i}|c_{i,k}|^{4})` of a `ket`
    :math:`|k\rangle = \sum_{i}c_{i,k}|i\rangle` in a given basis :math:`\{|i\rangle\}`. The complex probability
    amplitudes satisfy :math:`\sum_{i}|c_{i,k}|^{2} = 1`, therefore IPR = 1 is perfectly localised, and
    IPR = :math:`1/\mathcal{D}` is uniformly localised in :math:`\mathcal{D}` dimensional space.

    Parameters
    ----------
    basis : matrixList
        a ket state
    ket : Matrix
        a complete basis

    Returns
    -------
    float
        inverse participation ratio

    Examples
    --------
    >>> completeBasis = completeBasis(dimension=2)
    >>> state0 = normalise(0.2*basis(2, 0) + 0.8*basis(2,1))
    >>> iprKet(completeBasis, state0)
    1.1245136186770428
    >>> state1 = normalise(0.5*basis(2, 0) + 0.5*basis(2,1))
    >>> iprKet(completeBasis, state1)
    2.000000000000001
    >>> state2 = basis(2,1)
    >>> iprKet(completeBasis, state2)
    1.0
    """

    return 1/sum(fidelityPure(basKet, ket)**2 for basKet in basis) # type: ignore

def iprKetNB(ket: Matrix) -> float:
    r"""
    Calculates the IPR :math:`1/\sum_{i}|c_{i,k}|^{4}` of a ket :math:`|k\rangle := \begin{bmatrix} c_{1,k} \\ \vdots \\
    c_{i,k}
    \\ \vdots \\c_{\mathcal{D},k}
    \end{bmatrix}_{\mathcal{D}\times 1}` by using each entry :math:`c_{i,k}` as a complex amplitude.

    Parameters
    ----------
    ket : Matrix
        a ket state

    Returns
    -------
    float
        inverse participation ratio

    Examples
    --------
    >>> state0 = normalise(0.2*basis(2, 0) + 0.8*basis(2,1))
    >>> iprKetNB(state0)
    1.1245136186770428
    >>> state1 = normalise(0.5*basis(2, 0) + 0.5*basis(2,1))
    >>> iprKetNB(state1)
    2.000000000000001
    >>> state2 = basis(2,1)
    >>> iprKetNB(state2)
    1.0
    >>> state3 = basis(2,0)
    >>> iprKetNB(state3)
    1.0
    """

    if isinstance(ket, spmatrix):
        ket = ket.A
    return 1/np.sum(np.power((np.abs(ket.flatten())), 4))

def iprMatrix(mat1: Matrix, mat2: Matrix) -> float:
    r"""
    Calculates the IPR between two matrices :math:`1/\sum_{n, m}|\langle \psi_{n}|\Phi_{m}\rangle|^{4}` where :math:`\langle \psi_{n}|` is the 
    nth eigenvector of the first matrix and :math:|\Phi_{m}\rangle` is the mth eigenvector of the second matrix 
    Parameters
    ----------
    mat1 : Matrix
        a matrix (typically a unitary or hamiltonian)
    mat2 : Matrix 
        a matrix (typically a unitary or hamiltonian)

    Returns
    -------
    float
        inverse participation ratio

    """
    IPR = 0
    vals1, basis1 = sortedEigens(mat1)
    vals2, basis2 = sortedEigens(mat2)
    for j in range(len(basis1)):
        for i in range(len(basis2)):
            coeff = fidelityPure(basis1[i], basis2[j])**2
            IPR = IPR + coeff
    return 1/IPR