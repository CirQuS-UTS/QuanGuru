import QuantumToolbox.liouvillian as lio
import numpy as np

""" under construction """


class Simulation(object):
    def __init__(self, QSys):
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
    def times(self):
        return np.arange(0, self.finalTime + self.StepSize, self.StepSize)

    @property
    def sweepList(self):
        return np.arange(self.sweepMin, self.sweepMax + self.sweepPerturbation,
                         self.sweepPerturbation)

    def evolveTimeIndep(self, QSys, sweep):
        if hasattr(QSys, self.sweepKey):
            setattr(QSys, self.sweepKey, sweep)
        elif hasattr(self, self.sweepKey):
            setattr(self, self.sweepKey, sweep)
        else:
            print("Key is not an atribute")

        if self.qSys.Unitaries is None:
            unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam,
                                      timeStep=self.StepSize)
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

    def evolveTimeDep1(self, Qsys, sweep):
        state = self.qSys.initialState
        states = []
        for value in sweep:
            setattr(Qsys, self.timeKey, value)
            unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam,
                                      timeStep=self.StepSize)

            state = unitary @ state
            states.append(state)

        return states

    def evolveTD_get_excitations(self, Qsys, sweep):
        state = self.qSys.initialState
        states = []
        excitations_sweep = []

        for value in sweep:
            setattr(Qsys, self.timeKey, value)
            unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam,
                                      timeStep=self.StepSize)
            state = unitary @ state
            states.append(state)

            eigen_values, eigen_states = np.linalg.eig(self.qSys.totalHam.A)

            sort = np.argsort(eigen_values)
            eigen_states = np.transpose(eigen_states.conj())[sort]

            excitations = np.abs(np.transpose(eigen_states @ state))**2
            excitations_sweep.append(excitations)

        return excitations_sweep
