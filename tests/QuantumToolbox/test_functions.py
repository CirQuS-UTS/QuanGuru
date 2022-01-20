import numpy as np
import pytest
from quanguru.QuantumToolbox import linearAlgebra as la #pylint: disable=import-error
from quanguru.QuantumToolbox import operators as ops #pylint: disable=import-error
from quanguru.QuantumToolbox import functions as fns #pylint: disable=import-error
#testCase = collections.namedtuple('testCase', ['operator', 'state', 'expected'])

def test_expectationWithNumber(helpers):
    # using randomly generated ket states of random dimension, and also by converting them into density matrix
    # test expectation function by using number operator, whose expectation should be sum of photon_number*populations
    for _ in range(3):
        state, dim, excs = helpers.generateRndPureState()
        calcva = fns.expectation(ops.number(dim), state)
        expect = sum([k*v for (k, v) in excs.items()])
        assert round(calcva, 12) == round(expect, 12)
        denMat = la.outerProd(state)
        assert round(fns.expectation(ops.number(dim), denMat), 12) == round(expect, 12)

def test_expectationWithJz(helpers):
    # using randomly generated ket states of random j value, and also by converting them into density matrix
    # test expectation function by using Jz operator, whose expectation is jValue*populations
    for _ in range(3):
        state, dim, excs = helpers.generateRndPureState()
        calcva = fns.expectation(ops.Jz((dim-1)/2), state)
        expect = sum([((dim-1)/2-k)*v for (k, v) in excs.items()])
        assert round(calcva, 12) == round(expect, 12)
        denMat = la.outerProd(state)
        assert round(fns.expectation(ops.Jz((dim-1)/2), denMat), 12) == round(expect, 12)

def test_expectationWithSigmaz(helpers, singleQubitOperators):
    # using randomly generated ket states, and also by converting them into density matrix
    # test expectation function by using sigmaz operator, whose expectation is +-1*populations
    op = singleQubitOperators['sz']
    for _ in range(3):
        state, _, excs = helpers.generateRndPureState(dim=2)
        calcva = fns.expectation(op, state)
        expect = sum([((not bool(k))-k)*v for (k, v) in excs.items()])
        assert round(calcva, 12) == round(expect, 12)
        denMat = la.outerProd(state)
        assert round(fns.expectation(op, denMat), 12) == round(expect, 12)

@pytest.mark.parametrize("op, ex", [
    ['sz', [1, -1, 0, 0, 0, 0]], ['sy', [0, 0, 0, 0, 1, -1]], ['sx', [0, 0, 1, -1, 0, 0]]
])
def test_expectationWithSigmaOps(op, ex, specialQubitStates, singleQubitOperators):
    # test expectation of Pauli operators against eigenvectors
    op = singleQubitOperators[op]
    zp = fns.expectation(op, specialQubitStates['1'])
    zm = fns.expectation(op, specialQubitStates['0'])
    xp = fns.expectation(op, specialQubitStates['x+'])
    xm = fns.expectation(op, specialQubitStates['x-'])
    yp = fns.expectation(op, specialQubitStates['y+'])
    ym = fns.expectation(op, specialQubitStates['y-'])
    assert [round(a, 12) for a in [zp, zm, xp, xm, yp, ym]] == ex
    zpdm = fns.expectation(op, la.outerProd(specialQubitStates['1']))
    zmdm = fns.expectation(op, la.outerProd(specialQubitStates['0']))
    xpdm = fns.expectation(op, la.outerProd(specialQubitStates['x+']))
    xmdm = fns.expectation(op, la.outerProd(specialQubitStates['x-']))
    ypdm = fns.expectation(op, la.outerProd(specialQubitStates['y+']))
    ymdm = fns.expectation(op, la.outerProd(specialQubitStates['y-']))
    assert [round(a, 12) for a in [zpdm, zmdm, xpdm, xmdm, ypdm, ymdm]] == ex

