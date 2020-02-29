from qTools.classes.QPro import Gate
from qTools.classes.QSys import genericQSys
from qTools.QuantumToolbox import operators, operations
from numpy import pi

class xGate(Gate):
    instances = 0
    label = 'xGate'
    __slots__ = ['__angle']
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
            # FIXME creates the matrix everytime its called
            self.getUnitary = self.instantFlip
            self._Gate__implementation = typeStr

    @Gate.unitary.getter
    def unitary(self):
        if self._Step__unitary is not None:
            return self._Step__unitary
        else:
            return self.createUnitary()

'''def xGate(obj, *args):
    for arg in args:
        newXGate = xGate(superSys=arg)
        obj._genericQSys__qProtocol.add(newXGate)'''

