import numpy as np
import random as rnd
import pytest
import quanguru.classes.QSystem as QSys
import quanguru.QuantumToolbox.states as qSts
from quanguru.classes.QSys import QuantumSystem, qSystem

def test_initialStateOfNullSystem():
    # setting an initial state before the type of quantum system (single or composite) is determined
    # raises a ValueError
    qsys =  QSys.QuSystem()
    with pytest.raises(ValueError):
        qsys.initialState = 2
    with pytest.raises(ValueError):
        qsys.initialState = [1, 3]
    with pytest.raises(ValueError):
        qsys.initialState = {0:0.1, 1:0.2, 2:0.3, 3:0.4}
    with pytest.raises(ValueError):
        qsys._inpCoef = True
        qsys.initialState = {0:0.2*(1+1j), 2:0.2}
    with pytest.raises(ValueError):
        qsys.initialState = qSts.densityMatrix([qSts.basis(2, 1), qSts.basis(2, 0)], [0.5, 0.5])

@pytest.mark.parametrize("cls", [
                         QuantumSystem,
                         QSys.QuSystem
                         ])
def test_createInitialStateForSingleSystem(cls):
    qsys = cls(dimension=4)

    initState = qsys._createAstate(2)
    assert initState[0] == 0
    assert initState[1] == 0
    assert initState[2] == 1
    assert initState[3] == 0

    initState = qsys._createAstate([1, 3])
    assert initState[0] == 0
    assert initState[1] == 1/np.sqrt(2)
    assert initState[2] == 0
    assert initState[3] == 1/np.sqrt(2)

    initState = qsys._createAstate([0, 1, 3])
    assert initState[0] == 1/np.sqrt(3)
    assert initState[1] == 1/np.sqrt(3)
    assert initState[2] == 0
    assert initState[3] == 1/np.sqrt(3)

    initState = qsys._createAstate({0:0.1, 1:0.2, 2:0.3, 3:0.4})
    assert np.round(initState[0], 14) == np.round(np.sqrt(0.1), 14)
    assert np.round(initState[1], 14) == np.round(np.sqrt(0.2), 14)
    assert np.round(initState[2], 14) == np.round(np.sqrt(0.3), 14)
    assert np.round(initState[3], 14) == np.round(np.sqrt(0.4), 14)

    qsys._inpCoef = True
    initState = qsys._createAstate({0:0.2*(1+1j), 2:0.2})
    assert np.round(initState[0].real, 8) == 0.57735027
    assert np.round(initState[0].imag, 8) == 0.57735027
    assert initState[1] == 0
    assert np.round(initState[2], 8) == 0.57735027
    assert initState[3] == 0

    with pytest.raises(ValueError):
        initState = qsys._createAstate(qSts.densityMatrix([qSts.basis(2, 1), qSts.basis(2, 0)], [0.5, 0.5]))

    initState = qsys._createAstate(qSts.densityMatrix([qSts.basis(4, 1), qSts.basis(4, 0)], [0.25, 0.75]))
    print(initState.A)
    for ind1 in range(4):
        for ind2 in range(4):
            if ((ind1 == 0) and (ind2 == 0)):
                initState[ind1][:, ind2] = 0.25
            elif ((ind1 == 1) and (ind2 == 1)):
                initState[ind1][:, ind2] = 0.75
            else:
                initState[ind1][:, ind2] = 0

@pytest.mark.parametrize("cls, mth", [
                         [QuantumSystem, 'initialState'],
                         [QuantumSystem, '_createAstate'],
                         [QSys.QuSystem, 'initialState'],
                         [QSys.QuSystem, '_createAstate']
                         ])
