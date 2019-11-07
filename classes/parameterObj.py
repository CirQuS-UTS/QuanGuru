import numpy as np
import SaveRead.saveH5 as saveh
from datetime import datetime
import types


class Simulation(object):
    def __init__(self):
        self.allStates = True
        ################ Time Dependent Hamiltonian ################
        self.timeKey = ''

        ################ Default Simulation Parameters ##################
        # time parameters
        self.finalTime = 1.2  # total time of simulation
        self.StepSize = 0.02  # sampling time step

        # sweep parameters
        self.sweepKey = ''
        self.sweepMax = 3
        self.sweepMin = -3
        self.sweepPerturbation = 0.05

        ###################### Saving Options ########################
        self.irregular = False

    def __del__(self):
        class_name = self.__class__.__name__

class SystemParameters(object):
    """def __init__(self, diction={'g' : 1.79, 'resonatorDimension' : 200, 'resonatorFrequency' : 2, 'qubitFreqJC' : 0,
                                'qubitFreqAJC' : 0 ,'qubitFreq' : 0, 'offset' : 0, 'bitflipTime' : 0.04}):
        #ParamObj.__init__(self, name)
        ################# Default System Parameters #################
        self.__dict__ = diction"""
    def __init__(self):
        #ParamObj.__init__(self, name)
        ################# Default System Parameters #################
        self.g = 1.79
        self.resonatorDimension = 200
        self.resonatorFrequency = 2
        self.qubitFreqJC = 0
        self.qubitFreqAJC = 0
        self.qubitFreq = 0
        self.offset = 0
        self.bitflipTime = 0.04
        self.StepSize = 0.02



    @property
    def ratio(self):
        return ((2 * (self.StepSize + self.bitflipTime)) / self.StepSize) if self.offset != 0 else 2


class Model(object):
    def __init__(self):
        self.results = {}
        self.simulationParameters = Simulation()
        self.systemParameters = SystemParameters()
        self.results['y'] = []
        self.results['x'] = []
        self.timestamp = datetime.timestamp(datetime.now())

    def __del__(self):
        class_name = self.__class__.__name__

    def saveResults(self):
        saveh.saveData(self.results, self.timestamp, self.simulationParameters.irregular, self.simple)
        return self.__del__()

    def saveParameters(self):
        path = saveh.makeDir()
        saveName = path + '/' + str(self.timestamp) + '.txt'
        with open(saveName, 'w') as f:
            f.write(' \n'.join(["%s = %s" % (k, v) for k, v in self.simple.items()]))
        f.close()

    @classmethod
    def unitary(self):
        pass

    def statesToSave(self, states, key):
        l1 = []
        for ink in range(len(states)):
            l2 = []
            for kni in range(len(states[ink])):
                l2.append((states[ink][kni]).toarray())
            l1.append(l2)
        self.results[key] = l1

    @property
    def simple(self):
        dict1 = self.systemParameters.__dict__
        dict2 = self.simulationParameters.__dict__
        return {**dict2, **dict1}

    @property
    def times(self):
        return np.arange(0, self.simulationParameters.finalTime + self.systemParameters.StepSize, self.systemParameters.StepSize)

    @property
    def xvec(self, min=-4, max=4, steps=80):
        return np.linspace(min, max, steps)

    @property
    def timeDepParam(self):
        return np.arange(0, 1, 0.1)

    @property
    def sweepList(self):
        return np.arange(self.simulationParameters.sweepMin, self.simulationParameters.sweepMax
                         + self.simulationParameters.sweepPerturbation, self.simulationParameters.sweepPerturbation)

    @classmethod
    def addMethod(cls, func):
        return setattr(cls, func.__name__, types.MethodType(func, cls))