import random as rnd
import numpy as np
import quanguru as qg

def test_copyMultiBodyCoupledCompositeSystem():
    spinJ = rnd.randint(1, 8)/2
    thirdDim = rnd.randint(2, 10)

    qubit = qg.Qubit(frequency=10*rnd.random(), alias='subSys1')
    spin2 = qg.Spin(jValue=spinJ, frequency=10*rnd.random(), order=rnd.randint(1, 4), alias='subSys2')
    third = qg.QuantumSystem(dimension=thirdDim, frequency=10*rnd.random(), operator=qg.number, alias='subSys3')

    qComp = qubit + spin2 + third # order of this sum is important. It maps to the order of identity and other operators above

    qComp.createTerm(frequency=10*rnd.random(), 
                     operator=(qg.sigmap, qg.Jx, qg.Jy, qg.destroy, qg.create),
                     order=(rnd.randint(1, 4), rnd.randint(1, 4), rnd.randint(1, 4), rnd.randint(1, 4), rnd.randint(1, 4)),
                     qSystem=(qubit, spin2, spin2, third, third))

    copySys = qComp.copy()

    assert np.allclose(copySys.totalHamiltonian.A, qComp.totalHamiltonian.A)
