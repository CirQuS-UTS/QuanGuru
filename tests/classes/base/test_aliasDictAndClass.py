import random
import pickle
import string
import pytest
import qTools.classes.base as qbase #pylint: disable=import-error

def randString(N):
    return str(''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N)))

strings = [randString(random.randint(1, 10)) for _ in range(random.randint(4, 10))]

def test_aliasDictWithRegularStrings():
    # testing the aliasDict class with regular strings to see that the basic dictonary functionalities are not broken.
    alDict = qbase.aliasDict()
    # add a single item and verify
    alDict[1] = 2
    assert alDict[1] == 2
    # change the value and verify
    alDict[1] = 3
    assert alDict[1] == 3
    assert alDict[1] != 2
    # remove the item and verify
    del alDict[1]
    assert len(alDict) == 0

    # add two items and verify
    alDict[1] = 2
    alDict[1] = 1
    assert alDict[1] == 1
    alDict[2] = 3
    alDict[1] = 2
    assert alDict[1] == 2
    assert alDict[2] == 3
    # change one of them and verify
    alDict[1] = 4
    assert alDict[1] == 4
    assert alDict[1] != 2
    alDict[2] = 2
    assert alDict[2] == 2
    assert alDict[2] != 3
    # remove one and verify
    del alDict[1]
    assert len(alDict) == 1
    alDict[2] = 1
    assert len(alDict) == 1
    assert alDict[2] == 1
    assert alDict[2] != 2
    del alDict[2]
    assert len(alDict) == 0
    alDict[1] = 1
    assert len(alDict) == 1
    assert alDict[1] == 1

    # update works properly
    alDict.update(dict(zip(strings[:-1], strings[:-1])))
    for s in strings[:-1]:
        assert alDict[s] == s
    # setdefault changes value for an existing key
    randStr = randString(random.randint(4, 10))
    randInt = random.randint(0, len(alDict)-2)
    val = alDict.setdefault(strings[randInt], randStr)
    assert alDict[strings[randInt]] == val
    # setdefault creates key:value pair for a non-existing key
    # first check that the key does not exist
    with pytest.raises(KeyError):
        val = alDict[strings[-1]]
    alDict.setdefault(strings[-1], randStr)
    assert alDict[strings[-1]] == randStr

