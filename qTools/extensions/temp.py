import qTools.QuantumToolbox.liouvillian as lio
import numpy as np
import scipy.sparse as sp


def evolveTimeIndep(qSim, sweep, value):
    setattr(sweep.superSys, sweep.sweepKey, value)


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

