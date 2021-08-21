r"""
    Contains some basic single and two qubit gates.

    .. currentmodule:: quanguru.QuantumToolbox.basicGates

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
       `CNOT`                    |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `CPHASE`                  |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
       `Hadamard`                |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""


import numpy as np # type: ignore
import scipy.sparse as sp # type: ignore
from .customTypes import Matrix

def CNOT(sparse: bool = True) -> Matrix:
    data = [1, 1, 1, 1]
    rows = [0, 1, 2, 3]
    columns = [0, 1, 3, 2]
    n = sp.csc_matrix((data, (rows, columns)), shape=(4, 4))
    return n if sparse else n.toarray()

def CPHASE(phase: float, sparse: bool = True) -> Matrix:
    data = [1, 1, 1, np.exp(1j*phase)]
    rows = [0, 1, 2, 3]
    columns = [0, 1, 2, 3]
    n = sp.csc_matrix((data, (rows, columns)), shape=(4, 4))
    return n if sparse else n.toarray()

def Hadamard(sparse: bool = True) -> Matrix:
    data = [1/np.sqrt(2), 1/np.sqrt(2), 1/np.sqrt(2), -1/np.sqrt(2)]
    rows = [0, 0, 1, 1]
    columns = [0, 1, 0, 1]
    n = sp.csc_matrix((data, (rows, columns)), shape=(2, 2))
    return n if sparse else n.toarray()
