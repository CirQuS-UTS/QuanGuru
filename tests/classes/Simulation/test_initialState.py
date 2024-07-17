import pytest
from numpy import array, allclose
import quanguru as qg

def test_ketInitialStateInOpenSystem():
    """
    Testing that in an open system simulation, an initial state as a ket will be converted into a density matrix
    """
    sim = qg.Simulation()
    sim.stepCount = 1
    sim.stepSize = 1

    sys = qg.QuantumSystem(dimension=5)

    func = func = lambda self, collapseOps, decayRate: qg.identity(5)
    pro = qg.qProtocol(system=sys, createUnitary=func)
    diss = qg.dissipatorObj(system=sys, jOper=qg.identity(5), jRate=1)
    diss.addToProtocol(pro)

    sim.addProtocol(pro)
    sim.initialStateSystem = sys
    sim.initialState = array(
        [[0.        ],
        [0.18257419],
        [0.36514837],
        [0.54772256],
        [0.73029674]]
    )

    sim.run()

    test_state = array(
        [[0.        , 0.        , 0.        , 0.        , 0.        ],
        [0.        , 0.03333333, 0.06666667, 0.1       , 0.13333334],
        [0.        , 0.06666667, 0.13333333, 0.2       , 0.26666666],
        [0.        , 0.1       , 0.2       , 0.3       , 0.4       ],
        [0.        , 0.13333334, 0.26666666, 0.4       , 0.53333333]]
    )

    assert allclose(pro._genericProtocol__currentState, test_state)

def test_densityMatrixInitialStateInOpenSystem():
    """
    Testing that a density matrix set as the intial state does not get altered in preparing the simulation for an open system simulation
    """
    sim = qg.Simulation()
    sim.stepCount = 1
    sim.stepSize = 1

    sys = qg.QuantumSystem(dimension=5)

    func = func = lambda self, collapseOps, decayRate: qg.identity(5)
    pro = qg.qProtocol(system=sys, createUnitary=func)
    diss = qg.dissipatorObj(system=sys, jOper=qg.identity(5), jRate=1)
    diss.addToProtocol(pro)

    sim.addProtocol(pro)
    sim.initialStateSystem = sys
    sim.initialState = array(
        [[ 1.,  2.,  3.,  4.,  5.],
        [ 2.,  4.,  6.,  8., 10.],
        [ 3.,  6.,  9., 12., 15.],
        [ 4.,  8., 12., 16., 20.],
        [ 5., 10., 15., 20., 25.]]
    )

    sim.run()

    test_state = array(
        [[ 1.,  2.,  3.,  4.,  5.],
        [ 2.,  4.,  6.,  8., 10.],
        [ 3.,  6.,  9., 12., 15.],
        [ 4.,  8., 12., 16., 20.],
        [ 5., 10., 15., 20., 25.]]
    )

    assert allclose(pro._genericProtocol__currentState, test_state)

def test_nonAllowedInitialStateInOpenSystem():
    """
    Testing that an initial state that is neither a density matrix or ket will raise an error
    """
    sim = qg.Simulation()
    sim.stepCount = 1
    sim.stepSize = 1

    sys = qg.QuantumSystem(dimension=5)

    func = func = lambda self, collapseOps, decayRate: qg.identity(5)
    pro = qg.qProtocol(system=sys, createUnitary=func)
    diss = qg.dissipatorObj(system=sys, jOper=qg.identity(5), jRate=1)
    diss.addToProtocol(pro)

    sim.addProtocol(pro)
    sim.initialStateSystem = sys
    sim.initialState = array(
        [[1., 1.],
        [1., 1.],
        [1., 1.],
        [1., 1.],
        [1., 1.]]
    )

    errorStr = ''

    try:
        sim.run()
    except ValueError as e:
        errorStr = str(e)
    
    assert errorStr == "Initial state should be a ket (shape = (n, 1)) or density matrix (shape = (shape = (n, n))) for an open system simulation"

def test_1dKetInitialStateInOpenSystem():
    """
    Testing that an initial state that is a 1d vector (i.e. shape = (n)) will be converted into a 2d vector (shape = (n, 1))
    """
    sim = qg.Simulation()
    sim.stepCount = 1
    sim.stepSize = 1

    sys = qg.QuantumSystem(dimension=5)

    func = func = lambda self, collapseOps, decayRate: qg.identity(5)
    pro = qg.qProtocol(system=sys, createUnitary=func)

    sim.addProtocol(pro)
    sim.initialStateSystem = sys
    sim.initialState = array(
        [1., 2., 3., 4., 5.]
    )

    sim.run()

    test_state = array(
        [[ 1.,  2.,  3.,  4.,  5.],
        [ 2.,  4.,  6.,  8., 10.],
        [ 3.,  6.,  9., 12., 15.],
        [ 4.,  8., 12., 16., 20.],
        [ 5., 10., 15., 20., 25.]]
    )

    assert allclose(pro._genericProtocol__currentState, test_state)

