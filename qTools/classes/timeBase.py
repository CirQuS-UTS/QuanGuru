from qTools.classes.computeBase import stateBase, _parameter
# pylint: disable = cyclic-import

class timeBase(stateBase):
    instances = 0
    label = 'timeBase'

    __slots__ = ['__finalTime', '__stepSize', '__samples', '__step']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__finalTime = _parameter()
        self.__stepSize = _parameter()
        self.__samples = _parameter(1)
        self.__step = _parameter()

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        keys = ['stepSize', 'finalTime', 'samples', 'stepCount']
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
        if self._timeBase__stepSize._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__stepSize._value = self._timeBase__stepSize._bound._value # pylint: disable=protected-access
        self._timeBase__finalTime.value = fTime # pylint: disable=assigning-non-slot
        if self.stepSize is not None:
            self._timeBase__step.value = int((fTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot

    @property
    def stepCount(self):
        if self.finalTime is None:
            self._timeBase__finalTime.value = self._timeBase__step.value * self.stepSize # pylint: disable=E0237
        self._timeBase__step.value = int((self.finalTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot
        return self._timeBase__step.value

    @stepCount.setter
    def stepCount(self, num):
        self._paramUpdated = True
        if self._timeBase__finalTime._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__finalTime._value = self._timeBase__finalTime._bound._value# pylint: disable=protected-access
        self._timeBase__step.value = num # pylint: disable=assigning-non-slot
        if self.finalTime is not None:
            self._timeBase__stepSize.value = self.finalTime/num # pylint: disable=assigning-non-slot

    @property
    def stepSize(self):
        return self._timeBase__stepSize.value

    @stepSize.setter
    def stepSize(self, stepsize):
        self._paramUpdated = True
        if self._timeBase__finalTime._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__finalTime._value = self._timeBase__finalTime._bound._value# pylint: disable=protected-access
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

    def _bound(self, other, # pylint: disable=dangerous-default-value
               params=['_stateBase__delStates', '_stateBase__initialState', '_stateBase__initialStateInput'],
               re=False):
        keys = ['_timeBase__stepSize', '_timeBase__finalTime', '_timeBase__step']
        keysProp = ['stepSize', 'finalTime', 'stepCount']
        bounding = True
        for ind, key in enumerate(keys):
            if getattr(self, key)._bound is False: # pylint: disable=protected-access
                if getattr(other, key)._value is not None: # pylint: disable=protected-access
                    setattr(self, keysProp[ind], getattr(self, key)._value) # pylint: disable=protected-access

                if bounding:
                    for i, k in enumerate(keys):
                        if ((getattr(self, k)._bound is None) and # pylint: disable=protected-access
                                (getattr(other, k)._value is not None)): # pylint: disable=protected-access
                            setattr(self, keysProp[i], getattr(other, k)._value) # pylint: disable=protected-access
                            break
                    bounding = False

        for key in (*keys, *params, '_timeBase__samples'):
            try:
                if ((getattr(self, key)._bound is None) or re): # pylint: disable=protected-access
                    getattr(self, key)._bound = getattr(other, key) # pylint: disable=protected-access
            except AttributeError:
                pass
