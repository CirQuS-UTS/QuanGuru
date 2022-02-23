import random as rnd
import pytest
import quanguru.classes.QSystem as QSys
from quanguru.classes.QSys import QuantumSystemOld


@pytest.mark.parametrize("cls", [
                         QuantumSystemOld,
                         QSys.QuantumSystem
                         ])
def test_addAndremoveSubSysMethods(cls):
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

    # create a composite system with 3 of the single systems and check dimensions
    comp1.addSubSys([sing1, sing2, sing3])
    assert sing2 in comp1.subSys.values()
    assert comp1._dimsBefore == 1
    assert comp1._dimsAfter == 1
    assert comp1.dimension == sing1.dimension*sing2.dimension*sing3.dimension
    assert sing1._dimsAfter == sing2.dimension*sing3.dimension
    assert sing2._dimsAfter == sing3.dimension
    assert sing3._dimsAfter == 1
    assert sing3._dimsBefore == sing2.dimension*sing1.dimension
    assert sing2._dimsBefore == sing1.dimension
    assert sing1._dimsBefore == 1
    # remove one of them and check dimensions
    comp1.removeSubSys(sing2)
    assert sing2 not in comp1.subSys.values()
    assert comp1._dimsBefore == 1
    assert comp1._dimsAfter == 1
    assert comp1.dimension == sing1.dimension*sing3.dimension
    assert sing1._dimsAfter == sing3.dimension
    #assert sing2._dimsAfter == sing3.dimension
    assert sing3._dimsAfter == 1
    assert sing3._dimsBefore == sing1.dimension
    #assert sing2._dimsBefore == sing1.dimension
    assert sing1._dimsBefore == 1

    # compose two other composite system with 3 sub-systems
    comp2.addSubSys([sing4, sing5, sing6])
    comp3.addSubSys([sing7, sing8, sing9])
    # compose a composite system of composite systems
    comp4.addSubSys([comp1, comp2, comp3])

    # check that the subsystems are there
    assert comp1 in comp4.subSys.values()
    assert comp2 in comp4.subSys.values()
    assert comp3 in comp4.subSys.values()

    # check that the dimensions are correct
    assert comp4.dimension == comp1.dimension*comp2.dimension*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1._dimsAfter == comp2.dimension*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == comp2.dimension*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a sub-system (sing5) of comp2 by calling the removeSubSys on comp2
    comp2.removeSubSys(sing5)
    assert sing5 not in comp2.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing4.dimension*sing6.dimension)*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp2.dimension == (sing4.dimension*sing6.dimension)

    assert comp1._dimsAfter == (sing4.dimension*sing6.dimension)*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension*sing6.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a sub-system (sing6) of comp2 by calling the removeSubSys on comp3
    assert sing6 not in comp3.subSys.values()
    comp3.removeSubSys(sing6)
    assert sing6 not in comp2.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing4.dimension)*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp2.dimension == sing4.dimension

    assert comp1._dimsAfter == (sing4.dimension)*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a sub-system (sing8) of comp3 by calling the removeSubSys on comp4 (composite of the composites)
    comp4.removeSubSys(sing8)
    assert sing8 not in comp3.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing4.dimension)*(sing7.dimension*sing9.dimension)
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp3.dimension == (sing7.dimension*sing9.dimension)

    assert comp1._dimsAfter == (sing4.dimension)*(sing7.dimension*sing9.dimension)
    assert comp2._dimsAfter == (sing7.dimension*sing9.dimension)
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a composite sub-system comp2 by calling the removeSubSys on comp4
    comp4.removeSubSys(comp2)
    assert comp2 not in comp4.subSys.values()
    assert sing4 in comp2.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing7.dimension*sing9.dimension)
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp2.dimension == sing4.dimension

    assert comp1._dimsAfter == (sing7.dimension*sing9.dimension)
    assert comp2._dimsAfter == 1
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == comp1.dimension
    assert comp2._dimsBefore == 1
    assert comp1._dimsBefore == 1

    comp1.removeSubSys(comp3)
    assert comp3 not in comp4.subSys.values()
    assert comp1 in comp4.subSys.values()
    assert sing7 in comp3.subSys.values()
    assert sing8 not in comp3.subSys.values()
    assert sing9 in comp3.subSys.values()

    assert comp4.dimension == comp1.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp3.dimension == (sing7.dimension*sing9.dimension)

    assert comp1._dimsAfter == 1
    assert comp2._dimsAfter == 1
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == 1
    assert comp2._dimsBefore == 1
    assert comp1._dimsBefore == 1

    comp1.removeSubSys(comp1)
    assert comp1 not in comp4.subSys.values()
    assert sing1 in comp1.subSys.values()
    assert sing2 not in comp1.subSys.values()
    assert sing3 in comp1.subSys.values()

    assert comp4.dimension == 1
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1.dimension == sing1.dimension*sing3.dimension

    assert comp1._dimsAfter == 1
    assert comp2._dimsAfter == 1
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == 1
    assert comp2._dimsBefore == 1
    assert comp1._dimsBefore == 1