def test_initialStateClosedSystem():
    """
    Testing that any state is accepted as the initial state in a closed system simulation
    """
    sim = qg.Simulation()
    sim.stepCount = 1
    sim.stepSize = 1

    sys = qg.QuantumSystem(dimension=5)

    func = func = lambda self, collapseOps, decayRate: qg.identity(5)
    pro = qg.qProtocol(system=sys, createUnitary=func)

    sim.addProtocol(pro)
    sim.initialStateSystem = sys

    initial_states = [
        array(
            [[0.        ],
            [0.18257419],
            [0.36514837],
            [0.54772256],
            [0.73029674]]
        ),
        array(
            [[1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.]]
        ,
        ),
        array(
            [[1., 1.],
            [1., 1.],
            [1., 1.],
            [1., 1.],
            [1., 1.]]
        ),
        array(
            [1., 2., 3., 4., 5.]
        ),
    ]

    final_states = [
        array(
            [[0.        ],
            [0.18257419],
            [0.36514837],
            [0.54772256],
            [0.73029674]]
        ),
        array(
            [[1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.],
            [1., 1., 1., 1., 1.]]
        ,
        ),
        array(
            [[1., 1.],
            [1., 1.],
            [1., 1.],
            [1., 1.],
            [1., 1.]]
        ),
        array(
            [1., 2., 3., 4., 5.]
        ),
    ]

    for initial_state, final_state in initial_states:
        sim.initialState = initial_state
        sim.run()
        assert allclose(pro._genericProtocol__currentState, final_state)

def assertHelper(lastAssigned, vals, timeList):
    """
    Helper function to test the timelists have the correct:
        - length
        - stepSize
        - final time step is smaller than the total time
        - final time step is within one step of the total time
    """
    if lastAssigned == 'totalTime': vals['totalTime'] = vals["stepSize"]*vals["stepCount"]
    if lastAssigned == 'stepSize': vals['stepSize'] = vals["totalTime"]/vals["stepCount"]
    if lastAssigned == 'stepCount': vals['stepCount'] = int(vals["totalTime"]/vals["stepSize"])
    
    assert len(timeList) == vals['stepCount'] + 1
    assert timeList[1] == vals['stepSize']
    assert -1e-9 <= vals['totalTime'] - timeList[-1]
    assert abs(vals['totalTime'] - timeList[-1]) < vals['stepSize']

def generateTestVals():
    """
    Helper function to generate random test values for the time parameters
    """
    valsForTest = {
        "totalTime": round(random.uniform(5, 50), 2),
        "stepCount": random.randint(5, 20),
        "stepSize": round(random.uniform(1, 4), 2),
    }
    return valsForTest

def test_calculateTimeListTwoDefined():
    """
    Testing that the time list is correctly defined when only two are manually assigned
    """
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        sim = qg.Simulation()

        valsForTest = generateTestVals()

        setattr(sim, order[0], valsForTest[order[0]])
        setattr(sim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, sim.timeList)

        del sim

def test_calculateTimeListThreeDefined():
    """
    Testing that the time list is correctly defined when all three are manually assigned
    """
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of the time parameters above
    for order in permutations(timeParameters):
        sim = qg.Simulation()

        valsForTest = generateTestVals()

        setattr(sim, order[2], valsForTest[order[2]])
        setattr(sim, order[0], valsForTest[order[0]])
        setattr(sim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, sim.timeList)

        del sim

def test_calculateTimeListSixDefined():
    """
    Testing all three time parameters are correctly defined when all three are manually assigned and one is assigned repeatedly
    """
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of the time parameters above
    for order in permutations(timeParameters):
        sim = qg.Simulation()

        valsForTest = generateTestVals()

        setattr(sim, order[2], valsForTest[order[2]])
        setattr(sim, order[0], valsForTest[order[0]])
        setattr(sim, order[1], valsForTest[order[1]])

        #Repeated assignment of second parameter
        for i in range(3):
            if order[1] == 'totalTime': valsForTest[order[1]] = random.uniform(5, 50)
            if order[1] == 'stepCount': valsForTest[order[1]] = random.randint(5, 20)
            if order[1] == 'stepSize': valsForTest[order[1]] = random.uniform(1, 4)

            setattr(sim, order[1], valsForTest[order[1]])
            
        assertHelper(order[2], valsForTest, sim.timeList)
            
        del sim