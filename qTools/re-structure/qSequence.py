class qSequence(qUniversal):
    instances = 0
    label = '_sweep'
    __slots__ = ['__Sweeps', '__swCount']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__()
        self.__Sweeps = []
        self.__swCount = 0
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweeps(self):
        return self._qSequence__Sweeps

    @sweeps.setter
    def sweeps(self, sysDict):
        self._qSequence__Sweeps = {}
        for key, val in sysDict.items():
            self.addSweep(val, key)

    # TODO Change name to create
    def addSweep(self, sys, sweepKey, **kwargs):
        newSweep = Sweep(superSys=self, subSystems=sys, sweepKey=sweepKey, **kwargs)
        self._qSequence__Sweeps.append(newSweep)
        return newSweep

    @property
    def lCount(self):
        self._qSequence__swCount += 1
        return self._qSequence__swCount - 1

    @lCount.setter
    def lCount(self,val):
        self._qSequence__swCount = val