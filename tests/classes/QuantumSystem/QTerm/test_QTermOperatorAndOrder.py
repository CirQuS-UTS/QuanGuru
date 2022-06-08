import random as rnd
import pytest
from quanguru.QuantumToolbox.operators import sigmaz, number
from quanguru.classes.QSystem import QuantumSystem
from quanguru.classes.QTerms import QTerm
from quanguru.classes.QSystem import QuantumSystem

def test_PauliOperatorDimesionHasToBe2Case1():
    qs = QuantumSystem()
    qs.dimension = 3
    with pytest.raises(ValueError):
        qs.operator = sigmaz

def test_PauliOperatorDimesionHasToBe2Case2():
    qs = QuantumSystem()
    qs.operator = sigmaz
    with pytest.raises(ValueError):
        qs.dimension = 3

def test_PauliOperatorDimesionHasToBe2Case3():
    qSingle1 = QuantumSystem(dimension=rnd.randint(3, 10))
    qSingle2 = QuantumSystem(dimension=rnd.randint(2, 10))

    qComposite = QuantumSystem(subSys=[qSingle1,  qSingle2])

    couplingTerm = QTerm(superSys=qComposite)
    couplingTerm.qSystem = (qSingle1, qSingle1, qSingle2)
    with pytest.raises(ValueError):
        couplingTerm.operator = (sigmaz, sigmaz, number)

def test_PauliOperatorDimesionHasToBe2Case4():
    qSingle1 = QuantumSystem()
    qSingle2 = QuantumSystem()

    qComposite = QuantumSystem(subSys=[qSingle1, qSingle2])

    couplingTerm = qComposite.createTerm(superSys=qComposite, frequency=1, qSystem = (qSingle1, qSingle1), operator = (sigmaz, sigmaz))
    with pytest.raises(ValueError):
        qSingle1.dimension = 3

@pytest.mark.parametrize("oper", [sigmaz, number])
def test_cannotSetWithoutqSystem(oper):
    with pytest.raises(ValueError):
        QTerm(operator = oper)
    with pytest.raises(ValueError):
        QTerm(order = rnd.randint(2, 10))

    with pytest.raises(ValueError):
        qt1 = QTerm()
        qt1.operator = oper
    with pytest.raises(ValueError):
        qt1 = QTerm()
        qt1.order = rnd.randint(2, 10)

@pytest.mark.parametrize("oper", [sigmaz, number])
def test_singleqSystemSingleOper(oper):
    named1 = QuantumSystem()
    t1 = QTerm(qSystem=named1, operator=oper)
    assert t1.operator == oper
    assert len(t1.subSys) == 0

    with pytest.raises(TypeError):
        t1 = QTerm(qSystem=named1, operator=[oper, oper])

    t1 = QTerm()
    t1.qSystem=named1
    t1.operator=oper
    assert t1.operator == oper
    assert len(t1.subSys) == 0

    with pytest.raises(TypeError):
        t1 = QTerm()
        t1.qSystem=named1
        t1.operator=[oper, oper]

@pytest.mark.parametrize("oper", [sigmaz, number])
def test_multiqSystemMultiOper(oper):
    named1 = QuantumSystem()
    named2 = QuantumSystem()
    named3 = QuantumSystem()
    with pytest.raises(TypeError):
        t1 = QTerm(superSys=named1, qSystem=[named1, named2], operator=oper)

    with pytest.raises(ValueError):
        t1 = QTerm(superSys=named1, qSystem=[named1, named2], operator=[oper])

    t1 = QTerm(superSys=named1, qSystem=[named1, named2], operator=[oper, oper])
    assert t1.qSystem == [named1, named2]
    assert t1.operator == [oper, oper]
    opers = t1.operator
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.operator is opers[ind]
    opers = t1.operator
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(opers):
        assert te is subSys[ind].operator

    with pytest.raises(TypeError):
        t1 = QTerm()
        t1.superSys=named1
        t1.qSystem=[named1, named2, named3]
        t1.operator=oper

    with pytest.raises(ValueError):
        t1 = QTerm()
        t1.superSys=named1
        t1.qSystem=[named1, named2, named3]
        t1.operator=[oper, oper]

    t1 = QTerm()
    t1.superSys=named1
    t1.qSystem=[named1, named2, named3]
    t1.operator=[oper, oper, oper]
    assert t1.qSystem == [named1, named2, named3]
    assert t1.operator == [oper, oper, oper]
    opers = t1.operator
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.operator is opers[ind]
    opers = t1.operator
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(opers):
        assert te is subSys[ind].operator

@pytest.mark.parametrize("orde", [sigmaz, number])
def test_singleqSystemSingleOrder(orde):
    named1 = QuantumSystem()
    t1 = QTerm(qSystem=named1, order=orde)
    assert t1.order == orde
    assert len(t1.subSys) == 0

    with pytest.raises(TypeError):
        t1 = QTerm(qSystem=named1, order=[orde, orde])

    t1 = QTerm()
    t1.qSystem=named1
    t1.order=orde
    assert t1.order == orde
    assert len(t1.subSys) == 0

    with pytest.raises(TypeError):
        t1 = QTerm()
        t1.qSystem=named1
        t1.order=[orde, orde]

@pytest.mark.parametrize("orde", [2, 10])
def test_multiqSystemMultiOrder(orde):
    named1 = QuantumSystem()
    named2 = QuantumSystem()
    named3 = QuantumSystem()
    with pytest.raises(TypeError):
        t1 = QTerm(superSys=named1, qSystem=[named1, named2], order=orde)

    with pytest.raises(ValueError):
        t1 = QTerm(superSys=named1, qSystem=[named1, named2], order=[orde])

    t1 = QTerm(superSys=named1, qSystem=[named1, named2], order=[orde, orde])
    assert t1.qSystem == [named1, named2]
    assert t1.order == [orde, orde]
    opers = t1.order
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.order is opers[ind]
    opers = t1.order
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(opers):
        assert te is subSys[ind].order

    with pytest.raises(TypeError):
        t1 = QTerm(superSys=named1)
        t1.qSystem=[named1, named2, named3]
        t1.order=orde

    with pytest.raises(ValueError):
        t1 = QTerm(superSys=named1)
        t1.qSystem=[named1, named2, named3]
        t1.order=[orde, orde]

    t1 = QTerm(superSys=named1)
    t1.qSystem=[named1, named2, named3]
    t1.order=[orde, orde, orde]
    assert t1.qSystem == [named1, named2, named3]
    assert t1.order == [orde, orde, orde]
    opers = t1.order
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(subSys):
        assert te.order is opers[ind]
    opers = t1.order
    subSys = list(t1.subSys.values())
    for ind, te in enumerate(opers):
        assert te is subSys[ind].order
