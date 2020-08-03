from .QPro import Gate
from ..QuantumToolbox import operators #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox import operations #pylint: disable=relative-beyond-top-level

class xGate(Gate): # pylint: disable=too-many-ancestors
    instances = 0
    label = 'xGate'
    __slots__ = ['__angle']
    def __init__(self, **kwargs):
        super().__init__()
        self.__angle = None
        #self._createUnitary = self._gateImplements
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
            flipOp = operators.compositeOp(operators.Jx(sys[0].dimension, isDim=True),
                                           sys[0]._dimsBefore, sys[0]._dimsAfter) # pylint: disable=no-member
            for i in range(len(sys)-1):
                flipOp = operators.compositeOp(operators.Jx(sys[i].dimension, isDim=True),
                                               sys[i+1]._dimsBefore, sys[i+1]._dimsAfter) @ flipOp
            self._paramBoundBase__matrix = flipOp # pylint: disable=assigning-non-slot
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _gateImplements(self):
        if self.implementation.lower() == 'instant':
            unitary = self.instantFlip()
            self.fixed = True
        return unitary


class rotation(Gate): # pylint: disable=too-many-ancestors
    instances = 0
    label = 'rotation'
    __slots__ = ['__angle', 'rotationAxis']
    def __init__(self, **kwargs):
        super().__init__()
        self.__angle = None
        self.rotationAxis = None
        self.implementation = 'instant'
        #self._createUnitary = self._gateImplements
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def angle(self):
        return self._rotation__angle

    @angle.setter
    def angle(self, val):
        self._rotation__angle = val # pylint: disable=assigning-non-slot

    def _rotMat(self):
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
            sys = list(self.subSys.values())
            if self.rotationAxis.lower() == 'x':
                rotOp = operations.xRotation
            elif self.rotationAxis.lower() == 'y':
                rotOp = operations.yRotation
            elif self.rotationAxis.lower() == 'z':
                rotOp = operations.zRotation

            flipOp = operators.compositeOp(rotOp(self.angle), sys[0]._dimsBefore, sys[0]._dimsAfter) # pylint: disable=no-member
            for i in range(len(sys)-1):
                flipOp = operators.compositeOp(rotOp(self.angle), sys[i+1]._dimsBefore, sys[i+1]._dimsAfter) @ flipOp
            self._paramBoundBase__matrix = flipOp # pylint: disable=assigning-non-slot
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _gateImplements(self):
        if self.implementation.lower() == 'instant':
            unitary = self._rotMat()
            self.fixed = True
        return unitary

rotation._createUnitary = rotation._gateImplements # pylint: disable=protected-access
xGate._createUnitary = xGate._gateImplements
