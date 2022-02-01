import random
import pytest
import quanguru.classes.QSimBase as QSimBase #pylint: disable=import-error

def _parameterClassTestSub(ob, v1, v2, bo):
    assert ob.value == v1
    assert ob._value == v2
    assert ob._bound is bo

def test_parameterClass(helpers):
    # this is to test _parameter class
    # create 5 parameter instance of _parameter in various combinations
    # bound 4 of them and test the value, _value, and _bound
    strings = helpers.randStringList(7,8) 

    p0 = QSimBase._parameter()
    _parameterClassTestSub(p0, None, None, None)

    p1 = QSimBase._parameter(value=strings[0])
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p0, None, None, None)

    p2 = QSimBase._parameter(value=strings[1], _bound=p1)
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p2, strings[0], strings[1], p1)
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)

    p3 = QSimBase._parameter(value=strings[2], _bound=p2)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p2, strings[0], strings[1], p1)
    _parameterClassTestSub(p3, strings[0], strings[2], p2)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p2, strings[0], strings[1], p1)

    p4 = QSimBase._parameter()
    p4.value = strings[3]
    p4._bound = p3
    _parameterClassTestSub(p4, strings[0], strings[3], p3)

    # test the breaking of bound by setting a value
    p2.value = strings[4]
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p2, strings[4], strings[4], False)
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)

    _parameterClassTestSub(p3, strings[4], strings[2], p2)
    _parameterClassTestSub(p4, strings[4], strings[3], p3)

    p3.value = strings[5]
    _parameterClassTestSub(p2, strings[4], strings[4], False)
    _parameterClassTestSub(p3, strings[5], strings[5], False)
    _parameterClassTestSub(p4, strings[5], strings[3], p3)

    p4.value = strings[6]
    _parameterClassTestSub(p3, strings[5], strings[5], False)
    _parameterClassTestSub(p4, strings[6], strings[6], False)

def test_paramBoundBaseCreateBreakBound():
    # should work only with other paramBoundBase objects
    pb1 = QSimBase.paramBoundBase()
    pb2 = QSimBase.paramBoundBase()

    # _paramBound does not have a getter
    with pytest.raises(AttributeError):
        pbAR1 = QSimBase.paramBoundBase(_paramBound=pb1)
    with pytest.raises(AttributeError):
        pb2._paramBound = pb1

    # cannot bound with self
    with pytest.raises(ValueError):
        pb1._createParamBound(pb1)

    with pytest.raises(ValueError):
        pb2._createParamBound(pb2)

    # create a bound and verify
    pb2._createParamBound(pb1)
    assert pb1 in pb2._paramBoundBase__paramBound.values()
    assert pb1 in pb2._paramBound.values()

    # break the bound and verify
    pb2._breakParamBound(pb1)
    assert pb1 not in pb2._paramBoundBase__paramBound.values()
    assert pb1 not in pb2._paramBound.values()

def test_paramBoundBaseCreateBreakBoundWithList(helpers):
    # create some paramBound objects
    # and create and break the bounds by giving list of objects
    pbObj = [QSimBase.paramBoundBase() for ind in range(6)]
    assert all(pbObj[ind]._paramBound == {} for ind in range(6))

    riSmaller = random.randint(1, 4)
    riBigger = random.randint(riSmaller, 6)

    added = pbObj[riSmaller:riBigger]
    notAdded = [po for po in pbObj if po not in added]

    pbObj[0]._createParamBound(added)

    assert all(po in pbObj[0]._paramBound.values() for po in added)
    assert all(po not in pbObj[0]._paramBound.values() for po in notAdded)
    

def test_paramBoundBaseParamUpdated():
    # should work only with other paramBoundBase objects
    pb1 = QSimBase.paramBoundBase()
    assert pb1._paramUpdated is True
    pb2 = QSimBase.paramBoundBase()
    assert pb2._paramUpdated is True

    pb2._paramUpdated = False
    assert pb2._paramUpdated is False
    assert pb1._paramUpdated is True

    pb2._createParamBound(pb1)
    
    pb2._paramUpdated = False
    assert pb2._paramUpdated is False
    assert pb1._paramUpdated is False

    pb2._breakParamBound(pb1)

    pb2._paramUpdated = True
    assert pb2._paramUpdated is True
    assert pb1._paramUpdated is False

def test_paramBoundDelMatrices(helpers):
    # create some paramBound objects
    # store something in their _paramBoundBase__matrix
    # _createParamBound or addSubSys, then delMatrices through one
    strings = helpers.randStringList(7,8) 
    pbObj = [QSimBase.paramBoundBase() for ind in range(6)]
    assert all(pbObj[ind]._paramBoundBase__matrix == None for ind in range(6))
    for ind in range(6):
        pbObj[ind]._paramBoundBase__matrix = strings[ind]
    assert all(pbObj[ind]._paramBoundBase__matrix == strings[ind] for ind in range(6))
    pbObj[0].addSubSys(pbObj[1:3])
    pbObj[0]._createParamBound(pbObj[3:6])
    assert all(pbObj[ind]._paramBoundBase__matrix == strings[ind] for ind in range(6))
    pbObj[0].delMatrices()
    assert all(pbObj[ind]._paramBoundBase__matrix == None for ind in range(6))
