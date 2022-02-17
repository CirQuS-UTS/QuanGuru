from ast import operator
import random as rnd
import pytest
from quanguru.QuantumToolbox.operators import sigmaz, number
from quanguru.classes.QTerms import QTerm
from quanguru.classes.base import named

@pytest.mark.parametrize("oper", [sigmaz, number])
def test_cannotSetWithoutSuperSys(oper):
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
def test_singleSuperSysSingleOper(oper):
    named1 = named()
    t1 = QTerm(superSys=named1, operator=oper)
    assert t1.operator == oper

    with pytest.raises(TypeError):
        t1 = QTerm(superSys=named1, operator=[oper, oper])

    t1 = QTerm()
    t1.superSys=named1
    t1.operator=oper
    assert t1.operator == oper

    with pytest.raises(TypeError):
        t1 = QTerm()
        t1.superSys=named1
        t1.operator=[oper, oper]

@pytest.mark.parametrize("oper", [sigmaz, number])
def test_multiSuperSysMultiOper(oper):
    named1 = named()
    named2 = named()
    named3 = named()
    with pytest.raises(TypeError):
        t1 = QTerm(superSys=[named1, named2], operator=oper)

    with pytest.raises(ValueError):
        t1 = QTerm(superSys=[named1, named2], operator=[oper])

    t1 = QTerm(superSys=[named1, named2], operator=[oper, oper])
    assert t1.superSys == [named1, named2]
    assert t1.operator == [oper, oper]

    with pytest.raises(TypeError):
        t1 = QTerm()
        t1.superSys=[named1, named2, named3]
        t1.operator=oper

    with pytest.raises(ValueError):
        t1 = QTerm()
        t1.superSys=[named1, named2, named3]
        t1.operator=[oper, oper]

    t1 = QTerm()
    t1.superSys=[named1, named2, named3]
    t1.operator=[oper, oper, oper]
    assert t1.superSys == [named1, named2, named3]
    assert t1.operator == [oper, oper, oper]
