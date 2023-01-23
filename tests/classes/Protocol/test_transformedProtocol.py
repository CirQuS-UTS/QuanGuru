import quanguru as qg
import numpy as np
import random

def test_instantiation():
    """
    This 
    - tests that the transform protocol can be instantiated from any class that inherits from genericProtocol with the .createTransformation() method
        - tests that the appropriate attribute values are set from this instantiation method
    - tests that the class can be instantiated without any attribute values (empty instance)
    Test that ._paramUpdated is set to false on instantiation for both original and transformed

    """

    # Test transforming an empty protocol without assigning a function
    qProNoFunc = qg.genericProtocol()
    qTransNoFunc = qProNoFunc.createTransformation()
    assert qTransNoFunc.originalProtocol is qProNoFunc
    assert qTransNoFunc.transformationFunc is None
    assert qTransNoFunc.system is qProNoFunc.system
    assert (qTransNoFunc.name in qProNoFunc._paramBoundBase__paramBound.keys()
            and qProNoFunc._paramBoundBase__paramBound[qTransNoFunc.name] is qTransNoFunc)
    assert qTransNoFunc._paramUpdated

    # Test transforming an empty protocol with assigning a function
    def simpleTransform(originalProtocol, unitary):
        return unitary

    qProFunc = qg.genericProtocol()
    qTransFunc = qProFunc.createTransformation(transformationFunc=simpleTransform)
    assert qTransFunc.originalProtocol is qProFunc
    assert qTransFunc.transformationFunc is simpleTransform
    assert qTransFunc.system is qProFunc.system
    assert (qTransFunc.name in qProFunc._paramBoundBase__paramBound.keys()
            and qProFunc._paramBoundBase__paramBound[qTransFunc.name] is qTransFunc)
    assert qTransFunc._paramUpdated

    # Test creating a transformedProtocol using regular initiation
    qTransInit = qg.transformedProtocol()
    assert qTransInit.originalProtocol is None
    assert qTransInit.transformationFunc is None
    assert qTransInit.system is None
    assert qTransInit._paramUpdated is True

    # Test creating a transformedProtocol assigning using kwargs
    qTransInitKwargs = qg.transformedProtocol(originalProtocol=qProFunc, transformationFunc=simpleTransform)
    assert qTransInitKwargs.originalProtocol is qProFunc
    assert qTransInitKwargs.transformationFunc is simpleTransform
    assert qTransInitKwargs.system is qProFunc.system
    assert qTransInitKwargs._paramUpdated is True

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
    """
    def simpleTransform(originalProtocol, unitary):
        return unitary

    qub = qg.Qubit(frequency=round(random.random(), 2))
    unitary = unitary = np.random.rand(2, 2)
    func = lambda self, collapseOps, decayRate: unitary

    qPro = qg.genericProtocol(system=qub, createUnitary=func)
    assert np.array_equal(qPro.unitary(), unitary)

    qTransInitKwargs = qg.transformedProtocol(originalProtocol=qPro, transformationFunc=simpleTransform)
    assert qTransInitKwargs._paramUpdated is True

    # Check _paramUpdated false after unitary is accessed and calculated
    assert np.allclose(qTransInitKwargs.unitary(), unitary)
    assert qTransInitKwargs._paramUpdated is False

    # Change originalProcess unitary generation
    func2 = lambda self, collapseOps, decayRate: unitary.transpose()
    qPro.createUnitary = func2
    assert np.allclose(qPro.unitary(), unitary.transpose())

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
