import numpy as np
import pytest
import qTools.QuantumToolbox.evolution as evo#pylint: disable=import-error

sigmaOpers = ["sigmaMinusReference", "sigmaPlusReference", "sigmaZReference"]

preExpects = [np.array([[0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0]]),
              np.array([[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]),
              np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, preExpects)])
def test_preSO(op, expect, constants):
    assert np.allclose(evo._preSO(constants[op]), expect) #pylint:disable=protected-access

posExpects = [np.array([[0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]),
              np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0]]),
              np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, posExpects)])
def test_posSO(op, expect, constants):
    assert np.allclose(evo._posSO(constants[op]), expect) #pylint:disable=protected-access

preposExpects = [np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0]]),
                 np.array([[0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
                 np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, preposExpects)])
def test_preposSO(op, expect, constants):
    assert np.allclose(evo._preposSO(constants[op]), expect) #pylint:disable=protected-access

dissipatorExpects = [np.array([[-1, 0, 0, 0], [0, -0.5, 0, 0], [0, 0, -0.5, 0], [1, 0, 0, 0]]),
                     np.array([[0, 0, 0, 1], [0, -0.5, 0, 0], [0, 0, -0.5, 0], [0, 0, 0, -1]]),
                     np.array([[0, 0, 0, 0], [0, -2, 0, 0], [0, 0, -2, 0], [0, 0, 0, 0]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, dissipatorExpects)])
def test_dissipator(op, expect, constants):
    assert np.allclose(evo.dissipator(constants[op]), expect) #pylint:disable=protected-access
