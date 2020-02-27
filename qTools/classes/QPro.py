import qTools.QuantumToolbox.liouvillian as lio
from qTools.classes.QUni import qUniversal
from qTools.QuantumToolbox.operators import compositeOp
import numpy as np
""" under construction """

class qProtocol(qUniversal):
    instances = 0
    label = 'qProtocol'
    __slots__  = ['__steps', '__unitary']
    def __init__(self, **kwargs):
        super().__init__()
        self.__steps = []
        self.__unitary = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def steps(self):
        return self._qProtocol__steps

    def addStep(self, *args):
        for ii, step in enumerate(args):
            if step in self.steps:
                self.steps.append(copyStep(step))
            else:
                step.superSys = self.superSys
                self.steps.append(step)

    def createStep(self, n=1):
        newSteps = []
        for ind in range(n):
            newSteps.append(Step())
        self._qProtocol__steps.extend(newSteps)
        return newSteps if n > 1 else newSteps[0]

    @property
    def unitary(self):
        if self._qProtocol__unitary is not None:
            return self._qProtocol__unitary
        else:
            return self.createUnitary()

    @unitary.setter
    def unitary(self, uni):
        # TODO generalise this
        if uni is None:
            self.createUnitary()

    def createUnitary(self):
        unitary = self.steps[0].unitary
        for step in self.steps[1:]:
            unitary = step.unitary @ unitary
        self._qProtocol__unitary = unitary
        return unitary

class Step(qUniversal):
    instances = 0
    label = 'Step'
    __slots__ = ['__unitary']
    def __init__(self, **kwargs):
        super().__init__()
        self.__unitary = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def unitary(self):
        return self._Step__unitary

class copyStep(Step):
    instances = 0
    label = 'copyStep'
    __slots__ = []
    def __init__(self, superSys):
        self.superSys = superSys
    
    @property
    def unitary(self):
        return self.superSys._Step__unitary
        
class freeEvolution(Step):
    instances = 0
    label = 'freeEvolution'
    __slots__  = ['__stepSize', '__updates', 'getUnitary', '__fixed', '__sample']
    def __init__(self, **kwargs):
        super().__init__()
        self.__stepSize = 0
        self.__sample = 1
        self.__updates =  []
        self.__fixed = False
        self.getUnitary = self.getUnitaryNoUpdate
        self._qUniversal__setKwargs(**kwargs)

    @property
    def stepSize(self):
        return self._freeEvolution__stepSize

    @stepSize.setter
    def stepSize(self, val):
        self._freeEvolution__stepSize = val

    @property
    def sample(self):
        return self._freeEvolution__sample

    @sample.setter
    def sample(self, val):
        self._freeEvolution__sample = val

    def getUnitaryNoUpdate(self):
        unitary = lio.Liouvillian(2 * np.pi * self.superSys.totalHam, timeStep=(self.stepSize/self.sample))
        self._Step__unitary = unitary
        return unitary
        
    def getUnitaryUpdate(self):
        for update in self.updates:
            update.setup() 
        unitary = self.getUnitaryNoUpdate()
        for update in self.updates:
            update.setback()
        return unitary

    def getFixedUnitary(self):
        return self._Step__unitary

    def createFixed(self):
        unitary = self.getUnitaryNoUpdate()
        return unitary
        
    @property
    def fixed(self):
        return self._freeEvolution__fixed
    
    @fixed.setter
    def fixed(self, cond):
        if cond:
            self.getUnitary = self.getFixedUnitary
        else:
            if len(self.updates) == 0:    
                self.getUnitary = self.getUnitaryNoUpdate
            else:
                self.getUnitary = self.getUnitaryUpdate
        self._freeEvolution__fixed = cond

    def createUpdate(self, **kwargs):
        update = Update(**kwargs)
        self.addUpdate(update)
        return update
    
    def addUpdate(self, *args):
        for update in args:
            self.updates.append(update)
        self.getUnitary = self.getUnitaryUpdate

    def createUnitary(self):
        unitary = self.getUnitary()
        return unitary

    @property
    def unitary(self):
        if self._Step__unitary is not None:
            return self._qProtocol__unitary
        else:
            return self.createUnitary()

    @unitary.setter
    def unitary(self, uni):
        if uni is None:
            self.createUnitary()

class Gate(Step):
    instances = 0
    label = 'Gate'
    __slots__ =  ['__implementation']
    def __init__(self, **kwargs):
        super().__init__()
        self.__implementation = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def implementation(self):
        return self._Gate__implementation

    @implementation.setter
    def implementation(self, typeStr):
        self._Gate__implementation = typeStr


class Update(qUniversal):
    instances = 0
    label = 'Update'
    slots = ['system', 'key', 'value', '__memory']
    def __init__ (self, **kwargs):
        super().__init__()
        self.system = None
        self.key = None
        self.value = None
        self.__memory = None
        self._qUniversal__setKwargs(**kwargs)

    def setup(self):
        self._Update__memory = getattr(self.system, self.key)
        setattr(self.system, self.key, self.value)
    
    def setback(self):
        setattr(self.system, self.key, self._Update__memory)
