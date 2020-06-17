import numpy as np
import qTools.QuantumToolbox.evolution as lio
from qTools.QuantumToolbox.operators import identity
from qTools.classes.computeBase import _parameter, qBaseSim
from qTools.classes.updateBase import updateBase
from qTools.classes.QUni import qUniversal
from qTools.classes.Sweep import Sweep

# under construction

class genericProtocol(qBaseSim): # pylint: disable = too-many-instance-attributes
    instances = 0
    label = 'genericProtocol'
    numberOfExponentiations = 0

    @classmethod
    def _increaseExponentiationCount(cls):
        cls.numberOfExponentiations += 1

    __slots__ = ['__currentState', '__inProtocol', '__fixed', '__ratio', '__updates',
                 '_getUnitary', 'timeDependency', '__identity']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__currentState = _parameter()
        self.__identity = None
        self.__inProtocol = False
        self.__fixed = False
        self.__ratio = 1
        self.__updates = []
        self._getUnitary = self._defGetUnitary
        self.timeDependency = Sweep(superSys=self)
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def currentState(self):
        return self._genericProtocol__currentState.value

    @currentState.setter
    def currentState(self, inp):
        self._genericProtocol__currentState.value = inp

    @qBaseSim.initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self.simulation._stateBase__initialStateInput.value = inp # pylint: disable=protected-access
        self.simulation._stateBase__initialState.value = self.superSys._createAstate(inp) # pylint:disable=W0212,E1101

    def save(self):
        saveDict = super().save()
        stepsDict = {}
        for sys in self.subSys.values():
            stepsDict[sys.name] = sys.save()
        saveDict['steps'] = stepsDict
        return saveDict

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
        if self._paramUpdated:
            if not self.fixed:
                self._paramBoundBase__matrix = self.getUnitary() # pylint: disable=assigning-non-slot
        elif self._paramBoundBase__matrix is None: # pylint: disable=no-member
            self._paramBoundBase__matrix = self.getUnitary() # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def getUnitary(self):
        initialBool = self._paramBoundBase__paramUpdated # pylint: disable=no-member,
        for update in self._genericProtocol__updates:
            update.setup()
        self._paramBoundBase__paramUpdated = initialBool # pylint: disable=assigning-non-slot
        self._paramBoundBase__matrix = self._getUnitary() # pylint: disable=no-member, assigning-non-slot
        for update in self._genericProtocol__updates:
            update.setback()
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _defGetUnitary(self):
        runCreate = False
        if self._paramUpdated:
            if not self.fixed:
                runCreate = True
        elif self._paramBoundBase__matrix is None: # pylint: disable=no-member
            runCreate = True

        if runCreate:
            lc = 1
            td = False
            if len(self.timeDependency.sweeps) > 0:
                lc = self.timeDependency.indMultip
                td = False

            unitary = self._identity
            for ind in range(lc):
                if td:
                    self.timeDependency.runSweep(self.timeDependency._indicesForSweep(ind, *self.timeDependency.inds))
                unitary = self._createUnitary() @ unitary # pylint: disable=no-member
            self._paramBoundBase__matrix = unitary # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @property
    def _identity(self):
        if self._genericProtocol__identity is None:
            self._genericProtocol__identity = identity(self.superSys._totalDim) # pylint: disable=E0237, E1101
        elif self._genericProtocol__identity.shape[0] != self.superSys._totalDim: # pylint: disable=E1101
            self._genericProtocol__identity = identity(self.superSys._totalDim) # pylint: disable=E0237, E1101
        return self._genericProtocol__identity

class qProtocol(genericProtocol):
    instances = 0
    label = 'qProtocol'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        #self._createUnitary = self._defCreateUnitary # pylint: disable=assigning-non-slot
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

    def _defCreateUnitary(self):
        unitary = self._identity # pylint: disable=no-member
        for step in self.steps.values():
            unitary = step.getUnitary() @ unitary
        return unitary

qProtocol._createUnitary = qProtocol._defCreateUnitary


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

class freeEvolution(genericProtocol):
    instances = 0
    _externalInstances = 0
    _internalInstances = 0
    label = 'freeEvolution'

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #self._createUnitary = self.matrixExponentiation
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def matrixExponentiation(self):
        self._increaseExponentiationCount()
        unitary = lio.LiouvillianExp(2 * np.pi * self.superSys.totalHam, # pylint: disable=no-member
                                     timeStep=((self.simulation.stepSize*self.ratio)/self.simulation.samples))
        self._paramBoundBase__matrix = unitary # pylint: disable=assigning-non-slot
        return unitary

freeEvolution._createUnitary = freeEvolution.matrixExponentiation

class Gate(genericProtocol):
    instances = 0
    label = 'Gate'

    __slots__ = ['__implementation']

    def __init__(self, **kwargs):
        super().__init__()
        self.__implementation = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @genericProtocol.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        genericProtocol.superSys.fset(self, supSys) # pylint: disable=no-member
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
        if self.value != self.memoryValue:
            super()._runUpdate(self.value)

    def _setback(self):
        if self.value != self.memoryValue:
            super()._runUpdate(self._Update__memoryValue)
