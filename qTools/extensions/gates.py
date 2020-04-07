from qTools.classes.QPro import Gate
from qTools.classes.QSys import genericQSys
from qTools.QuantumToolbox import operators, operations
from numpy import pi

class xGate(Gate):
    instances = 0
    label = 'xGate'
    __slots__ = ['__angle']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__angle = None
        self._qUniversal__setKwargs(**kwargs)
    
    @property
    def angle(self):
        return self._xGate__angle

    @angle.setter
    def angle(self, val):
        self._xGate__angle = val

    def instantFlip(self):
        if self._Step__unitary is None:
            flipOp = operators.compositeOp(operators.sigmax(), self.superSys._qSystem__dimsBefore, self.superSys._qSystem__dimsAfter)
            self._Step__unitary = flipOp
        return self._Step__unitary

    def getUnitary(self):
        super().getUnitary()
        if self.implementation == 'instant':
            return self.instantFlip()
