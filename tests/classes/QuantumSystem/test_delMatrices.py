import random as rnd
import pytest
import quanguru.classes.QSystem as QSys
from quanguru.classes.QSys import QuantumSystemOld

def addMatrices(listOfObj, listOfMatrices, listOfInitialStates, _except):
    for ind, qsys in enumerate(listOfObj):
        if qsys not in _except:
            qsys._paramBoundBase__matrix = listOfMatrices[ind]
            qsys.simulation._stateBase__initialState._value = listOfInitialStates[ind]

def assertMatrixVals(listOfObj, expBool, _except):
    for qsys in listOfObj:
        if qsys not in _except:
            assert ((qsys._paramBoundBase__matrix is None) is expBool)
            assert ((qsys.simulation._stateBase__initialState.value is None) is expBool)

def createAndAssert(listOfObj, listOfMatrices, exceptList):
    addMatrices(listOfObj, listOfMatrices, listOfMatrices, exceptList)
    assertMatrixVals(listOfObj, False, exceptList)

@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_delMatrixAfterRemoveSubSysWithDummyMatrix(cls):
    # matrices to be set delete _paramBoundBase__matrix and _stateBase__initialState._value
    # create 4 objects to be used as composite systems
    comp1 = cls()
    comp2 = cls()
    comp3 = cls()
    comp4 = cls()
    # create 9 single quantum system with a random dimension
    sing1 = cls(dimension=rnd.randint(3, 10))
    sing2 = cls(dimension=rnd.randint(3, 10))
    sing3 = cls(dimension=rnd.randint(3, 10))
    sing4 = cls(dimension=rnd.randint(3, 10))
    sing5 = cls(dimension=rnd.randint(3, 10))
    sing6 = cls(dimension=rnd.randint(3, 10))
    sing7 = cls(dimension=rnd.randint(3, 10))
    sing8 = cls(dimension=rnd.randint(3, 10))
    sing9 = cls(dimension=rnd.randint(3, 10))

    listOfObj = [comp1, sing1, sing2, sing3, comp2, sing4, sing5, sing6, comp3, sing7, sing8, sing9, comp4]
    listOfMatrices = [rnd.randint(3, 10) for _ in range(len(listOfObj))]
    exceptList = []

    createAndAssert(listOfObj, listOfMatrices, exceptList)
    # create a composite system with 3 of the single systems 
    comp1.addSubSys(listOfObj[1:4])
    assertMatrixVals(listOfObj[0:4], True, exceptList)
    assertMatrixVals(listOfObj[4:], False, exceptList)

    createAndAssert(listOfObj, listOfMatrices, exceptList)
    # remove one of them
    comp1.removeSubSys(sing2)
    assertMatrixVals(listOfObj[0:4], True, exceptList)
    exceptList.append(sing2)
    assertMatrixVals(listOfObj[4:], False, exceptList)
    
    createAndAssert(listOfObj, listOfMatrices, exceptList)
    # compose two other composite system with 3 sub-systems
    comp2.addSubSys([sing4, sing5, sing6])
    assertMatrixVals(listOfObj[4:8], True, exceptList)
    comp3.addSubSys([sing7, sing8, sing9])
    assertMatrixVals(listOfObj[8:12], True, exceptList)
    # compose a composite system of composite systems
    comp4.addSubSys([comp1, comp2, comp3])
    assertMatrixVals(listOfObj, True, exceptList)
    
    createAndAssert(listOfObj, listOfMatrices, exceptList)
    # remove a sub-system (sing5) of comp2 by calling the removeSubSys on comp2
    comp2.removeSubSys(sing5)
    assertMatrixVals(listOfObj, True, exceptList)
    exceptList.append(sing5)
    
    
    createAndAssert(listOfObj, listOfMatrices, exceptList)
    # remove a sub-system (sing6) of comp2 by calling the removeSubSys on comp3
    comp3.removeSubSys(sing6)
    assertMatrixVals(listOfObj, True, exceptList)
    exceptList.append(sing6)
    
    createAndAssert(listOfObj, listOfMatrices, exceptList)
    # remove a sub-system (sing8) of comp3 by calling the removeSubSys on comp4 (composite of the composites)
    comp4.removeSubSys(sing8)
    assertMatrixVals(listOfObj, True, exceptList)
    exceptList.append(sing8)

    createAndAssert(listOfObj, listOfMatrices, exceptList)
    # remove a composite sub-system comp2 by calling the removeSubSys on comp4
    comp4.removeSubSys(comp2)
    assertMatrixVals(listOfObj, True, exceptList)
    exceptList += [comp2, *list(comp2.subSys.values())]
    
    createAndAssert(listOfObj, listOfMatrices, exceptList)
    comp1.removeSubSys(comp3)
    assertMatrixVals([comp3, *list(comp3.subSys.values())], True, exceptList)
    assertMatrixVals([comp1, *list(comp1.subSys.values())], True, exceptList)
    assertMatrixVals([comp4], True, exceptList)
    assertMatrixVals(listOfObj, True, exceptList)
    exceptList += [comp3, *list(comp3.subSys.values())]

    createAndAssert(listOfObj, listOfMatrices, exceptList)
    comp1.removeSubSys(comp1)
    assertMatrixVals(listOfObj, True, exceptList)
    exceptList.append(comp1)
    