def test_fidelityPure(helpers):
    # using randomly generated states, and also by converting them into density matrix
    # test fidelity (which uses linerAlgebra.py) against hard coded calculation of fidelity from populations
    for _ in range(3):
        state1, dim1, excs1 = helpers.generateRndPureState()
        state2, _, excs2 = helpers.generateRndPureState(dim=dim1)
        fid = fns.fidelityPure(state1, state2)
        fin = abs(sum([np.sqrt(excs2[k2]*excs1[k1]) for k1 in excs1 for k2 in excs2 if k1 == k2]))**2
        assert round(fid, 12) == round(fin, 12)
        state1 = la.outerProd(state1)
        fid = fns.fidelityPure(state1, state2)
        assert round(fid, 12) == round(fin, 12)
        state2 = la.outerProd(state2)
        fid = fns.fidelityPure(state1, state2)
        assert round(fid, 12) == round(fin, 12)

stateNames = ['0', '1', 'x+', 'x-', 'y+', 'y-']
bellStateN = ['BellPhi+', 'BellPhi-', 'BellPsi+', 'BellPsi-']
productNames = ['product1', 'product2', 'product3', 'product4']
@pytest.mark.parametrize("state1, state2, fid", [
    *[(stateNames[0], name, f) for name, f in zip(stateNames, [1, 0, 0.5, 0.5, 0.5, 0.5])],
    *[(stateNames[1], name, f) for name, f in zip(stateNames, [0, 1, 0.5, 0.5, 0.5, 0.5])],
    *[(stateNames[2], name, f) for name, f in zip(stateNames, [0.5, 0.5, 1, 0, 0.5, 0.5])],
    *[(stateNames[3], name, f) for name, f in zip(stateNames, [0.5, 0.5, 0, 1, 0.5, 0.5])],
    *[(stateNames[4], name, f) for name, f in zip(stateNames, [0.5, 0.5, 0.5, 0.5, 1, 0])],
    *[(stateNames[5], name, f) for name, f in zip(stateNames, [0.5, 0.5, 0.5, 0.5, 0, 1])],
    *[(bellStateN[0], name, f) for name, f in zip(bellStateN, [1, 0, 0, 0])],
    *[(bellStateN[1], name, f) for name, f in zip(bellStateN, [0, 1, 0, 0])],
    *[(bellStateN[2], name, f) for name, f in zip(bellStateN, [0, 0, 1, 0])],
    *[(bellStateN[3], name, f) for name, f in zip(bellStateN, [0, 0, 0, 1])]
])
def test_fidelityPureWithSpecialQubitStates(state1, state2, fid, specialQubitStates):
    # test fidelity with some known ket states (and their density matrices) and expected fidelities between them
    state1 = specialQubitStates[state1]
    state2 = specialQubitStates[state2]
    fidCalc = fns.fidelityPure(state1, state2)
    assert round(fidCalc, 12) == fid
    state1 = la.outerProd(state1)
    fidCalc = fns.fidelityPure(state1, state2)
    assert round(fidCalc, 12) == fid
    state2 = la.outerProd(state2)
    fidCalc = fns.fidelityPure(state1, state2)
    assert round(fidCalc, 12) == fid

@pytest.mark.parametrize("mat1, mat2, fid", [
    *[(stateNames[0]+'dm', name+'dm', f) for name, f in zip(stateNames, [1, 0, 0.5, 0.5, 0.5, 0.5])],
    *[(stateNames[1]+'dm', name+'dm', f) for name, f in zip(stateNames, [0, 1, 0.5, 0.5, 0.5, 0.5])],
    *[(stateNames[2]+'dm', name+'dm', f) for name, f in zip(stateNames, [0.5, 0.5, 1, 0, 0.5, 0.5])],
    *[(stateNames[3]+'dm', name+'dm', f) for name, f in zip(stateNames, [0.5, 0.5, 0, 1, 0.5, 0.5])],
    *[(stateNames[4]+'dm', name+'dm', f) for name, f in zip(stateNames, [0.5, 0.5, 0.5, 0.5, 1, 0])],
    *[(stateNames[5]+'dm', name+'dm', f) for name, f in zip(stateNames, [0.5, 0.5, 0.5, 0.5, 0, 1])],
    *[(bellStateN[0]+'dm', name+'dm', f) for name, f in zip(bellStateN, [1, 0, 0, 0])],
    *[(bellStateN[1]+'dm', name+'dm', f) for name, f in zip(bellStateN, [0, 1, 0, 0])],
    *[(bellStateN[2]+'dm', name+'dm', f) for name, f in zip(bellStateN, [0, 0, 1, 0])],
    *[(bellStateN[3]+'dm', name+'dm', f) for name, f in zip(bellStateN, [0, 0, 0, 1])]
])
def test_fidelityWithPureDensityMatrices(mat1, mat2, fid, specialQubitStates):
    # test fidelity with some known density matrices
    fidCalc = fns.fidelityPure(specialQubitStates[mat1], specialQubitStates[mat2])
    assert round(fidCalc, 12) == fid

