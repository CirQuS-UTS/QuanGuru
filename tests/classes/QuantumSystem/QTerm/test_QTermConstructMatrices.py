from ast import operator
import random as rnd
import numpy as np
from quanguru.QuantumToolbox.operators import Jz
from quanguru.classes.QTerms import QTerm
from quanguru.classes.QSystem import QuSystem
import quanguru as qg


def test_constructMatricesOfQTermWithSingleQSystem():
    randDims = [rnd.randint(3, 10) for _ in range(6)] 

    qsys1 = QuSystem(dimension=randDims[0], _dimsBefore=1, _dimsAfter=1)
    t1 = QTerm(qSystems=qsys1, operator=qg.number)
    assert np.allclose(t1._freeMatrix.A, qg.number(randDims[0]).A)

    qsys1 = QuSystem(dimension=randDims[1], _dimsBefore=1, _dimsAfter=1)
    t1 = QTerm(qSystems=qsys1, operator=qg.destroy)
    assert np.allclose(t1._freeMatrix.A, qg.destroy(randDims[1]).A)

    qsys1 = QuSystem(dimension=randDims[2], _dimsBefore=1, _dimsAfter=1)
    t1 = QTerm(qSystems=qsys1, operator=qg.Jx)
    assert np.allclose(t1._freeMatrix.A, qg.Jx(0.5*(randDims[2]-1)).A)

    qsys1 = QuSystem(dimension=randDims[3], _dimsBefore=1, _dimsAfter=1)
    t1 = QTerm(qSystems=qsys1, operator=qg.Jm)
    assert np.allclose(t1._freeMatrix.A, qg.Jm(0.5*(randDims[3]-1)).A)

    qsys1 = QuSystem(dimension=randDims[4], _dimsBefore=1, _dimsAfter=1)
    t1 = QTerm(qSystems=qsys1, operator=qg.sigmay)
    assert np.allclose(t1._freeMatrix.A, qg.sigmay().A)

    qsys1 = QuSystem(dimension=randDims[5], _dimsBefore=1, _dimsAfter=1)
    t1 = QTerm(qSystems=qsys1, operator=qg.sigmap)
    assert np.allclose(t1._freeMatrix.A, qg.sigmap().A)
