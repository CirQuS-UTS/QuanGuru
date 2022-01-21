import random
import pickle
import multiprocessing
from functools import partial
import pytest
import quanguru.classes.base as qbase #pylint: disable=import-error

qbase.named()._resetAll() # pylint:disable=protected-access

@pytest.mark.parametrize("cls", [qbase.named, qbase.qBase])
def test_instanceNumberIncrementationsAndDefaultNames(cls, helpers):
    # resetting the numbers for the parametrization
    qbase.named()._resetAll() # pylint:disable=protected-access
    # create 5 objects and verify each number and name are correct. parametrised to be tested with child classes
    for i in range(5):
        # create an external/explicit instance
        obExternal = cls()
        # verify the number of external instances is correct
        assert obExternal._externalInstances == (i+1) # pylint:disable=protected-access
        # verify the name is correct
        assert obExternal.name == cls.label + str(cls._externalInstances) # pylint:disable=protected-access
        # verify the string repr matches name
        assert str(obExternal) == obExternal.name
        # verify that the name cannot be changed
        with pytest.raises(AttributeError):
            obExternal.name = helpers.randString(random.randint(4, 10))

        # create an internal instance
        obInternal = cls(_internal=True)
        # verify the number of internal instances is correct
        assert obInternal._internalInstances == (i+1) # pylint:disable=protected-access
        # verify the name is correct
        assert obInternal.name == "_" + cls.label + str(cls._internalInstances) # pylint:disable=protected-access
        # verify the string repr matches name
        assert str(obInternal) == obInternal.name
        # verify that the name cannot be changed
        with pytest.raises(AttributeError):
            obInternal.name = helpers.randString(random.randint(4, 10))

        # verify total numbers are correct
        assert obInternal._instances == 2*(i+1) # pylint:disable=protected-access
        assert obExternal._instances == 2*(i+1) # pylint:disable=protected-access
        assert qbase.named._totalNumberOfInst == 2*(i+1) # pylint:disable=protected-access
    qbase.named()._resetAll() # pylint:disable=protected-access

def _aliasAddSub(aobj, astrings, rsFunc):
    # created for test_addingAliasInNamedOrChildInstances
    # tests getByNameOrAlias and equality of name to any string in aliases
    # reach by its name, name.name, and any alias
    for s in [aobj.name, aobj.name.name, *astrings]:
        assert aobj.name == s
        assert aobj.getByNameOrAlias(s) is aobj
    
    # some random str does not work
    with pytest.raises(ValueError):
        aobj.getByNameOrAlias(rsFunc(random.randint(1, 10)))

def _createWithoutAlias(cls, stri, rsFunc):
    # created for test_addingAliasInNamedOrChildInstances
    # create two objects without any alias
    obj1 = cls(_internal=bool(random.randint(0,1)))
    # run the sub-routine
    _aliasAddSub(obj1, [], rsFunc)
    obj2 = cls(_internal=bool(random.randint(0,1)))
    # run the sub-routine
    _aliasAddSub(obj2, [], rsFunc)
    return obj1, obj2

def _createWithAlias(cls, stri, rsFunc):
    # created for test_addingAliasInNamedOrChildInstances
    # create with a list of aliases
    obj3 = cls(_internal=bool(random.randint(0,1)), alias=stri[0:2])
    # run the sub-routine
    _aliasAddSub(obj3, stri[0:2], rsFunc)
    # create with a single alias
    obj4 = cls(_internal=bool(random.randint(0,1)), alias=stri[2])
    # run the sub-routine
    _aliasAddSub(obj4, [stri[2]], rsFunc)
    return obj3, obj4

@pytest.mark.parametrize("cls, reset", [
                         [qbase.named, True], [qbase.qBase, True],
                         [qbase.named, False], [qbase.qBase, False]
                         ])
def test_addingAliasInNamedOrChildInstances(cls, reset, helpers):
    # adding alias to an instance of named class and reaching it using its name or an alias by using getByNameOrAlias
    # method, which raises an error if the given name/alias does not belong to any object
    createFuncList = [_createWithoutAlias, _createWithAlias]
    for i in range(2):
        if reset:
            qbase.named()._resetAll() # pylint:disable=protected-access
        strings2 = helpers.randStringList(9)

        ob1, ob2 = createFuncList[i](cls, strings2, helpers.randString)
        ob3, ob4 = createFuncList[(i+1)%2](cls, strings2, helpers.randString)
        
        # add a list of alias
        ob1.alias = strings2[3]
        ob2.alias = strings2[4:6]
        ob3.alias = strings2[6]
        ob4.alias = strings2[7:]

        # make sure you cannot add an existing alias to another object
        with pytest.raises(ValueError):
            ob2.alias = strings2[0]

        # make sure you cannot add an existing alias to another object
        with pytest.raises(ValueError):
            ob4.alias = strings2[0:2]

    # reset to uncouple tests
    qbase.named()._resetAll() # pylint:disable=protected-access

def forMultiProcessingTest(obj, strings, i):
    # used in the below multiprocessing test to check you can get the object by its name alias etc. during multiprocess
    setattr(obj, "_internal", i)
    obj.alias = strings[0: random.randint(1, len(strings)-1)]
    assert obj.getByNameOrAlias(obj.name) is obj
    assert obj.getByNameOrAlias(obj.alias[random.randint(0, len(obj.alias)-1)]) is obj
    assert obj.getByNameOrAlias(obj.name)._internal == obj._internal

@pytest.mark.parametrize("cls", [qbase.named, qbase.qBase])
def test_getByNameOrAliasWithMultiProcessing(cls, helpers):
    strings = helpers.randStringList()
    # first make sure that the object properly pickles. the equality is satisfied just by looking at their names, since
    # the names are unique
    ob = cls(_internal=False, alias=[helpers.randString(random.randint(3, 10)), helpers.randString(random.randint(3, 10))])
    obp = pickle.dumps(ob)
    ob1 = pickle.loads(obp)
    assert ob1.name == ob.name
    assert ob1.alias == ob.alias
    # create a pool and call forMultiProcessingTest in the map
    _pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1)
    _pool.map(partial(partial(forMultiProcessingTest, ob), strings), range(5), chunksize=1)
    _pool.close()
    _pool.join()
    qbase.named()._resetAll() # pylint:disable=protected-access
