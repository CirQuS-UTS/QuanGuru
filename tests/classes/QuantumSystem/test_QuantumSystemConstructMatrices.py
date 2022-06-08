import pytest
import random as rnd
import numpy as np
from quanguru.classes.QSystem import QuantumSystem
from quanguru.QuantumToolbox.operators import sigmam, destroy
from quanguru.QuantumToolbox import compositeOp

def test_arbitraryCompositeOperatorStorageAndCreation():
    dim1, dim2, dim3 = rnd.randint(3, 10), rnd.randint(3, 10), rnd.randint(3, 10)
    qsys1 = QuantumSystem(dimension=dim1)
    qsys1._compositeOperator = destroy
    assert np.allclose(qsys1._compositeOperator[destroy].A, destroy(dim1).A)
    qsys1.dimension = dim2
    assert np.allclose(qsys1._compositeOperator[destroy].A, destroy(dim2).A)
    qsys1.dimension = 2*dim1
    assert np.allclose(qsys1._compositeOperator[destroy].A, destroy(2*dim1).A)
    qsys2 = QuantumSystem(dimension=dim2)
    compSys = qsys2 + qsys1
    assert np.allclose(qsys1._compositeOperator[destroy].A, compositeOp(destroy(2*dim1), dimB=dim2, dimA=1).A)
    qsys1.dimension = dim1
    compSys += QuantumSystem(dimension=dim3)
    assert np.allclose(qsys1._compositeOperator[destroy].A, compositeOp(destroy(dim1), dimB=dim2, dimA=dim3).A)
    compSys -= qsys2
    assert np.allclose(qsys1._compositeOperator[destroy].A, compositeOp(destroy(dim1), dimB=1, dimA=dim3).A)


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
