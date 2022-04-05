import pytest
import random as rnd
import quanguru.classes.QSystem as QSys
from quanguru.classes.QSys import QuantumSystemOld
import quanguru.QuantumToolbox.operators as QOps

def test_dimensionHasToBeInt():
    qsys1 = QSys.QuantumSystem(dimension=rnd.randint(2, 20))
    with pytest.raises(TypeError):
        qsys2 = QSys.QuantumSystem(dimension="10")

    qsys3 = QSys.QuantumSystem()
    qsys3.dimension=rnd.randint(2, 20)
    with pytest.raises(TypeError):
        qsys4 = QSys.QuantumSystem()
        qsys4.dimension="10"


@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_dimensionValues(cls):
    # create a quantum system
    qsystem = cls()
    # create 3 other systems with dimension info
    someRandInt1 = rnd.randint(2, 20)
    asystem1 = cls(dimension=someRandInt1)
    assert asystem1.dimension == someRandInt1
    someRandInt2 = rnd.randint(2, 20)
    asystem2 = cls() if cls is QSys.QuantumSystem else cls(dimension=someRandInt2)
    asystem2.dimension = someRandInt2
    assert asystem2.dimension == someRandInt2
    asystem3 = cls(dimension=3)
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

@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_dimensionABValues(cls):
    # create a quantum system
    qsystem = cls()

    # create 4 other systems with dimension info
    someRandInt1 = rnd.randint(2, 20)
    asystem1 = cls(dimension=someRandInt1)
 
    someRandInt2 = rnd.randint(2, 20)
    asystem2 = cls(dimension = someRandInt2)

    asystem3 = cls(dimension=3)
    asystem4 = cls(dimension=3)

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

@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_totalDim(cls):
    someRandInt1 = rnd.randint(2, 20)
    someRandInt2 = rnd.randint(2, 20)
    # create a quantum system
    qsystem = cls()
    # create 3 other systems with dimension info
    asystem1 = cls(dimension=someRandInt1)
    asystem2 = cls(dimension = someRandInt2)
    asystem3 = cls(dimension=3)
    # add the sub-systems
    qsystem.addSubSys([asystem1, asystem2, asystem3])

    assert qsystem._totalDim == someRandInt1*someRandInt2*3
    assert asystem1._totalDim == someRandInt1*someRandInt2*3
    assert asystem2._totalDim == someRandInt1*someRandInt2*3
    assert asystem3._totalDim == someRandInt1*someRandInt2*3

@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_addingSameSubSysAgainDoNotChangeDimensions(cls):
    someRandInt1 = rnd.randint(2, 20)
    # create a quantum system
    qsystem = cls()
    # create 3 other systems with dimension info
    asystem1 = cls(dimension=someRandInt1)
    # add the sub-systems
    qsystem.addSubSys(asystem1)
    qsystem.addSubSys(asystem1)
    assert asystem1._dimsAfter == 1
    assert asystem1._dimsBefore == 1

@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_nestedDimensionBeforeAfterSetsProperly(cls):
    ranInts = [rnd.randint(3, 20) for _ in range(4)]
    # create 4 more systems to be sub-systems
    asystem1 = cls(dimension = ranInts[0])
    asystem2 = cls(dimension = ranInts[1])
    asystem3 = cls(dimension = ranInts[2])
    asystem4 = cls(dimension = ranInts[3])
    # create two quantum systems and add two sub-system to each qsystem
    qsystem1 = cls(subSys=[asystem1, asystem2])
    qsystem2 = cls(subSys=[asystem3, asystem4])

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
    qsystem3 = cls(subSys=[qsystem1, qsystem2])

    dim3 = ranInts[0]*ranInts[1]*ranInts[2]*ranInts[3]
    assert qsystem1.dimension == dim1
    assert qsystem2.dimension == dim2
    assert qsystem3.dimension == dim3

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

@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_nestedDimensionBeforeAfterSetsAndUpdatesProperly(cls):
    ranInts = [rnd.randint(3, 20) for _ in range(6)]
    # create two quantum systems
    qsystem1 = cls()
    qsystem2 = cls()
    # create 4 more systems to be sub-systems
    asystem1 = cls(dimension = ranInts[0])
    asystem2 = cls(dimension = ranInts[1])
    asystem3 = cls(dimension = ranInts[2])
    asystem4 = cls(dimension = ranInts[3])
    # add two to each qsystem
    qsystem1.addSubSys([asystem1, asystem2])
    qsystem2.addSubSys([asystem3, asystem4])

    randInd = rnd.randint(0, 3)
    randSys = [asystem1, asystem2, asystem3, asystem4][randInd]
    randSys.dimension = ranInts[4]

    dim1 = asystem1.dimension*asystem2.dimension
    dim2 = asystem3.dimension*asystem4.dimension
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
    qsystem3 = cls(subSys=[qsystem1, qsystem2])

    randInd = rnd.randint(0, 3)
    randSys = [asystem1, asystem2, asystem3, asystem4][randInd]
    randSys.dimension = ranInts[5]

    dim1 = asystem1.dimension*asystem2.dimension
    dim2 = asystem3.dimension*asystem4.dimension
    dim3 = dim1*dim2
    assert qsystem1.dimension == dim1
    assert qsystem2.dimension == dim2
    assert qsystem3.dimension == dim3

    assert qsystem1._totalDim == dim3
    assert qsystem2._totalDim == dim3

    assert asystem1._totalDim == dim3
    assert asystem2._totalDim == dim3

    assert asystem3._totalDim == dim3
    assert asystem4._totalDim == dim3
    
    assert asystem1._dimsAfter == asystem2.dimension*asystem3.dimension*asystem4.dimension
    assert asystem1._dimsBefore == 1
    assert asystem2._dimsAfter == asystem3.dimension*asystem4.dimension
    assert asystem2._dimsBefore == asystem1.dimension

    assert asystem3._dimsAfter == asystem4.dimension
    assert asystem3._dimsBefore == asystem1.dimension*asystem2.dimension
    
    assert asystem4._dimsAfter == 1
    assert asystem4._dimsBefore == asystem1.dimension*asystem2.dimension*asystem3.dimension

def test_nestedSubSysDimesions():
    ranInts = [rnd.randint(3, 20) for _ in range(4)]
    asystem1 = QSys.QuantumSystem(dimension = ranInts[0])
    asystem2 = QSys.QuantumSystem(dimension = ranInts[1])
    asystem3 = QSys.QuantumSystem(dimension = ranInts[2])
    asystem4 = QSys.QuantumSystem(dimension = ranInts[3])

    qsystem1 = QSys.QuantumSystem(subSys=[asystem1, asystem2])
    qsystem2 = QSys.QuantumSystem(subSys=[asystem3, asystem4])

    assert qsystem1.subSysDimensions == ranInts[:2]
    assert qsystem2.subSysDimensions == ranInts[2:]
    assert asystem1.subSysDimensions == ranInts[0]
    assert asystem2.subSysDimensions == ranInts[1]
    assert asystem3.subSysDimensions == ranInts[2]
    assert asystem4.subSysDimensions == ranInts[3]

    qsystem3 = QSys.QuantumSystem(subSys=[qsystem1, qsystem2])

    assert qsystem3.subSysDimensions == [ranInts[:2], ranInts[2:]]
    assert qsystem1.subSysDimensions == ranInts[:2]
    assert qsystem2.subSysDimensions == ranInts[2:]
    assert asystem1.subSysDimensions == ranInts[0]
    assert asystem2.subSysDimensions == ranInts[1]
    assert asystem3.subSysDimensions == ranInts[2]
    assert asystem4.subSysDimensions == ranInts[3]
