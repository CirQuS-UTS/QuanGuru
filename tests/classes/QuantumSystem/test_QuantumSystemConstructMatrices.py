import pytest
from quanguru.classes.QSystem import QuantumSystem

def test_noAttributeConstructMatricesForSingle():
    # create a quantum system
    qsys = QuantumSystem()
    with pytest.warns(Warning):
        qsys._constructMatrices()

def test_noAttributeConstructMatricesForComposite():
    # create a quantum system
    qsys1 = QuantumSystem()
    qsys2 = QuantumSystem(subSys=qsys1)
    with pytest.warns(Warning):
        qsys2._constructMatrices()
    with pytest.warns(Warning):
        qsys1._constructMatrices()
