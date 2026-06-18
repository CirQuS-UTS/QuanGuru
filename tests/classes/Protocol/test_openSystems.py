from quanguru import (
    QuantumSystem, 
    dissipatorObj,
    freeEvolution,
    Simulation,
    qProtocol,
    sigmap, sigmaz, sigmax, sigmay,
    Liouvillian,
)
from numpy import allclose, sqrt, array

def testLiouvillian():
    """Test that the Liouvillian is correctly generated for a simple system with a single dissipator."""
    QuantumSystem._resetAll()

    kappa = 1
    omega = 1
    stepSize = 0.01

    qubit = QuantumSystem(frequency=omega, operator=sigmaz, dimension=2)
    pro = qubit.simulation.protocols[0]

    diss_obj = dissipatorObj(
    system=qubit, 
    jOper=sigmap(), 
    jRate=kappa, 
    )
    diss_obj.addToProtocol(pro)

    qubit.simulation.stepSize = stepSize
    
    lioEXP = pro.unitary().toarray() 

    lioGEN = array([
        [1.        +0.j        , 0.        +0.j        ,
        0.        +0.j        , 0.00995017+0.j        ],
       [0.        +0.j        , 0.99481348+0.01989892j,
        0.        +0.j        , 0.        +0.j        ],
       [0.        +0.j        , 0.        +0.j        ,
        0.99481348-0.01989892j, 0.        +0.j        ],
       [0.        +0.j        , 0.        +0.j        ,
        0.        +0.j        , 0.99004983+0.j        ]
    ])

    assert allclose(lioEXP, lioGEN)


def testTrotterFirstOrderStepLiouvillian():
    """Test that the Liouvillian is correctly generated for a first order Trotter step (nested protocol) with a single dissipator."""

    QuantumSystem._resetAll()
    
    kappa = 1
    omega = 1
    stepSize = 0.01

    qubit = QuantumSystem(frequency=0, operator=sigmaz, dimension=2)

    qubit.createTerm(
        operator=sigmax, 
        frequency=omega/sqrt(2), 
        alias='x'
    )
    qubit.createTerm(
        operator=sigmay,
        frequency=omega/sqrt(2),
        alias='y'
    )

    step_x = freeEvolution(superSys=qubit, ratio=1/2)
    step_x.createUpdate(system=['y'], key='frequency', value=0)

    step_y = freeEvolution(superSys=qubit, ratio=1)
    step_y.createUpdate(system=['x'], key='frequency', value=0)

    diss_obj = dissipatorObj(
    system=qubit, 
    jOper=sigmap(), 
    jRate=kappa, 
    )
    diss_obj.addToProtocol(step_x)
    diss_obj.addToProtocol(step_y)

    sim = Simulation()
    pro = qProtocol(superSys=qubit, steps=[step_x, step_y], alias='trotter')
    sim.addProtocol(pro)

    sim.stepSize = stepSize
    
    lioEXP = pro.unitary().toarray()

    lioGEN = array([
        [ 9.99937907e-01-3.38813179e-21j, -7.00048345e-03-3.48687556e-03j,
        -7.00048345e-03+3.48687556e-03j,  1.49492868e-02+3.38813179e-21j],
       [ 7.05301003e-03-3.51347740e-03j,  9.92466116e-01-4.94386566e-05j,
        -3.71467532e-05+4.94386566e-05j, -6.91264873e-03+3.49593188e-03j],
       [ 7.05301003e-03+3.51347740e-03j, -3.71467532e-05-4.94386566e-05j,
         9.92466116e-01+4.94386566e-05j, -6.91264873e-03-3.49593188e-03j],
       [ 6.20933403e-05+6.77626358e-21j,  7.00048345e-03+3.48687556e-03j,
         7.00048345e-03-3.48687556e-03j,  9.85050713e-01-6.77626358e-21j]
    ])

    assert allclose(lioEXP, lioGEN)

def testTrotterSecondOrderStepLiouvillian():
    """Test that the Liouvillian is correctly generated for a second order Trotter step (nested protocol with a copyStep) with a single dissipator."""

    QuantumSystem._resetAll()
    
    kappa = 1
    omega = 1
    stepSize = 0.01

    qubit = QuantumSystem(frequency=0, operator=sigmaz, dimension=2)

    qubit.createTerm(
        operator=sigmax, 
        frequency=omega/sqrt(2), 
        alias='x'
    )
    qubit.createTerm(
        operator=sigmay,
        frequency=omega/sqrt(2),
        alias='y'
    )

    step_x = freeEvolution(superSys=qubit, ratio=1/2)
    step_x.createUpdate(system=['y'], key='frequency', value=0)

    step_y = freeEvolution(superSys=qubit, ratio=1)
    step_y.createUpdate(system=['x'], key='frequency', value=0)

    diss_obj = dissipatorObj(
    system=qubit, 
    jOper=sigmap(), 
    jRate=kappa, 
    )
    diss_obj.addToProtocol(step_x)
    diss_obj.addToProtocol(step_y)

    sim = Simulation()
    pro = qProtocol(superSys=qubit, steps=[step_x, step_y, step_x], alias='trotter')
    sim.addProtocol(pro)

    sim.stepSize = stepSize
    
    lioEXP = pro.unitary().toarray()

    lioGEN = array([
        [ 9.99900998e-01-3.38808954e-21j, -6.96539411e-03-6.96526438e-03j,
        -6.96539411e-03+6.96526438e-03j,  1.98989300e-02+6.75932310e-21j],
       [ 7.03539953e-03-7.03526849e-03j,  9.89951121e-01-1.35525272e-20j,
        -1.25597782e-07+9.86304287e-05j, -6.89538869e-03+6.89526026e-03j],
       [ 7.03539953e-03+7.03526849e-03j, -1.25597782e-07-9.86304287e-05j,
         9.89951121e-01-3.38813179e-21j, -6.89538869e-03-6.89526026e-03j],
       [ 9.90016927e-05+6.77622133e-21j,  6.96539411e-03+6.96526438e-03j,
         6.96539411e-03-6.96526438e-03j,  9.80101070e-01-1.01474549e-20j]
    ])

    assert allclose(lioEXP, lioGEN)