import pytest
import random as rnd
import quanguru.classes.QSystem as QSys

@pytest.mark.parametrize("attrName, attrVal", [
                         ["_QuSystem__compSys", False],
                         ["dimension", 3]
                         ])
def test_cannotAddSubSysToSingleQuantumSystem(attrName, attrVal):
    # create a quantum system
    singleSys = QSys.QuSystem()
    # set a relevant attribute that turns _QuSystem__compSys to False
    setattr(singleSys, attrName, attrVal)
    # create another system
    anotherSys = QSys.QuSystem()
    # trying to add anotherSys as subSys should raise TypeError
    with pytest.raises(TypeError):
        singleSys.addSubSys(anotherSys)
    
    # make sure that the subsys is empty
    assert len(singleSys.subSys) == 0

@pytest.mark.parametrize("attrName, attrVal, defVal", [
                         ["dimension", 3, 1]
                         ])
def test_cannotSetSingleSysAttrToCompSystem(attrName, attrVal, defVal):
    # create a quantum system
    qsystem = QSys.QuSystem()
    # create another to add as a subSys
    asystem = QSys.QuSystem()
    qsystem.addSubSys(asystem)

    # assert that the _QuSystem__compSys is changed
    assert qsystem._QuSystem__compSys is True

    # make sure that setting single system parameters warns
    with pytest.warns(Warning):
        setattr(qsystem, attrName, attrVal)

    # make sure that above call does not change the value
    assert getattr(qsystem, attrName) == defVal
 
def test_dimensionValues():
    # create a quantum system
    qsystem = QSys.QuSystem()
    # create 3 other systems with dimension info
    someRandInt1 = rnd.randint(2, 20)
    asystem1 = QSys.QuSystem(dimension=someRandInt1)
    assert asystem1.dimension == someRandInt1
    someRandInt2 = rnd.randint(2, 20)
    asystem2 = QSys.QuSystem()
    asystem2.dimension = someRandInt2
    assert asystem2.dimension == someRandInt2
    asystem3 = QSys.QuSystem(dimension=3)
    assert asystem3.dimension == 3

    # add the sub-systems
    qsystem.addSubSys([asystem1, asystem2, asystem3])

    # make sure that above call does not modify the dimension info for sub-systems
    assert asystem1.dimension == someRandInt1
    assert asystem2.dimension == someRandInt2
    assert asystem3.dimension == 3

    # make sure that composite dimension is correct
    assert qsystem.dimension == (someRandInt1*someRandInt2*3)
    assert qsystem.dimension == (asystem1.dimension*asystem2.dimension*asystem3.dimension)

    # make sure that above call does not modify the dimension info for sub-systems
    assert asystem1.dimension == someRandInt1
    assert asystem2.dimension == someRandInt2
    assert asystem3.dimension == 3

def test_dimensionABValues():
    # create a quantum system
    qsystem = QSys.QuSystem()

    # create 4 other systems with dimension info
    someRandInt1 = rnd.randint(2, 20)
    asystem1 = QSys.QuSystem(dimension=someRandInt1)
 
    someRandInt2 = rnd.randint(2, 20)
    asystem2 = QSys.QuSystem(dimension = someRandInt2)

    asystem3 = QSys.QuSystem(dimension=3)
    asystem4 = QSys.QuSystem(dimension=3)

    # add the sub-system1 and check dimesions
    qsystem.addSubSys(asystem1)

    assert qsystem.dimension == asystem1.dimension
    assert qsystem._dimsAfter == 1
    assert qsystem._dimsBefore == 1
    assert asystem1._dimsAfter == 1
    assert asystem1._dimsBefore == 1

    # add the sub-system2 and check dimesions
    qsystem.addSubSys(asystem2)

    assert qsystem.dimension == asystem1.dimension*asystem2.dimension
    assert qsystem._dimsAfter == 1
    assert qsystem._dimsBefore == 1
    assert asystem1._dimsAfter == asystem2.dimension
    assert asystem1._dimsBefore == 1
    assert asystem2._dimsBefore == asystem1.dimension
    assert asystem2._dimsAfter == 1


    # add the other two subSystems
    qsystem.addSubSys([asystem3, asystem4])

    assert qsystem.dimension == asystem1.dimension*asystem2.dimension*asystem3.dimension*asystem4.dimension
    assert qsystem._dimsAfter == 1
    assert qsystem._dimsBefore == 1
    assert asystem1._dimsAfter == asystem2.dimension*asystem3.dimension*asystem4.dimension
    assert asystem1._dimsBefore == 1
    assert asystem2._dimsAfter == asystem3.dimension*asystem4.dimension
    assert asystem2._dimsBefore == asystem1.dimension
    assert asystem3._dimsAfter == asystem4.dimension
    assert asystem3._dimsBefore == asystem1.dimension*asystem2.dimension
    assert asystem4._dimsAfter == 1
    assert asystem4._dimsBefore == asystem1.dimension*asystem2.dimension*asystem3.dimension

