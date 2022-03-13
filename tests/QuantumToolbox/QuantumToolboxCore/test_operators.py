import random as rn
import numpy as np
import pytest
from quanguru.QuantumToolbox import linearAlgebra as la#pylint: disable=import-error
from quanguru.QuantumToolbox import states#pylint: disable=import-error
from quanguru.QuantumToolbox import operators as ops #pylint: disable=import-error


def checkGivenRuleForAnArray(cOp, rule, *args):
    # assert correctness of elements in a matrix by comparing against a given rule that calculated the expected value
    # used in many tests below to verify the operator entries are as expected from a given rule
    dim = cOp.shape[0]
    for ind1 in range(dim):
        for ind2 in range(dim):
            expected = rule(ind1, ind2, *args)
            found = cOp[ind1][ind2]
            assert np.round(found.real, 13) == np.round(expected.real, 13)
            assert np.round(found.imag, 13) == np.round(expected.imag, 13)

@pytest.mark.parametrize("op, rule", [[ops.number, lambda ind1, ind2: ind1*(not bool(ind1-ind2))],
                                      [ops.create, lambda ind1, ind2: np.sqrt(ind1)*(not bool(ind1-ind2-1))],
                                      [ops.destroy, lambda ind1, ind2: np.sqrt(ind2)*(not bool(ind2-ind1-1))],
                                      [ops.identity, lambda ind1, ind2: (not bool(ind1-ind2))]])
def test_bosonOperators(op, rule):
    # check the value of each element against a given rule, i.e. the definition the matrices
    for _ in range(5):
        dim = rn.randint(2, 20)
        numOp = op(dim).A
        checkGivenRuleForAnArray(numOp, rule)

@pytest.mark.parametrize("op, fnc", [['sigmaMinusReference', ops.sigmam], ['sigmaPlusReference', ops.sigmap],
                                     ['sigmaXReference', ops.sigmax], ['sigmaYReference', ops.sigmay],
                                     ['sigmaZReference', ops.sigmaz]])
def test_PauliSpinOperators(op, fnc, referenceValues): #pylint:disable=invalid-name
    # check against hard-coded reference arrays
    assert np.allclose(fnc().A, referenceValues[op])

@pytest.mark.parametrize("op, bo", [[ops.destroy, 0], [ops.create, 1], [ops.Jp, 0], [ops.Jm, 1]])
def test_ladderOperatorsOnEdges(op, bo):
    # check if they give zero kets, when applied to corresponding edges
    for _ in range(5):
        dim = rn.randint(1, 20)
        rOp = op(dim)
        state = states.basis(rOp.shape[0], (rOp.shape[0] - 1)*bo)
        assert np.allclose((rOp@state).A, states.zerosKet(rOp.shape[0], sparse=False))

@pytest.mark.parametrize("op, bo", [[ops.destroy, -1], [ops.create, 1], [ops.Jp, -1], [ops.Jm, 1]])
def test_ladderOperatorsOnRndPlaces(op, bo):
    # check if they raise/lower correctly
    for _ in range(5):
        dim = rn.randint(4, 20)
        rOp = op(dim)
        dim = rOp.shape[0]
        sPos = rn.randint(1, dim-2)
        state = states.basis(dim, sPos)
        assert np.allclose(states.normalise(rOp@state).A, states.basis(dim, sPos+bo).A)

@pytest.mark.parametrize("op, rule", [
    [ops.Jp, lambda ind1, ind2, jVal: np.sqrt(((2*jVal)-ind1)*(ind1+1))*(not bool(ind2-ind1-1))],
    [ops.Jm, lambda ind1, ind2, jVal: np.sqrt(((2*jVal)-ind2)*(ind2+1))*(not bool(ind1-ind2-1))],
    [ops.Jz, lambda ind1, ind2, jVal: (jVal - ind1)*(not bool(ind1-ind2))],
    [ops.Js, lambda ind1, ind2, jVal: (jVal*(jVal+1))*(not bool(ind1-ind2))]])
def test_higherSpinOperators(op, rule):
    # check the value of each element against a given rule, i.e. the definition the matrices
    for _ in range(5):
        jVal = 0.5*rn.randint(1, 20)
        jOp = op(jVal).A
        checkGivenRuleForAnArray(jOp, rule, jVal)

def test_displacement():
    # displacing vacuum should give a coherent state and test compares the resultant state properties with coherent
    # state properties
    vacuumState = states.basis(20, 0)
    alphaReal = 1.5*rn.random()
    alphaImag = 1.5*rn.random()
    alpha = alphaReal+alphaImag*1j
    displacementOp = ops.displacement(alpha, 20)
    displacedVacuum = displacementOp @ vacuumState

    # test the photon number distribution
    for n in range(10):
        calc = abs(la.innerProd(displacedVacuum, states.basis(20, n)))**2
        expc = abs(((np.e**(-(abs(alpha)**2)/2))*((alpha**n)/(np.sqrt(np.math.factorial(n))))))**2
        assert np.round(calc, 5) == np.round(expc, 5)

    # test average photon number
    assert np.round(la.trace(ops.number(20) @ states.densityMatrix(displacedVacuum)), 8).real == np.round(abs(alpha)**2, 8)

    # coherent state is the eigenstate of destroy with eigenvalue alpha
    assert np.allclose((ops.destroy(20)@displacedVacuum).A, (alpha*displacedVacuum).A, atol=1e-04, rtol=1e-04)
