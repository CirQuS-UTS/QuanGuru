from qTools.classes.QPro import Gate
from qTools.QuantumToolbox import operators, operations
from numpy import pi

class xGate(Gate):
    instances = 0
    label = 'qUniversal'
    def __init__(self, **kwargs):
        super().__init__()
        self.__angle = None
        self.getUnitary = None
        self._qUniversal__setKwargs(**kwargs)
    
    @property
    def angle(self):
        return self._xGate__angle

    @angle.setter
    def angle(self, val):
        self._xGate__angle = val

    def instantFlip(self):
        flipOp = operators.compositeOp(operations.xRotation(pi/2), self.superSys._qSystem__dimsBefore, self.superSys._qSystem__dimsAfter)
        self._Step__unitary = flipOp
        return flipOp

    @Gate.implementation.setter
    def implementation(self, typeStr):
        if typeStr.lower() == 'instant':
            self.getUnitary = self.instantFlip
            self._Gate__implementation = typeStr

    def createUnitary(self):
        unitary = self.getUnitary()
        return unitary

    @Gate.unitary.getter
    def unitary(self):
        if self._Step__unitary is not None:
            return self._Step__unitary
        else:
            return self.createUnitary()


