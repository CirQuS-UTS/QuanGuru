import pytest
import numpy as np
from quanguru.classes.QSystem import QuantumSystem
from quanguru.QuantumToolbox.operators import sigmam

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

def test_onlyDimensionConstructMatricesForSingle():
    # create a quantum system
    qsys1 = QuantumSystem(dimension=2)
    with pytest.warns(Warning):
        qsys1._constructMatrices()

def test_dimensionAndOperatorCreatesMatrix():
    qsys = QuantumSystem(dimension=2, operator=sigmam)
    qsys._constructMatrices()
    assert np.allclose(qsys._firstTerm._paramBoundBase__matrix.A, sigmam(sparse=False))
