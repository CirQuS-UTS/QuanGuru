import pytest
from qTools.QuantumToolbox import operators as ops #pylint: disable=import-error
from qTools.QuantumToolbox import functions as fns #pylint: disable=import-error
#testCase = collections.namedtuple('testCase', ['operator', 'state', 'expected'])

@pytest.mark.parametrize("op, rule", [[ops.number, lambda excs, dim: sum([k*v for (k, v) in excs.items()])]])
def test_expectation(op, rule, helpers):
    for _ in range(5):
        state, dim, excs = helpers.generateRndPureState()
        calcva = fns.expectation(op(dim), state)
        expect = rule(excs, dim)
        assert round(calcva, 12) == round(expect, 12)
