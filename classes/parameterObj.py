import numpy as np
from SaveRead.saveH5 import saveData
from datetime import datetime
import types


class ParamObj(object):
    def __init__(self, name):
        self.name = name
        self.results = {}
        self.states = []

        ################# Default System Parameters #################
        self.g = 1.79
        self.resonatorDimension = 200
        self.resonatorFrequency = 2
        self.qubitFreqJC = 0
        self.qubitFreqAJC = 0
        self.qubitFreq = 0
        self.offset = 0

        ################ Default Simulation Parameters ##################
        # time parameters
        self.finalTime = 1.2                        # total time of simulation
        self.StepSize = 0.02                        # sampling time step
        self.constantStepSize = True                # is sampling time step constant at each step
        self.StepSizeList = [0.02]                  # list of sampling time steps if sampling is not constant
        self.subTrotter = False                     # is each sampling step composed of multiple DQS steps
        self.trotterStep = self.StepSize            # Trotter step size in DQS
        self.constantTrotterStep = True             # is Trotter step size constant at each step
        self.TrotterStepList = self.StepSizeList    # list of Trotter steps if bot constant at each step
        self.bitflipTime = 0.04

        # sweep parameters
        self.sweepKey = ''
        self.sweepMax = 3
        self.sweepMin = -3
        self.sweepPerturbation = 0.05

        ################ Time Dependent Hamiltonian ################
        self.timeDepHam = False
        self.timeKey = 'g'
        self.timeDepParam = np.arange(0, 1, 0.1)


        ###################### Default Phase-space ########################
        self.xvec = np.linspace(-4, 4, 80)

    def __del__(self):
        class_name = self.__class__.__name__

    def save(self):
        dic = {'g': self.g, 'resonator Dimension': self.resonatorDimension,
               'resonator Frequency': self.resonatorFrequency, 'qubit frequency': self.qubitFreq,
               'step size': self.StepSize, 'qubitFreqJC': self.qubitFreqJC, 'qubitFreqAJC': self.qubitFreqAJC,
               'finalTime': self.finalTime, 'StepSize': self.StepSize, 'sweepMax': self.sweepMax,
               'sweepMin': self.sweepMin, 'sweepPerturbation': self.sweepPerturbation, 'sweepKey': self.sweepKey}

        now = datetime.now()
        timestamp = datetime.timestamp(now)
        path = saveData(self.results, timestamp, self.irregular)
        saveName = path + '/' + str(timestamp) + '.txt'
        with open(saveName, 'w') as f:
            f.write(' '.join(["%s = %s" % (k, v) for k, v in dic.items()]))
        return self.__del__()

    @classmethod
    def unitary(self):
        pass

    def statesToSave(self, states, key):
        l1 = []
        for ink in range(len(self.sweepList)):
            l2 = []
            for kni in range(len(self.times)):
                l2.append((states[ink][kni]).toarray())
            l1.append(l2)
        self.results[key] = l1

    @property
    def irregular(self):
        return True if self.sweepKey == 'Step Size' else False

    @property
    def TrotterStep(self):
        return self.StepSize if not self.subTrotter else self.trotterStep

    @property
    def times(self):
        return np.arange(0, self.finalTime + self.StepSize, self.StepSize)

    @property
    def ratio(self):
        return ((2 * (self.TrotterStep + self.bitflipTime))/self.TrotterStep) if self.offset != 0 else 2

    @property
    def TrotterTimes(self):
        return np.arange(0, self.StepSize + self.TrotterStep, self.TrotterStep)

    @property
    def sweepList(self):
        return np.arange(self.sweepMin, self.sweepMax + self.sweepPerturbation, self.sweepPerturbation)

    @classmethod
    def addMethod(cls, func):
        return setattr(cls, func.__name__, types.MethodType(func, cls))