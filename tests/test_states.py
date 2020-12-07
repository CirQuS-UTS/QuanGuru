import pytest
import numpy as np
from qTools.QuantumToolbox import states #pylint: disable=import-error

@pytest.mark.parametrize("params,expected", [
    ((8,3,True), np.array([[0],[0],[0],[1],[0],[0],[0],[0]])),
    ((7,6,False), np.array([[0],[0],[0],[0],[0],[0],[1]]))
    ])
def test_basis(params,expected):
    psi = states.basis(*params)
    if not isinstance(psi, np.ndarray):
        psi = psi.A
    assert (psi == expected).all()

@pytest.mark.parametrize("params,expected", [
    ((5,True), [np.array([[1],[0],[0],[0],[0]]),
                np.array([[0],[1],[0],[0],[0]]),
                np.array([[0],[0],[1],[0],[0]]),
                np.array([[0],[0],[0],[1],[0]]),
                np.array([[0],[0],[0],[0],[1]])]),
    ((3,False), [np.array([[1],[0],[0]]),
                 np.array([[0],[1],[0]]),
                 np.array([[0],[0],[1]])])
    ])
def test_completeBasis(params,expected):
    psiList = states.completeBasis(*params)
    for i,p in enumerate(psiList):
        if not isinstance(p, np.ndarray):
            psiList[i] = p.A
    assert all([(p == e).all() for p,e in zip(psiList,expected)])

@pytest.mark.parametrize("params,expected", [
    ((6,0,True), np.array([[1,0,0,0,0,0]])),
    ((9,7,False), np.array([[0,0,0,0,0,0,0,1,0]]))
    ])
def test_basisBra(params,expected):
    psiBra = states.basisBra(*params)
    if not isinstance(psiBra, np.ndarray):
        psiBra = psiBra.A
    assert (psiBra == expected).all()

def test_superPos():
    assert True is True

@pytest.mark.parametrize("params,expected", [
    ((states.superPos(2,[0,1])), np.array([[0.5,0.5],[0.5,0.5]])),
    ((states.superPos(2,[0,1]),states.basis(2,0)), np.array([[0.707,0],[0.707,0]]))
    ])
def test_outerProd(params,expected):
    rho = states.outerProd(*params)
    if not isinstance(rho, np.ndarray):
        rho = rho.A
    assert (np.around(rho,3)==expected).all()

@pytest.mark.parametrize("params,expected", [
    ((states.superPos(2,[0,1])), np.array([[0.5,0.5],[0.5,0.5]])),
    (([states.superPos(2,[0,1]),states.basis(2,0)],[0.5,0.5]), np.array([[0.75,0.25],[0.25,0.25]]))
    ])
def test_densityMatrix(params,expected):
    rho = states.densityMatrix(*params)
    if not isinstance(rho, np.ndarray):
        rho = rho.A
    assert (np.around(rho,3)==expected).all()
