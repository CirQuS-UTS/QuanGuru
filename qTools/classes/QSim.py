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
    
    print('states in __timeEvol', len(states))
    return states


def updateParams(Sweeps):
    for sweep in Sweeps:
        val = sweep.sweepList[sweep.lCounts]
        setattr(sweep.superSys, sweep.sweepKey, val)


def updateBefore(sequence, qSim=None):
    num = sequence.lCount
    if num < len(sequence.sweeps):
        updateParams(sequence.sweeps[num])
        updateBefore(sequence)


def updateParamsEvolve(Sweeps, sequence, qSim):
    for sweep in Sweeps:
        val = sweep.sweepList[sweep.lCounts]
        setattr(sweep.superSys, sweep.sweepKey, val)
        print("here", val)
    updateBeforeEvolve(sequence, qSim)
    

def updateBeforeEvolve(sequence, qSim):
    num = sequence.lCount
    if num < len(sequence.sweeps):
        updateParamsEvolve(sequence.sweeps[num], sequence, qSim)
    else:
        states = __timeEvol(qSim)
        print('len states in updateBeforeEvolve', len(states))
        return states

def timeEvol(qSim, p=None):
    qSeq = qSim.beforeLoop
    updateBefore(qSeq)
    states = __parOrNot(qSeq.superSys, p)
    return states


def __parOrNot(qSim, p):
    if p is None:
        states = []
        for ind in range(len(qSim.Loop.sweeps[0][0].sweepList)):
            for sw in qSim.Loop.sweeps:
                updateParams(sw)
            print('cav freq is', qSim.qSys.subSystems['Cavity1'].frequency)
            states.append(__tEvol(qSim, ind))
        return states


def __tEvol(qSim, ind):
    states = updateBeforeEvolve(qSim.whileLoop, qSim=qSim)
    #print('states in __tEvol', len(states))
    return states


    


'''def timeEvolAfter(qSim, vaL):
    if vaL < (len(qSim.sequence.sweeps)-1):
        lx = qSim.sequence.sweeps[lc][0].lCounts
        sw = qSim.sequence.sweeps[lx]
        for ind in range(len(sw)):
            setattr(sw[ind].superSys, sw[ind].sweepKey, sw[ind].sweepList[lx])
        timeEvolAfter(qSim, vaL+1)
    else:
        states = []
        lx = qSim.sequence.sweeps[lc][0].lCounts
        sw = qSim.sequence.sweeps[lx]
        for ind in range(len(sw[0].sweepList)):
            states.append(__timeEvol(qSim, sw))
        print('states in timeEvolveAfter', len(states))
        return states


def __pTimeEvol(qSim, p, lc):
    vaL = lc
    if p is None:
        states = []
        for ind in range(len(qSim.sequence.sweeps[vaL][0].sweepList)):
            lx = qSim.sequence.sweeps[vaL][0].lCounts
            for swe in qSim.sequence.sweeps[vaL]:
                setattr(swe.superSys, swe.sweepKey, swe.sweepList[lx])
                states.append(__timeEvol(qSim, vaL))
        print('states in __pTimeEvol', len(states))
        return states
    else:
        states = p.map(partial(timeEvolAfter, qSim), [x for x in range(len(Sweep.Paral.sweepList)-1)])
        return states
'''

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
        return self.__lCount - 1

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
        self.__Sweeps = [[]]
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
        if newSweep.loop <= len(self.sweeps):
            self.__Sweeps[newSweep.loop].append(newSweep)
        else:
            self.__Sweeps.append([newSweep])
        return newSweep

    @property
    def lCount(self):
        self.__swCount += 1
        return self.__swCount - 1

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
        self.states = None
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

        self.states = timeEvol(self, p)

    @staticmethod
    def __res(seq):
        for ind in range(len(seq.sweeps)):
            for ind2 in range(len(seq.sweeps[ind])):
                seq.sweeps[ind][ind2].lCounts = 0

    @times.setter
    def times(self, tlist):
        self.__times = tlist
