import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp
import qTools.QuantumToolbox.states as qSt
from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
from functools import partial
""" under construction """


class Sweep(qUniversal):
    instances = 0
    label = 'Sweep'
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


class qSequence(qUniversal):
    instances = 0
    label = '_sweep'
    __slots__ = ['__Sweeps','__key']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__Sweeps = {}
        self.__key = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweeps(self):
        return self.__sweeps

    @sweeps.setter
    def sweeps(self, sysDict):
        self.__Sweeps = {}
        for key, val in sysDict.items():
            self.addSweep(val, key)

    def addSweep(self, sys, label, **kwargs):
        newSweep = sweep(superSys=sys, sweepKey=label, **kwargs)
        if sys in self.__Sweeps.keys():
            if isinstance(self.__Sweeps[sys], dict):
                self.__Sweeps[sys][label] = newSweep
            else:
                oldSw = self.__Sweeps[sys]
                self.__Sweeps[sys] = {}
                self.__Sweeps[sys][oldSw.sweepKey] = oldSw
                self.__Sweeps[sys][label] = newSweep
        else:
            self.__Sweeps[sys] = newSweep
        return newSweep


class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    __slots__ = ['__qSys', 'sequence', '__stepSize', 'finalTime']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__qSys = QuantumSystem()
        self.sequence = qSequence(superSys=self)
        self.__stepSize = 0.01
        self.finalTime = 1.5
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
    def __compute(func, state):
        return func(state)

