"""
    Contains protocol/step objects for gate operations.

    .. currentmodule:: quanguru.classes.QGates

    .. autosummary::

        SpinRotation
        xGate


    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `SpinRotation`             |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
      `xGate`                    |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============
"""

from .QPro import Gate
from .QSimBase import setAttr
from ..QuantumToolbox import evolution
from ..QuantumToolbox import operators #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox import spinRotations #pylint: disable=relative-beyond-top-level

class SpinRotation(Gate): # pylint: disable=too-many-ancestors
    label = 'SpinRotation'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    __slots__ = ['__angle', '__rotationAxis', 'phase', '_rotationOp']
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__angle = None
        self.__rotationAxis = None
        self._rotationOp = None
        self.phase = 1
        #self._createUnitary = self._rotMat
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def angle(self):
        return self._SpinRotation__angle

    @angle.setter
    def angle(self, val):
        setAttr(self, '_SpinRotation__angle', val)

    @property
    def rotationAxis(self):
        return self._SpinRotation__rotationAxis # pylint: disable=no-member

    @rotationAxis.setter
    def rotationAxis(self, axStr):
        setAttr(self, '_SpinRotation__rotationAxis', axStr)
        if axStr.lower() == 'x':
            self._rotationOp = operators.Jx
        elif axStr.lower() == 'y':
            self._rotationOp = operators.Jy
        elif axStr.lower() == 'z':
            self._rotationOp = operators.Jz
        else:
            raise ValueError('unknown axis')

    def _rotMat(self, collapseOps = None, decayRates = None, openSys=False): #pylint:disable=unused-argument
        if ((self._paramBoundBase__matrix is None) or (self._paramBoundBase__paramUpdated is True)): # pylint: disable=no-member
            sys = list(self.subSys.values())
            rotOp = self._rotationOp
            flipOp = operators.compositeOp(rotOp(sys[0].dimension, isDim=True), sys[0]._dimsBefore, sys[0]._dimsAfter) # pylint: disable=no-member,line-too-long # noqa: E501
            flipUn = evolution.Unitary(self.phase*self.angle*flipOp)
            for i in range(len(sys)-1):
                flipOpN = operators.compositeOp(rotOp(sys[i+1].dimension, isDim=True),
                                                sys[i+1]._dimsBefore, sys[i+1]._dimsAfter)
                flipUn = evolution.Unitary(self.phase*self.angle*flipOpN) @ flipUn
            self._paramBoundBase__matrix = evolution._prepostSO(flipUn) if (openSys or isinstance(collapseOps, list) or self._isOpen) else flipUn # pylint: disable=assigning-non-slot,line-too-long,protected-access
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

class xGate(SpinRotation): # pylint: disable=too-many-ancestors
    label = 'xGate'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.rotationAxis = 'x'
        #self._createUnitary = self._gateImplements
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def instantFlip(self, openSys=False):
        if ((self._paramBoundBase__matrix is None) or (self._paramBoundBase__paramUpdated is True)): # pylint: disable=no-member
            sys = list(self.subSys.values())
            if self.rotationAxis.lower() == 'x':
                rotOp = spinRotations.xRotation
            elif self.rotationAxis.lower() == 'y':
                rotOp = spinRotations.yRotation
            elif self.rotationAxis.lower() == 'z':
                rotOp = spinRotations.zRotation
            flipOp = operators.compositeOp(rotOp(self.angle), sys[0]._dimsBefore, sys[0]._dimsAfter) # pylint: disable=no-member
            for i in range(len(sys)-1):
                flipOp = operators.compositeOp(rotOp(self.angle), sys[i+1]._dimsBefore, sys[i+1]._dimsAfter) @ flipOp
            self._paramBoundBase__matrix = evolution._prepostSO(flipOp) if openSys else flipOp # pylint: disable=assigning-non-slot,protected-access
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _gateImplements(self, collapseOps = None, decayRates = None): #pylint:disable=unused-argument
        if self.implementation is None:
            unitary = self._rotMat(openSys = isinstance(collapseOps, list) or self._isOpen)
        elif self.implementation.lower() in ('instant', 'flip'): # pylint: disable=no-member
            unitary = self.instantFlip(openSys = isinstance(collapseOps, list) or self._isOpen)
        return unitary

SpinRotation._createUnitary = SpinRotation._rotMat # pylint: disable=protected-access
xGate._createUnitary = xGate._gateImplements
