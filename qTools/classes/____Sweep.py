from numpy import arange, logspace


class _sweep(qUniversal):
    instances = 0
    label = '_sweep'
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepStep', '__sweepList', 'logSweep', 'sweepFunction']
    # FIXME enable this, but not necessarily this way
    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__()
        # TODO make these properties so that sweepList is dynamic ?
        self.sweepKey = None
        self.sweepMax = None
        self.sweepMin = None
        self.sweepStep = None
        self.__sweepList = None
        self.logSweep = False
        self.sweepFunction = None
        self._qUniversal__setKwargs(**kwargs)

    @qUniversal.subSys.setter
    def subSys(self, subSys):
        super().addSubSys(subSys)

    @property
    def sweepList(self):
        return self._Sweep__sweepList

    @sweepList.setter
    def sweepList(self, sList):
        if sList is None:
            if self.logSweep is False:
                self._Sweep__sweepList = arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)
            elif self.logSweep is True:
                self._Sweep__sweepList = logspace(self.sweepMin, self.sweepMax, num=self.sweepPert, base=10.0)
        else:
            self._Sweep__sweepList = sList

    def runSweep(self, ind):
        if self.sweepFunction is None:
            val = self.sweepList[ind]
            for subSys in self.subSys.values():
                setattr(subSys, self.sweepKey, val)
        else:
            self.sweepFunction(self, self.superSys.superSys)


class Sweep(qUniversal):
    instances = 0
    label = 'Sweep'
    __slots__ = []
    # TODO init errors
    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweeps(self):
        return self._qUniversal__subSys

    @sweeps.setter
    def sweeps(self, sysDict):
        super().subSys = sysDict

    def createSweep(self, sys, sweepKey, **kwargs):
        newSweep = _sweep(superSys=self, subSys=sys, sweepKey=sweepKey, **kwargs)
        super().addSubSys(newSweep)
        return newSweep

