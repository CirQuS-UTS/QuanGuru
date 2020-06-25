from .computeBase import paramBoundBase
from numpy import pi

class genericDrive(paramBoundBase):
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
    
    def totalShape(self, timeList):
        if ((self._paramBoundBase__matrix is None) or (self._paramUpdated)):
            shapeList = []
            for time in timeList:
                shapeList.append(self.apply(time))
            self._paramBoundBase__matrix = shapeList
        return self._paramBoundBase__matrix

    def apply(self):
        return 0

class qDrive(genericDrive):
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def pulses(self):
        return self._qUniversal__subSys

    @pulses.setter
    def pulses(self, pulse):
        genericDrive.subSys.fset(self, pulse) # pylint: disable=no-member

    def addPulse(self, rotation=None, **pulseParams):
        self._paramUpdated = True
        p = pulse(**pulseParams)
        if rotation is not None:
            print(p.integrateShape([p.t0 + i*((p.t1 - p.t0)/1000) for i in range(1000)]))
            p._scale = rotation / (2*pi*p.integrateShape([p.t0 + i*((p.t1 - p.t0)/1000) for i in range(1001)]))
        super().addSubSys(p)
        p._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return p

    def apply(self, time):
        coef = super().apply()
        for p in self.pulses.values():
            coef += p.apply(time)
        return coef
            

class pulse(genericDrive):
    __slots__ = ['__t0', '__t1', '__func', 'funcArgs','funcKwargs', '_scale']
    def __init__(self, **kwargs):
        super().__init__()
        self.__t0 = None
        self.__t1 = None
        self.__func = None
        self.funcKwargs = {}
        self.funcArgs = []
        self._scale = 1
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def t0(self):
        return self._pulse__t0

    @t0.setter
    def t0(self, val):
        self._pulse__t0 = val
        self._paramUpdated = True

    @property
    def t1(self):
        return self._pulse__t1

    @t1.setter
    def t1(self, val):
        self._pulse__t1 = val
        self._paramUpdated = True

    @property
    def func(self):
        return self._pulse__func

    @func.setter
    def func(self, f):
        self._pulse__func = f
        self._paramUpdated = True

    def apply(self, time):
        return self._scale*self.func(time, *self.funcArgs, **self.funcKwargs) if self.t1 > time > self.t0 else super().apply()

    def integrateShape(self, timePoints):
        integral = 0
        for ind in range(len(timePoints)-1):
            integral += self.apply((timePoints[ind+1]+timePoints[ind])/2)*(timePoints[ind+1]-timePoints[ind])
        return integral
