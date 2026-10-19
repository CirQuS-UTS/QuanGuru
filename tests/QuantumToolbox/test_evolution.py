import numpy as np
import pytest
import quanguru.QuantumToolbox.evolution as evo#pylint: disable=import-error
from quanguru import sigmam, sigmaz
from numpy import array

sigmaOpers = ["sigmaMinusReference", "sigmaPlusReference", "sigmaZReference"]

preExpects = [np.array([[0, 0, 0, 0], [1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 1, 0]]),
              np.array([[0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]),
              np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, preExpects)])
def test_preSO(op, expect, referenceValues):
    # test the preSO for sigma -, +, and Z operators by comparing expected results
    assert np.allclose(evo._preSO(referenceValues[op]), expect) #pylint:disable=protected-access

posExpects = [np.array([[0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]),
              np.array([[0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0]]),
              np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, posExpects)])
def test_postSO(op, expect, referenceValues):
    # test the posSO for sigma -, +, and Z operators by comparing expected results
    assert np.allclose(evo._postSO(referenceValues[op]), expect) #pylint:disable=protected-access

preposExpects = [np.array([[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [1, 0, 0, 0]]),
                 np.array([[0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]),
                 np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, preposExpects)])
def test_prepostSO(op, expect, referenceValues):
    # test the preposSO for sigma -, +, and Z operators by comparing expected results
    assert np.allclose(evo._prepostSO(referenceValues[op], referenceValues[op].T), expect) #pylint:disable=protected-access

dissipatorExpects = [np.array([[-1, 0, 0, 0], [0, -0.5, 0, 0], [0, 0, -0.5, 0], [1, 0, 0, 0]]),
                     np.array([[0, 0, 0, 1], [0, -0.5, 0, 0], [0, 0, -0.5, 0], [0, 0, 0, -1]]),
                     np.array([[0, 0, 0, 0], [0, -2, 0, 0], [0, 0, -2, 0], [0, 0, 0, 0]])]
@pytest.mark.parametrize("op, expect", [[o, e] for (o, e) in zip(sigmaOpers, dissipatorExpects)])
def test_dissipator(op, expect, referenceValues):
    # test the dissipator for sigma -, +, and Z operators by comparing expected results
    assert np.allclose(evo.dissipator(referenceValues[op]), expect)

def test_NegativeTimeLiouvillianExp():
    gen = evo.LiouvillianExp(Hamiltonian=sigmaz().toarray(), timeStep=-1, collapseOperators=[sigmam().toarray()], decayRates=[1/2])
    exp = array([
        [ 0.60653066+0.j        ,  0.        +0.j        ,          0.        +0.j        ,  0.        +0.j        ],
        [ 0.        +0.j        , -0.32409548-0.70816155j,          0.        +0.j        ,  0.        +0.j        ],
        [ 0.        +0.j        ,  0.        +0.j        ,         -0.32409548+0.70816155j,  0.        +0.j        ],
        [ 0.39346934+0.j        ,  0.        +0.j        ,          0.        +0.j        ,  1.        +0.j        ]
    ])
    assert np.allclose(gen, exp)