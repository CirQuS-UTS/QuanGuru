from qTools.classes.computeBase import computeBase, _parameter


class timeBase(computeBase):
    instances = 0
    label = 'timeBase'

    __slots__ = ['__finalTime', '__stepSize', '__samples', '__step']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))
        self.__finalTime = _parameter(None)
        self.__stepSize = _parameter(None)
        self.__samples = _parameter(None)
        self.__step = _parameter(None)

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        keys = ['_timeBase__stepSize', '_timeBase__finalTime', '_timeBase__samples', '_timeBase__step']
        try:
            saveDict = super().save()
        except TypeError:
            saveDict = {}

        if self.superSys is not None:
            saveDict['superSys'] = self.superSys.name # pylint: disable=no-member

        for key in keys:
            saveDict[key] = getattr(self, key)
        return saveDict

    @property
    def finalTime(self):
        return self._timeBase__finalTime.value

    @finalTime.setter
    def finalTime(self, fTime):
        self._paramUpdated = True
        self._timeBase__finalTime.value = fTime # pylint: disable=assigning-non-slot
        if self.stepSize is not None:
            self._timeBase__step.value = int((fTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot

    @property
    def stepCount(self):
        if self.finalTime is None:
            self._timeBase__finalTime.value = self._timeBase__step.value * self.stepSize # pylint: disable=assigning-non-slot
        return int((self.finalTime//self.stepSize) + 1)

    @stepCount.setter
    def stepCount(self, num):
        self._paramUpdated = True
        self._timeBase__step.value = num # pylint: disable=assigning-non-slot
        if self.finalTime is not None:
            self._timeBase__stepSize.value = self.finalTime/num # pylint: disable=assigning-non-slot

    @property
    def stepSize(self):
        return self._timeBase__stepSize.value

    @stepSize.setter
    def stepSize(self, stepsize):
        self._paramUpdated = True
        self._timeBase__stepSize.value = stepsize # pylint: disable=assigning-non-slot
        if self.finalTime is not None:
            self._timeBase__step.value = int((self.finalTime//stepsize) + 1) # pylint: disable=assigning-non-slot

    @property
    def samples(self):
        return self._timeBase__samples.value

    @samples.setter
    def samples(self, num):
        self._paramUpdated = True
        self._timeBase__samples.value = num # pylint: disable=assigning-non-slot
            