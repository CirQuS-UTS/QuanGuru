import random
import string
import pickle
import multiprocessing
from functools import partial
from attr import s
import pytest
import quanguru.classes.base as qbase #pylint: disable=import-error

qbase.named()._resetAll() # pylint:disable=protected-access

def randString(N):
    return str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N)))

strings = [randString(random.randint(1, 10)) for _ in range(random.randint(4, 10))]

@pytest.mark.parametrize("cls", [qbase.named, qbase.qBase])
def test_instanceNumberIncrementationsAndDefaultNames(cls):
    # resetting the numbers for the parametrization
    qbase.named()._resetAll() # pylint:disable=protected-access
    cls()._resetAll() # pylint:disable=protected-access
    # create 5 objects and verify each number and name is correct. parametrised to be tested with child classes
    for i in range(5):
        # create an external/explicit instance
        obExternal = cls()
        # verify the number of external instances is correct
        assert obExternal._externalInstances == (i+1) # pylint:disable=protected-access
        # verify the name is correct
        assert obExternal.name == cls.label + str(cls._externalInstances) # pylint:disable=protected-access
        # verify the string repr matches name
        assert str(obExternal) == obExternal.name

        # create an internal instance
        obInternal = cls(_internal=True)
        # verify the number of internal instances is correct
        assert obInternal._internalInstances == (i+1) # pylint:disable=protected-access
        # verify the name is correct
        assert obInternal.name == "_" + cls.label + str(cls._internalInstances) # pylint:disable=protected-access
        # verify the string repr matches name
        assert str(obExternal) == obExternal.name

        # verify total numbers are correct
        assert obInternal._instances == 2*(i+1) # pylint:disable=protected-access
        assert qbase.named._totalNumberOfInst == 2*(i+1) # pylint:disable=protected-access
    qbase.named()._resetAll() # pylint:disable=protected-access
    cls()._resetAll() # pylint:disable=protected-access

@pytest.mark.parametrize("cls", [qbase.named, qbase.qBase])
def test_addingAliasInNamedOrChildInstances(cls):
    # adding alias to an instance of named class and reaching it using its name or an alias by using getByNameOrAlias
    # method, which raises an error if the given name/alias does not belong to any object
    for i in range(2):
        obj = cls(_internal=bool(i))
        obd = cls(_internal=bool(i))
        strings2 = [randString(random.randint(1, 10)) for _ in range(random.randint(4, 10))]
        # add a list of alias
        obj.alias = strings2[0:-1]
        # make sure you cannot add an exisiting alias to another object
        with pytest.raises(ValueError):
            obd.alias = strings2[0]
        # reach by its name, name.name, and any alias
        for s in [obj.name, obj.name.name, *strings2[0:-1]]:
            assert obj.name == s
            assert obj.getByNameOrAlias(s) is obj
        # some random str does not work
        with pytest.raises(ValueError):
            obj.getByNameOrAlias(strings2[-1])
    # reset to uncouple tests
    qbase.named()._resetAll() # pylint:disable=protected-access
    cls()._resetAll() # pylint:disable=protected-access

def forMultiProcessingTest(obj, i):
    # used in the below multiprocessing test to check you can get the object by its name alias etc. during multiprocess
    setattr(obj, "_internal", i)
    obj.alias = strings[0: random.randint(1, len(strings)-1)]
    assert obj.getByNameOrAlias(obj.name) is obj
    assert obj.getByNameOrAlias(obj.alias[random.randint(0, len(obj.alias)-1)]) is obj
    assert obj.getByNameOrAlias(obj.name)._internal == obj._internal

@pytest.mark.parametrize("cls", [qbase.named, qbase.qBase])
def test_getByNameOrAliasWithMultiProcessing(cls):
    # first make sure that the object properly pickles. the equality is satisfied just by looking at their names, since
    # the names are unique
    ob = cls(_internal=False)
    ob1 = pickle.loads(pickle.dumps(ob))
    assert ob1.name == ob.name
    # create a pool and call forMultiProcessingTest in the map
    _pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1)
    _pool.map(partial(forMultiProcessingTest, ob), range(5), chunksize=1)
    _pool.close()
    _pool.join()
    qbase.named()._resetAll() # pylint:disable=protected-access
    cls()._resetAll() # pylint:disable=protected-access