def test_initialStateSetterForSingleSystem(cls, mth):
    qsys = cls(dimension=4)

    qsys.initialState = 2
    initState = getattr(qsys, mth)() if callable(getattr(qsys, mth)) else getattr(qsys, mth)
    assert initState[0] == 0
    assert initState[1] == 0
    assert initState[2] == 1
    assert initState[3] == 0

    qsys.initialState = [1, 3]
    initState = getattr(qsys, mth)() if callable(getattr(qsys, mth)) else getattr(qsys, mth)
    assert initState[0] == 0
    assert initState[1] == 1/np.sqrt(2)
    assert initState[2] == 0
    assert initState[3] == 1/np.sqrt(2)

    qsys.initialState = [0, 1, 3]
    initState = getattr(qsys, mth)() if callable(getattr(qsys, mth)) else getattr(qsys, mth)
    assert initState[0] == 1/np.sqrt(3)
    assert initState[1] == 1/np.sqrt(3)
    assert initState[2] == 0
    assert initState[3] == 1/np.sqrt(3)

    qsys.initialState = {0:0.1, 1:0.2, 2:0.3, 3:0.4}
    initState = getattr(qsys, mth)() if callable(getattr(qsys, mth)) else getattr(qsys, mth)
    assert np.round(initState[0], 14) == np.round(np.sqrt(0.1), 14)
    assert np.round(initState[1], 14) == np.round(np.sqrt(0.2), 14)
    assert np.round(initState[2], 14) == np.round(np.sqrt(0.3), 14)
    assert np.round(initState[3], 14) == np.round(np.sqrt(0.4), 14)

    qsys._inpCoef = True
    qsys.initialState = {0:0.2*(1+1j), 2:0.2}
    initState = getattr(qsys, mth)() if callable(getattr(qsys, mth)) else getattr(qsys, mth)
    assert np.round(initState[0].real, 8) == 0.57735027
    assert np.round(initState[0].imag, 8) == 0.57735027
    assert initState[1] == 0
    assert np.round(initState[2], 8) == 0.57735027
    assert initState[3] == 0

    with pytest.raises(ValueError):
        qsys.initialState = qSts.densityMatrix([qSts.basis(2, 1), qSts.basis(2, 0)], [0.5, 0.5])

    qsys.initialState = qSts.densityMatrix([qSts.basis(4, 1), qSts.basis(4, 0)], [0.25, 0.75])
    initState = qsys.initialState
    for ind1 in range(4):
        for ind2 in range(4):
            if ((ind1 == 0) and (ind2 == 0)):
                initState[ind1][:, ind2] = 0.25
            elif ((ind1 == 1) and (ind2 == 1)):
                initState[ind1][:, ind2] = 0.75
            else:
                initState[ind1][:, ind2] = 0

def test_compositeStateInitialStateSetterInputsAndErrors():
    # create a quantum system
    qsystem = QSys.QuSystem()
    # create 3 other systems with dimension info
    # create 3 other systems with dimension info
    someRandInt1 = rnd.randint(2, 20)
    asystem1 = QSys.QuSystem(dimension=someRandInt1)
    someRandInt2 = rnd.randint(2, 20)
    asystem2 = QSys.QuSystem(dimension = someRandInt2)
    asystem3 = QSys.QuSystem(dimension=3)
    # compose the qsystem
    qsystem.addSubSys([asystem1, asystem2, asystem3])

    # try setting initial state with a list
    qsystem.initialState = [0, 1, 2]

    # try setting initial state with a list
    qsystem.initialState = (0, 1, 2)

    # try setting initial state with a dictionary
    with pytest.raises(TypeError):
        qsystem.initialState = {0:0.1, 1:0.5, 2:0.4}

    # try setting initial state with a shorter list
    with pytest.raises(ValueError):
        qsystem.initialState = [0, 1]

    # try setting initial state with a longer list
    with pytest.raises(ValueError):
        qsystem.initialState = [0, 1, 2, 0]

@pytest.mark.parametrize("cls", [
                         QuantumSystem,
                         QSys.QuSystem
                         ])
def test_createInitialStateForCompositeSystemThroughCompositeSystem1Layer(cls):
    # create a quantum system
    qsystem = cls()

    # create 3 other systems with dimension info
    someRandInt1 = rnd.randint(2, 20)
    asystem1 = cls(dimension=someRandInt1)
    someRandInt2 = rnd.randint(2, 20)
    asystem2 = cls(dimension = someRandInt2)
    asystem3 = cls(dimension=3)

    # add the subSystems for the composite system
    qsystem.addSubSys([asystem1, asystem2, asystem3])

    # call the create initial state function with a proper input
    qsystem._createAstate([1, 1, 1, 1])
