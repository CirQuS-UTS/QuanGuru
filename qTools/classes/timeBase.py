from qTools.classes.computeBase import computeBase
from collections import OrderedDict

class timeBase(computeBase):
    instances = 0
    label = 'timeBase'
    
    __slots__ = ['__finalTime', '__stepSize', '__samples', '__step', '__bound', '__paramUpdated', '__inBound']
    
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__paramUpdated = False
        self.__finalTime = None
        self.__stepSize = None
        self.__samples = None
        self.__step = None
        self.__bound = self
        self.__inBound = OrderedDict()

        self._qUniversal__setKwargs(**kwargs)

    @property
    def _paramUpdated(self):
        return self._timeBase__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._timeBase__paramUpdated = boolean
        for sys in self._timeBase__inBound.values():
            if sys is not self:
                sys._paramUpdated = boolean

    @property
    def bound(self):
        return self._timeBase__bound

    @property
    def finalTime(self):
        if self.bound is not self:
            return self.bound.finalTime
        else:
            return self._timeBase__finalTime

    @finalTime.setter
    def finalTime(self, fTime):
        self._paramUpdated = True
        self._timeBase__finalTime = fTime
        if self.stepSize is not None:
            self._timeBase__step = int((fTime//self.stepSize) + 1)

    @property
    def stepCount(self):
        if self.finalTime is None:
            self._timeBase__finalTime = self._timeBase__step * self.stepSize
        return int((self.finalTime//self.stepSize) + 1)

    @stepCount.setter
    def stepCount(self, num):
        self._paramUpdated = True
        self._timeBase__step = num
        if self.finalTime is not None:
            self._timeBase__stepSize = self.finalTime/num

    @property
    def stepSize(self):
        if self.bound is not self:
            return self.bound.stepSize
        else:
            return self._timeBase__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self._paramUpdated = True
        self._timeBase__stepSize = stepsize
        if self.finalTime is not None:
            self._timeBase__step = int((self.finalTime//stepsize) + 1)

    @property
    def samples(self):
        return self._timeBase__samples

    @samples.setter
    def samples(self, num):
        self._paramUpdated = True
        self._timeBase__samples = num

    def prepare(self, obj):
        if self.stepSize is None:
            if hasattr(obj, '_timeBase__inBound'):
                obj._timeBase__inBound[self.name] = self
            self._timeBase__bound = obj

        if self.samples is None:
            self.samples = obj.samples

        if self.stepSize is None:
            self.stepSize = obj.stepSize