def test_entropyPureState(specialQubitStates):
    # should give zero for a pure state (uses known states), tests both ket and density matrix inputs
    for v in specialQubitStates.values():
        assert round(fns.entropy(v), 12) == 0
        assert round(fns.entropy(la.outerProd(v)), 12) == 0

@pytest.mark.parametrize('name', bellStateN)
def test_entropyReducedBell(name, specialQubitStates):
    # test entropy of reduced Bell states, tests both ket and density matrix inputs
    qs1 = la.partialTrace(0, [2, 2], specialQubitStates[name])
    qs2 = la.partialTrace(1, [2, 2], specialQubitStates[name])
    e1 = fns.entropy(qs1)
    e2 = fns.entropy(qs2)
    expe = round(np.log(2), 12)
    assert e1 == e2
    assert round(e1, 12) == expe
    assert round(fns.entropy(la.outerProd(qs1)), 12) == expe
    assert round(fns.entropy(la.outerProd(qs2)), 12) == expe

@pytest.mark.parametrize('name, val', [*[(b, 1) for b in bellStateN], *[(p, 0) for p in productNames]])
def test_concurrenceBellAndProduct(name, val, specialQubitStates):
    # test concurrence of Bell states, tests both ket and density matrix inputs
    state = specialQubitStates[name]
    cKet = fns.concurrence(state)
    cDm = fns.concurrence(la.outerProd(state))
    assert round(cKet, 12) == val
    assert round(cDm, 12) == val

sq2 = 1/np.sqrt(2)
@pytest.mark.parametrize("mat1, mat2, dis", [
    *[(stateNames[0]+'dm', name+'dm', f) for name, f in zip(stateNames, [0, 1, sq2, sq2, sq2, sq2])],
    *[(stateNames[1]+'dm', name+'dm', f) for name, f in zip(stateNames, [1, 0, sq2, sq2, sq2, sq2])],
    *[(stateNames[2]+'dm', name+'dm', f) for name, f in zip(stateNames, [sq2, sq2, 0, 1, sq2, sq2])],
    *[(stateNames[3]+'dm', name+'dm', f) for name, f in zip(stateNames, [sq2, sq2, 1, 0, sq2, sq2])],
    *[(stateNames[4]+'dm', name+'dm', f) for name, f in zip(stateNames, [sq2, sq2, sq2, sq2, 0, 1])],
    *[(stateNames[5]+'dm', name+'dm', f) for name, f in zip(stateNames, [sq2, sq2, sq2, sq2, 1, 0])],
    *[(bellStateN[0]+'dm', name+'dm', f) for name, f in zip(bellStateN, [0, 1, 1, 1])],
    *[(bellStateN[1]+'dm', name+'dm', f) for name, f in zip(bellStateN, [1, 0, 1, 1])],
    *[(bellStateN[2]+'dm', name+'dm', f) for name, f in zip(bellStateN, [1, 1, 0, 1])],
    *[(bellStateN[3]+'dm', name+'dm', f) for name, f in zip(bellStateN, [1, 1, 1, 0])]
])
def test_traceDistanceWithPureDensityMatrices(mat1, mat2, dis, specialQubitStates):
    # uses density matrices of known states and compare the output with known values
    disCalc = fns.traceDistance(specialQubitStates[mat1], specialQubitStates[mat2])
    assert round(disCalc, 12) == round(dis, 12)
