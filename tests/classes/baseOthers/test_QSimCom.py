import pytest
import quanguru as qg

@pytest.mark.parametrize('clas', [qg.QuantumSystem])
def test_setAndGetInternalSimulationParametersThroughSelf(clas):
    inst1 = clas(stepSize=1)
    assert inst1.stepSize == inst1.simulation.stepSize

    with pytest.raises(AttributeError):
        inst1.stepSizes = 2
