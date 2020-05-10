from qTools.classes.QPro import Gate
from qTools.QuantumToolbox import operators

class xGate(Gate):
    instances = 0
    label = 'xGate'
    __slots__ = ['__angle']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__angle = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def angle(self):
        return self._xGate__angle

    @angle.setter
    def angle(self, val):
        self._xGate__angle = val # pylint: disable=assigning-non-slot

    def instantFlip(self):
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
            flipOp = operators.compositeOp(operators.sigmax(), self.superSys._qSystem__dimsBefore, self.superSys._qSystem__dimsAfter) # pylint: disable=no-member
            self._paramBoundBase__matrix = flipOp # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def createUnitary(self):
        if self.implementation == 'instant':
            self._funcToCreateUnitary = self.instantFlip
        super().createUnitary()
