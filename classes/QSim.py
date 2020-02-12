import QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp
from classes.QSys import QuantumSystem
import QuantumToolbox.states as qSt
from classes.QUni import qUniversal
""" under construction """


class _sweep(qUniversal):
    __slots__ = ['Label', 'sweepMax', 'sweepMin', 'sweepPert']
    def __init__(self, **kwargs):
        super().__init__()
        self.superSys = None
        self.Label = None
        self.sweepMax = 1
        self.sweepMin = 0
        self.sweepPert = 0.1

        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweepList(self):
        return np.arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)


class Sweep(qUniversal):
    # __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self.__Systems = {}
        self._qUniversal__setKwargs(**kwargs)

    @property
    def Systems(self):
        return self.__Systems

    @Systems.setter
    def Systems(self, dict):
        self.__Systems = {}
        for key, val in dict.items():
            self.addSystem(val, key)

    def addSystem(self, sys, label, **kwargs):
        newSweep = _sweep(superSys=sys, Label=label, **kwargs)
        self.__Systems[sys] = newSweep
        return newSweep


class Simulation(object):
    def __init__(self, QSys=None):
        self.qSys = QSys
        self.allStates = True
        # Time Dependent Hamiltonian
        self.timeKey = ''

        # Default Simulation Parameters
        # time parameters
        self.finalTime = 1  # total time of simulation
        self.StepSize = 0.02  # sampling time step

        # sweep parameters
        self.sweepKey = ''
        self.sweepMax = 3
        self.sweepMin = -3
        self.sweepPerturbation = 0.05

        # Saving Options
        self.irregular = False

    def __del__(self):
        class_name = self.__class__.__name__


    @property
    def qSys(self):
        return self.__qSys

    @qSys.setter
    def qSys(self, val):
        QuantumSystem.constructCompSys(val)
        self.__qSys = val

    @property
    def times(self):
        return np.arange(0, self.finalTime + self.StepSize, self.StepSize)

    @property
    def sweepList(self):
        return np.arange(self.sweepMin, self.sweepMax + self.sweepPerturbation, self.sweepPerturbation)

    def evolveTimeIndep(self, QSys, sweep):
        if hasattr(QSys, self.sweepKey):
            setattr(QSys, self.sweepKey, sweep)
        elif hasattr(self, self.sweepKey):
            setattr(self, self.sweepKey, sweep)
        else:
            print("Key is not an atribute")

        if self.qSys.Unitaries is None:
            unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam, timeStep=self.StepSize)
        else:
            unitary = self.qSys.Unitaries(self.qSys, self.StepSize)

        state = self.qSys.initialState
        if self.allStates:
            states = [state]
            for ii in range(len(self.times) - 1):
                state = unitary @ state
                states.append(state)
            return states
        else:
            for ii in range(len(self.times) - 1):
                state = unitary @ state
            return state

    def randStep(self, QSys, sweep):
        if hasattr(QSys, self.sweepKey):
            setattr(QSys, self.sweepKey, sweep)
        elif hasattr(self, self.sweepKey):
            setattr(self, self.sweepKey, sweep)
        else:
            print("no attribute")

        UnitaryList = []
        for stepSize in self.yData:
            UnitaryList.append(self.qSys.Unitaries(self.qSys, stepSize))

        state = self.qSys.initialState
        if self.allStates:
            states = [state]
            for ijkn in range(len(UnitaryList)):
                unitary = UnitaryList[ijkn]
                state = unitary @ state
                states.append(state)
            return states
        else:
            for ijkn in range(UnitaryList):
                unitary = UnitaryList[ijkn]
                state = unitary @ state
            return state

    def evolveTimeDep(self, Qsys, sweep):
        state = self.qSys.initialState
        states = []
        for value in sweep:
            setattr(Qsys, self.timeKey, value)
            unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam, timeStep=self.StepSize)

            state = unitary @ state
            states.append(state)

        return states

    def evolveTD_get_excitations(self, Qsys, sweep):
        state = self.qSys.initialState
        excitations_sweep = []

        for value in sweep:
            setattr(Qsys, self.timeKey, value)
            unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam, timeStep=self.StepSize)
            state = unitary @ state

            eigen_values, eigen_states = sp.linalg.eig(self.qSys.totalHam.A)

            sort = np.argsort(eigen_values)
            eigen_states = np.transpose(eigen_states.conj())[sort]

            excitations = (np.abs(np.transpose(eigen_states @ state))**2)[0]
            excitations_sweep.append(excitations)

        return np.transpose(excitations_sweep)

