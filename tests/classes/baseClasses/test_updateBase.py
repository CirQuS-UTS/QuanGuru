import random
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

def test_updateBaseWithNamedObjectsDirectly(helpers):
    # since we don't want this test to rely on the child classes,
    # we will update the superSys attributes of qBase instances with strings
    # but, this is not a test of superSys attribute as it is meant to hold named objects.

    randStrings = helpers.randStringList(4,5)

    # say we have the below qBase objects with the references qub1, qub2
    qub1 = base.qBase(superSys=randStrings[0])
    qub2 = base.qBase(superSys=randStrings[1])
    # and, we want to change their superSys through a sweep or update

    # we can create an updateBase object as follows
    # by providing the reference qub1 and the name of the attribute 'superSys'
    s1 = baseClasses.updateBase(system=qub1, key='superSys')

    # you can also create an update first, and set the system and key after that
    s2 = baseClasses.updateBase()
    s2.system = qub2
    s2.key = 'superSys'

    # assert the current superSys
    assert qub1.superSys == randStrings[0]
    assert qub2.superSys == randStrings[1]

    # run the update with the new value for the superSys
    s1._runUpdate(randStrings[2])
    # assert that this changes the value for qub1, and does not affect qub2
    assert qub1.superSys == randStrings[2] 
    assert qub2.superSys == randStrings[1]

    s2._runUpdate(randStrings[-1])
    # assert that the superSys is updated
    assert qub1.superSys == randStrings[2] 
    assert qub2.superSys == randStrings[-1]

    baseClasses.updateBase._resetAll() # pylint:disable=protected-access

def test_updateBaseWithNamedObjectsUsingAlias(helpers):
    # since we don't want this test to rely on the child classes,
    # we will update the superSys attributes of qBase instances with strings
    # but, this is not a test of superSys attribute as it is meant to hold named objects.

    # testing both name/alias access and updating the same value for multiple objects simultaneous

    # create some random strings
    randStrings = helpers.randStringList(4,5)
    randAlias = helpers.randString(5)
    randAliases = helpers.randStringList(4,5)

    # say we have the below qBase objects with the references qub1, qub2, qub3
    qub1 = base.qBase(superSys=randStrings[0])
    qub2 = base.qBase(superSys=randStrings[1], alias=randAlias)
    qub3 = base.qBase(superSys=randStrings[1], alias=randAliases)
    # and, we want to change their superSys through a sweep or update

    # we can create an updateBase object as follows
    # by providing either their names and/or aliases
    s1 = baseClasses.updateBase(system=['qBase1', randAlias], key='superSys')
    # add qub3 after instantiation
    s1.system = randAliases[-1]  # this does not remove/replace the existing list, but adds the qub3 into it

    # assert the current superSys
    assert qub1.superSys == randStrings[0]
    assert qub2.superSys == randStrings[1]
    assert qub3.superSys == randStrings[1]

    # run the update with the new value for the superSys
    s1._runUpdate(randStrings[-1])
    # assert that superSys is updated
    assert qub1.superSys == randStrings[-1]
    assert qub2.superSys == randStrings[-1]
    assert qub3.superSys == randStrings[-1]

    baseClasses.updateBase._resetAll() # pylint:disable=protected-access

def test_updateBaseWithAuxiliaryClass():
    # let's create a qBase, and store something in auxObj
    qa = base.qBase()
    randInt1 = random.randint(1, 100)
    randInt2 = random.randint(1, 100)
    qa.auxObj.someAuxInfo = randInt1

    s4 = baseClasses.updateBase(system=qa.auxObj, key='someAuxInfo')

    # assert the current someAuxInfo
    assert qa.auxObj.someAuxInfo == randInt1
    # run the update with the new value for the someAuxInfo
    s4._runUpdate(randInt2)
    # assert that the someAuxInfo is updated
    assert qa.auxObj.someAuxInfo == randInt2

def test_updateBaseWithAuxDict():
    randInt1 = random.randint(1, 100)
    randInt2 = random.randint(1, 100)
    # let's create a qBase, and store something in aux dictionary
    qa = base.qBase()
    qa.auxDict['some key'] = randInt1

    # let's create a updateBase, but this time we won't give system, but set _aux to True
    s5 = baseClasses.updateBase(_aux=True, key='some key')
    # assert the current value of aux['some key']
    assert qa.auxDict['some key'] == randInt1
    # run the update with the new value for the aux['some key']
    s5._runUpdate(randInt2)
    # assert that the aux['some key'] is updated 
    assert qa.auxDict['some key'] == randInt2
