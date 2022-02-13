import numpy as np
import quanguru.classes.QSystem as QSys
import quanguru.QuantumToolbox.states as qSts

def test_createInitialStateForSingleSystem():
    cls = QSys.QuSystem
    qsys = cls(dimension=4)

    initState = qsys._createInitialState(2)
    assert initState[0] == 0
    assert initState[1] == 0
    assert initState[2] == 1
    assert initState[3] == 0

    initState = qsys._createInitialState([1, 3])
    assert initState[0] == 0
    assert initState[1] == 1/np.sqrt(2)
    assert initState[2] == 0
    assert initState[3] == 1/np.sqrt(2)

    initState = qsys._createInitialState([0, 1, 3])
    assert initState[0] == 1/np.sqrt(3)
    assert initState[1] == 1/np.sqrt(3)
    assert initState[2] == 0
    assert initState[3] == 1/np.sqrt(3)

    initState = qsys._createInitialState({0:0.1, 1:0.2, 2:0.3, 3:0.4})
    assert np.round(initState[0], 14) == np.round(np.sqrt(0.1), 14)
    assert np.round(initState[1], 14) == np.round(np.sqrt(0.2), 14)
    assert np.round(initState[2], 14) == np.round(np.sqrt(0.3), 14)
    assert np.round(initState[3], 14) == np.round(np.sqrt(0.4), 14)

    qsys._inpCoef = True
    initState = qsys._createInitialState({0:0.2*(1+1j), 2:0.2})
    assert np.round(initState[0].real, 8) == 0.57735027
    assert np.round(initState[0].imag, 8) == 0.57735027
    assert initState[1] == 0
    assert np.round(initState[2], 8) == 0.57735027
    assert initState[3] == 0
