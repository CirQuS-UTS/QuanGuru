import random
import quanguru.classes.base as qbase #pylint: disable=import-error

def test_keySearchWithRegularStrings(helpers):
    strings = helpers.randStringList()
    # create a dictionary first
    dictionary = {key : random.randint(1, 10) for key in strings}
    # testing the keySearch method with regular strings to see that it returns the same string.
    assert qbase.keySearch(dictionary, strings[0]) == strings[0]
    assert qbase.keySearch(dictionary, strings[0]) != strings[1]
    # test for a string which is not inside a dictionary
    someString = helpers.randString(random.randint(3, 10))
    assert qbase.keySearch(dictionary, someString) == someString
    
def test_keySearchWithAliasClassAndRegularStrings(helpers): # pylint: disable=too-many-statements
    strings = helpers.randStringList()
    # create a dictionary first
    dictionary = {key : random.randint(1, 10) for key in strings}
    # create an instance of aliasClass
    aliasObj1 = qbase.aliasClass(name=helpers.randString(random.randint(3, 10)),
                                alias=[helpers.randString(random.randint(3, 10)),
                                helpers.randString(random.randint(3, 10))])
    dictionary[aliasObj1] = 2
    # test the keySearch method with a key that is an aliasClass object
    assert qbase.keySearch(dictionary, aliasObj1) == aliasObj1
    assert qbase.keySearch(dictionary, aliasObj1.name) == aliasObj1
    assert qbase.keySearch(dictionary, aliasObj1) == aliasObj1.name
    assert qbase.keySearch(dictionary, aliasObj1.name) == aliasObj1.name
    # test the keySearch method with an alias
    assert qbase.keySearch(dictionary, aliasObj1.alias[0]) == aliasObj1.name
    assert qbase.keySearch(dictionary, aliasObj1.alias[1]) == aliasObj1.name
    assert qbase.keySearch(dictionary, aliasObj1.alias[0]) == aliasObj1
    # create a second aliasClass object with the name same as first object's name
    aliasObj2 = qbase.aliasClass(name=aliasObj1.name,
                                alias=[helpers.randString(random.randint(3, 10)), 
                                       helpers.randString(random.randint(3, 10))])
    # test the keySearch method with the second aliasClass object
    assert qbase.keySearch(dictionary, aliasObj2) == aliasObj1
    assert qbase.keySearch(dictionary, aliasObj2.name) == aliasObj1.name                                
    assert qbase.keySearch(dictionary, aliasObj2) == aliasObj1.name
    assert qbase.keySearch(dictionary, aliasObj2.alias[0]) != aliasObj1
    assert qbase.keySearch(dictionary, aliasObj2.alias[0]) != aliasObj1.name
    # create a third aliasClass object with an alias same as first object's alias
    aliasObj3 = qbase.aliasClass(name=helpers.randString(random.randint(3, 10)),
                                alias=[aliasObj1.alias[0], helpers.randString(random.randint(3, 10))])
    # test the keySearch method with the third aliasClass object
    assert qbase.keySearch(dictionary, aliasObj3.alias[0]) == aliasObj1
    assert qbase.keySearch(dictionary, aliasObj3.alias[0]) == aliasObj1.name
    assert qbase.keySearch(dictionary, aliasObj3.alias[1]) != aliasObj1
    assert qbase.keySearch(dictionary, aliasObj3) == aliasObj1
    assert qbase.keySearch(dictionary, aliasObj3) == aliasObj1.name
    assert qbase.keySearch(dictionary, aliasObj3.name) != aliasObj1
    assert qbase.keySearch(dictionary, aliasObj3.name) != aliasObj1.name
