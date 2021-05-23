import numpy as np
import pytest
from quanguru.QuantumToolbox import linearAlgebra as la #pylint: disable=import-error
from quanguru.QuantumToolbox import states #pylint: disable=import-error

def test_basisByRandom(helpers):
    # generate random integers for dimension and excitation, then check item in excitation position is 1 and others 0
    for _ in range(5):
        dim, exc = helpers.generateRndDimAndExc(0)
        st = states.basis(dim, exc).A
        assert st[exc] == 1
        assert all([(st[j] == 0) for j in range(dim) if j != exc])

@pytest.mark.parametrize("params,expected", [
    ((8, 3, True), np.array([[0], [0], [0], [1], [0], [0], [0], [0]])),
    ((7, 6, False), np.array([[0], [0], [0], [0], [0], [0], [1]]))
    ])
def test_basis(params, expected):
    # compare the output with hard-coded fixed values
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
    # compare the output with hard-coded fixed values
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
    # compare the output with hard-coded fixed values
    psiBra = states.basisBra(*params)
    if not isinstance(psiBra, np.ndarray):
        psiBra = psiBra.A
    assert (psiBra == expected).all()

def test_superPosIntInput(helpers):
    # superPos with integer input is equivalent to basis method, thus testing their equivalence with 5 random values
    for _ in range(5):
        dim, exc = helpers.generateRndDimAndExc(0)
        assert np.allclose(states.superPos(dim, exc).A, states.basis(dim, exc).A)

def test_superPosListInput(helpers):
    # testing the list input case that returns equal weight superposition. 1 hard coded case, 1 given values compared
    # 5 random values compared with expected results as a sum of basis
    assert np.allclose(states.superPos(2, [0, 1]).A, np.array([[0.70710678], [0.70710678]]))
    assert np.allclose(states.superPos(3, [0, 1, 2]).A, (1/np.sqrt(3))*(states.basis(3, 0) + states.basis(3, 1) +
                                                                        states.basis(3, 2)).A)
    for _ in range(5):
        dim, comps = helpers.generateRndStateParams()
        state = sum([np.sqrt(1/len(comps))*states.basis(dim, k) for k in comps])
        assert np.allclose(states.superPos(dim, comps.keys()).A, state.A)

def test_superPosDictInput(helpers):
    # testing the dict input by comparing randomly generated states with sum of basis
    for _ in range(5):
        state, dim, excs = helpers.generateRndPureState()
        assert np.allclose(states.superPos(dim, excs).A, state.A)
        state, dim, excs = helpers.generateRndPureState(2)
        state = (1/la.norm(state))*state
        assert np.allclose(states.superPos(dim, excs, populations=False).A, state.A)

@pytest.mark.parametrize("params,expected", [
    ((states.superPos(2, [0, 1])), np.array([[0.5, 0.5], [0.5, 0.5]])),
    ((states.superPos(2, [0, 1]), states.basis(2, 0)), np.array([[0.707, 0], [0.707, 0]]))
    ])
def test_outerProd(params, expected):
    # compare the output with hard-coded fixed values
    rho = states.linAlOuterProd(*params)
    if not isinstance(rho, np.ndarray):
        rho = rho.A
    assert (np.around(rho, 3) == expected).all()

@pytest.mark.parametrize("params,expected", [
    ((states.superPos(2, [0, 1])), np.array([[0.5, 0.5], [0.5, 0.5]])),
    (([states.superPos(2, [0, 1]), states.basis(2, 0)], [0.5, 0.5]), np.array([[0.75, 0.25], [0.25, 0.25]]))
    ])
def test_densityMatrix(params, expected):
    # compare the output with hard-coded fixed values
    rho = states.densityMatrix(*params)
    if not isinstance(rho, np.ndarray):
        rho = rho.A
    assert (np.around(rho, 3) == expected).all()

def test_densityMatrixRandomPure(helpers):
    # test comparing the sum of outer product of 5 random pure states with densityMatrix function outputs
    for _ in range(5):
        state, _, _ = helpers.generateRndPureState()
        assert np.allclose(states.densityMatrix(state).A, la.outerProd(state).A)

def test_densityMatrixRandomMixed(helpers):
    # test comparing the weighted sum (makes mixed state) of outer product of 5 random states with densityMatrix
    # function outputs
    for _ in range(5):
        dim, excs = helpers.generateRndStateParams()
        comps = [states.basis(dim, k) for k in excs]
        state = sum([v*(la.outerProd(states.basis(dim, k))) for k, v in excs.items()])
        assert np.allclose(states.densityMatrix(comps, excs.values()).A, state.A)

def test_normalise(helpers):
    # test normalise by generating random `non-normalised` states, than normalise them, turn into density matrix, trace
    # should be 1
    for _ in range(5):
        dim, excs = helpers.generateRndStateParams()
        state = sum([v*states.basis(dim, k) for k, v in excs.items()])
        assert round(la.trace(states.normalise(la.outerProd(state))), 13) == 1

@pytest.mark.parametrize('name', ['Phi+', 'Phi-', 'Psi+', 'Psi-'])
def test_BellStates(name, specialQubitStates): #pylint:disable=invalid-name
    # test the Bell state functions by comparing with hard coded reference values inside specialQubitStates fixture
    assert np.allclose(states.BellStates(name).A, specialQubitStates['Bell'+name])
