import QuantumToolbox.evolution as evo
import numpy as np

sigma_minus = np.array([[0, 0],
    [1, 0]])
test1 = np.array([[0, 0, 0, 0],
    [1, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 1, 0]])

def test_willPass():
    assert (np.allclose(evo._preSO(sigma_minus), test1)) is True # pylint: disable=comparison-with-itself

sigma_plus = np.array([[0, 1],
    [0, 0]])

test2 = np.array([[0, 1, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 1],
    [0, 0, 0, 0]])

def test_willPass():
    assert (np.allclose(evo._preSO(sigma_plus), test2)) is True # pylint: disable=comparison-with-itself

sigma_z = np.array([[1, 0],
    [0, -1]])

test3 = np.array([[1, 0, 0, 0],
    [0, -1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, -1]])

def test_willPass():
    assert (np.allclose(evo._preSO(sigma_z), test3)) is True # pylint: disable=comparison-with-itself