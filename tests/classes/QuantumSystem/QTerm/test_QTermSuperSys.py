import random as rnd
import pytest
from quanguru.classes.base import named
from quanguru.classes.QTerms import QTerm

def test_cannotSetBothSuperSysAndQSystemsAtInstantiation(helpers):
    randname1 = helpers.randString(rnd.randint(4, 10))
    named1 = named(alias=randname1)
    with pytest.raises(ValueError):
        QTerm(superSys=named1, qSystems=named1)

def test_superSysOfQTermIsNamedWithSetter(helpers):
    # create some random strings to use as alias
    randname0 = helpers.randString(rnd.randint(4, 10))
    randname1 = helpers.randString(rnd.randint(4, 10))
    randname2 = helpers.randString(rnd.randint(4, 10))
    randname3 = helpers.randString(rnd.randint(4, 10))
    # create two named object and assign some alias
    named1 = named(alias=randname1)
    named2 = named(alias=[randname2, randname3])
    # create 3 qterm objects
    termOb1 = QTerm()
    termOb2 = QTerm()
    termOb3 = QTerm()

    # setting the superSys to a random string that is not the name/alias of a named raises ValueError
    with pytest.raises(ValueError):
        termOb1.superSys = randname0
    # can use the alias to set the superSys
    termOb2.superSys = randname1
    assert termOb2.superSys is named1
    # can use the named object itself to set the superSys
    termOb2.superSys = named2
    assert termOb2.superSys is named2
    # can use any of the multiple aliases
    termOb3.superSys = randname3
    assert termOb3.superSys is named2

def test_superSysOfQTermIsNamedAtInstantiation(helpers):
    randname0 = helpers.randString(rnd.randint(4, 10))
    randname1 = helpers.randString(rnd.randint(4, 10))
    randname2 = helpers.randString(rnd.randint(4, 10))
    randname3 = helpers.randString(rnd.randint(4, 10))
    named1 = named(alias=randname1)
    named2 = named(alias=[randname2, randname3])

    # setting the superSys to a random string that is not the name/alias of a named raises ValueError
    with pytest.raises(ValueError):
        QTerm(superSys = randname0)
    # can use the alias to set the superSys
    termOb2 = QTerm(superSys=randname1)
    assert termOb2.superSys is named1
    # can use the named object itself to set the superSys
    termOb3 = QTerm(superSys=named2)
    assert termOb3.superSys is named2
    # can set/change the superSys with another named
    termOb2.superSys = named2
    assert termOb2.superSys is named2
    # can set/change the superSys with any of the multiple aliases
    termOb3.superSys = randname1
    assert termOb3.superSys is named1
