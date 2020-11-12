import numpy as np
from qTools.QuantumToolbox import states #pylint: disable=import-error

def test_basis():
    testSparse = np.array([[0],[0],[0],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0]])
    testArray = np.array([[0],[0],[0],[0],[0],[0],[1]])
    psiSparse = states.basis(13, 3, sparse=True)
    psiArray = states.basis(7, 6, sparse=False)
    assert (psiSparse.A == testSparse).all() and (psiArray == testArray).all()

def test_completeBasis():
    testSparse = [np.array([[1],[0],[0],[0],[0]]),
                  np.array([[0],[1],[0],[0],[0]]),
                  np.array([[0],[0],[1],[0],[0]]),
                  np.array([[0],[0],[0],[1],[0]]),
                  np.array([[0],[0],[0],[0],[1]])]
    testArray = [np.array([[1],[0],[0]]),
                np.array([[0],[1],[0]]),
                np.array([[0],[0],[1]])]
    psiSparse = states.completeBasis(5, sparse=True)
    psiArray = states.completeBasis(3, sparse=False)
    assert all([(p.A == t).all() for p,t in zip(psiSparse,testSparse)]) and \
           all([(p == t).all() for p,t in zip(psiArray,testArray)])

def test_basisBra():
    testSparse = np.array([[1,0,0,0,0,0]])
    testArray = np.array([[0,0,0,0,0,0,0,1,0]])
    psiSparse = states.basisBra(6, 0, sparse=True)
    psiArray = states.basisBra(9, 7, sparse=False)
    assert (psiSparse.A == testSparse).all() and (psiArray == testArray).all()

def test_superPos():
    assert True is False

def test_outerProd():
    testOP1 = np.array([[0.5,0.5],[0.5,0.5]])
    testOP2 = np.array([[0.707,0],[0.707,0]])
    rho1 = states.outerProd(states.superPos(2,[0,1]))
    rho2 = states.outerProd(states.superPos(2,[0,1]),states.basis(2,0))
    assert (np.around(rho1.A,3)==testOP1).all() and (np.around(rho2.A,3)==testOP2).all()

def test_densityMatrix():
    testDM1 = np.array([[0.5,0.5],[0.5,0.5]])
    testDM2 = np.array([[0.75,0.25],[0.25,0.25]])
    rho1 = states.densityMatrix(states.superPos(2,[0,1]))
    rho2 = states.densityMatrix([states.superPos(2,[0,1]),states.basis(2,0)],[0.5,0.5])
    assert (np.around(rho1.A,3)==testDM1).all() and (np.around(rho2.A,3)==testDM2).all()
