import random
import string
import pytest
import quanguru.classes.base as base
import quanguru.classes.baseClasses as baseClasses #pylint: disable=import-error


def test_updateBaseWithDummyClass():
    # create a dummy class for testing
    class testClass:#pylint:disable=too-few-public-methods
        def __init__(self) -> None:
            super().__init__()
    
    # create an instance of the test class
    ob1 = testClass()
    # create and set an attribute to it
    attrValInit = random.randint(1, 100)
    attrValNew = random.randint(1, 100)
    setattr(ob1, "newAttribute", attrValInit)

    # add the ob1 into updateBase subSys
    s0 = baseClasses.updateBase(key='newAttribute')
    s0._qBase__subSys["testClass"] = ob1

    # assert that the current newAttribute is not changed by above actions
    assert ob1.newAttribute == attrValInit

    # change the value of this newAttribute with an updateBase
    # run the update as follows with the new value for the newAttribute
    s0._runUpdate(attrValNew)

    # assert that newAttribute is updated to attrValNew
    assert ob1.newAttribute == attrValNew

    baseClasses.updateBase._resetAll() # pylint:disable=protected-access

def test_updateBaseWithNamedObjects():
    # since we don't want this test to rely on the child classes,
    # we will update the superSys attributes of qBase instances with strings
    # but, this is not a test of superSys attribute as it is meant to hold named objects.

    # say we have the below qBase objects with the references qub1, qub2
    qub1 = base.qBase(superSys='asd')
    qub2 = base.qBase(superSys='asd')
    # and, we want to change their frequencies through a sweep or update

    # we can create an updateBase object as follows
    # by providing the reference qub1 and the name of the attribute 'superSys'
    s1 = baseClasses.updateBase(system=qub1, key='superSys')

    # you can also create an update first, and set the system and key after that
    s2 = baseClasses.updateBase()
    s2.system = qub2
    s2.key = 'superSys'

    # print the current superSys
    print(qub1.superSys, qub2.superSys)

    # run the update as follows with the new value for the superSys
    s1._runUpdate(3)
    s2._runUpdate(5)
    # print the updated/current superSys
    print(qub1.superSys, qub2.superSys)
