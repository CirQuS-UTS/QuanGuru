import random as rnd
import pytest
import quanguru.classes.QSystem as QSys
from quanguru.classes.QSys import QuantumSystem

# tests for composite vs single system cases of the quantum system object

@pytest.mark.parametrize("cls", [
                         QuantumSystem,
                         QSys.QuSystem
                         ])
def test_addNestAndremoveSubSysNonNest(cls):
    comp1 = cls()
    comp2 = cls()
    comp3 = cls()
    comp4 = cls()
    sing1 = cls(dimension=rnd.randint(3, 10))
    sing2 = cls(dimension=rnd.randint(3, 10))
    sing3 = cls(dimension=rnd.randint(3, 10))
    sing4 = cls(dimension=rnd.randint(3, 10))
    sing5 = cls(dimension=rnd.randint(3, 10))
    sing6 = cls(dimension=rnd.randint(3, 10))
    sing7 = cls(dimension=rnd.randint(3, 10))
    sing8 = cls(dimension=rnd.randint(3, 10))
    sing9 = cls(dimension=rnd.randint(3, 10))

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

    comp1.removeSubSys(sing2)
    assert sing2 not in comp1.subSys.values()
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

    comp2.addSubSys([sing4, sing5, sing6])
    comp3.addSubSys([sing7, sing8, sing9])
    comp4.addSubSys([comp1, comp2, comp3])

    assert comp1 in comp4.subSys.values()
    assert comp2 in comp4.subSys.values()
    assert comp3 in comp4.subSys.values()

    assert comp4.dimension == comp1.dimension*comp2.dimension*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1._dimsAfter == comp2.dimension*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == comp2.dimension*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    comp2.removeSubSys(sing5)

    assert comp4.dimension == comp1.dimension*(sing4.dimension*sing6.dimension)*comp3.dimension
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1._dimsAfter == (sing4.dimension*sing6.dimension)*comp3.dimension
    assert comp2._dimsAfter == comp3.dimension
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension*sing6.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    comp4.removeSubSys(sing8)

    assert comp4.dimension == comp1.dimension*(sing4.dimension*sing6.dimension)*(sing7.dimension*sing9.dimension)
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1._dimsAfter == (sing4.dimension*sing6.dimension)*(sing7.dimension*sing9.dimension)
    assert comp2._dimsAfter == (sing7.dimension*sing9.dimension)
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == (sing4.dimension*sing6.dimension)*comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

    comp4.removeSubSys(comp2)

    assert comp4.dimension == comp1.dimension*(sing7.dimension*sing9.dimension)
    assert comp4._dimsBefore == 1
    assert comp4._dimsAfter == 1

    assert comp1._dimsAfter == (sing7.dimension*sing9.dimension)
    assert comp2._dimsAfter == (sing7.dimension*sing9.dimension)
    assert comp3._dimsAfter == 1
    assert comp3._dimsBefore == comp1.dimension
    assert comp2._dimsBefore == comp1.dimension
    assert comp1._dimsBefore == 1

