from qTools.classes.computeBase import computeBase


class timeBase(computeBase):
    instances = 0
    label = 'timeBase'

    __slots__ = ['__finalTime', '__stepSize', '__samples', '__step', '__bound']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__finalTime = None
        self.__stepSize = None
        self.__samples = None
        self.__step = None
        self.__bound = self

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        keys = ['_timeBase__stepSize', '_timeBase__finalTime', '_timeBase__samples', '_timeBase__step']
        try:
            saveDict = super().save()
        except TypeError:
            saveDict = {}

        if self.superSys is not None:
            saveDict['superSys'] = self.superSys.name # pylint: disable=no-member
        saveDict['bound'] = self.bound.name
        if self.bound is self:
            for key in keys:
                saveDict[key] = getattr(self, key)
        return saveDict

    @property
    def bound(self):
        return self._timeBase__bound

    @property
    def finalTime(self):
        if self.bound is not self:
            fTime = self.bound.finalTime
        else:
            fTime = self._timeBase__finalTime
        return fTime

    @finalTime.setter
    def finalTime(self, fTime):
        self._paramUpdated = True
        self._timeBase__finalTime = fTime # pylint: disable=assigning-non-slot
        if self.stepSize is not None:
            self._timeBase__step = int((fTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot

    @property
    def stepCount(self):
        if self.finalTime is None:
            self._timeBase__finalTime = self._timeBase__step * self.stepSize # pylint: disable=assigning-non-slot
        return int((self.finalTime//self.stepSize) + 1)

    @stepCount.setter
    def stepCount(self, num):
        self._paramUpdated = True
        self._timeBase__step = num # pylint: disable=assigning-non-slot
        if self.finalTime is not None:
            self._timeBase__stepSize = self.finalTime/num # pylint: disable=assigning-non-slot

    @property
    def stepSize(self):
        if self.bound is not self:
            stepSize = self.bound.stepSize
        else:
            stepSize = self._timeBase__stepSize
        return stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self._paramUpdated = True
        self._timeBase__stepSize = stepsize # pylint: disable=assigning-non-slot
        if self.finalTime is not None:
            self._timeBase__step = int((self.finalTime//stepsize) + 1) # pylint: disable=assigning-non-slot

    @property
    def samples(self):
        return self._timeBase__samples

    @samples.setter
    def samples(self, num):
        self._paramUpdated = True
        self._timeBase__samples = num # pylint: disable=assigning-non-slot
            