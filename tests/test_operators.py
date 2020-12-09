import numpy as np
import random as rn
import pytest
from qTools.QuantumToolbox import states
from qTools.QuantumToolbox import operators as ops #pylint: disable=import-error
from .constants import (sigmaMinusReference, sigmaPlusReference, sigmaXReference, sigmaYReference, sigmaZReference)


def checkGivenRuleForAnArray(cOp, rule, *args):
    dim = cOp.shape[0]
    for ind1 in range(dim):
        for ind2 in range(dim):
            expected = rule(ind1, ind2, *args)
            found = cOp[ind1][ind2]
            assert round(found.real, 13) == round(expected.real, 13)
            assert round(found.imag, 13) == round(expected.imag, 13)

@pytest.mark.parametrize("op, rule", [[ops.number, lambda ind1, ind2: ind1*int(not bool(ind1-ind2))],
                                      [ops.create, lambda ind1, ind2: np.sqrt(ind1)*int(not bool(ind1-ind2-1))],
                                      [ops.destroy, lambda ind1, ind2: np.sqrt(ind2)*int(not bool(ind2-ind1-1))],
                                      [ops.identity, lambda ind1, ind2: int(not bool(ind1-ind2))]])
def test_bosonOperators(op, rule):
    # check the value of each element against a given rule, i.e. the definition the matrices
    for _ in range(5):
        dim = rn.randint(2, 20)
        numOp = op(dim).A
        checkGivenRuleForAnArray(numOp, rule)

@pytest.mark.parametrize("op, fnc", [[sigmaMinusReference, ops.sigmam], [sigmaPlusReference, ops.sigmap],
                                     [sigmaXReference, ops.sigmax], [sigmaYReference, ops.sigmay],
                                     [sigmaZReference, ops.sigmaz]])
def test_PauliSpinOperators(op, fnc): #pylint:disable=invalid-name
    # check against hard-coded reference arrays
    assert np.allclose(fnc().A, op)

@pytest.mark.parametrize("op, bo", [[ops.destroy, 0], [ops.create, 1], [ops.Jp, 0], [ops.Jm, 1]])
def test_ladderOperatorsOnEdges(op, bo):
    # check if they give zero kets, when applied to corresponding edges
    for _ in range(5):
        dim = rn.randint(1, 20)
        rOp = op(dim)
        state = states.basis(rOp.shape[0], (rOp.shape[0] - 1)*bo)
        assert np.allclose((rOp@state).A, states.zeros(rOp.shape[0], sparse=False))

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
    [ops.Jp, lambda ind1, ind2, jVal: np.sqrt(((2*jVal)-ind1)*(ind1+1))*int(not bool(ind2-ind1-1))],
    [ops.Jm, lambda ind1, ind2, jVal: np.sqrt(((2*jVal)-ind2)*(ind2+1))*int(not bool(ind1-ind2-1))],
    [ops.Jz, lambda ind1, ind2, jVal: (jVal - ind1)*int(not bool(ind1-ind2))],
    [ops.Js, lambda ind1, ind2, jVal: (jVal*(jVal+1))*int(not bool(ind1-ind2))]
])
def test_higherSpinOperators(op, rule):
    for _ in range(5):
        jVal = 0.5*rn.randint(1, 20)
        jOp = op(jVal).A
        checkGivenRuleForAnArray(jOp, rule, jVal)