def test_totalDim():
    someRandInt1 = rnd.randint(2, 20)
    someRandInt2 = rnd.randint(2, 20)
    # create a quantum system
    qsystem = QSys.QuSystem()
    # create 3 other systems with dimension info
    asystem1 = QSys.QuSystem(dimension=someRandInt1)
    asystem2 = QSys.QuSystem(dimension = someRandInt2)
    asystem3 = QSys.QuSystem(dimension=3)
    # add the sub-systems
    qsystem.addSubSys([asystem1, asystem2, asystem3])

    assert qsystem._totalDim == someRandInt1*someRandInt2*3
    assert asystem1._totalDim == someRandInt1*someRandInt2*3
    assert asystem2._totalDim == someRandInt1*someRandInt2*3
    assert asystem3._totalDim == someRandInt1*someRandInt2*3

def test_addingSameSubSysAgainDoNotChangeDimensions():
    someRandInt1 = rnd.randint(2, 20)
    # create a quantum system
    qsystem = QSys.QuSystem()
    # create 3 other systems with dimension info
    asystem1 = QSys.QuSystem(dimension=someRandInt1)
    # add the sub-systems
    qsystem.addSubSys(asystem1)
    qsystem.addSubSys(asystem1)
    assert asystem1._dimsAfter == 1
    assert asystem1._dimsBefore == 1

def test_nestedDimensionBeforeAfterSetsProperly():
    ranInts = [rnd.randint(3, 20) for _ in range(4)]
    # create two quantum systems
    qsystem1 = QSys.QuSystem()
    qsystem2 = QSys.QuSystem()
    # create 4 more systems to be sub-systems
    asystem1 = QSys.QuSystem(dimension = ranInts[0])
    asystem2 = QSys.QuSystem(dimension = ranInts[1])
    asystem3 = QSys.QuSystem(dimension = ranInts[2])
    asystem4 = QSys.QuSystem(dimension = ranInts[3])
    # add two to each qsystem
    qsystem1.addSubSys([asystem1, asystem2])
    qsystem2.addSubSys([asystem3, asystem4])

    dim1 = ranInts[0]*ranInts[1]
    dim2 = ranInts[2]*ranInts[3]
    assert qsystem1.dimension == dim1
    assert asystem1._totalDim == dim1
    assert asystem2._totalDim == dim1

    assert qsystem2.dimension == dim2
    assert asystem3._totalDim == dim2
    assert asystem4._totalDim == dim2

    assert asystem1._dimsAfter == asystem2.dimension
    assert asystem1._dimsBefore == 1
    assert asystem2._dimsAfter == 1
    assert asystem2._dimsBefore == asystem1.dimension
    
    assert asystem3._dimsAfter == asystem4.dimension
    assert asystem3._dimsBefore == 1
    assert asystem4._dimsAfter == 1
    assert asystem4._dimsBefore == asystem3.dimension

    # combine two qsystem into another qsystem
    qsystem3 = QSys.QuSystem(subSys=[qsystem1, qsystem2])

    dim3 = ranInts[0]*ranInts[1]*ranInts[2]*ranInts[3]
    assert qsystem3.dimension == dim3

    assert qsystem1.dimension == dim1

    assert qsystem2.dimension == dim2

    assert qsystem1._totalDim == dim3
    assert qsystem2._totalDim == dim3

    assert asystem1._totalDim == dim3
    assert asystem2._totalDim == dim3

    assert asystem3._totalDim == dim3
    assert asystem4._totalDim == dim3
    
    assert asystem1._dimsAfter == ranInts[1]*ranInts[2]*ranInts[3]
    assert asystem1._dimsBefore == 1
    assert asystem2._dimsAfter == ranInts[2]*ranInts[3]
    assert asystem2._dimsBefore == ranInts[0]

    assert asystem3._dimsAfter == ranInts[3]
    assert asystem3._dimsBefore == ranInts[0]*ranInts[1]
    
    assert asystem4._dimsAfter == 1
    assert asystem4._dimsBefore == ranInts[0]*ranInts[1]*ranInts[2]
