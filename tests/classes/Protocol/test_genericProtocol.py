import quanguru as qg

def test_internalDict():
    """
    Testing that:
        - Attributes that are not part of the slots of genericProtocol, its children, or its parents are 
        set as key-value pairs in the _internalDict attribute of any particular instance
        - This functionality does not conflict with the current ability to access parameters of the .simulation attribute of QSimComp instances
        directly through the instance itself (i.e. we can acess qSystem.simulation.stepSize via qSystem.stepSize)
    """
    qPro = qg.genericProtocol()
    
    qPro.abc = 5
    qPro.stepSize = 3

    assert qPro._internalDict == dict(abc=5)
    assert qPro.abc == 5
    assert qPro.stepSize == 3