def test_addAndremoveSubSysOperators():
    cls = QSys.QuantumSystem
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

    # create a composite system with 3 of the single systems and check dimensions
    comp1 += sing1
    comp1 += sing2
    comp1 += sing3
    assert sing2 in comp1.subSys.values()
    assert comp1._dimsBefore == 1
    assert comp1._dimsAfter == 1
    assert comp1.dimension == sing1.dimension*sing2.dimension*sing3.dimension
    assert sing1._dimsAfter == sing2.dimension*sing3.dimension
    assert sing2._dimsAfter == sing3.dimension
    assert sing3._dimsAfter == 1
    assert sing3._dimsBefore == sing2.dimension*sing1.dimension
    assert sing2._dimsBefore == sing1.dimension
    assert sing1._dimsBefore == 1
    # remove one of them and check dimensions
    comp1 -= sing2
    assert sing2 not in comp1.subSys.values()
    assert comp1._dimsBefore == 1
    assert comp1._dimsAfter == 1
    assert comp1.dimension == sing1.dimension*sing3.dimension
    assert sing1._dimsAfter ==sing3.dimension
    #assert sing2._dimsAfter == sing3.dimension
    assert sing3._dimsAfter == 1
    assert sing3._dimsBefore == sing1.dimension
    #assert sing2._dimsBefore == sing1.dimension
    assert sing1._dimsBefore == 1

    # compose two other composite system with 3 sub-systems
    comp2 += sing4
    comp2 += sing5
    comp2 += sing6
    comp3 += sing7
    comp3 += sing8
    comp3 += sing9
    # compose a composite system of composite systems
    comp4 += comp1
    comp4 += comp2
    comp4 += comp3

    # check that the subsystems are there
    assert comp4._hasInSubs(comp1)
    assert comp4._hasInSubs(comp2)
    assert comp4._hasInSubs(comp3)

    # check that the dimensions are correct
    assert comp4.dimension == comp1.dimension*comp2.dimension*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1._dimsAfter == comp2.dimension*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == comp2.dimension*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a sub-system (sing5) of comp2 by calling the removeSubSys on comp2
    comp2 -= sing5
    assert sing5 not in comp2.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing4.dimension*sing6.dimension)*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp2.dimension == (sing4.dimension*sing6.dimension)

    assert comp1._dimsAfter == (sing4.dimension*sing6.dimension)*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension*sing6.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a sub-system (sing6) of comp2 by calling the removeSubSys on comp3
    assert sing6 not in comp3.subSys.values()
    comp3 -= sing6
    assert sing6 not in comp2.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing4.dimension)*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp2.dimension == sing4.dimension

    assert comp1._dimsAfter == (sing4.dimension)*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a sub-system (sing8) of comp3 by calling the removeSubSys on comp4 (composite of the composites)
    comp4 -= sing8
    assert sing8 not in comp3.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing4.dimension)*(sing7.dimension*sing9.dimension)
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp3.dimension == (sing7.dimension*sing9.dimension)

    assert comp1._dimsAfter == (sing4.dimension)*(sing7.dimension*sing9.dimension)
    assert comp2._dimsAfter == (sing7.dimension*sing9.dimension)
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    # remove a composite sub-system comp2 by calling the removeSubSys on comp4
    comp4 -= comp2
    assert comp2 not in comp4.subSys.values()
    assert sing4 in comp2.subSys.values()

    assert comp4.dimension == comp1.dimension*(sing7.dimension*sing9.dimension)
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp2.dimension == sing4.dimension

    assert comp1._dimsAfter == (sing7.dimension*sing9.dimension)
    assert comp2._dimsAfter == 1
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == comp1.dimension
    assert comp2._dimsBefore == 1
    assert comp1._dimsBefore == 1

    comp1 -= comp3
    assert comp3 not in comp4.subSys.values()
    assert comp4._hasInSubs(comp1)
    assert sing7 in comp3.subSys.values()
    assert sing8 not in comp3.subSys.values()
    assert sing9 in comp3.subSys.values()

    assert comp4.dimension == comp1.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp3.dimension == (sing7.dimension*sing9.dimension)

    assert comp1._dimsAfter == 1
    assert comp2._dimsAfter == 1
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == 1
    assert comp2._dimsBefore == 1
    assert comp1._dimsBefore == 1

    comp1 -= comp1
    assert not comp4._hasInSubs(comp1)
    assert sing1 in comp1.subSys.values()
    assert sing2 not in comp1.subSys.values()
    assert sing3 in comp1.subSys.values()

    assert comp4.dimension == 1
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1.dimension == sing1.dimension*sing3.dimension

    assert comp1._dimsAfter == 1
    assert comp2._dimsAfter == 1
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == 1
    assert comp2._dimsBefore == 1
    assert comp1._dimsBefore == 1

