import pytest
import random as rnd
import numpy as np
from quanguru.classes.baseClasses import paramBoundBase #pylint: disable=import-error
from quanguru.QuantumToolbox.operators import destroy, create, Jx
from quanguru.QuantumToolbox.linearAlgebra import hc

@pytest.mark.parametrize('oper', [destroy, create, Jx])
def test_HermitianConjuageOfMatrix(oper):
    p1 = paramBoundBase()
    p1._paramBoundBase__matrix = oper(rnd.randint(3, 10))
    assert np.allclose(p1._hc.A, hc(p1._paramBoundBase__matrix).A)
    p1._paramBoundBase__matrix = oper(rnd.randint(3, 10))
    assert np.allclose(p1._hc.A, hc(p1._paramBoundBase__matrix).A)
