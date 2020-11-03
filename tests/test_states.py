import numpy as np
from qTools.QuantumToolbox.states import basis #pylint: disable=import-error

def test_basis():
    psiSparse = basis(13, 3, sparse=True)
    psiArray = basis(7, 6, sparse=False)
    assert (psiSparse.toarray()==np.array([[0],[0],[0],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0]])).all() and \
        (psiArray==np.array([[0],[0],[0],[0],[0],[0],[1]])).all()
