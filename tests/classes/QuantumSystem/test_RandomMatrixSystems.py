import quanguru.classes.QSystem as QSys
from quanguru.QuantumToolbox.operators import goeH, gueH, gueHT
from random import randint

def test_seedNumsInstantiation():
    """
    Test that the seedNums attribute is set to a random value upon instantiation if not provided.
    """
    dim = 10
    H1 = QSys.RandGOE(dimension=dim, frequency=1)
    H2 = QSys.RandGOE(dimension=dim, frequency=1)
    assert not (H1.totalHamiltonian == H2.totalHamiltonian).all()
    H3 = QSys.RandGUE(dimension=dim, frequency=1)
    H4 = QSys.RandGUE(dimension=dim, frequency=1)
    assert not (H3.totalHamiltonian == H4.totalHamiltonian).all()
    H5 = QSys.RandGUEt(dimension=dim, frequency=1)
    H6 = QSys.RandGUEt(dimension=dim, frequency=1)
    assert not (H5.totalHamiltonian == H6.totalHamiltonian).all()

def test_seedNumsPassedToOperator():
    """
    Test that the seedNums attribute is passed to the operator function on .totalHamiltonian call.
    """
    dim = 10
    seedNums = [randint(1, 1000), randint(1, 1000)]

    GOE1 = QSys.RandGOE(dimension=dim, frequency=1, seedNums=seedNums)
    assert (GOE1.totalHamiltonian == goeH(dim, seedNums)).all()

    GUE1 = QSys.RandGUE(dimension=dim, frequency=1, seedNums=seedNums)
    assert (GUE1.totalHamiltonian == gueH(dim, seedNums)).all()

def test_seedNumsChange():
    """
    Test that changing the seedNums attribute changes the generated totalHamiltonian.
    """
    dim = 10
    # test if the random totalHamiltonian is generated correctly with the given seed number
    seedNums = [randint(1, 1000), randint(1, 1000)]
    GOE1 = QSys.RandGOE(dimension=dim, frequency=1, seedNums=seedNums)
    GOE2 = QSys.RandGOE(dimension=dim, frequency=1, seedNums=seedNums)
    assert (GOE1.totalHamiltonian == GOE2.totalHamiltonian).all()
    GUE1 = QSys.RandGUE(dimension=dim, frequency=1, seedNums=seedNums)
    GUE2 = QSys.RandGUE(dimension=dim, frequency=1, seedNums=seedNums)
    assert (GUE1.totalHamiltonian == GUE2.totalHamiltonian).all()
    GUEt1 = QSys.RandGUEt(dimension=dim, frequency=1, seedNums=seedNums)
    GUEt2 = QSys.RandGUEt(dimension=dim, frequency=1, seedNums=seedNums)
    assert (GUEt1.totalHamiltonian == GUEt2.totalHamiltonian).all()
    # change the seed number and check if the totalHamiltonian is changed
    seedNums2 = [randint(1, 1000), randint(1, 1000)]
    GOE3 = QSys.RandGOE(dimension=dim, frequency=1, seedNums=seedNums2)
    GOE1.seedNums = seedNums2
    assert not (GOE1.totalHamiltonian == GOE2.totalHamiltonian).all()
    assert (GOE1.totalHamiltonian == GOE3.totalHamiltonian).all()
    GUE3 = QSys.RandGUE(dimension=dim, frequency=1, seedNums=seedNums2)
    GUE1.seedNums = seedNums2
    assert not (GUE1.totalHamiltonian == GUE2.totalHamiltonian).all()
    assert (GUE1.totalHamiltonian == GUE3.totalHamiltonian).all()
    GUEt3 = QSys.RandGUEt(dimension=dim, frequency=1, seedNums=seedNums2)
    GUEt1.seedNums = seedNums2
    assert not (GUEt1.totalHamiltonian == GUEt2.totalHamiltonian).all()
    assert (GUEt1.totalHamiltonian == GUEt3.totalHamiltonian).all()