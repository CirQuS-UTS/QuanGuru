import random as rnd
import numpy as np
from quanguru.QuantumToolbox.operators import Jz, sigmax
from quanguru.classes.QTerms import QTerm
from quanguru.classes.QSystem import QuSystem
import quanguru as qg


def test_constructMatricesOfQTermWithSingleQSystem():
    randDims = [rnd.randint(3, 10) for _ in range(6)] 

    qsys1 = QuSystem(dimension=randDims[0])
    t1 = QTerm(qSystems=qsys1, operator=qg.number)
    assert np.allclose(t1._freeMatrix.A, qg.number(randDims[0]).A)

    qsys1 = QuSystem(dimension=randDims[1])
    t1 = QTerm(qSystems=qsys1, operator=qg.destroy)
    assert np.allclose(t1._freeMatrix.A, qg.destroy(randDims[1]).A)

    qsys1 = QuSystem(dimension=randDims[2])
    t1 = QTerm(qSystems=qsys1, operator=qg.Jx)
    assert np.allclose(t1._freeMatrix.A, qg.Jx(0.5*(randDims[2]-1)).A)

    qsys1 = QuSystem(dimension=randDims[3])
    t1 = QTerm(qSystems=qsys1, operator=qg.Jm)
    assert np.allclose(t1._freeMatrix.A, qg.Jm(0.5*(randDims[3]-1)).A)

    qsys1 = QuSystem(dimension=randDims[4])
    t1 = QTerm(qSystems=qsys1, operator=qg.sigmay)
    assert np.allclose(t1._freeMatrix.A, qg.sigmay().A)

    qsys1 = QuSystem(dimension=randDims[5])
    t1 = QTerm(qSystems=qsys1, operator=qg.sigmap)
    assert np.allclose(t1._freeMatrix.A, qg.sigmap().A)

def test_constructMaticesOfQTermWithMultipleQSystem():
    randDims = [rnd.randint(3, 10) for _ in range(4)]

    qsys1 = QuSystem(dimension=randDims[0])
    qsys2 = QuSystem(dimension=randDims[1])
    qsys3 = QuSystem(dimension=2)
    qsys4 = QuSystem(dimension=2)
    qsys5 = QuSystem(dimension=randDims[2])
    qsys6 = QuSystem(dimension=randDims[3])

    compSys1 = QuSystem(subSys=[qsys1, qsys2, qsys3])
    t1 = QTerm(qSystems=[qsys1, qsys2], operator=[qg.create, qg.Jp])
    assert  np.allclose(t1._freeMatrix.A, qg.tensorProd(qg.create(randDims[0]), qg.Jp(0.5*(randDims[1]-1)), qg.identity(2)).A)

    t1 = QTerm(qSystems=[qsys3, qsys2], operator=[qg.sigmax, qg.Jp])
    assert  np.allclose(t1._freeMatrix.A, qg.tensorProd(qg.identity(randDims[0]), qg.Jp(0.5*(randDims[1]-1)), qg.sigmax()).A)

    t1 = QTerm(qSystems=[qsys1, qsys3], operator=[qg.create, qg.sigmax])
    assert  np.allclose(t1._freeMatrix.A, qg.tensorProd(qg.create(randDims[0]), qg.identity(randDims[1]), qg.sigmax()).A)

    compSys1 = QuSystem(subSys=[qsys6, qsys5, qsys4])
    t1 = QTerm(qSystems=[qsys6, qsys5, qsys4], operator=[qg.create, qg.Jp, qg.sigmax])
    assert  np.allclose(t1._freeMatrix.A, qg.tensorProd(qg.create(randDims[3]), qg.Jp(0.5*(randDims[2]-1)), qg.sigmax()).A)

    t1 = QTerm(qSystems=[qsys6, qsys4, qsys5], operator=[qg.create, qg.sigmax, qg.Jp])
    assert  np.allclose(t1._freeMatrix.A, qg.tensorProd(qg.create(randDims[3]), qg.Jp(0.5*(randDims[2]-1)), qg.sigmax()).A)

    t1 = QTerm(qSystems=[qsys5, qsys6, qsys4], operator=[qg.Jp, qg.create, qg.sigmax])
    assert  np.allclose(t1._freeMatrix.A, qg.tensorProd(qg.create(randDims[3]), qg.Jp(0.5*(randDims[2]-1)), qg.sigmax()).A)
