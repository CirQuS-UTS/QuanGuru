import pytest
import random
from itertools import permutations
import quanguru as qg

def assertHelper(lastAssigned, vals, timeBase):
    """
    Helper function to test the assertions for each test of the time parameters
    """
    if lastAssigned == 'totalTime': vals['totalTime'] = vals["stepSize"]*vals["stepCount"]
    if lastAssigned == 'stepSize': vals['stepSize'] = vals["totalTime"]/vals["stepCount"]
    if lastAssigned == 'stepCount': vals['stepCount'] = int(vals["totalTime"]/vals["stepSize"])
        
    assert timeBase._timeBase__totalTime.value == vals["totalTime"]
    assert timeBase._timeBase__stepSize.value == vals["stepSize"]
    assert timeBase._timeBase__stepCount.value == vals["stepCount"]

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

def test_calculateTimeParameterTwoDefined():
    """
    Testing all three time parameters are correctly defined when only two are manually assigned
    (The unassigned parameter should be calculated based on the values of the other two)
    """
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        tim = qg.QSimBase.timeBase()

        valsForTest = generateTestVals()

        setattr(tim, order[0], valsForTest[order[0]])
        setattr(tim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, tim)

        del tim

def test_calculateTimeParameterThreeDefined():
    """
    Testing all three time parameters are correctly defined when all three are manually assigned
    (The least recent defined parameter should be overwritten based on the two most recently defined)
    """
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of the time parameters above
    for order in permutations(timeParameters):
        tim = qg.QSimBase.timeBase()

        valsForTest = generateTestVals()

        #Assigning the third time parameter to see if it gets overwritten
        setattr(tim, order[2], valsForTest[order[2]])
        setattr(tim, order[0], valsForTest[order[0]])
        setattr(tim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, tim)

        del tim

def test_calculateTimeParameterSixDefined():
    """
    Testing all three time parameters are correctly defined when all three are manually assigned and one is assigned repeatedly
    (The least recent defined parameter should be overwritten based on the two most recently defined)
    (Only the most recent value assignment from the repeated assignment should be used)
    """
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of the time parameters above
    for order in permutations(timeParameters):
        tim = qg.QSimBase.timeBase()

        valsForTest = generateTestVals()

        setattr(tim, order[2], valsForTest[order[2]])
        setattr(tim, order[0], valsForTest[order[0]])
        setattr(tim, order[1], valsForTest[order[1]])

        #Repeated assignment of second parameter
        for i in range(3):
            if order[1] == 'totalTime': valsForTest[order[1]] = random.uniform(5, 50)
            if order[1] == 'stepCount': valsForTest[order[1]] = random.randint(5, 20)
            if order[1] == 'stepSize': valsForTest[order[1]] = random.uniform(1, 4)

            setattr(tim, order[1], valsForTest[order[1]])
            
            assertHelper(order[2], valsForTest, tim)

        del tim