def test_aliasDictWithAliasClassAndRegularStrings(): # pylint: disable=too-many-statements
    # testing the aliasDict class with regular strings and AliasClass object keys.
    alDict = qbase.aliasDict()
    aliasObj1 = qbase.aliasClass(name=randString(random.randint(1, 10)),
                                alias=[randString(random.randint(1, 10)), randString(random.randint(1, 10))])
    aliasObj2 = qbase.aliasClass(name=randString(random.randint(1, 10)),
                                alias=[randString(random.randint(1, 10)), randString(random.randint(1, 10))])
    # add a single item and verify by using the object, its name, and each alias
    alDict[aliasObj1] = 2
    assert alDict[aliasObj1] == 2
    assert alDict[aliasObj1.name] == 2
    assert alDict[aliasObj1.alias[0]] == 2
    assert alDict[aliasObj1.alias[1]] == 2
    # change the value and verify by using the object, its name, and each alias
    alDict[aliasObj1] = 3
    assert alDict[aliasObj1] == 3
    assert alDict[aliasObj1] != 2
    alDict[aliasObj1.name] = 3
    assert alDict[aliasObj1.name] == 3
    assert alDict[aliasObj1.name] != 2
    alDict[aliasObj1.alias[0]] = 3
    assert alDict[aliasObj1.alias[0]] == 3
    assert alDict[aliasObj1.alias[0]] != 2
    alDict[aliasObj1.alias[1]] = 3
    assert alDict[aliasObj1.alias[1]] == 3
    assert alDict[aliasObj1.alias[1]] != 2
    # verify that some other aliasObj does not work
    with pytest.raises(KeyError):
        val = alDict[aliasObj2]
    # remove the item and verify by using the object, its name, and each alias
    del alDict[aliasObj1]
    assert len(alDict) == 0
    alDict[aliasObj1] = 2
    del alDict[aliasObj1.name]
    assert len(alDict) == 0
    alDict[aliasObj1] = 2
    del alDict[aliasObj1.alias[0]]
    assert len(alDict) == 0
    alDict[aliasObj1] = 2
    del alDict[aliasObj1.alias[1]]
    assert len(alDict) == 0

    # if a string key equal to the name (or an alias) of an aliasClass object already exists, alias object and its name
    # (or the alias) can be used to change the value but not any alias (or name/any other alias)
    # NOTE if there are more than one string keys in the dictonary that are in the members (tuple of its name and
    # aliases) of an aliasClass object, this changes the first key that the search method finds. For example, in an
    # ordered dict, it will change the earliest element
    assert len(alDict) == 0
    alDict[aliasObj2.name] = 2
    alDict[aliasObj1.name] = 1
    alDict[aliasObj2.alias[0]] = 1
    assert alDict[aliasObj2] == 2
    assert alDict[aliasObj2.alias[0]] == 1
    with pytest.raises(KeyError):
        val = alDict[aliasObj2.alias[1]]
    del alDict[aliasObj2]
    assert len(alDict) == 2
    del alDict[aliasObj1]
    assert len(alDict) == 1
    del alDict[aliasObj2.alias[0]]
    assert len(alDict) == 0


    # add (and change) two items and verify by using the object, its name, and each alias
    alDict[aliasObj1] = 2
    alDict[aliasObj1] = 1
    assert alDict[aliasObj1] == 1
    assert alDict[aliasObj1.name] == 1
    assert alDict[aliasObj1.alias[0]] == 1
    assert alDict[aliasObj1.alias[1]] == 1
    alDict[aliasObj2] = 3
    alDict[aliasObj1] = 2
    assert alDict[aliasObj1] == 2
    assert alDict[aliasObj1.name] == 2
    assert alDict[aliasObj1.alias[0]] == 2
    assert alDict[aliasObj1.alias[1]] == 2
    assert alDict[aliasObj2] == 3
    assert alDict[aliasObj2.name] == 3
    assert alDict[aliasObj2.alias[0]] == 3
    assert alDict[aliasObj2.alias[1]] == 3
    # remove one and verify
    del alDict[aliasObj1.name]
    assert len(alDict) == 1
    assert alDict[aliasObj2] == 3
    assert alDict[aliasObj2.name] == 3
    assert alDict[aliasObj2.alias[0]] == 3
    assert alDict[aliasObj2.alias[1]] == 3
    del alDict[aliasObj2]
    assert len(alDict) == 0

    # create a list of aliasClass objects to be used as the key and extend with strings, then shuffle
    names = [randString(random.randint(1, 10)) for _ in range(5)]
    aliases1 = [randString(random.randint(1, 10)) for _ in range(5)]
    aliases2 = [randString(random.randint(1, 10)) for _ in range(5)]
    listOfAliasObj = [qbase.aliasClass(name=names[i], alias=[aliases1[i], aliases2[i]]) for i in range(5)]
    listOfAliasObj.extend(strings)
    while True:
        random.shuffle(listOfAliasObj)
        if isinstance(listOfAliasObj[-1], qbase.aliasClass):
            break

    # create a dictionary with values are the keys
    alDict.update(dict(zip(listOfAliasObj[:-1], listOfAliasObj[:-1])))

    # check the dictonary contains the right key:value pair by directly using the objects themselves
    for s in listOfAliasObj[:-1]:
        assert alDict[s] == s

    # check if the key is an aliasClass, you can use its name or alias to get value
    for k, v  in alDict.items():
        if isinstance(k, qbase.aliasClass):
            assert alDict[k.name] == v
            assert alDict[k.alias[0]] == v
            assert alDict[k.alias[1]] == v

    # verify that setdefault works with aliasClass objs
    while True:
        randStr = randString(random.randint(4, 10))
        randInt = random.randint(0, len(alDict)-2)
        if isinstance(alDict[listOfAliasObj[randInt]], qbase.aliasClass):
            val = alDict.setdefault(listOfAliasObj[randInt], randStr)
            assert alDict[listOfAliasObj[randInt]] == val
            alDict.setdefault(listOfAliasObj[-1], randStr)
            assert alDict[listOfAliasObj[-1]] == randStr
            break

