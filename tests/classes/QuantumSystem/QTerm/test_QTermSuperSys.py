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
    with pytest.raises(ValueError):
        termOb1.qSystems = randname0
    # can use the alias to set the superSys
    termOb2.superSys = randname1
    assert termOb2.superSys is named1
    # can use the named object itself to set the superSys
    termOb2.qSystems = named2
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
    with pytest.raises(ValueError):
        QTerm(qSystems = randname0)
    # can use the alias to set the superSys
    termOb2 = QTerm(superSys=randname1)
    assert termOb2.superSys is named1
    termOb2 = QTerm(qSystems=randname2)
    assert termOb2.superSys is named2
    # can use the named object itself to set the superSys
    termOb3 = QTerm(superSys=named2)
    assert termOb3.superSys is named2
    termOb3 = QTerm(qSystems=named1)
    assert termOb3.superSys is named1
    # can set/change the superSys with another named
    termOb2.superSys = named2
    assert termOb2.superSys is named2
    # can set/change the superSys with any of the multiple aliases
    termOb3.superSys = randname1
    assert termOb3.superSys is named1

def test_multipleSuperSys(helpers):
    randname = helpers.randString(rnd.randint(4, 10))
    # create some named objects to use as superSys
    named1 = named()
    named2 = named()
    named3 = named(alias=randname)
    named4 = named()
    # set superSys with a mixture of name, alias, and object at instantiation
    term1 = QTerm(superSys=(named1, named2.name, randname))
    assert term1.superSys == [named1, named2, named3]
    # set superSys through qSystems with a mixture of name, alias, and object at instantiation
    term2 = QTerm(qSystems=[named2.name, randname, named4])
    assert term2.superSys == [named2, named3, named4]
    # set superSys with a mixture of name, alias, and object after instantiation
    term3 = QTerm()
    term3.superSys = [named1, named2.name, randname]
    assert term3.superSys == [named1, named2, named3]
    # set superSys through qSystems with a mixture of name, alias, and object at instantiation
    term4 = QTerm()
    term4.qSystems = (named2.name, randname, named4)
    assert term4.superSys == [named2, named3, named4]

def test_superSysSetterSideEffects(helpers):
    randname = helpers.randString(rnd.randint(4, 10))
    # create some named objects to use as superSys
    named1 = named()
    named2 = named()
    named3 = named(alias=randname)
    named4 = named()

    # with a single superSys at instantiation
    term1 = QTerm(superSys=named1)
    assert term1.order == 1
    assert term1.operator is None
    assert len(term1.subSys) == 0
    
    # with a single superSys after instantiation
    term1 = QTerm()
    term1._QTerm__order = 10
    term1._QTerm__operator = 11
    term1.addSubSys([named1, named2])
    assert term1.order == 10
    assert term1.operator == 11
    assert named1 in term1.subSys.values()
    assert named2 in term1.subSys.values()
    term1.superSys = named1
    assert term1.order == 1
    assert term1.operator is None
    assert named1 not in term1.subSys.values()
    assert named2 not in term1.subSys.values()

    term1 = QTerm(superSys=named1)
    assert len(term1.subSys) == 0
    assert term1.superSys is named1

    term1.superSys = named2.name
    assert len(term1.subSys) == 0
    assert term1.superSys is named2

    term1.superSys = randname
    assert len(term1.subSys) == 0
    assert term1.superSys is named3

    term1 = QTerm(superSys=(named1, named2.name, randname))
    assert term1.order == 1
    assert term1.operator is None
    assert named1 not in term1.subSys.values()
    assert named2 not in term1.subSys.values()

    term1 = QTerm()
    term1._QTerm__order = 10
    term1._QTerm__operator = 11
    term1.addSubSys([named1, named2])
    assert term1.order == 10
    assert term1.operator == 11
    assert named1 in term1.subSys.values()
    assert named2 in term1.subSys.values()
    term1.superSys = (named1, named2.name, randname)
    assert term1.order == 1
    assert term1.operator is None
    assert named1 not in term1.subSys.values()
    assert named2 not in term1.subSys.values()

    term1 = QTerm(superSys=(named1, named2.name, randname))
    supSys = term1.superSys
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.superSys is supSys[ind]
    supSys = term1.superSys
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(supSys):
        assert te is subSys[ind].superSys

    term1.superSys = (named2.name, randname, named4)
    assert named1 not in term1.superSys
    assert named2 in term1.superSys
    assert named3 in term1.superSys
    assert named4 in term1.superSys
    supSys = term1.superSys
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.superSys is supSys[ind]
    supSys = term1.superSys
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(supSys):
        assert te is subSys[ind].superSys
