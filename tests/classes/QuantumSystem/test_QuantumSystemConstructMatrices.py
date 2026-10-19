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
    assert np.allclose(qsys1._compositeOperator[destroy].toarray(), destroy(dim1).toarray())
    qsys1.dimension = dim2
    assert np.allclose(qsys1._compositeOperator[destroy].toarray(), destroy(dim2).toarray())
    qsys1.dimension = 2*dim1
    assert np.allclose(qsys1._compositeOperator[destroy].toarray(), destroy(2*dim1).toarray())
    qsys2 = QuantumSystem(dimension=dim2)
    compSys = qsys2 + qsys1
    assert np.allclose(qsys1._compositeOperator[destroy].toarray(), compositeOp(destroy(2*dim1), dimB=dim2, dimA=1).toarray())
    qsys1.dimension = dim1
    compSys += QuantumSystem(dimension=dim3)
    assert np.allclose(qsys1._compositeOperator[destroy].toarray(), compositeOp(destroy(dim1), dimB=dim2, dimA=dim3).toarray())
    compSys -= qsys2
    assert np.allclose(qsys1._compositeOperator[destroy].toarray(), compositeOp(destroy(dim1), dimB=1, dimA=dim3).toarray())


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
    assert np.allclose(qsys._firstTerm._paramBoundBase__matrix.toarray(), sigmam(sparse=False))
