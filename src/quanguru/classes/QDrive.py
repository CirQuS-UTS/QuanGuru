"""
    THESE ARE JUST SOME INITIAL IDEAS. NOT COMPLETED OR USED YET.

    .. currentmodule:: quanguru.classes.QDrive

    .. autosummary::

        genericDrive
        qDrive
        pulse

"""

from numpy import pi

from .baseClasses import paramBoundBase
from .QSimBase import setAttr

class genericDrive(paramBoundBase):
    label = 'genericDrive'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def totalShape(self, timeList):
        if ((self._paramBoundBase__matrix is None) or (self._paramUpdated)): # pylint: disable=no-member
            shapeList = []
            for time in timeList:
                shapeList.append(self.apply(time))
            self._paramBoundBase__matrix = shapeList #pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def apply(self, time): #pylint:disable=no-self-use,unused-argument
        return 0

class qDrive(genericDrive):
    label = 'qDrive'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def pulses(self):
        return self._qBase__subSys # pylint: disable=no-member

    @pulses.setter
    def pulses(self, npulse):
        genericDrive.subSys.fset(self, npulse) # pylint: disable=no-member

    def addPulse(self, rotation=None, **pulseParams):
        self._paramUpdated = True
        p = pulse(**pulseParams)
        if rotation is not None:
            print(p.integrateShape([p.t0 + i*((p.t1 - p.t0)/1000) for i in range(1000)]))
            p._scale = rotation / (2*pi*p.integrateShape([p.t0 + i*((p.t1 - p.t0)/1000) for i in range(1001)]))
        super().addSubSys(p)
        p._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access,no-member
        return p

    def apply(self, time):
        coef = super().apply(time)
        for p in self.pulses.values():
            coef += p.apply(time)
        return coef

class pulse(genericDrive):
    label = 'pulse'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    __slots__ = ['__t0', '__t1', '__func', 'funcArgs', 'funcKwargs', '_scale']
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__t0 = None #pylint:disable=invalid-name
        self.__t1 = None #pylint:disable=invalid-name
        self.__func = None
        self.funcKwargs = {}
        self.funcArgs = []
        self._scale = 1
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def t0(self): #pylint:disable=invalid-name
        return self._pulse__t0

    @t0.setter
    def t0(self, val): #pylint:disable=invalid-name
        setAttr(self, '_pulse__t0', val)

    @property
    def t1(self): #pylint:disable=invalid-name
        return self._pulse__t1

    @t1.setter
    def t1(self, val): #pylint:disable=invalid-name
        setAttr(self, '_pulse__t1', val)

    @property
    def func(self):
        return self._pulse__func

    @func.setter
    def func(self, f):
        setAttr(self, '_pulse__func', f)

    def apply(self, time):
        return self._scale*self.func(time, *self.funcArgs, **self.funcKwargs) if self.t1 > time > self.t0 else super().apply(time) # pylint:disable=line-too-long # noqa: E501

    def integrateShape(self, timePoints):
        integral = 0
        for ind in range(len(timePoints)-1):
            integral += self.apply((timePoints[ind+1]+timePoints[ind])/2)*(timePoints[ind+1]-timePoints[ind])
        return integral
