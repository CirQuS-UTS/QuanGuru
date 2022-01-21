import random
import pytest
import quanguru.classes.base as qbase #pylint: disable=import-error

@pytest.mark.parametrize("cls", [qbase.qBase])
def test_auxDictAndObj(cls, helpers):
    strings = helpers.randStringList()
    # create internal and external instances and add items to aux dictionary
    for i in range(2):
        inst1 = cls(_internal=bool(i))
        inst2 = cls(_internal=bool(i))

        # 1) test the auxiliary dictionary

        # verify that the dictionaries are the same
        assert inst1.auxDict is inst2.auxDict
        assert inst1.auxDict is cls._auxiliaryDict
        # add items
        inst1.auxDict[strings[0]] = strings[1]
        inst2.auxDict[strings[2]] = strings[3]
        # verify that the dictionaries are still the same
        assert inst1.auxDict is inst2.auxDict
        assert inst1.auxDict is cls._auxiliaryDict
        # verify that the cross calls works (duh! the same dictionary)
        assert inst2.auxDict[strings[0]] == strings[1]
        assert inst1.auxDict[strings[2]] == strings[3]

        # test the setter, which updates the dict
        inst1.auxDict = {1:1.1, 2:2.2}
        # verify that the dictionaries are still the same
        assert inst1.auxDict is inst2.auxDict
        assert inst1.auxDict is cls._auxiliaryDict
        # verify that the cross calls works (duh! the same dictionary)
        assert inst2.auxDict[1] == 1.1
        assert inst2.auxDict[2] == 2.2

        # 2) test the auxiliary object

        # verify that the objects are the same
        assert inst1.auxObj is inst2.auxObj
        assert inst1.auxObj is cls._auxiliaryObj
        # add attributes
        setattr(inst1.auxObj, strings[0], strings[1])
        setattr(inst2.auxObj, strings[2], strings[3])
        # verify that the objects are still the same
        assert inst1.auxObj is inst2.auxObj
        assert inst1.auxObj is cls._auxiliaryObj
        # verify that the cross calls works (duh! the same object)
        assert getattr(inst1.auxObj, strings[2], strings[3])
        assert getattr(inst1.auxObj, strings[0], strings[1])

@pytest.mark.parametrize("cls", [qbase.qBase])
def test_superSysProperty(cls):
    # create internal and external instances and add items to aux dictionary
    for i in range(2):
        inst1 = cls(_internal=bool(i))
        inst2 = cls(_internal=bool(i))
        # make sure default None is returned by the getter
        assert inst1.superSys is None
        assert inst2.superSys is None
        # set-get and assert
        inst1.superSys = inst2
        inst2.superSys = inst2
        assert inst1.superSys is inst2
        assert inst2.superSys is inst2
        # change by the setter and assert by the getter
        inst1.superSys = inst1
        inst2.superSys = inst1
        assert inst1.superSys is inst1
        assert inst2.superSys is inst1

def assertRemoved(remOb, mainOb):
    assert remOb not in mainOb.subSys.values()
    with pytest.raises(KeyError):
        mainOb.subSys[remOb.name]
    with pytest.raises(KeyError):
        mainOb.subSys[remOb.alias[0]]

@pytest.mark.parametrize("cls", [qbase.qBase])
def test_subSysAddRemoveResetMethods(cls, helpers):
    # create internal and external instances and add items to aux dictionary
    for i in range(2):
        # create a single object and a list object to be used for subSys
        inst1 = cls(_internal=bool(i))
        insts = [cls(_internal=bool(i)) for x in range(8)]
        # create bunch of strings to be used as alias
        strings2 = [helpers.randString(random.randint(3, 10)) for _ in range(12)]
        # add the first element and assert that its in the subSys
        inst1.addSubSys(insts[0])
        assert insts[0] in inst1.subSys.values()
        # assert that you can get it by its name
        assert inst1.subSys[insts[0].name] is insts[0]
        # add alias and assert that you can get it by any of the alias
        insts[0].alias = strings2[0:1]
        assert all(inst1.subSys[key] is insts[0] for key in strings2[0:1])

        # add a subSys by giving the class (instead of an instance)
        newIns = inst1.addSubSys(cls)
        assert newIns not in [inst1, *insts]
        # assert that you can get it by its name
        assert inst1.subSys[newIns.name] is newIns
        # add alias and assert that you can get it by any of the alias
        newIns.alias = strings2[2:3]
        assert all(inst1.subSys[key] is newIns for key in strings2[2:3])

        # add a subSys by its name
        retIns = inst1.addSubSys(insts[1].name)
        assert retIns is insts[1]
        assert insts[1] in inst1.subSys.values()
        assert inst1.subSys[insts[1].name] is retIns
        insts[1].alias = strings2[4:5]
        assert all(inst1.subSys[key] is retIns for key in strings2[4:5])

        # add a subSys by it alias
        assert insts[2] not in inst1.subSys.values()
        insts[2].alias = strings2[6:7]
        retIns = inst1.addSubSys(strings2[6])
        assert retIns is insts[2]
        assert inst1.subSys[insts[2].name] is retIns
        assert inst1.subSys[insts[2].alias[0]] is retIns

        # add a subSys by its name.name
        retIns = inst1.addSubSys(insts[3].name.name)
        assert retIns is insts[3]
        assert insts[3] in inst1.subSys.values()
        assert inst1.subSys[insts[3].name] is retIns
        insts[3].alias = strings2[8:9]
        assert all(inst1.subSys[key] is retIns for key in strings2[8:9])

        # add a list of subSys
        insts[4].alias = strings2[10]
        inst1.addSubSys([insts[4].alias[0], insts[5].name.name])
        assert insts[4] in inst1.subSys.values()
        assert insts[5] in inst1.subSys.values()

        # add a tuple of subSys
        insts[6].alias = strings2[11]
        inst1.addSubSys((insts[6].alias[0], insts[7].name.name))
        assert insts[6] in inst1.subSys.values()
        assert insts[7] in inst1.subSys.values()

        # remove with the object
        inst1.removeSubSys(insts[0])
        assertRemoved(insts[0],inst1)

        # remove with name
        inst1.removeSubSys(insts[1].name)
        assertRemoved(insts[1],inst1)

        # remove with alias
        inst1.removeSubSys(insts[2].alias[0])
        assertRemoved(insts[2],inst1)

        # remove with name.name
        inst1.removeSubSys(insts[3].name.name)
        assertRemoved(insts[3],inst1)

        # remove a list of subSys
        inst1.removeSubSys([insts[4].name, insts[6]])
        assertRemoved(insts[4],inst1)
        assertRemoved(insts[6],inst1)

        # resetSubSys subSys
        assert len(inst1.subSys.values()) > 0
        inst1.resetSubSys()
        assert len(inst1.subSys.values()) == 0