def test_aliasDictPicklingAndRepr():
    # create a list of aliasClass objects to be used as the key and extend with strings, then shuffle
    names = [randString(random.randint(1, 10)) for _ in range(5)]
    aliases1 = [randString(random.randint(1, 10)) for _ in range(5)]
    aliases2 = [randString(random.randint(1, 10)) for _ in range(5)]
    listOfAliasObj = [qbase.aliasClass(name=names[i], alias=[aliases1[i], aliases2[i]]) for i in range(5)]
    listOfAliasObj.extend(strings)
    random.shuffle(listOfAliasObj)
    # create a dictionary with values are the keys
    alDict = qbase.aliasDict()
    alDict.update(dict(zip(listOfAliasObj, listOfAliasObj)))

    aldictpicle = pickle.loads(pickle.dumps(alDict))
    assert aldictpicle == alDict
    assert eval(repr(alDict)) == alDict

def test_aliasNamingBothAtInstantiationAndAfter():
    # testing the name property of alias object.

    # 1) test two different ways of naming it:
    # a) at instantiation
    aliasObj = qbase.aliasClass(name=strings[0])
    assert aliasObj.name is not None
    assert aliasObj.name == strings[0]
    # b) after instantiation
    aliasObj = qbase.aliasClass()
    assert  aliasObj.name is None
    aliasObj.name = strings[1]
    assert aliasObj.name == strings[1]

    # 2) test that the name has to be string, i.e. raises error otherwise.
    aliasObj = qbase.aliasClass()
    with pytest.raises(TypeError):
        aliasObj.name = 2
    with pytest.raises(TypeError):
        aliasObj.name = qbase.aliasClass()
    with pytest.raises(AssertionError):
        qbase.aliasClass(name=2)

    # 3) test that the name cannot be changed after its set to a string
    aliasObj = qbase.aliasClass()
    aliasObj.name = strings[2]
    with pytest.warns(UserWarning, match="name cannot be changed"):
        aliasObj.name = strings[3]
    assert aliasObj.name == strings[2]

def test_aliasClassAliasProperty():
    # test adding new aliases
    # 1) empty list if not assigned
    aliasObj = qbase.aliasClass()
    assert aliasObj.alias == []

    # 2) test assigning alias at instantiation
    # a) a list of aliases
    aliasObj = qbase.aliasClass(alias=strings)
    assert aliasObj.alias == strings
    # b) a single alias
    aliasObj = qbase.aliasClass(alias=strings[0])
    assert strings[0] in aliasObj.alias
    assert aliasObj.alias == [strings[0]]

    # 3) after instantiation
    # a) a list of aliases
    aliasObj = qbase.aliasClass()
    aliasObj.alias = strings
    assert aliasObj.alias == strings
    # b) a single alias
    # b.1) first alias
    aliasObj = qbase.aliasClass()
    aliasObj.alias=strings[0]
    assert strings[0] in aliasObj.alias
    assert aliasObj.alias == [strings[0]]
    # b.2) second alias
    aliasObj.alias=strings[1]
    assert strings[1] in aliasObj.alias
    assert aliasObj.alias == strings[0:2]

def test_stringRepresntaionOfAliasClass():
    # test the string representation of aliasClass is equal to its name
    aliasObj = qbase.aliasClass(name=strings[0], alias=strings[1:3])
    strRep = str(aliasObj)
    assert aliasObj.name == strRep

def test_equalityOfTwoAliasClassInstances():
    # they should be equal if there is a match in their names or an alias
    # cases: 1) name = name, 2) name = an alias, 3) an alias = another alias, 4) name = name & an alias = another alias,
    # 5) no equality, and 6) ob1 != ob4 and ob1 = ob3 does not imply ob3 != ob4, they might be equal
    aliasObj1 = qbase.aliasClass(name=strings[0], alias=strings[1])
    aliasObj2 = qbase.aliasClass(name=strings[0], alias=strings[2])
    aliasObj3 = qbase.aliasClass(name=strings[2], alias=strings[1])
    aliasObj4 = qbase.aliasClass(name=strings[2], alias=strings[3])
    aliasObj1c = qbase.aliasClass(name=strings[0], alias=strings[1])
    assert aliasObj1 == aliasObj2 # case 1
    assert aliasObj2 == aliasObj3 # case 2
    assert aliasObj3 == aliasObj1 # case 3
    assert aliasObj1 == aliasObj1c # case 4
    assert aliasObj1 != aliasObj4 # case 5
    assert aliasObj3 == aliasObj4 # case 6

def test_hashValueOfAliasObjects():
    # hash value is equal to the hash of the name and not to some other string
    aliasObj = qbase.aliasClass(name=strings[0], alias=strings[1:3])
    assert hash(aliasObj) == hash(strings[0])
    assert hash(aliasObj) != hash(strings[1])
