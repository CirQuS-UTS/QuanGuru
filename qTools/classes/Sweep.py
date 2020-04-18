from numpy import arange, logspace
from functools import reduce

from qTools.classes.updateBase import updateBase
from qTools.classes.computeBase import computeBase

__all__ = [
    'Sweep'
]

class _sweep(updateBase):
    instances = 0
    label = '_sweep'

    toBeSaved = updateBase.toBeSaved.extendedCopy(['sweepMax', 'sweepMin', 'sweepStep', 'sweepList', 'logSweep', 'multiParam'])

    __slots__ = ['sweepMax', 'sweepMin', 'sweepStep', '_sweepList', 'logSweep', 'multiParam']
   
    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        
        self._updateBase__function = self._defSweep

        self.sweepMax = None
        self.sweepMin = None
        self.sweepStep = None
        self._sweepList = None
        self.logSweep = False
        self.multiParam = False
        
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweepFunction(self):
        return self._updateBase__function

    @sweepFunction.setter
    def sweepFunction(self, func):
        self._updateBase__function = func

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

    @staticmethod
    def _defSweep(self, ind):
        val = self.sweepList[ind]
        self._runUpdate(val)

    def runSweep(self, ind):
        self._updateBase__function(self, ind)

class Sweep(computeBase):
    instances = 0
    label = 'Sweep'
    __slots__ = ['__inds', '__indMultip']
    # TODO init errors
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))

        self.__inds = []
        self.__indMultip = None

        self._qUniversal__setKwargs(**kwargs)

    def save(self):
        saveDict = super().save()
        sweepsDict = {}
        for sw in self.subSys.values():
            sweepsDict[sw.name] = sw.save()
        saveDict['sweeps'] = sweepsDict
        return saveDict

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
        super().addSubSys(sysDict)
        
    def removeSweep(self, sys):
        if isinstance(sys, _sweep):
            self.removeSubSys(sys)
        else:
            for sweep in self.subSys.values():
                sweep.removeSubSys(sys)

    def createSweep(self, system, sweepKey, **kwargs):
        newSweep = _sweep(superSys=self, subSys=system, sweepKey=sweepKey, **kwargs)
        super().addSubSys(newSweep)
        return newSweep

    def prepare(self):
        if len(self.subSys) > 0:
            self._Sweep__inds = []
            for indx, sweep in enumerate(self.subSys.values()):
                if sweep.multiParam is True:
                    self._Sweep__inds.insert(0,len(sweep.sweepList))
                elif indx == 0:
                    self._Sweep__inds.insert(0,len(sweep.sweepList))
            self._Sweep__indMultip = reduce(lambda x, y: x*y, self._Sweep__inds)

    def runSweep(self, ind):
        indx = 0
        for sweep in self.sweeps.values():
            if sweep.multiParam is True:
                indx += 1
            sweep.runSweep(ind[indx])
