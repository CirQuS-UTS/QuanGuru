import random as rnd
import pytest
from quanguru.classes.baseClasses import paramBoundBase
from quanguru.classes.QTerms import QTerm

def test_qSystemsOfQTermIsNamedWithSetter(helpers):
    # create some random strings to use as alias
    randname0 = helpers.randString(rnd.randint(4, 10))
    randname1 = helpers.randString(rnd.randint(4, 10))
    randname2 = helpers.randString(rnd.randint(4, 10))
    randname3 = helpers.randString(rnd.randint(4, 10))
    # create two named object and assign some alias
    named1 = paramBoundBase(alias=randname1)
    named2 = paramBoundBase(alias=[randname2, randname3])
    # create 3 qterm objects
    termOb1 = QTerm()
    termOb2 = QTerm()
    termOb3 = QTerm()

    # setting the qSystems to a random string that is not the name/alias of a named raises ValueError
    with pytest.raises(ValueError):
        termOb1.qSystems = randname0
    with pytest.raises(ValueError):
        termOb1.qSystems = randname0
    # can use the alias to set the qSystems
    termOb2.qSystems = randname1
    assert termOb2.qSystems is named1
    # can use the named object itself to set the qSystems
    termOb2.qSystems = named2
    assert termOb2.qSystems is named2
    # can use any of the multiple aliases
    termOb3.qSystems = randname3
    assert termOb3.qSystems is named2

def test_qSystemsOfQTermIsNamedAtInstantiation(helpers):
    randname0 = helpers.randString(rnd.randint(4, 10))
    randname1 = helpers.randString(rnd.randint(4, 10))
    randname2 = helpers.randString(rnd.randint(4, 10))
    randname3 = helpers.randString(rnd.randint(4, 10))
    named1 = paramBoundBase(alias=randname1)
    named2 = paramBoundBase(alias=[randname2, randname3])

    # setting the qSystems to a random string that is not the name/alias of a named raises ValueError
    with pytest.raises(ValueError):
        QTerm(qSystems = randname0)
    with pytest.raises(ValueError):
        QTerm(qSystems = randname0)
    # can use the alias to set the qSystems
    termOb2 = QTerm(qSystems=randname1)
    assert termOb2.qSystems is named1
    termOb2 = QTerm(qSystems=randname2)
    assert termOb2.qSystems is named2
    # can use the named object itself to set the qSystems
    termOb3 = QTerm(qSystems=named2)
    assert termOb3.qSystems is named2
    termOb3 = QTerm(qSystems=named1)
    assert termOb3.qSystems is named1
    # can set/change the qSystems with another named
    termOb2.qSystems = named2
    assert termOb2.qSystems is named2
    # can set/change the qSystems with any of the multiple aliases
    termOb3.qSystems = randname1
    assert termOb3.qSystems is named1

def test_multipleSuperSys(helpers):
    randname = helpers.randString(rnd.randint(4, 10))
    # create some named objects to use as qSystems
    named1 = paramBoundBase()
    named2 = paramBoundBase()
    named3 = paramBoundBase(alias=randname)
    named4 = paramBoundBase()
    # set qSystems with a mixture of name, alias, and object at instantiation
    term1 = QTerm(superSys=named1, qSystems=(named1, named2.name, randname))
    assert term1.qSystems == [named1, named2, named3]
    # set qSystems through qSystems with a mixture of name, alias, and object at instantiation
    term2 = QTerm(superSys=named1, qSystems=[named2.name, randname, named4])
    assert term2.qSystems == [named2, named3, named4]
    # set qSystems with a mixture of name, alias, and object after instantiation
    term3 = QTerm(superSys=named1)
    term3.qSystems = [named1, named2.name, randname]
    assert term3.qSystems == [named1, named2, named3]
    # set qSystems through qSystems with a mixture of name, alias, and object at instantiation
    term4 = QTerm(superSys=named1)
    term4.qSystems = (named2.name, randname, named4)
    assert term4.qSystems == [named2, named3, named4]

def test_qSystemsSetterSideEffects(helpers):
    randname = helpers.randString(rnd.randint(4, 10))
    # create some named objects to use as qSystems
    named1 = paramBoundBase()
    named2 = paramBoundBase()
    named3 = paramBoundBase(alias=randname)
    named4 = paramBoundBase()

    # with a single qSystems at instantiation
    term1 = QTerm(qSystems=named1)
    assert term1.order == 1
    assert term1.operator is None
    assert len(term1.subSys) == 0
    
    # with a single qSystems after instantiation
    term1 = QTerm(superSys=named1)
    term1._QTerm__order = 10
    term1._QTerm__operator = 11
    term1.addSubSys([named1, named2])
    assert term1.order == 10
    assert term1.operator == 11
    assert named1 in term1.subSys.values()
    assert named2 in term1.subSys.values()
    term1.qSystems = named1
    assert term1.order == 1
    assert term1.operator is None
    assert named1 not in term1.subSys.values()
    assert named2 not in term1.subSys.values()

    term1 = QTerm(qSystems=named1)
    assert len(term1.subSys) == 0
    assert term1.qSystems is named1

    term1.qSystems = named2.name
    assert len(term1.subSys) == 0
    assert term1.qSystems is named2

    term1.qSystems = randname
    assert len(term1.subSys) == 0
    assert term1.qSystems is named3

    term1 = QTerm(superSys=named1, qSystems=(named1, named2.name, randname))
    assert term1.order == 1
    assert term1.operator is None
    assert named1 not in term1.subSys.values()
    assert named2 not in term1.subSys.values()

    term1 = QTerm(superSys=named1)
    term1._QTerm__order = 10
    term1._QTerm__operator = 11
    term1.addSubSys([named1, named2])
    assert term1.order == 10
    assert term1.operator == 11
    assert named1 in term1.subSys.values()
    assert named2 in term1.subSys.values()
    term1.qSystems = (named1, named2.name, randname)
    assert term1.order == 1
    assert term1.operator is None
    assert named1 not in term1.subSys.values()
    assert named2 not in term1.subSys.values()

    term1 = QTerm(superSys=named1, qSystems=(named1, named2.name, randname))
    supSys = term1.qSystems
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.qSystems is supSys[ind]
    supSys = term1.qSystems
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(supSys):
        assert te is subSys[ind].qSystems

    term1.qSystems = (named2.name, randname, named4)
    assert named1 not in term1.qSystems
    assert named2 in term1.qSystems
    assert named3 in term1.qSystems
    assert named4 in term1.qSystems
    supSys = term1.qSystems
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.qSystems is supSys[ind]
    supSys = term1.qSystems
    subSys = list(term1.subSys.values())
    for ind, te in enumerate(supSys):
        assert te is subSys[ind].qSystems
