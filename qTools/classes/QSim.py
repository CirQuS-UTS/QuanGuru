import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp
import qTools.QuantumToolbox.states as qSt
from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
from functools import partial
""" under construction """


class sweep(qUniversal):
    instances = 0
    label = 'sweep'
    __parallel = None
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepPert', '__sweepList', 'logSweep', '_parallel']
    # TODO write exceptions if gone keep
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
        self._qUniversal__setKwargs(**kwargs)

    @property
    def parallel(self):
        return self._parallel

    @parallel.setter
    def parallel(self, val):
        if self.__parallel is not None:
            raise ValueError('Dude!')
        else:
            self._parallel = True
            self.__parallel = self

    @property
    def sweepList(self):
        if self.__sweepList is None:
            if self.logSweep is False:
                return np.arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)
            elif self.logSweep is True:
                return np.logspace(self.sweepMin, self.sweepMax, num=self.sweepPert, base=10.0)
        else:
            return self.__sweepList

    @sweepList.setter
    def sweepList(self, sList):
        self.__sweepList = sList



class qSequence(qUniversal):
    instances = 0
    label = '_sweep'
    __slots__ = ['__Systems', '__system','__key']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__Systems = {}
        self.__system = None
        self.__key = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def Systems(self):
        return self.__Systems

    @Systems.setter
    def Systems(self, sysDict):
        self.__Systems = {}
        for key, val in sysDict.items():
            self.addSweep(val, key)

    def addSweep(self, sys, label, **kwargs):
        newSweep = sweep(superSys=sys, sweepKey=label, **kwargs)
        if sys in self.__Systems.keys():
            if isinstance(self.__Systems[sys], dict):
                self.__Systems[sys][label] = newSweep
            else:
                oldSw = self.__Systems[sys]
                self.__Systems[sys] = {}
                self.__Systems[sys][oldSw.sweepKey] = oldSw
                self.__Systems[sys][label] = newSweep
        else:
            self.__Systems[sys] = newSweep
        return newSweep


class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    __slots__ = ['__qSys','sweep','sequence','timeSweep','__stepSize','finalTime','allStates','__tProtocol']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__qSys = QuantumSystem()
        self.sweep = Sweep(superSys=self)
        self.sequence = qSequence(superSys=self)
        self.timeSweep = self.sweep.addSweep(sys=self, label='time')
        self.timeSweep.sweepMax = 1
        self.timeSweep.sweepMin = 0
        self.timeSweep.sweepPert = 0.02
        self.__stepSize = 0.01
        self.finalTime = 1.5
        self.allStates = True
        self.__tProtocol = None
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

    """@times.setter
    def times(self, tList):
        self.timeSweep.sweepList = tList"""
 
    def addSweep(self, obj, label, **kwargs):
        newSwe = self.sweep.addSweep(sys=obj, label=label, **kwargs)
        return newSwe

    @property
    def tProtocol(self):
        return self.__tProtocol

    @tProtocol.setter
    def tProtocol(self, protoc):
        self.__tProtocol = protoc

    @property
    def stepSize(self):
        return self.__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self.__stepSize = stepsize
    
    def run(self, p=None):
        if self.qSys._QuantumSystem__constructed == False:
            self.qSys.constructCompSys()

        if p is None:
            self.__update(self.sweepBefore)
            self.__timeEvolve()
            self.__compute()
        else:
            states = p.map(partial(partial(self.tProtocol, self), sweep), sweep.sweepList)
        return states

    @staticmethod
    def __update(Sweep, value):
        for system in Sweep.Systems:
            setattr(sweep.superSys, sweep.sweepKey, value)

    @staticmethod
    def __timeEvolveStates(state, times):
        states[state]
        for ii in range(len(times) - 1):
            state = unitary @ state
            states.append(state)
        return state

    @staticmethod
    def __timeEvolveCompute(state, times):
        states[state]
        for ii in range(len(times) - 1):
            state = unitary @ state
            states.append(state)
        return state

    @staticmethod
    def __timeEvolveStates(state, times):
        states[state]
        for ii in range(len(times) - 1):
            state = unitary @ state
            states.append(state)
        return state

    @staticmethod
    def __compute(func, state):
        return func(state)

