import QuantumToolbox.liouvillian as lio
import numpy as np


class Simulation(object):
    def __init__(self, QSys):
        self.qSys = QSys
        self.allStates = True
        ################ Time Dependent Hamiltonian ################
        self.timeKey = ''

        ################ Default Simulation Parameters ##################
        # time parameters
        self.finalTime = 1.2  # total time of simulation
        self.StepSize = 0.005  # sampling time step

        # sweep parameters
        self.sweepKey = ''
        self.sweepMax = 3
        self.sweepMin = -3
        self.sweepPerturbation = 0.05

        ###################### Saving Options ########################
        self.irregular = False

    def __del__(self):
        class_name = self.__class__.__name__

    @property
    def times(self):
        return np.arange(0, self.finalTime + self.StepSize, self.StepSize)

    @property
    def sweepList(self):
        return np.arange(self.sweepMin, self.sweepMax + self.sweepPerturbation, self.sweepPerturbation)

    def evolveTimeIndep(self, QSys, sweep):
        setattr(QSys, self.sweepKey, sweep)

        if self.qSys.Unitaries == None:
            unitary = lio.Liouvillian(2 * np.pi * self.qSys.totalHam, timeStep=self.StepSize)
        else:
            unitary = self.qSys.Unitaries(self.qSys, self.StepSize)


        state = self.qSys.initialState
        if self.allStates:
            states = [state]
            for ijkn in range(len(self.times) - 1):
                state = unitary @ state
                states.append(state)
            return states
        else:
            for ijkn in range(len(self.times) - 1):
                state = unitary @ state
            return state