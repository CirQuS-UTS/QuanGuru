import random as rn
import numpy as np
import pytest
from qTools.QuantumToolbox import linearAlgebra as la #pylint: disable=import-error
from qTools.QuantumToolbox import states #pylint: disable=import-error

def generateRndDimAndExc(min):
    dim = rn.randint(2, 20)
    return dim, rn.randint(min, dim-1)

def test_basisByRandom():
    # generate random integers for dimension and excitation, then check item in excitation position is 1 and others 0
    for _ in range(10):
        dim, exc = generateRndDimAndExc(0)
        st = states.basis(dim, exc).A
        assert st[exc] == 1
        assert all([(st[j] == 0) for j in range(dim) if j != exc])


@pytest.mark.parametrize("params,expected", [
    ((8, 3, True), np.array([[0], [0], [0], [1], [0], [0], [0], [0]])),
    ((7, 6, False), np.array([[0], [0], [0], [0], [0], [0], [1]]))
    ])
def test_basis(params, expected):
    psi = states.basis(*params)
    if not isinstance(psi, np.ndarray):
        psi = psi.A
    assert (psi == expected).all()

@pytest.mark.parametrize("params,expected", [
    ((5, True), [np.array([[1], [0], [0], [0], [0]]),
                 np.array([[0], [1], [0], [0], [0]]),
                 np.array([[0], [0], [1], [0], [0]]),
                 np.array([[0], [0], [0], [1], [0]]),
                 np.array([[0], [0], [0], [0], [1]])]),
    ((3, False), [np.array([[1], [0], [0]]),
                  np.array([[0], [1], [0]]),
                  np.array([[0], [0], [1]])])
    ])
def test_completeBasis(params, expected):
    psiList = states.completeBasis(*params)
    for i, p in enumerate(psiList):
        if not isinstance(p, np.ndarray):
            psiList[i] = p.A
    assert all([(p == e).all() for p, e in zip(psiList, expected)])

@pytest.mark.parametrize("params,expected", [
    ((6, 0, True), np.array([[1, 0, 0, 0, 0, 0]])),
    ((9, 7, False), np.array([[0, 0, 0, 0, 0, 0, 0, 1, 0]]))
    ])
def test_basisBra(params, expected):
    psiBra = states.basisBra(*params)
    if not isinstance(psiBra, np.ndarray):
        psiBra = psiBra.A
    assert (psiBra == expected).all()


def test_superPosIntInput():
    # superPos with integer input is equivalent to basis method, thus testing their equivalence with 10 random values
    for _ in range(10):
        dim, exc = generateRndDimAndExc(0)
        assert np.allclose(states.superPos(dim, exc).A, states.basis(dim, exc).A)

def test_superPosListInput():
    # testing the list input case that returns equal weight superposition. 1 hard coded case, 1 given values compared
    # 5 random values compared with expected results as a sum of basis
    assert np.allclose(states.superPos(2, [0, 1]).A, np.array([[0.70710678], [0.70710678]]))
    assert np.allclose(states.superPos(3, [0, 1, 2]).A, (1/np.sqrt(3))*(states.basis(3, 0) + states.basis(3, 1) +
                                                                        states.basis(3, 2)).A)
    for _ in range(5):
        dim, ncom = generateRndDimAndExc(1)
        comps = list(dict.fromkeys([rn.randint(1, dim-1) for k in range(ncom)]))
        state = sum([np.sqrt(1/len(comps))*states.basis(dim, k) for k in comps])
        assert np.allclose(states.superPos(dim, comps).A, state.A)

def test_superPosDictInput():
    # testing the dict input by comparing randomly generated states with sum of basis
    for _ in range(5):
        dim1, ncom = generateRndDimAndExc(1)
        comps = list(dict.fromkeys([rn.randint(1, dim1-1) for k in range(ncom)]))
        pops = np.random.dirichlet(np.ones(len(comps)), size=1)[0]
        excs = dict(zip(comps, pops))
        state = sum([np.sqrt(v)*states.basis(dim1, k) for k, v in excs.items()])
        assert np.allclose(states.superPos(dim1, excs).A, state.A)
        state = sum([v*states.basis(dim1, k) for k, v in excs.items()])
        state = (1/la.norm(state))*state
        assert np.allclose(states.superPos(dim1, excs, populations=False).A, state.A)

@pytest.mark.parametrize("params,expected", [
    ((states.superPos(2, [0, 1])), np.array([[0.5, 0.5], [0.5, 0.5]])),
    ((states.superPos(2, [0, 1]), states.basis(2, 0)), np.array([[0.707, 0], [0.707, 0]]))
    ])
def test_outerProd(params, expected):
    rho = states.outerProd(*params)
    if not isinstance(rho, np.ndarray):
        rho = rho.A
    assert (np.around(rho, 3) == expected).all()

@pytest.mark.parametrize("params,expected", [
    ((states.superPos(2, [0, 1])), np.array([[0.5, 0.5], [0.5, 0.5]])),
    (([states.superPos(2, [0, 1]), states.basis(2, 0)], [0.5, 0.5]), np.array([[0.75, 0.25], [0.25, 0.25]]))
    ])
def test_densityMatrix(params, expected):
    rho = states.densityMatrix(*params)
    if not isinstance(rho, np.ndarray):
        rho = rho.A
    assert (np.around(rho, 3) == expected).all()
