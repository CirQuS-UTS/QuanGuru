import pytest
import random
from itertools import permutations
import quanguru as qg

def assertHelper(lastAssigned, vals, timeBase):
    if lastAssigned == 'totalTime': vals['totalTime'] = vals["stepSize"]*vals["stepCount"]
    if lastAssigned == 'stepSize': vals['stepSize'] = vals["totalTime"]/vals["stepCount"]
    if lastAssigned == 'stepCount': vals['stepCount'] = int(vals["totalTime"]/vals["stepSize"])
        
    assert timeBase._timeBase__totalTime.value == vals["totalTime"]
    assert timeBase._timeBase__stepSize.value == vals["stepSize"]
    assert timeBase._timeBase__stepCount.value == vals["stepCount"]

def test_calculateThirdTimeParameterUnassigned():
    # Testing that the third time parameter out of the three is correctly calculated and assigned when only the other two are defined
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        tim = qg.QSimBase.timeBase()

        valsForTest = {
            "totalTime": random.uniform(5, 50),
            "stepCount": random.randint(5, 20),
            "stepSize": random.uniform(1, 4),
        }

        setattr(tim, order[0], valsForTest[order[0]])
        setattr(tim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, tim)

        del tim

def test_calculateThirdTimeParameterAssigned():
    # Testing that the third time parameter out of the three is correctly calculated and assigned when only the other two are defined
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        tim = qg.QSimBase.timeBase()

        valsForTest = {
            "totalTime": random.uniform(5, 50),
            "stepCount": random.randint(5, 20),
            "stepSize": random.uniform(1, 4),
        }

        #Assigning the third time parameter to see if it gets overwritten
        setattr(tim, order[2], valsForTest[order[2]])
        setattr(tim, order[0], valsForTest[order[0]])
        setattr(tim, order[1], valsForTest[order[1]])

        assertHelper(order[2], valsForTest, tim)

        del tim

def test_calculateThirdTimeParameterRepeatedAssignment():
    # Testing that the third time parameter out of the three is correctly calculated and assigned when only the other two are defined
    timeParameters = ['totalTime', 'stepSize', 'stepCount']

    # Assign time parameters in the order of every permutation of two of the time parameters above
    for order in permutations(timeParameters):
        tim = qg.QSimBase.timeBase()

        valsForTest = {
            "totalTime": random.uniform(5, 50),
            "stepCount": random.randint(5, 20),
            "stepSize": random.uniform(1, 4),
        }

        #Assigning the third time parameter to see if it gets overwritten
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

#Tests for;
# - correct timeLists from params (length, stepCount, 0 <= timeList[-1] - totalTime < stepSize)
# - timeLists being correctly calculated from JUST the last two defined timeParameters