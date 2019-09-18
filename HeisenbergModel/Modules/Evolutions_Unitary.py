from QuantumToolbox.liouvillian import Liouvillian

def DigitalTwo(obj, stepSize):
    UnitaryDigital = Liouvillian(obj.hXY, timeStep=stepSize) @ Liouvillian(obj.hXZ, timeStep=stepSize) @\
                     Liouvillian(obj.hYZ, timeStep=stepSize)
    return UnitaryDigital

def IdealTwo(obj):
    UnitaryIdeal = Liouvillian(obj.hH, timeStep=obj.StepSize)
    return UnitaryIdeal

def DigitalThree(obj):
    UnitaryDigital = Liouvillian(obj.hXY3, timeStep=obj.StepSize) @ Liouvillian(obj.h1XY, timeStep=obj.StepSize) @ \
                     Liouvillian(obj.hXZ3, timeStep=obj.StepSize) @ Liouvillian(obj.h1XZ, timeStep=obj.StepSize) @ \
                     Liouvillian(obj.hYZ3, timeStep=obj.StepSize) @ Liouvillian(obj.h1YZ, timeStep=obj.StepSize)
    return UnitaryDigital

def IdealThree(obj):
    UnitaryIdeal = Liouvillian(obj.hH3, timeStep=obj.StepSize)
    return UnitaryIdeal

