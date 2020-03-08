from numpy import arange, logspace
from functools import reduce
from qTools.classes.QUni import qUniversal
from qTools.classes.updateBase import updateBase

__all__ = [
    'Sweep'
]

class _sweep(updateBase):
    instances = 0
    label = '_sweep'
    __slots__ = ['sweepMax', 'sweepMin', 'sweepStep', '_sweepList', 'logSweep', 'sweepFunction']
    # FIXME enable this, but not necessarily this way
    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__()
        # TODO make these properties so that sweepList is dynamic ?
        self.sweepMax = None
        self.sweepMin = None
        self.sweepStep = None
        self._sweepList = None
        self.logSweep = False
        self.sweepFunction = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweepKey(self):
        return self._updateBase__key

    @sweepKey.setter
    def sweepKey(self, keyStr):
        self._updateBase__key = keyStr

    @property
    def sweepList(self):
        return self._sweepList

    @sweepList.setter
    def sweepList(self, sList):
        if sList is None:
            if self.logSweep is False:
                self._sweepList = arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)
            elif self.logSweep is True:
                self._sweepList = logspace(self.sweepMin, self.sweepMax, num=self.sweepPert, base=10.0)
        else:
            self._sweepList = sList

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
    __slots__ = ['__inds', '__indMultip', 'compute', 'calculate']
    # TODO init errors
    def __init__(self, **kwargs):
        super().__init__()
        self.compute = None
        # TODO Behaviour of calculate ?
        self.calculate = None
        self.__inds = []
        self.__indMultip = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def inds(self):
        return self._Sweep__inds

    @property
    def indMultip(self):
        return self._Sweep__indMultip

    @property
    def sweeps(self):
        return self._qUniversal__subSys

    @sweeps.setter
    def sweeps(self, sysDict):
        super().subSys = sysDict
    # TODO remove a specific sweep or all the sweep for a specific system
    def createSweep(self, system, sweepKey, **kwargs):
        newSweep = _sweep(superSys=self, subSys=system, sweepKey=sweepKey, **kwargs)
        super().addSubSys(newSweep)
        return newSweep

    def prepare(self):
        if len(self.subSys) > 0:
            self._Sweep__inds = [None for i in range(len(self.subSys))]
            for sweep in self.subSys.values():
                self._Sweep__inds[-(sweep.ind+1)] = len(sweep.sweepList)-1
            self._Sweep__indMultip = reduce(lambda x, y: x*y, self._Sweep__inds)

    def runSweep(self, ind):
        for sweep in self.sweeps.values():
            sweep.runSweep(ind[sweep.ind])
