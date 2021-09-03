r"""
    Contains the classes for protocols.

    .. currentmodule:: quanguru.classes.QPro

    .. autosummary::

        genericProtocol
        qProtocol
        copyStep
        freeEvolution
        Gate
        Update

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
      `genericProtocol`          |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `qProtocol`                |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `copyStep`                 |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `freeEvolution`            |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `Gate`                     |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `Update`                   |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""
import numpy as np

from ..QuantumToolbox.linearAlgebra import hc #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox import evolution as lio #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox.operators import identity #pylint: disable=relative-beyond-top-level

from .base import qBase, addDecorator
from .baseClasses import _parameter, qBaseSim, updateBase
from .QSweep import Sweep

class genericProtocol(qBaseSim): # pylint: disable = too-many-instance-attributes
    label = 'genericProtocol'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    numberOfExponentiations = 0

    @classmethod
    def _increaseExponentiationCount(cls):
        cls.numberOfExponentiations += 1

    __slots__ = ['__currentState', '__inProtocol', '__fixed', '__ratio', '__updates',
                 '_getUnitary', 'timeDependency', '__identity', 'sampleStates', 'stepSample', '_antiStep']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._antiStep = False
        self.__currentState = _parameter()
        self.__identity = None
        self.__inProtocol = False
        self.__fixed = False
        self.__ratio = 1
        self.__updates = []
        self._getUnitary = self._defGetUnitary
        self.sampleStates = []
        self.stepSample = False
        self.timeDependency = Sweep(superSys=self)
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

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

    def prepare(self, collapseOps = None, decayRates = None):
        if self.fixed is True:
            self.getUnitary(collapseOps, decayRates)

        for step in self.subSys.values():
            if isinstance(step, genericProtocol):
                step.prepare(collapseOps, decayRates)

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
        if self.simulation._timeBase__bound is None:
            self.simulation._bound(supSys.simulation) # pylint: disable=protected-access
        self.simulation._qBase__subSys[self] = self.superSys # pylint: disable=protected-access

    def unitary(self, collapseOps = None, decayRates = None):
        if self.superSys is not None:
            self.superSys._timeDependency() # pylint: disable=no-member

        if self._paramUpdated:
            if not self.fixed:
                self._paramBoundBase__matrix = self.getUnitary(collapseOps, decayRates) # pylint: disable=assigning-non-slot
        elif self._paramBoundBase__matrix is None: # pylint: disable=no-member
            self._paramBoundBase__matrix = self.getUnitary(collapseOps, decayRates) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def getUnitary(self, collapseOps = None, decayRates = None):
        if self.superSys is not None:
            self.superSys._timeDependency() # pylint: disable=no-member

        for update in self._genericProtocol__updates:
            update.setup()
        self._paramBoundBase__matrix = self._getUnitary(collapseOps, decayRates) # pylint: disable=no-member, assigning-non-slot
        for update in self._genericProtocol__updates:
            update.setback()
        self._paramUpdatedToFalse()
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _paramUpdatedToFalse(self):
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot

    def _defGetUnitary(self, collapseOps = None, decayRates = None):
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
                td = True

            unitary = self._identity(openSys=isinstance(collapseOps, list))
            #print(isinstance(collapseOps, list), unitary.shape, self.alias)
            for ind in range(lc):
                if td:
                    self.timeDependency.runSweep(self.timeDependency._indicesForSweep(ind, *self.timeDependency.inds))
                #print(self._createUnitary(collapseOps, decayRates).shape, self.name, self.alias, unitary.shape)
                unitary = self._createUnitary(collapseOps, decayRates) @ unitary # pylint: disable=no-member
            self._paramBoundBase__matrix = unitary # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def _identity(self, openSys=False):
        dimension = 0
        if self.superSys is None:
            dimension = list(self.subSys.values())[0]._totalDim#pylint:disable=E0237,E1101
        dimension = self.superSys._totalDim if (dimension == 0) else dimension # pylint: disable=E0237, E1101
        #elif self._genericProtocol__identity is None:
        #    dimension = self.superSys._totalDim # pylint: disable=E0237, E1101
        #elif self._genericProtocol__identity.shape[0] != self.superSys._totalDim: # pylint: disable=E1101
        #    dimension = self.superSys._totalDim # pylint: disable=E0237, E1101
        self._genericProtocol__identity = identity(dimension = dimension**2 if openSys else dimension)# pylint: disable=E0237, E1101
        return self._genericProtocol__identity

class qProtocol(genericProtocol):
    label = 'qProtocol'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        #self._createUnitary = self._defCreateUnitary # pylint: disable=assigning-non-slot
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def _paramUpdatedToFalse(self):
        super()._paramUpdatedToFalse()
        for step in self.subSys.values():
            step._paramUpdatedToFalse()

    @genericProtocol._paramUpdated.getter
    def _paramUpdated(self):# pylint: disable=invalid-overridden-method
        for subS in self.subSys.values():
            if subS._paramUpdated:
                self._paramBoundBase__paramUpdated = True # pylint: disable=assigning-non-slot
                break
        return self._paramBoundBase__paramUpdated # pylint: disable=no-member

    @property
    def steps(self):
        return self._qBase__subSys # pylint: disable=no-member

    @steps.setter
    def steps(self, stps):
        self.addStep(*stps)

    def addStep(self, *args):
        '''
        Copy step ensures the exponentiation
        '''
        for step in args:
            if isinstance(step, copyStep):
                super().addSubSys(step)
            elif step._genericProtocol__inProtocol:
                super().addSubSys(copyStep(step))
            else:
                super().addSubSys(step)
                step._genericProtocol__inProtocol = True
                step._genericProtocol__currentState._bound = self._genericProtocol__currentState #pylint:disable=W0212,E1101
                step.simulation._bound(self.simulation, re=True) # pylint: disable=protected-access
                if ((step.superSys is None) and (self.superSys is not None)):
                    step.superSys = self.superSys

    def _puValues(self, step, vals):#pylint:disable=dangerous-default-value
        subSysList = list(self.subSys.values())
        ind = subSysList.index(step) + 1
        if len(vals) == 0:
            for st in subSysList[ind:]:
                vals.append(st._paramUpdated)
        else:
            for ind2, st in enumerate(subSysList[ind:]):
                st._paramUpdated = vals[ind2]
        return vals

    def _defCreateUnitary(self, collapseOps = None, decayRates = None):
        unitary = self._identity(openSys=isinstance(collapseOps, list)) # pylint: disable=no-member
        for step in self.steps.values():
            vals = self._puValues(step, [])
            unitary = step.getUnitary(collapseOps, decayRates) @ unitary
            self._puValues(step, vals)
        return unitary

qProtocol._createUnitary = qProtocol._defCreateUnitary

class copyStep(qBase):
    label = 'copyStep'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []

    def __init__(self, superSys, **kwargs):
        super().__init__()
        self.superSys = superSys
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def _paramUpdatedToFalse(self):
        pass

    @property
    def _paramUpdated(self):
        return self.superSys._paramUpdated

    @property
    def simulation(self):
        return self.superSys.simulation

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        pass

    def getUnitary(self, collapseOps = None, decayRates = None): #pylint:disable=unused-argument
        return self.superSys.unitary(collapseOps, decayRates)

    def unitary(self, collapseOps = None, decayRates = None): #pylint:disable=unused-argument
        return self.superSys.unitary(collapseOps, decayRates)

class freeEvolution(genericProtocol):
    label = 'freeEvolution'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #self._createUnitary = self.matrixExponentiation
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    _freqCoef = 2 * np.pi
    def matrixExponentiation(self, collapseOps = None, decayRates = None):
        collapseOpsA = [hc(op) for op in collapseOps] if self._antiStep else collapseOps
        self._increaseExponentiationCount()
        unitary = lio.LiouvillianExp(self._freqCoef * self.superSys.totalHam, # pylint: disable=no-member
                                     timeStep=((self.simulation.stepSize*self.ratio)/self.simulation.samples),
                                     collapseOperators=collapseOpsA, decayRates=decayRates)
        self._paramBoundBase__matrix = unitary # pylint: disable=assigning-non-slot
        return unitary

freeEvolution._createUnitary = freeEvolution.matrixExponentiation

class Gate(genericProtocol):
    label = 'Gate'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__implementation']

    def __init__(self, **kwargs):
        super().__init__()
        self.__implementation = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def system(self):
        return list(self.subSys.values())

    @addDecorator
    def addSubSys(self, subSys, **kwargs):
        newSys = super().addSubSys(subSys, **kwargs)
        if self.simulation._timeBase__bound is None:
            self.simulation._bound(newSys.simulation) # pylint: disable=protected-access
        # FIXME this becomes 'fixed' unless the dimension is changed.
        #if self.implementation.lower() != 'instant':
        newSys._paramBoundBase__paramBound[self.name] = self
        return newSys

    @system.setter
    def system(self, sys):
        self.addSubSys(sys)

    def addSys(self, sys):
        self.system = sys

    @property
    def implementation(self):
        return self._Gate__implementation

    @implementation.setter
    def implementation(self, typeStr):
        self._Gate__implementation = typeStr # pylint: disable=assigning-non-slot

class Update(updateBase):
    label = 'Update'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['value', '__memoryValue', 'setup', 'setback']

    def __init__(self, **kwargs):
        super().__init__()
        self.value = None
        self.setup = self._setup
        self.setback = self._setback
        self.__memoryValue = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def memoryValue(self):
        return self._Update__memoryValue

    @memoryValue.setter
    def memoryValue(self, value):
        self._Update__memoryValue = value # pylint: disable=assigning-non-slot

    @property
    def updateFunction(self):
        """
        The updateFunction property:

        - **getter** : ``returns _updateBase__function`` which is used in custom sweeps
        - **setter** : sets ``_updateBase__function`` callable
        - **type** : ``callable``
        """

        return self._updateBase__function # pylint: disable=no-member

    @updateFunction.setter
    def updateFunction(self, func):
        self._updateBase__function = func # pylint: disable=assigning-non-slot

    def _setup(self):
        self.memoryValue = getattr(list(self.subSys.values())[0], self.key)
        if self._updateBase__function is None: # pylint: disable=no-member
            super()._runUpdate(self.value)
        else:
            self._updateBase__function(self) # pylint: disable=no-member

    def _setback(self):
        if self.value != self.memoryValue:
            super()._runUpdate(self.memoryValue)
