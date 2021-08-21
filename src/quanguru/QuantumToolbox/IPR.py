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

from .functions import fidelityPure

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

    return 1/sum([fidelityPure(basKet, ket)**2 for basKet in basis]) # type: ignore

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
