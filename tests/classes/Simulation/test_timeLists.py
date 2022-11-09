import pytest
import random
from itertools import permutations
import quanguru as qg

def assertHelper(lastAssigned, vals, timeList):
    if lastAssigned == 'totalTime': vals['totalTime'] = vals["stepSize"]*vals["stepCount"]
    if lastAssigned == 'stepSize': vals['stepSize'] = vals["totalTime"]/vals["stepCount"]
    if lastAssigned == 'stepCount': vals['stepCount'] = int(vals["totalTime"]/vals["stepSize"])
    
    assert len(timeList) == vals['stepCount'] + 1
    assert timeList[1] == vals['stepSize']
    assert 0 <= vals['totalTime'] - timeList[-1]
    assert abs(vals['totalTime'] - timeList[-1]) < vals['stepSize']

def test_calculateTimeListTwoDefined():
    # Testing that the third time parameter out of the three is correctly calculated and assigned when only the other two are defined
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        sim = qg.Simulation()

        valsForTest = {
            "totalTime": random.uniform(5, 50),
            "stepCount": random.randint(5, 20),
            "stepSize": random.uniform(1, 4),
        }

        setattr(sim, order[0], valsForTest[order[0]])
        setattr(sim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, sim.timeList)

        del sim

def test_calculateTimeListThreeDefined():
    # Testing that the third time parameter out of the three is correctly calculated and assigned when only the other two are defined
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        sim = qg.Simulation()

        valsForTest = {
            "totalTime": random.uniform(5, 50),
            "stepCount": random.randint(5, 20),
            "stepSize": random.uniform(1, 4),
        }

        setattr(sim, order[2], valsForTest[order[2]])
        setattr(sim, order[0], valsForTest[order[0]])
        setattr(sim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, sim.timeList)

        del sim

def test_calculateTimeListSixDefined():
    # Testing that the third time parameter out of the three is correctly calculated and assigned when only the other two are defined
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        sim = qg.Simulation()

        valsForTest = {
            "totalTime": random.uniform(5, 50),
            "stepCount": random.randint(5, 20),
            "stepSize": random.uniform(1, 4),
        }

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