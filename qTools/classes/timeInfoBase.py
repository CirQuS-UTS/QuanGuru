from qTools.classes.QUni import qUniversal

class timeBase(qUniversal):
    instances = 0
    label = 'timeBase'
    
    __slots__ = ['delStates', '__finalTime', '__stepSize', '__samples', '__step', 'compute', 'calculate']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__()

        self.delStates = False

        self.__finalTime = None
        self.__stepSize = None
        self.__samples = 1
        self.__step = None

        self.compute = None
        self.calculate = None

        self._qUniversal__setKwargs(**kwargs)

    @property
    def finalTime(self):
        return self._Simulation__finalTime

    @finalTime.setter
    def finalTime(self, fTime):
        self._Simulation__finalTime = fTime
        if self.stepSize is not None:
            self._Simulation__step = int((fTime//self.stepSize) + 1)

    @property
    def steps(self):
        if self.finalTime is None:
            self._Simulation__finalTime = self._Simulation__step * self.stepSize
        return int((self.finalTime//self.stepSize) + 1)

    @steps.setter
    def steps(self, num):
        self._Simulation__step = num
        if self.finalTime is not None:
            self._Simulation__stepSize = self.finalTime/num

    @property
    def stepSize(self):
        return self._Simulation__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self._Simulation__stepSize = stepsize
        if self.finalTime is not None:
            self._Simulation__step = int((self.finalTime//stepsize) + 1)

    @property
    def samples(self):
        return self._Simulation__samples

    @samples.setter
    def samples(self, num):
        self._Simulation__samples = num
