import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp
import qTools.QuantumToolbox.states as qSt
from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
from functools import partial
from qTools.classes.exceptions import sweepInitError


""" under construction be careful """

# TODO mutable arguments can be used cleverly
def runSimulation(qSim, p, statesList=[], resultsList=[]):
    condition = qSim.beforeLoop.lCount
    print(condition,len(qSim.beforeLoop.sweeps[0].sweepList))
    runSequence(qSim.beforeLoop)
    res = runLoop(qSim, p)
    if len(qSim.beforeLoop.sweeps) > 0:
        statesList.append(res[0])
        resultsList.append(res[1])
        if condition < (len(qSim.beforeLoop.sweeps[0].sweepList)-1):
            qSim._Simulation__res(qSim.Loop)
            qSim._Simulation__res(qSim.whileLoop)
            return runSimulation(qSim, p)
        else:
            return [statesList, resultsList]
    else:
        return res


def runLoop(qSim, p):
    states = []
    results = []
    if p is None:
        for ind in range(len(qSim.Loop.sweeps[0].sweepList)-1):
            res = runTime(qSim, ind)
            # FIXME make this more elegent
            st1 = [qSim.qSys.initialState]
            rs1 = [qSim._Simulation__compute(qSim.qSys, qSim.qSys.initialState)]
            for ind0 in range(len(res[0])):
                st1.append(res[0][ind0])
                rs1.append(res[1][ind0])
            states.append(st1)
            results.append(rs1)
    else:
        res = p.map(partial(runTime, qSim), range(len(qSim.Loop.sweeps[0].sweepList)-1))
        # FIXME make this more elegent
        for ind in range(len(qSim.Loop.sweeps[0].sweepList)-1):
            st1 = [qSim.qSys.initialState]
            rs1 = [qSim._Simulation__compute(qSim.qSys, qSim.qSys.initialState)]
            for ind0 in range(len(res[ind][0])):
                st1.append(res[ind][0][ind0])
                rs1.append(res[ind][1][ind0])
            states.append(st1)
            results.append(rs1)
        

    return [states, results]


def runTime(qSim, ind):
    for sw in qSim.Loop.sweeps:
        runSweep(sw, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    qSim._Simulation__res(qSim.whileLoop)
    res = runEvolve(qSim)
    return res


def runEvolve(qSim):
    conditionW = qSim.whileLoop.lCount
    runSequence(qSim.whileLoop)
    res = __timeEvol(qSim)
    if len(qSim.whileLoop.sweeps) > 0:
        print('here')
        if conditionW < (len(qSim.whileLoop.sweeps[0].sweepList)-1):
            return runEvolve(qSim)
        else:
            return res
    else:
        return res


def __timeEvol(qSim):
    if qSim.qSys.Unitaries is None:
        unitary = lio.Liouvillian(2 * np.pi * qSim.qSys.totalHam, timeStep=qSim.stepSize/(qSim.steps/qSim.samples))
    else:
        unitary = qSim.qSys.Unitaries(qSim.qSys, qSim.stepSize/(qSim.steps/qSim.samples))
    
    state = qSim.qSys.lastState
    states = []
    results = []
    for ii in range(qSim.samples):
        state = unitary @ state
        states.append(state)
        result = qSim._Simulation__compute(qSim.qSys, state)
        results.append(result)
    return [states, results]



def runSweep(swe, ind):
    val = swe.sweepList[ind]
    setattr(swe.superSys, swe.sweepKey, val)


def runSequence(qSeq):
    for sweep in qSeq.sweeps:
        ind = sweep.lCounts
        runSweep(sweep, ind)



class Sweep(qUniversal):
    # TODO can be included to qSystems by a method
    instances = 0
    label = 'Sweep'
    Paral = None
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepPert', '__sweepList', 'logSweep', '_parallel', 'loop', '__lCount']
    # TODO write exceptions if gone keep
    # FIXME enable this
    #@sweepInitError
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
        return self._qSequence__Sweeps

    @sweeps.setter
    def sweeps(self, sysDict):
        self._qSequence__Sweeps = {}
        for key, val in sysDict.items():
            self.addSweep(val, key)

    def addSweep(self, sys, sweepKey, **kwargs):
        newSweep = Sweep(superSys=sys, sweepKey=sweepKey, **kwargs)
        self._qSequence__Sweeps.append(newSweep)
        return newSweep

    @property
    def lCount(self):
        self._qSequence__swCount += 1
        return self._qSequence__swCount - 1

    @lCount.setter
    def lCount(self,val):
        self._qSequence__swCount = val

# FIXME remove this somehow
def comp(qSim, state):
    Simulation._Simulation__compute += 1

class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    __compute = 0
    __slots__ = ['__qSys', 'sequence', '__stepSize', 'finalTime', '__times', 'states', 'beforeLoop', 'Loop', 'whileLoop', 'compute', '__sample', '__step']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__qSys = QuantumSystem()
        self.beforeLoop = qSequence(superSys=self)
        self.Loop = qSequence(superSys=self)
        self.whileLoop = qSequence(superSys=self)
        self.__times = None
        self.__stepSize = 0.02
        # FIXME current scheme does not require final time, but it's given, it should handle
        self.finalTime = 1.5
        self.states = []
        self.compute = comp
        self.__sample = 1
        self.__step = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def steps(self):
        return self._Simulation__step

    @steps.setter
    def steps(self, num):
        self._Simulation__step = num

    @property
    def samples(self):
        if len(self.whileLoop.sweeps) == 0:
            return self.steps
        else:
            return self._Simulation__sample

    @samples.setter
    def samples(self, num):
        self._Simulation__sample = num

    
    def __compute(self, qSys, state):
        res = self.compute(qSys, state)
        return res

    def __del__(self):
        class_name = self.__class__.__name__

    @property
    def qSys(self):
        self._Simulation__qSys.superSys = self
        return self._Simulation__qSys

    @qSys.setter
    def qSys(self, val):
        QuantumSystem.constructCompSys(val)
        self._Simulation__qSys = val

    @property
    def times(self):
        return np.arange(0, self.finalTime+self.stepSize, self.stepSize)
    
    @property
    def times(self):
        return self._Simulation__times

    @property
    def stepSize(self):
        return self._Simulation__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self._Simulation__stepSize = stepsize
    
    def run(self, p=None):
        if self.qSys._QuantumSystem__constructed == False:
            self.qSys.constructCompSys()
        
        self._Simulation__res(self.beforeLoop)
        self._Simulation__res(self.Loop)
        self._Simulation__res(self.whileLoop)
        '''statesList = [] 
        resultsList = []'''
        res = runSimulation(self, p)
        return res[0], res[1]

    @staticmethod
    def __res(seq):
        seq.lCount = 0
        for ind in range(len(seq.sweeps)):
            seq.sweeps[ind].lCounts = 0

    @times.setter
    def times(self, tlist):
        self._Simulation__times = tlist
