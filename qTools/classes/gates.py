from qTools.classes.QPro import Gate
from qTools.QuantumToolbox import operators

class xGate(Gate): # pylint: disable=too-many-ancestors
    instances = 0
    label = 'xGate'
    __slots__ = ['__angle']
    def __init__(self, **kwargs):
        super().__init__()
        self.__angle = None
        self._createUnitary = self._gateImplements
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def angle(self):
        return self._xGate__angle

    @angle.setter
    def angle(self, val):
        self._xGate__angle = val # pylint: disable=assigning-non-slot

    def instantFlip(self):
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
            sys = list(self.subSys.values())
            flipOp = operators.compositeOp(operators.sigmax(), sys[0]._qSystem__dimsBefore,
                                           sys[0]._qSystem__dimsAfter) # pylint: disable=no-member
            for i in range(len(sys)-1):
                flipOp = sys[i+1] @ flipOp
            self._paramBoundBase__matrix = flipOp # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _gateImplements(self):
        if self.implementation.lower() == 'instant':
            unitary = self.instantFlip()
        return unitary
