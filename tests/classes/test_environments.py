from numpy import e
import pytest
from quanguru.classes.environment import thermalBath

@pytest.mark.parametrize("attribute", ['temperature', 'charFreq'])
def test_bathParameterSettingMakesParamUpdatedTrue(attribute):
    # test if the paramUpdated works properly when a parameter is changed.

    # by default paramUpdated is always True
    assert thermalBath()._paramUpdated

    # create a thermalBath and see if paramUpdated is True
    thBath = thermalBath()
    assert thBath._paramUpdated

    # set paramUpdated to False, assert it. set the attribute its current value and check if paramUpdated is still False
    thBath._paramUpdated = False
    assert not thBath._paramUpdated
    setattr(thBath, attribute, getattr(thBath, attribute))
    assert not thBath._paramUpdated

    # set the attribute to some other value (2x+1) and check if paramUpdated is True
    setattr(thBath, attribute, 2*getattr(thBath, attribute)+1)
    assert thBath._paramUpdated


@pytest.mark.parametrize("attribute", ['temperature', 'charFreq'])
def test_bathParameterValueChangesProperly(attribute):
    # test if the value of the attribute is properly changed.
    # create a thermalBath and set the attribute to 2x+1 where x is its default value
    thBath = thermalBath()
    defVal = getattr(thBath, attribute)
    setattr(thBath, attribute, 2*defVal+1)
    assert thBath._paramUpdated
    assert getattr(thBath, attribute) == 2*defVal+1

def test_bathNbar():
    # test the nbar value
    # by default it should be zero
    thBath = thermalBath()
    assert thBath.nBar == 0
    # test it for temperature = 1
    thBath.temperature = 1
    assert thBath._paramUpdated
    assert thBath.nBar == 1/(e-1)
    assert not thBath._paramUpdated
