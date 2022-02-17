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
    named1 = named()
    t1 = QTerm(superSys=named1, operator=oper)
    assert t1.operator == oper

    with pytest.raises(TypeError):
        t1 = QTerm(superSys=named1, operator=[oper, oper])
