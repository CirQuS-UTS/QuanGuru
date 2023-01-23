import quanguru as qg

def test_instantiation():
    """
    This 
    - tests that the transform protocol can be instantiated from any class that inherits from genericProtocol with the .transformed() method
        - tests that the appropriate attribute values are set from this instantiation method
    - tests that the class can be instantiated without any attribute values (empty instance)
    """

    # Test transforming an empty protocol without assigning a function
    qPro = qg.genericProtocol()

    # Test transforming an empty protocol without assigning a function d

    pass

def test_parameterUpdating():
    """
    checks that ._paramUpdated is properly switched to True when
    - any parameters are changed
        - .transformationFunc
        - ._originalUnitary
    - any important parameters in the original protocol are changed
        - i.e. whenever ._paramUpdated is flicked to true in the original
        (This will require combing through current protocol classes to check when paramUpdated should be flicked to True)
        (WILL NEED TO CHECK THAT WHEN .createUnitary is changed, ._paramUpdated is flicked to True)
        (This also includes checking that when appropriate parameters are changed in the superSys and simulation objects, protocols are appropriately 
        updated) (this can be in its own issue)
    
    Also, test that calling .unitary() in the original protocol doesn't flick off the ._paramUpdated in the transformedProtocol

    Test that ._paramUpdated is set to false on instantiation for both original and transformed
    """
    pass

def test_unitaryCalls():
    """
    Tests different cases of unitary calls
        - when .unitary() of the transformed protocol is called before the original has generated its unitary, then the original has to generate its
        unitary
        - when .unitary() of the transformed protocol is called and the original has paramUpdated = True, then the original has to generate its
        unitary
        - when .unitary() of the transformed protocol is called, ._paramUpdated is set to True, and the orignal has 
        paramUpdated = False, then the unitary is fetched from ._paramBoundBase__matrix of original
        - when .unitary() of the transformed protocol is called and ._paramUpdated is set to False, then the unitary is fetched from 
        ._paramBoundBase__matrix of the transformed

    Tests that the transformed protocol stores the unitary in ._paramBoundBase__matrix after each call of .unitary()
    """
    pass


def test_transformationFunc():
    """
    Testing that the correct parameters are passed to the user defined transformation function 
    Testing that the transformation function is applied correctly
    """
    pass
