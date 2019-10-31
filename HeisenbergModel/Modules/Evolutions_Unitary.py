import QuantumToolbox.liouvillian as liou

def DigitalTwo(obj, stepSize):
    UnitaryDigital = liou.Liouvillian(obj.hXY, timeStep=stepSize) @ liou.Liouvillian(obj.hXZ, timeStep=stepSize) @\
                     liou.Liouvillian(obj.hYZ, timeStep=stepSize)
    return UnitaryDigital

def IdealTwo(obj,stepSize):
    UnitaryIdeal = liou.Liouvillian(obj.hH, timeStep=stepSize)
    return UnitaryIdeal

def DigitalThree(obj,stepSize):
    UnitaryDigital = liou.Liouvillian(obj.hXY3, timeStep=stepSize) @ liou.Liouvillian(obj.h1XY, timeStep=stepSize) @ \
                     liou.Liouvillian(obj.hXZ3, timeStep=stepSize) @ liou.Liouvillian(obj.h1XZ, timeStep=stepSize) @ \
                     liou.Liouvillian(obj.hYZ3, timeStep=stepSize) @ liou.Liouvillian(obj.h1YZ, timeStep=stepSize)
    return UnitaryDigital

def IdealThree(obj,stepSize):
    UnitaryIdeal = liou.Liouvillian(obj.hH3, timeStep=stepSize)
    return UnitaryIdeal