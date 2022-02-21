import pytest
import quanguru.classes.QSystem as QSys

# tests for composite vs single system cases of the quantum system object

@pytest.mark.parametrize("attrName, attrVal", [
                         ["_QuantumSystem__compSys", False],
                         ["dimension", 3]
                         ])
def test_cannotAddSubSysToSingleQuantumSystem(attrName, attrVal):
    # create a quantum system
    singleSys = QSys.QuantumSystem()
    # set a relevant attribute that turns _QuantumSystem__compSys to False
    setattr(singleSys, attrName, attrVal)
    # create another system
    anotherSys = QSys.QuantumSystem()
    # trying to add anotherSys as subSys should raise TypeError
    with pytest.raises(TypeError):
        singleSys.addSubSys(anotherSys)
    
    # make sure that the subsys is empty
    assert len(singleSys.subSys) == 0

@pytest.mark.parametrize("attrName, attrVal, defVal", [
                         ["dimension", 3, 1]
                         ])
def test_cannotSetSingleSysAttrToCompSystem(attrName, attrVal, defVal):
    # create a quantum system
    qsystem = QSys.QuantumSystem()
    # create another to add as a subSys
    asystem = QSys.QuantumSystem()
    qsystem.addSubSys(asystem)

    # assert that the _QuantumSystem__compSys is changed
    assert qsystem._QuantumSystem__compSys is True

    # make sure that setting single system parameters warns
    with pytest.warns(Warning):
        setattr(qsystem, attrName, attrVal)

    # make sure that above call does not change the value
    assert getattr(qsystem, attrName) == defVal