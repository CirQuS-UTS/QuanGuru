import pytest
import random
from itertools import permutations
import quanguru as qg

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

def test_currentTimeOnSweep():

    out = []

    sim = qg.Simulation()
    sim.totalTime = 1
    sim.stepSize = 0.5

    sys = qg.QuantumSystem(dimension=2, operator=qg.identity, frequency=1)

    sim.addQSystems(sys)

    some_sweep = sim.Sweep.createSweep(
        system=sys, 
        sweepKey='attribute', 
        sweepMin=0, 
        sweepMax=1, 
        sweepStep=0.5
    )

    def compute(sim, state):
        out.append(sim._currentTime)

    sim.compute = compute

    sim.initialStateSystem = sys
    sim.initialState = qg.basis(2, 0)

    sim.run()

    assert out == [0, 0.5, 1.0]*3

def test_stepCountAndTimeListOnSweepWithTimeDependecy():

    qub = qg.Qubit(frequency=1, alias='qubit')
    qub.initialState = qg.basis(qub.dimension, 1)

    qub.stepCount = 10
    qub.totalTime = 1

    omegaSweep = qub.simulation.timeDependency.createSweep(
    system=qub,
    sweepKey='frequency',
    sweepList=qub.timeList,
    )

    qub.run()

    assert omegaSweep.sweepList == qub.timeList






