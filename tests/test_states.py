import numpy as np
from qTools.QuantumToolbox.states import basis,completeBasis,basisBra #pylint: disable=import-error

def test_basis():
    testSparse = np.array([[0],[0],[0],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0]])
    testArray = np.array([[0],[0],[0],[0],[0],[0],[1]])
    psiSparse = basis(13, 3, sparse=True)
    psiArray = basis(7, 6, sparse=False)
    assert (psiSparse.toarray() == testSparse).all() and (psiArray == testArray).all()

def test_completeBasis():
    testSparse = [np.array([[1],[0],[0],[0],[0]]),
                  np.array([[0],[1],[0],[0],[0]]),
                  np.array([[0],[0],[1],[0],[0]]),
                  np.array([[0],[0],[0],[1],[0]]),
                  np.array([[0],[0],[0],[0],[1]])]
    testArray = [np.array([[1],[0],[0]]),
                np.array([[0],[1],[0]]),
                np.array([[0],[0],[1]])]
    psiSparse = completeBasis(5, sparse=True)
    psiArray = completeBasis(3, sparse=False)
    assert all([(p.toarray() == t).all() for p,t in zip(psiSparse,testSparse)]) and \
           all([(p == t).all() for p,t in zip(psiArray,testArray)])

def test_basisBra():
    testSparse = np.array([[1,0,0,0,0,0]])
    testArray = np.array([[0,0,0,0,0,0,0,1,0]])
    psiSparse = basisBra(6, 0, sparse=True)
    psiArray = basisBra(9, 7, sparse=False)
    assert (psiSparse.toarray() == testSparse).all() and (psiArray == testArray).all()
