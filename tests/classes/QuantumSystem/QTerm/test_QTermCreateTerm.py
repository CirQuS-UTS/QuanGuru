from quanguru.classes.baseClasses import paramBoundBase
from quanguru.classes.QTerms import QTerm
from quanguru.QuantumToolbox.operators import sigmaz, sigmay, sigmax

def assertTheseVals(t1, *args):
    assert t1.qSystem == args[0]
    assert t1.operator == args[1]
    assert t1.order == args[2]
    assert t1.frequency == args[3]
    assert len(t1.subSys) == args[4]

def test_QTermCreateTerm():
    named1 = paramBoundBase()
    named2 = paramBoundBase()
    named3 = paramBoundBase()
    named4 = paramBoundBase()

    t1 = QTerm._createTerm(named1, named1, sigmaz)
    assertTheseVals(t1, named1, sigmaz, 1, None, 0)

    t1 = QTerm._createTerm(named1, named1, sigmaz, order=2, frequency=3)
    assertTheseVals(t1, named1, sigmaz, 2, 3, 0)

    t1 = QTerm._createTerm(named1, [named1, named2, named3], [sigmaz, sigmay, sigmax])
    assertTheseVals(t1, [named1, named2, named3], [sigmaz, sigmay, sigmax], [1, 1, 1], None, 3)

    t1 = QTerm._createTerm(named1, [named1, named2, named3, named4], [sigmaz,sigmaz, sigmay, sigmax], order=[0, 1, 2, 3], frequency=4)
    assertTheseVals(t1, [named1, named2, named3, named4], [sigmaz, sigmaz, sigmay, sigmax], [0, 1, 2, 3], 4, 4)
