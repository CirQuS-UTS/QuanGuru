import random
import quanguru.classes.baseClasses as baseClasses #pylint: disable=import-error

def _parameterClassTestSub(ob, v1, v2, bo):
    assert ob.value == v1
    assert ob._value == v2
    assert ob._bound is bo

def test_parameterClass(helpers):
    # this is to test _parameter class
    # create 5 parameter instance of _parameter in various combinations
    # bound 4 of them and test the value, _value, and _bound
    strings = helpers.randStringList(7,8) 

    p0 = baseClasses._parameter()
    _parameterClassTestSub(p0, None, None, None)

    p1 = baseClasses._parameter(value=strings[0])
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p0, None, None, None)

    p2 = baseClasses._parameter(value=strings[1], _bound=p1)
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p2, strings[0], strings[1], p1)
    _parameterClassTestSub(p0, None, None, None)
    _parameterClassTestSub(p1, strings[0], strings[0], None)

    p3 = baseClasses._parameter(value=strings[2], _bound=p2)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p2, strings[0], strings[1], p1)
    _parameterClassTestSub(p3, strings[0], strings[2], p2)
    _parameterClassTestSub(p1, strings[0], strings[0], None)
    _parameterClassTestSub(p2, strings[0], strings[1], p1)

    p4 = baseClasses._parameter()
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