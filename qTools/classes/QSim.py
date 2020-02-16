import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp
import qTools.QuantumToolbox.states as qSt
from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
from functools import partial
from qTools.classes.exceptions import sweepInitError
""" under construction """


def __timeEvol(qSim):
    if qSim.qSys.Unitaries is None:
        unitary = lio.Liouvillian(2 * np.pi * qSim.qSys.totalHam, timeStep=qSim.stepSize)
    else:
        unitary = qSim.qSys.Unitaries(qSim.qSys, qSim.stepSize)

    state = qSim.qSys.initialState
    states = [state]
    for ii in range(len(qSim.times) - 1):
        state = unitary @ state
        states.append(state)
    return states


def runSweep(swe, ind):
    val = swe.sweepList[ind]
    setattr(swe.superSys, swe.sweepKey, val)

def runSequence(qSeq):
    for sweep in qSeq.sweeps:
        ind = sweep.lCounts
        runSweep(sweep, ind)

def runSimulation(qSim, p):
    condition = qSim.beforeLoop.lCount
    runSequence(qSim.beforeLoop)
    states = runLoop(qSim, p)
    if len(qSim.beforeLoop.sweeps) > 0:
        if condition < (len(qSim.beforeLoop.sweeps[0].sweepList)-1):
            qSim._Simulation__res(qSim.Loop)
            qSim._Simulation__res(qSim.whileLoop)
            return runSimulation(qSim, p)
        else:
            return states
    else:
        return states

def runLoop(qSim, p):
    if p is None:
        states = []
        for ind in range(len(qSim.Loop.sweeps[0].sweepList)-1):
            states.append(runTime(qSim, ind))
    else:
        states = p.map(partial(runTime, qSim), range(len(qSim.Loop.sweeps[0].sweepList)-1))
    return states

def runTime(qSim, ind):
    for sw in qSim.Loop.sweeps:
        runSweep(sw, ind)
    states = runEvolve(qSim)
    return states

def runEvolve(qSim):
    conditionW = qSim.whileLoop.lCount
    runSequence(qSim.whileLoop)
    states = __timeEvol(qSim)
    if len(qSim.whileLoop.sweeps) > 0:
        if conditionW < (len(qSim.whileLoop.sweeps[0].sweepList)-1):
            return runEvolve(qSim)
        else:
            return states
    else:
        return states

class Sweep(qUniversal):
    # TODO can be included to qSystems by a method
    instances = 0
    label = 'Sweep'
    Paral = None
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepPert', '__sweepList', 'logSweep', '_parallel', 'loop', '__lCount']
    # TODO write exceptions if gone keep
    @sweepInitError
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO make these properties
        self.sweepKey = None
        self.sweepMax = None
        self.sweepMin = None
        self.sweepPert = None
        self.__sweepList = None
        self.logSweep = False
        self._parallel = False
        self.loop = 0
        self.__lCount = 0
        self._qUniversal__setKwargs(**kwargs)

    @property
    def parallel(self):
        return self._parallel

    @parallel.setter
    def parallel(self, val):
        if Sweep.Paral is not None:
            # FIXME should raise an error but then two **kwargs in init calls this twice
            pass
        else:
            self._parallel = True
            Sweep.Paral = self

    @property
    def sweepList(self):
        return self.__sweepList

    @sweepList.setter
    def sweepList(self, sList):
        if sList is None:
            if self.logSweep is False:
                self.__sweepList = np.arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)
            elif self.logSweep is True:
                self.__sweepList = np.logspace(self.sweepMin, self.sweepMax, num=self.sweepPert, base=10.0)
        else:
            self.__sweepList = sList

    @property
    def lCounts(self):
        self.__lCount += 1
        return self.__lCount-1

    @lCounts.setter
    def lCounts(self,val):
        self.__lCount = val


class qSequence(qUniversal):
    instances = 0
    label = '_sweep'
    __slots__ = ['__Sweeps', '__swCount']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__Sweeps = []
        self.__swCount = 0
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweeps(self):
        return self.__Sweeps

    @sweeps.setter
    def sweeps(self, sysDict):
        self.__Sweeps = {}
        for key, val in sysDict.items():
            self.addSweep(val, key)

    def addSweep(self, sys, sweepKey, **kwargs):
        newSweep = Sweep(superSys=sys, sweepKey=sweepKey, **kwargs)
        self.__Sweeps.append(newSweep)
        return newSweep

    @property
    def lCount(self):
        self.__swCount += 1
        return self.__swCount-1

    @lCount.setter
    def lCount(self,val):
        self.__swCount = val


class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    __slots__ = ['__qSys', 'sequence', 'compute', '__stepSize', 'finalTime', '__times', 'states', 'beforeLoop', 'Loop', 'whileLoop']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__qSys = QuantumSystem()
        self.beforeLoop = qSequence(superSys=self)
        self.Loop = qSequence(superSys=self)
        self.whileLoop = qSequence(superSys=self)
        self.compute = None
        self.__times = None
        self.__stepSize = 0.01
        self.finalTime = 1.5
        self.states = []
        self._qUniversal__setKwargs(**kwargs)

    def __del__(self):
        class_name = self.__class__.__name__

    @property
    def qSys(self):
        self.__qSys.superSys = self
        return self.__qSys

    @qSys.setter
    def qSys(self, val):
        QuantumSystem.constructCompSys(val)
        self.__qSys = val

    @property
    def times(self):
        return np.arange(0, self.finalTime+self.stepSize, self.stepSize)
    
    @property
    def times(self):
        return self.__times

    @property
    def stepSize(self):
        return self.__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self.__stepSize = stepsize
    
    def run(self, p=None):
        if self.qSys._QuantumSystem__constructed == False:
            self.qSys.constructCompSys()
        
        self.__res(self.beforeLoop)
        self.__res(self.Loop)
        self.__res(self.whileLoop)

        states = runSimulation(self, p)
        return states

    @staticmethod
    def __res(seq):
        for ind in range(len(seq.sweeps)):
            seq.sweeps[ind].lCounts = 0

    @times.setter
    def times(self, tlist):
        self.__times = tlist
