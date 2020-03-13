class Sweep(qUniversal):
    instances = 0
    label = 'Sweep'
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepPert', '__sweepList', 'logSweep', '__lCount', 'sweepFunction']
    # FIXME enable this, but not necessarily this way
    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__()
        # TODO make these properties so that sweepList is dynamic
        self.sweepKey = None
        self.sweepMax = None
        self.sweepMin = None
        self.sweepPert = None
        self.__sweepList = None
        self.logSweep = False
        self.__lCount = 0
        self.sweepFunction = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweepList(self):
        return self._Sweep__sweepList

    @sweepList.setter
    def sweepList(self, sList):
        if sList is None:
            if self.logSweep is False:
                self._Sweep__sweepList = np.arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)
            elif self.logSweep is True:
                self._Sweep__sweepList = np.logspace(self.sweepMin, self.sweepMax, num=self.sweepPert, base=10.0)
        else:
            self._Sweep__sweepList = sList

    @property
    def lCounts(self):
        self._Sweep__lCount += 1
        return self._Sweep__lCount-1

    @lCounts.setter
    def lCounts(self,val):
        self._Sweep__lCount = val

    def runSweep(self, ind):
        if self.sweepFunction is None:
            val = self.sweepList[ind]
            for subSys in self.subSystems.values():
                setattr(subSys, self.sweepKey, val)
            # TODO Decide if single or multiple subbSys
            #setattr(self.subSystems, self.sweepKey, val)
        else:
            self.sweepFunction(self, self.superSys.superSys)
    # TODO Decide if single or multiple subbSys
    """@qUniversal.subSystems.setter
    def subSystems(self, subS):
        self._qUniversal__subSys = subS"""