import numpy as np
import qTools.QuantumToolbox.evolution as lio
from qTools.QuantumToolbox.operators import identity
from qTools.classes.computeBase import _parameter, qBaseSim
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

    __slots__ = ['__currentState', '__inProtocol', '__fixed', '__ratio', '__updates', '_createUnitary']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__currentState = _parameter()
        self.__inProtocol = False
        self.__fixed = False
        self.__ratio = 1
        self.__updates = []
        self._createUnitary = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def currentState(self):
        return self._genericProtocol__currentState.value

    @currentState.setter
    def currentState(self, inp):
        self._genericProtocol__currentState.value = inp

    @property
    def initialState(self):
        if self.simulation._stateBase__initialState.value is None: # pylint: disable=protected-access
            try:
                self.simulation._stateBase__initialState.value =\
                    self.superSys._initialState(self.simulation._initialStateInput) # pylint: disable=W0212, E1101
            except: # pylint: disable=bare-except
                self.simulation._stateBase__initialState.value = self.superSys.initialState # pylint:disable=W0212,E1101
        return self.simulation._stateBase__initialState.value # pylint: disable=protected-access

    @initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self.simulation._stateBase__initialStateInput.value = inp # pylint: disable=protected-access
        self.simulation._stateBase__initialState.value = self.superSys._initialState(inp) # pylint:disable=W0212,E1101

    def save(self):
        saveDict = super().save()
        stepsDict = {}
        for sys in self.subSys.values():
            stepsDict[sys.name] = sys.save()
        saveDict['steps'] = stepsDict
        return saveDict

    def _runCreateUnitary(self):
        pass

    def getUnitary(self):
        for update in self._genericProtocol__updates:
            update.setup()
        self._runCreateUnitary()
        for update in self._genericProtocol__updates:
            update.setback()
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

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
        self.superSys = supSys # pylint: disable=no-member

    def prepare(self):
        if self.fixed is True:
            self.getUnitary()

        for step in self.subSys.values():
            if isinstance(step, genericProtocol):
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
        supSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        self.simulation._bound(supSys.simulation) # pylint: disable=protected-access
        self.simulation._qUniversal__subSys[self] = self.superSys # pylint: disable=protected-access

    @property
    def unitary(self):
        return self.getUnitary()

class qProtocol(genericProtocol):
    instances = 0
    label = 'qProtocol'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def steps(self):
        return self._qUniversal__subSys # pylint: disable=no-member

    @steps.setter
    def steps(self, stps):
        self.addStep(*stps)

    def addStep(self, *args):
        '''
        Copy step ensures the exponentiation
        '''
        for step in args:
            self._paramBoundBase__paramBound[step.name] = step # pylint: disable=no-member
            if step._genericProtocol__inProtocol:
                super().addSubSys(copyStep(step))
            else:
                super().addSubSys(step)
                step._genericProtocol__inProtocol = True
                step._genericProtocol__currentState._bound = self._genericProtocol__currentState #pylint:disable=W0212,E1101
                step.simulation._bound(self.simulation, re=True) # pylint: disable=protected-access
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
        self._paramBoundBase__matrix = unitary # pylint: disable=assigning-non-slot


class Step(genericProtocol):
    instances = 0
    label = 'Step'

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._createUnitary = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def _runCreateUnitary(self):
        super()._runCreateUnitary()
        self._funcToCreateUnitary() # pylint: disable=assigning-non-slot

    def getUnitary(self):
        if self._paramUpdated:
            if not self.fixed:
                super().getUnitary()

        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
            super().getUnitary()

        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _funcToCreateUnitary(self):
        if not callable(self._createUnitary):
            raise TypeError('?')
        self._paramBoundBase__matrix = self._createUnitary() # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

class copyStep(qUniversal):
    instances = 0
    label = 'copyStep'

    __slots__ = []

    def __init__(self, superSys, **kwargs):
        super().__init__()
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
    _externalInstances = 0
    _internalInstances = 0
    label = 'freeEvolution'

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._createUnitary = self.matrixExponentiation
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def matrixExponentiation(self):
        self._increaseExponentiationCount()
        unitary = lio.LiouvillianExp(2 * np.pi * self.superSys.totalHam, # pylint: disable=no-member
                                     timeStep=((self.simulation.stepSize*self.ratio)/self.simulation.samples))
        self._paramBoundBase__matrix = unitary # pylint: disable=assigning-non-slot
        return unitary

class Gate(Step):
    instances = 0
    label = 'Gate'

    __slots__ = ['__implementation']

    def __init__(self, **kwargs):
        super().__init__()
        self.__implementation = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @Step.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        Step.superSys.fset(self, supSys) # pylint: disable=no-member
        self.addSubSys(supSys)

    @property
    def system(self):
        return list(self.subSys.values())

    @system.setter
    def system(self, sys):
        if not isinstance(sys, list):
            sys = [sys]
        for s in tuple(*[sys]):
            self.addSubSys(s)
        self.superSys = tuple(sys)[0]

    def addSys(self, sys):
        self.system = sys

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
        super().__init__()
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
        self._Update__memoryValue = getattr(list(self.subSys.values())[0], self.key) # pylint:disable=assigning-non-slot
        for sys in self.subSys.values():
            if self._Update__memoryValue != getattr(sys, self.key): # pylint: disable=assigning-non-slot
                raise ValueError('?')

        if self.value != self.memoryValue:
            super()._runUpdate(self.value)

    def _setback(self):
        if self.value != self.memoryValue:
            super()._runUpdate(self._Update__memoryValue)
