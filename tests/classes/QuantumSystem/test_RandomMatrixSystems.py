import pytest
import quanguru.classes.QSystem as QSys
import random as rnd

def test_randomMatrix():
    # test if the random totalHamiltonian without seed number is generated randomly 
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

    # test if the random totalHamiltonian is generated correctly with the given seed number
    seedNum = [rnd.randint(1, 1000), rnd.randint(1, 1000)]
    GOE1 = QSys.RandGOE(dimension=dim, frequency=1, seedNum=seedNum)
    GOE2 = QSys.RandGOE(dimension=dim, frequency=1, seedNum=seedNum)
    assert (GOE1.totalHamiltonian == GOE2.totalHamiltonian).all()
    GUE1 = QSys.RandGUE(dimension=dim, frequency=1, seedNum=seedNum)
    GUE2 = QSys.RandGUE(dimension=dim, frequency=1, seedNum=seedNum)
    assert (GUE1.totalHamiltonian == GUE2.totalHamiltonian).all()
    GUEt1 = QSys.RandGUEt(dimension=dim, frequency=1, seedNum=seedNum)
    GUEt2 = QSys.RandGUEt(dimension=dim, frequency=1, seedNum=seedNum)
    assert (GUEt1.totalHamiltonian == GUEt2.totalHamiltonian).all()
    # change the seed number and check if the totalHamiltonian is changed
    seedNum2 = [rnd.randint(1, 1000), rnd.randint(1, 1000)]
    GOE3 = QSys.RandGOE(dimension=dim, frequency=1, seedNum=seedNum2)
    GOE1.seedNum = seedNum2
    assert not (GOE1.totalHamiltonian == GOE1.totalHamiltonian).all()
    assert (GOE1.totalHamiltonian == GOE3.totalHamiltonian).all()
    GUE3 = QSys.RandGUE(dimension=dim, frequency=1, seedNum=seedNum2)
    GUE1.seedNum = seedNum2
    assert not (GUE1.totalHamiltonian == GUE2.totalHamiltonian).all()
    assert (GUE1.totalHamiltonian == GUE3.totalHamiltonian).all()
    GUEt3 = QSys.RandGUEt(dimension=dim, frequency=1, seedNum=seedNum2)
    GUEt1.seedNum = seedNum2
    assert not (GUEt1.totalHamiltonian == GUEt2.totalHamiltonian).all()
    assert (GUEt1.totalHamiltonian == GUEt3.totalHamiltonian).all()