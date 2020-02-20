import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp
import qTools.QuantumToolbox.states as qSt
from qTools.classes.QSys import QuantumSystem, qSystem
from qTools.classes.QUni import qUniversal
from functools import partial
from qTools.classes.exceptions import sweepInitError
import sys


""" under construction be careful """
class Sweep(qUniversal):
    instances = 0
    label = 'Sweep'
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepPert', '__sweepList', 'logSweep', 'loop', '__lCount']
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
        self.loop = 0
        self.__lCount = 0
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

    
    def runSweep(self):
        val = self.sweepList[self.lCounts]
        setattr(self.superSys, self.sweepKey, val)


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
    __slots__ = ['__qSys', '__stepSize', 'finalTime', 'states', 'beforeLoop', 'Loop', 'whileLoop', 'compute', '__sample', '__step']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__qSys = QuantumSystem()
        self.beforeLoop = qSequence(superSys=self)
        self.Loop = qSequence(superSys=self)
        self.whileLoop = qSequence(superSys=self)
        self.__stepSize = 0.02
        # FIXME current scheme does not require final time, but it's given, it should handle
        self.finalTime = None
        self.states = []
        self.compute = comp
        self.__sample = 1
        self.__step = 1
        self._qUniversal__setKwargs(**kwargs)


    @property
    def ratio(self):
        if len(self.whileLoop.sweeps) > 0:
            return self.samples
        else:
            return self.steps/self.samples

    @property
    def steps(self):
        if len(self.whileLoop.sweeps) > 0:
            return len(self.whileLoop.sweeps[0].sweepList)
        elif self.finalTime is not None:
            return int(round(self.finalTime/self.stepSize))
        else:
            return self._Simulation__step

    @steps.setter
    def steps(self, num):
        self._Simulation__step = num

    @property
    def samples(self):
        if len(self.whileLoop.sweeps) > 0:
            return self._Simulation__sample
        else:
            return self.steps

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
        if isinstance(val, QuantumSystem):
            QuantumSystem.constructCompSys(val)
        self._Simulation__qSys = val

    @property
    def stepSize(self):
        return self._Simulation__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self._Simulation__stepSize = stepsize
    
    def run(self, p=None):
        if isinstance(self.qSys, QuantumSystem):
            # TODO Check first if constructed
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




# TODO mutable arguments can be used cleverly
def runSimulation(qSim, p, statesList=[], resultsList=[]):
    """if len(qSim.whileLoop.sweeps) > 0:
        if len(qSim.whileLoop.sweeps[0].sweepList) > 1500:
            sys.setrecursionlimit(2*len(qSim.whileLoop.sweeps[0].sweepList))"""
    condition = qSim.beforeLoop.lCount
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
    if len(qSim.Loop.sweeps) > 0:
        if p is None:
            for ind in range(len(qSim.Loop.sweeps[0].sweepList)-1):
                res = runTime(qSim, ind)
                # FIXME make this more elegent
                st1 = [qSim.qSys.initialState]
                rs1 = [qSim._Simulation__compute(qSim.qSys, qSim.qSys.initialState)]
                for ind0 in range(len(res[0])-1):
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
                for ind0 in range(len(res[ind][0])-1):
                    st1.append(res[ind][0][ind0])
                    rs1.append(res[ind][1][ind0])
                states.append(st1)
                results.append(rs1)
    else:
        # TODO improve these parts in general, possibly decorate
        results = [qSim._Simulation__compute(qSim.qSys, qSim.qSys.initialState)]
        states = [qSim.qSys.initialState]
        # TODO going to modify these for better, but take reseting the final state at the start of time evol into account
        qSim.qSys.lastState = qSim.qSys.initialState
        res = runEvolve(qSim, states, results)
        del results[-1]
        del states[-1]
    return [states, results] if len(results) > 2 else res

# TODO work on these to make them more compact
def runTime(qSim, ind):
    for sw in qSim.Loop.sweeps:
        runSweep(sw, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    qSim._Simulation__res(qSim.whileLoop)
    results = []
    states = []
    res = runEvolve(qSim, states, results)
    return res


def runEvolve(qSim, states, results):
    conditionW = qSim.whileLoop.lCount
    runSequence(qSim.whileLoop)
    res = __timeEvol(qSim)
    for ind in range(qSim.samples):
        results.append(res[1][ind])
        states.append(res[0][ind])
        
    if len(qSim.whileLoop.sweeps) > 0:
        if conditionW < (len(qSim.whileLoop.sweeps[0].sweepList)-1):
            return runEvolve(qSim, states, results)
        else:
            return [states, results]
    else:
        return res


def __timeEvol(qSim):
    # TODO fix this ratio/sample/steps issue
    if qSim.qSys.Unitaries is None:
        unitary = lio.Liouvillian(2 * np.pi * qSim.qSys.totalHam, timeStep=qSim.stepSize/qSim.ratio)
    else:
        unitary = qSim.qSys.Unitaries(qSim.qSys, qSim.stepSize/qSim.ratio)
        
    state = qSim.qSys.lastState
    states = []
    results = []
    for ii in range(qSim.samples):
        state = unitary @ state
        states.append(state)
        result = qSim._Simulation__compute(qSim.qSys, state)
        results.append(result)
        qSim.qSys.lastState = state
    return [states, results]


def runSequence(qSeq):
    for sweep in qSeq.sweeps:
        sweep.runSweep()
