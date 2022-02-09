import random
import pytest
import quanguru.classes.baseClasses as baseClasses #pylint: disable=import-error

def _useTestComputeBaseFunctions(obj, *args):
    return [*args]

def test_computeBaseFunctions(helpers):
    strings = helpers.randStringList(7,8)
    #strings = ['a', 'b', 'c', 'd', 'e', 'f']
    # create two instances assign functions and test
    comp1 = baseClasses.computeBase()
    comp2 = baseClasses.computeBase()

    assert comp1._computeBase__compute(*strings[0:2]) is None
    assert comp2._computeBase__compute(*strings[0:2]) is None
    comp1.compute = _useTestComputeBaseFunctions
    assert comp1._computeBase__compute(*strings[0:2]) == strings[0:2]
    assert comp2._computeBase__compute(*strings[0:2]) is None
    
    assert comp1._computeBase__calculate('start', *strings[2:4]) is None
    assert comp2._computeBase__calculate('start', *strings[2:4]) is None
    comp1.calculateStart = _useTestComputeBaseFunctions
    assert comp1._computeBase__calculate('start', *strings[2:4]) == strings[2:4]
    assert comp2._computeBase__calculate('start', *strings[2:4]) is None

    assert comp1._computeBase__calculate('end', *strings[4:6]) is None
    assert comp2._computeBase__calculate('end', *strings[4:6]) is None
    comp1.calculateEnd = _useTestComputeBaseFunctions
    assert comp1._computeBase__calculate('end', *strings[4:6]) == strings[4:6]
    assert comp2._computeBase__calculate('end', *strings[4:6]) is None

    comp1.compute = strings[0]
    with pytest.warns(Warning):
        assert comp1._computeBase__compute(*strings[4:6]) == strings[0]

    comp1.calculateStart = strings[1]
    with pytest.warns(Warning):
        assert comp1._computeBase__calculate('start',*strings[4:6]) == strings[1]

    comp1.calculateEnd = strings[2]
    with pytest.warns(Warning):
        assert comp1._computeBase__calculate('end',*strings[4:6]) == strings[2]

def test_computeBaseAlias(helpers):
    # here alias also adds the given string alias or strings in list of aliases to the qRes
    l1 = [random.randint(1, 100), helpers.randString(5), None, helpers.randString(3)]
    cb = baseClasses.computeBase(alias=l1)
    assert cb.alias == l1
    assert cb.qRes.alias == [s+'Results' for s in [cb.name.name, l1[1], l1[3]]]
