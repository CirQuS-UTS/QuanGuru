import qTools.QuantumToolbox.evolution as lio
from qTools.classes.timeBase import timeBase
from qTools.QuantumToolbox.operators import identity
import numpy as np
from qTools.classes.updateBase import updateBase
from qTools.classes.QUni import qUniversal
""" under construction """

class qProtocol(timeBase):
    instances = 0
    label = 'qProtocol'
    __slots__  = ['__unitary', 'lastState']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__unitary = None
        self.lastState = None
        self._qUniversal__setKwargs(**kwargs)

    @timeBase.superSys.setter
    def superSys(self, supSys):
        timeBase.superSys.fset(self, supSys)
        self.qRes.name = self.superSys.name + self.name + 'Results'

    @property
    def steps(self):
        return self._qUniversal__subSys

    @steps.setter
    def steps(self, stps):
        self.addStep(*stps)

    def addStep(self, *args):
        for ii, step in enumerate(args):
            if step in self.steps.values():
                super().addSubSys(copyStep(step))
            else:
                super().addSubSys(step)
                # TODO is this really necessary ?
                if step.superSys is None:
                    step.superSys = self.superSys

    def createStep(self, n=1):
        newSteps = []
        for ind in range(n):
            newSteps.append(super().createSubSys(Step()))
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
        unitary = identity(self.superSys.dimension)
        for step in self.steps.values():
            unitary = step.createUnitary() @ unitary
        self._qProtocol__unitary = unitary
        return unitary

    def prepare(self, obj):
        super().prepare(obj)
        for step in self.steps.values():
            if not isinstance(step, copyStep):
                step.prepare(self)
                if not isinstance(step, qProtocol):
                    if step.fixed is True:
                        step.getUnitary()
                        #step.createUnitary = step.createUnitaryFixedFunc

    def delMatrices(self):
        self._qProtocol__unitary = None
        for step in self.steps.valus():
            if not isinstance(step, copyStep):
                step.delMatrices()

class Step(timeBase):
    instances = 0
    label = 'Step'
    __slots__ = ['__unitary', '__ratio', '__updates', '__fixed','__bound', 'lastState']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__unitary = None
        self.__ratio = None
        self.__updates = []
        self.__fixed = False
        self.__bound = self
        self.lastState = None
        self._qUniversal__setKwargs(**kwargs)

    @timeBase.superSys.setter
    def superSys(self, supSys):
        timeBase.superSys.fset(self, supSys)
        if supSys is not None:
            if hasattr(self.superSys, '_genericQSys__unitary'):
                if self is self.superSys._genericQSys__unitary:
                    self.qRes.name = self.superSys.name + 'Results'
            else:
                self.qRes.name = self.superSys.name + self.name + 'Results'

    @property
    def updates(self):
       return self._Step__updates

    @property
    def ratio(self):
        return self._Step__ratio

    @ratio.setter
    def ratio(self, val):
        self._Step__ratio = val

    @property
    def fixed(self):
        return self._Step__fixed

    @fixed.setter
    def fixed(self, boolean):
        self._Step__fixed = boolean

    def createUnitary(self):
        if ((self.superSys._paramUpdated is True) or (self.bound._paramUpdated is True)):
            self._paramUpdated = True

        if self._paramUpdated is False:
            return self._Step__unitary
        elif self.fixed is True:
            return self._Step__unitary
        elif len(self._Step__updates) == 0:
            return self.getUnitary()
        else:
            for update in self._Step__updates:
                update.setup() 
            unitary = self.getUnitary()
            for update in self._Step__updates:
                update.setback()
            return unitary

    @property
    def unitary(self):
        if self._Step__unitary is not None:
            if ((self.superSys._paramUpdated is False) and (self.bound._paramUpdated is False)):
                self._paramUpdated = False

            if self._timeBase__paramUpdated is False:
                unitary = self._Step__unitary
            else:
                unitary = self.createUnitary()
                self._paramUpdated = False
                self.superSys._paramUpdated = False
                self.bound._paramUpdated = False
            return unitary
        else:
            return self.createUnitary()

    def createUpdate(self, **kwargs):
        update = Update(**kwargs)
        self.addUpdate(update)
        return update
    
    def addUpdate(self, *args):
        for update in args:
            self._Step__updates.append(update)
        #self.getUnitary = self.getUnitaryUpdate

    def getUnitary(self):
        pass

    def prepare(self, obj):
        super().prepare(obj)
        if self.ratio is None:
            self.ratio = 1

    def delMatrices(self):
        if self.fixed is True:
            self.createUnitary = self.createUnitaryFunc
        self._Step__unitary = None

class copyStep(qUniversal):
    instances = 0
    label = 'copyStep'
    __slots__ = []
    def __init__(self, superSys, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.superSys = superSys
        self._qUniversal__setKwargs(**kwargs)
    
    def createUnitary(self):
        return self.superSys._Step__unitary
        
class freeEvolution(Step):
    instances = 0
    label = 'freeEvolution'
    __slots__  = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs)

    def getUnitary(self):
        super().getUnitary()
        unitary = lio.LiouvillianExp(2 * np.pi * self.superSys.totalHam, timeStep=((self.stepSize*self.ratio)/self.samples))
        self._Step__unitary = unitary
        return unitary

class Gate(Step):
    instances = 0
    label = 'Gate'
    __slots__ =  ['__implementation']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__implementation = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def implementation(self):
        return self._Gate__implementation

    @implementation.setter
    def implementation(self, typeStr):
        self._Gate__implementation = typeStr

class Update(updateBase):
    instances = 0
    label = 'Update'
    slots = ['value', '__memoryValue', '__memoryBool']
    def __init__ (self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.value = None
        self.__memoryValue = None
        self.__memoryBool = None
        self._qUniversal__setKwargs(**kwargs)
        
    @property
    def key(self):
        return self._updateBase__key

    @key.setter
    def key(self, keyStr):
        self._updateBase__key = keyStr

    def setup(self):
        self._Update__memory = getattr(self.system, self.key)
        self._Update__memoryBool = self.system._paramUpdated
        super()._runUpdate(self.value)
    
    def setback(self):
        super()._runUpdate(self._Update__memory)
        self.system._paramUpdated = self._Update__memoryBool
