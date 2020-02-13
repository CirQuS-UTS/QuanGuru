import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp


def evolveTimeIndep(obj, sweep):
    setattr(obj, obj.superSys.superSys.sweep._Sweep__Systems[obj].sweepKey, sweep)


    if obj.superSys.superSys.qSys.Unitaries is None:
        unitary = lio.Liouvillian(2 * np.pi * obj.superSys.superSys.qSys.totalHam, timeStep=obj.superSys.superSys.timeSweep.sweepPert)
    else:
        unitary = obj.superSys.superSys.qSys.Unitaries(obj.superSys.superSys.qSys, obj.superSys.superSys.timeSweep.sweepPert)

    state = obj.superSys.superSys.qSys.initialState
    if obj.superSys.superSys.allStates:
        states = [state]
        for ii in range(len(obj.superSys.superSys.times) - 1):
            state = unitary @ state
            states.append(state)
        return states
    else:
        for ii in range(len(obj.superSys.superSys.times) - 1):
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

