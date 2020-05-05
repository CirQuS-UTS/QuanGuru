import numpy as np
import qTools.QuantumToolbox.evolution as lio
from qTools.QuantumToolbox.operators import identity
from qTools.classes.qBaseSim import qBaseSim
from qTools.classes.updateBase import updateBase
from qTools.classes.QUni import qUniversal

# under construction

class genericProtocol(qBaseSim):
    instances = 0
    label = 'genericProtocol'
    numberOfExponentiations = 0

    @classmethod
    def _increaseExponentiationCount(cls):
        cls.numberOfExponentiations += 1

    __slots__ = ['lastState', '__inProtocol', '__fixed', '__ratio', '__updates', '_funcToCreateUnitary']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.lastState = None
        self.__inProtocol = False
        self.__fixed = False
        self.__ratio = 1
        self.__updates = []
        self._funcToCreateUnitary = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        stepsDict = {}
        for sys in self.subSys.values():
            stepsDict[sys.name] = sys.save()
        saveDict['steps'] = stepsDict
        return saveDict

    def _runCreateUnitary(self):
        pass

    def getUnitary(self, callAfterUpdate=_runCreateUnitary):
        for update in self._genericProtocol__updates:
            update.setup()
        callAfterUpdate(self)
        for update in self._genericProtocol__updates:
            update.setback()

    def createUpdate(self, **kwargs):
        update = Update(**kwargs)
        self.addUpdate(update)
        return update

    def addUpdate(self, *args):
        for update in args:
            self._genericProtocol__updates.append(update) # pylint: disable=no-member

    @property
    def updates(self):
        return self._genericProtocol__updates

    @property
    def ratio(self):
        return self._genericProtocol__ratio

    @ratio.setter
    def ratio(self, val):
        self._genericProtocol__ratio = val # pylint: disable=assigning-non-slot

    @property
    def system(self):
        return self.superSys

    @system.setter
    def system(self, supSys):
        qBaseSim.superSys.fset(self, supSys) # pylint: disable=no-member

    def prepare(self):
        if self.fixed is True:
            self.getUnitary()

        for step in self.subSys.values():
            if not isinstance(step, copyStep):
                step.prepare()

    @property
    def fixed(self):
        return self._genericProtocol__fixed

    @fixed.setter
    def fixed(self, boolean):
        self._genericProtocol__fixed = boolean # pylint: disable=assigning-non-slot

    @qBaseSim.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        qBaseSim.superSys.fset(self, supSys) # pylint: disable=no-member
        supSys._qBase__paramBound[self.name] = self # pylint: disable=protected-access

    @property
    def unitary(self):
        if self._qUniversal__matrix is not None: # pylint: disable=no-member
            if ((self.fixed is True) or (self._paramUpdated is False)):
                unitary = self._qUniversal__matrix # pylint: disable=no-member
            else:
                unitary = self.getUnitary() # pylint: disable=assignment-from-no-return
                self._qBase__paramUpdated = False  # pylint: disable=assigning-non-slot
        else:
            self._qBase__paramUpdated = False  # pylint: disable=assigning-non-slot
            unitary = self.getUnitary() # pylint: disable=assignment-from-no-return
        return unitary

class qProtocol(genericProtocol):
    instances = 0
    label = 'qProtocol'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def steps(self):
        return self._qUniversal__subSys # pylint: disable=no-member

    @steps.setter
    def steps(self, stps):
        self.addStep(*stps)

    def addStep(self, *args):
        for step in args:
            self._qBase__paramBound[step.name] = step # pylint: disable=no-member
            if step._genericProtocol__inProtocol:
                super().addSubSys(copyStep(step))
            else:
                super().addSubSys(step)
                step._genericProtocol__inProtocol = True
                if step.superSys is None:
                    step.superSys = self.superSys

    def createStep(self, n=1):
        newSteps = []
        for _ in range(n):
            newSteps.append(super().createSubSys(Step()))
        return newSteps if n > 1 else newSteps[0]

    def _runCreateUnitary(self):
        super()._runCreateUnitary()
        unitary = identity(self.superSys.dimension) # pylint: disable=no-member
        for step in self.steps.values():
            unitary = step.getUnitary() @ unitary
        self._qUniversal__matrix = unitary # pylint: disable=assigning-non-slot

    def getUnitary(self, callAfterUpdate=_runCreateUnitary):
        super().getUnitary(callAfterUpdate=callAfterUpdate)
        return self._qUniversal__matrix # pylint: disable=no-member


class Step(genericProtocol):
    instances = 0
    label = 'Step'

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._funcToCreateUnitary = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def _runCreateUnitary(self):
        super()._runCreateUnitary()
        self.createUnitary() # pylint: disable=assigning-non-slot

    def getUnitary(self, callAfterUpdate=_runCreateUnitary):
        if ((self.fixed is True) and (self._qUniversal__matrix is None)): # pylint: disable=no-member
            super().getUnitary(callAfterUpdate=callAfterUpdate)
        elif ((self.fixed is False) and ((self._paramUpdated is True) or (self._qUniversal__matrix is None))): # pylint: disable=no-member
            super().getUnitary(callAfterUpdate=callAfterUpdate)
        self._qBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._qUniversal__matrix # pylint: disable=no-member

    def createUnitary(self):
        if not callable(self._funcToCreateUnitary):
            raise TypeError('?')
        self._qUniversal__matrix = self._funcToCreateUnitary() # pylint: disable=assigning-non-slot
        return self._qUniversal__matrix # pylint: disable=no-member

class copyStep(qUniversal):
    instances = 0
    label = 'copyStep'

    __slots__ = []

    def __init__(self, superSys, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.superSys = superSys
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        saveDict['superSys'] = self.superSys.name
        return saveDict

    def getUnitary(self):
        return self.superSys.unitary

class freeEvolution(Step):
    instances = 0
    label = 'freeEvolution'

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._funcToCreateUnitary = self.matrixExponentiation
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def matrixExponentiation(self):
        self._increaseExponentiationCount()
        unitary = lio.LiouvillianExp(2 * np.pi * self.superSys.totalHam, # pylint: disable=no-member
                                     timeStep=((self.simulation.stepSize*self.ratio)/self.simulation.samples))
        self._qUniversal__matrix = unitary # pylint: disable=assigning-non-slot
        return unitary

class Gate(Step):
    instances = 0
    label = 'Gate'

    __slots__ = ['__implementation']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__implementation = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def implementation(self):
        return self._Gate__implementation

    @implementation.setter
    def implementation(self, typeStr):
        self._Gate__implementation = typeStr # pylint: disable=assigning-non-slot

class Update(updateBase):
    instances = 0
    label = 'Update'

    toBeSaved = qUniversal.toBeSaved.extendedCopy(['value'])

    __slots__ = ['value', '__memoryValue', 'setup', 'setback']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.value = None
        self.setup = self._setup
        self.setback = self._setback
        self.__memoryValue = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def memoryValue(self):
        return self._Update__memoryValue

    @memoryValue.setter
    def memoryValue(self, value):
        self._Update__memoryValue = value # pylint: disable=assigning-non-slot

    def _setup(self):
        self._Update__memoryValue = getattr(list(self.subSys.values())[0], self.key) # pylint: disable=assigning-non-slot
        for sys in self.subSys.values():
            if self._Update__memoryValue != getattr(sys, self.key): # pylint: disable=assigning-non-slot
                raise ValueError('?')

        if self.value != self.memoryValue:
            super()._runUpdate(self.value)

    def _setback(self):
        if self.value != self.memoryValue:
            super()._runUpdate(self._Update__memoryValue)
