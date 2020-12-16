import numpy as np
import pytest
from qTools.QuantumToolbox import linearAlgebra as la #pylint: disable=import-error
from qTools.QuantumToolbox import operators as ops #pylint: disable=import-error
from qTools.QuantumToolbox import functions as fns #pylint: disable=import-error
#testCase = collections.namedtuple('testCase', ['operator', 'state', 'expected'])

def test_expectationWithNumber(helpers):
    for _ in range(3):
        state, dim, excs = helpers.generateRndPureState()
        calcva = fns.expectation(ops.number(dim), state)
        expect = sum([k*v for (k, v) in excs.items()])
        assert round(calcva, 12) == round(expect, 12)

def test_expectationWithJz(helpers):
    for _ in range(3):
        state, dim, excs = helpers.generateRndPureState()
        calcva = fns.expectation(ops.Jz((dim-1)/2), state)
        expect = sum([((dim-1)/2-k)*v for (k, v) in excs.items()])
        assert round(calcva, 12) == round(expect, 12)

def test_expectationWithSigmaz(helpers, singleQubitOperators):
    op = singleQubitOperators['sz']
    for _ in range(3):
        state, _, excs = helpers.generateRndPureState(dim=2)
        calcva = fns.expectation(op, state)
        expect = sum([((not bool(k))-k)*v for (k, v) in excs.items()])
        assert round(calcva, 12) == round(expect, 12)

@pytest.mark.parametrize("op, ex", [
    ['sz', [1, -1, 0, 0, 0, 0]], ['sy', [0, 0, 0, 0, 1, -1]], ['sx', [0, 0, 1, -1, 0, 0]]
])
def test_expectationWithSigmaOps(op, ex, specialQubitStates, singleQubitOperators):
    op = singleQubitOperators[op]
    zp = fns.expectation(op, specialQubitStates['1'])
    zm = fns.expectation(op, specialQubitStates['0'])
    xp = fns.expectation(op, specialQubitStates['x+'])
    xm = fns.expectation(op, specialQubitStates['x-'])
    yp = fns.expectation(op, specialQubitStates['y+'])
    ym = fns.expectation(op, specialQubitStates['y-'])
    assert [round(a, 12) for a in [zp, zm, xp, xm, yp, ym]] == ex

def test_fidelityPure(helpers):
    for _ in range(3):
        state1, dim1, excs1 = helpers.generateRndPureState()
        state2, _, excs2 = helpers.generateRndPureState(dim=dim1)
        fid = fns.fidelityPure(state1, state2)
        fin = abs(sum([np.sqrt(excs2[k2]*excs1[k1]) for k1 in excs1 for k2 in excs2 if k1 == k2]))**2
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
    fidCalc = fns.fidelityPure(specialQubitStates[state1], specialQubitStates[state2])
    assert round(fidCalc, 12) == fid

def test_entropyPureState(specialQubitStates):
    # should give zero
    for v in specialQubitStates.values():
        assert round(fns.entropy(v), 12) == 0

@pytest.mark.parametrize('name', bellStateN)
def test_entropyReducedBell(name, specialQubitStates):
    qs1 = la.partialTrace(0, [2, 2], specialQubitStates[name])
    qs2 = la.partialTrace(1, [2, 2], specialQubitStates[name])
    e1 = fns.entropy(qs1)
    e2 = fns.entropy(qs2)
    assert e1 == e2
    assert round(e1, 12) == round(np.log(2), 12)

@pytest.mark.parametrize('name, val', [*[(b, 1) for b in bellStateN], *[(p, 0) for p in productNames]])
def test_concurrenceBellAndProduct(name, val, specialQubitStates):
    c = fns.concurrence(specialQubitStates[name])
    assert round(c, 12) == val

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
    fidCalc = fns.fidelityPure(specialQubitStates[mat1], specialQubitStates[mat2])
    assert round(fidCalc, 12) == fid

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
    disCalc = fns.traceDistance(specialQubitStates[mat1], specialQubitStates[mat2])
    assert round(disCalc, 12) == round(dis, 12)
