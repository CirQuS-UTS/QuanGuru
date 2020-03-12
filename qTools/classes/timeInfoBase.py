from qTools.classes.QUni import qUniversal
from qTools.classes.QResDict import qResults

class timeBase(qUniversal):
    instances = 0
    label = 'timeBase'
    
    __slots__ = ['delStates', '__finalTime', '__stepSize', '__samples', '__step', 'compute', 'calculate', 'qRes']
    
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))

        self.delStates = False

        self.__finalTime = None
        self.__stepSize = None
        self.__samples = 1
        self.__step = None

        self.compute = None
        self.calculate = None

        self._qUniversal__setKwargs(**kwargs)
        self.qRes = qResults(superSys=self)
        
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

    def __compute(self, states):
        if self.compute is not None:
            self.compute(self, *states)
