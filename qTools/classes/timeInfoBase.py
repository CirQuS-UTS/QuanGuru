from qTools.classes.QUni import qUniversal
from qTools.classes.QResDict import qResults

class timeBase(qUniversal):
    instances = 0
    label = 'timeBase'
    
    __slots__ = ['__delStates', '__finalTime', '__stepSize', '__samples', '__step', 'compute', 'calculate', 'qRes', '__compute']
    
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))

        self.__delStates = False

        self.__finalTime = None
        self.__stepSize = None
        self.__samples = 1
        self.__step = None

        self.compute = None
        self.calculate = None

        self.__compute = self._computeSave

        self._qUniversal__setKwargs(**kwargs)
        self.qRes = qResults(superSys=self)
        

    @property
    def delStates(self):
        return self._timeBase__delStates

    @delStates.setter
    def delStates(self, boolean):
        if boolean is True:
            self._timeBase__compute = self._computeDel
        elif boolean is False:
            self._timeBase__compute = self._computeSave
        self._timeBase__delStates = boolean

    @property
    def finalTime(self):
        return self._timeBase__finalTime

    @finalTime.setter
    def finalTime(self, fTime):
        self._timeBase__finalTime = fTime
        if self.stepSize is not None:
            self._timeBase__step = int((fTime//self.stepSize) + 1)

    @property
    def steps(self):
        if self.finalTime is None:
            self._timeBase__finalTime = self._timeBase__step * self.stepSize
        return int((self.finalTime//self.stepSize) + 1)

    @steps.setter
    def steps(self, num):
        self._timeBase__step = num
        if self.finalTime is not None:
            self._timeBase__stepSize = self.finalTime/num

    @property
    def stepSize(self):
        return self._timeBase__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self._timeBase__stepSize = stepsize
        if self.finalTime is not None:
            self._timeBase__step = int((self.finalTime//stepsize) + 1)

    @property
    def samples(self):
        return self._timeBase__samples

    @samples.setter
    def samples(self, num):
        self._timeBase__samples = num

    def _computeDel(self, states, keys):
        if self.compute is not None:
            self.compute(self, *states)

    def _computeSave(self, states, keys):
        for ind, key in enumerate(keys):
            self.qRes.states[key].append(states[ind])

        if self.compute is not None:
            self.compute(self, *states)
