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

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `genericProtocol`          |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
      `qProtocol`                |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
      `copyStep`                 |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
      `freeEvolution`            |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
      `Gate`                     |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
      `Update`                   |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============

"""
from ..QuantumToolbox import evolution as lio #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox.operators import identity #pylint: disable=relative-beyond-top-level

from .base import qBase, addDecorator
from .baseClasses import updateBase
from .QSimBase import _parameter
from .QSimComp import QSimComp
from .QSweep import Sweep

class genericProtocol(QSimComp): # pylint: disable = too-many-instance-attributes
    label = 'genericProtocol'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    #: (**class attribute**) to store number of exponentiations, incremented by _increaseExponentiationCount method
    numberOfExponentiations = 0

    @classmethod
    def _increaseExponentiationCount(cls):
        r"""
        This is a classmethod (used internally) to increment the `numberOfExponentiations` count.
        """
        cls.numberOfExponentiations += 1
        return cls.numberOfExponentiations

    __slots__ = ['__currentState', '__inProtocol', '__fixed', '__ratio', '__updates', '__dissipator', '_openSys',
                 '_getUnitary', 'timeDependency', '__identity', 'sampleStates', 'stepSample']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: during time evolution, the current state of the protocol at the current time is stored in this attribute
        #: it is an instance of `_parameter` so that the nested-protocols can refer to the same state that is store
        #: by the outer-most protocol.
        self.__currentState = _parameter()
        #: stores an identity matrix with the total dimension of the system of the protocol.
        #: this is used internally and introduces slight performance enhancement.
        self.__identity = None
        #: some steps might be used more than once in the same protocol or in different protocol/s. with this boolean,
        #: it is determined if self is already a step in a protocol, so that a `copyStep` (of self) is used when self is
        #: used again as a step in the same protocol or in different protocol/s.
        self.__inProtocol = False
        #: when parameters of a step are going to be fixed during the whole simulation (including parameter sweeps),
        #: we can label it as fixed to optimize number of exponentiations.
        self.__fixed = False
        #: ratio of the stepSize of self to the stepSize of simulation. Used for higher order Trotterisations, so that
        #: there is only one step size to be swept and the relative step sizes are determined by this ratio, which
        #: might also be negative as required by higher (than 2) Trotterisation orders.
        self.__ratio = 1
        #: stores a list of updates for this protocol/step.
        self.__updates = []
        #: when constructing the unitary evolution of a protocol, certain parts of this creation might be replaced by
        #: other methods depending on the solution method we used. this attribute stores the `_getUnitary`, which is
        #: part of getUnitary method that (uses createUnitary and) returns the unitary matrix.
        # TODO docs - Create a tutorial explaning _getUnitary.
        self._getUnitary = self._defGetUnitary
        #: when we use compute function with delStates, we might want to sample several number of time-steps first, then
        #: call the compute, which might provide performance benefits when using other solution methods than matrix
        #: exponentiation. This list is used for this purpose (and also relies on samples number of self.simulation).
        # TODO requires a tutorial and NOTE not completely decided on every detail of how to use this.
        self.sampleStates = []
        #: boolean to determine if a single state or a list of states is samples (related to sampleStates)
        self.stepSample = False
        #: This is an instance of sweep class, but it is called at every time-step, so that we can change a parameter
        #: as a function of time.
        # TODO new approach of _timeDependency method in QSystem is much more flexible and
        # intuitive than this, and I will more that approach to QSimComp class to make it also available here.
        self.timeDependency = Sweep(superSys=self)
        #: a dictionary to store the dissipator objects used in open-system simulations
        self.__dissipator = {}
        #: boolean to determine if it is an open-system simulation.
        self._openSys = False
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def dimension(self):
        return 1

    @property
    def _dissipator(self):
        return self._genericProtocol__dissipator

    @property
    def _isOpen(self):
        subOpen = any((s._isOpen for s in self.subSys.values() if hasattr(s, '_isOpen'))) # pylint: disable=protected-access
        self._openSys = len(self._dissipator) > 0 or subOpen or self._openSys
        for s in self.subSys.values():
            if hasattr(s, '_openSys'):
                s._openSys = self._openSys # pylint: disable=protected-access
        return self._openSys

    @property
    def currentState(self):
        return self._genericProtocol__currentState.value

    @currentState.setter
    def currentState(self, inp):
        self._genericProtocol__currentState.value = inp

    @QSimComp.initialState.setter # pylint: disable=no-member
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

    @QSimComp.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        QSimComp.superSys.fset(self, supSys) # pylint: disable=no-member
        supSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        if self.simulation._timeBase__bound is None:
            self.simulation._bound(supSys.simulation) # pylint: disable=protected-access
        self.simulation._qBase__subSys[self] = self.superSys # pylint: disable=protected-access

    def unitary(self):
        collapseOps = None if not self._isOpen else [ds.jOperMatrix for ds in self._dissipator.keys()]
        decayRates = None if not self._isOpen else list(self._dissipator.values())
        if self.superSys is not None:
            self.superSys._timeDependency() # pylint: disable=no-member

        if self._paramUpdated:
            if not self.fixed:
                self._paramBoundBase__matrix = self.getUnitary(collapseOps, decayRates) # pylint: disable=assigning-non-slot
        elif self._paramBoundBase__matrix is None: # pylint: disable=no-member
            self._paramBoundBase__matrix = self.getUnitary(collapseOps, decayRates) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def getUnitary(self, collapseOps = None, decayRates = None):
        if collapseOps is None:
            collapseOps = None if not self._isOpen else [ds.jOperMatrix for ds in self._dissipator.keys()]
            decayRates = None if not self._isOpen else list(self._dissipator.values())
        else:
            collapseOps = collapseOps + [ds.jOperMatrix for ds in self._dissipator.keys()]
            decayRates = decayRates + list(self._dissipator.values())
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

            unitary = self._identity(openSys=self._isOpen)
            for ind in range(lc):
                if td:
                    self.timeDependency.runSweep(self.timeDependency._indicesForSweep(ind, *self.timeDependency.inds))
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
        super().__init__(_internal=kwargs.pop('_internal', False))
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

    def addSubSys(self, subSys, **kwargs):
        return self.addStep(subSys, **kwargs)

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
        unitary = self._identity(openSys=self._isOpen) # pylint: disable=no-member
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
        super().__init__(_internal=kwargs.pop('_internal', False))
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
        return self.superSys.unitary()

    def unitary(self): #pylint:disable=unused-argument
        return self.superSys.unitary()

    @property
    def _isOpen(self):
        return self.superSys._isOpen # pylint: disable=protected-access

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
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    _freqCoef = 1 #2 * np.pi
    def matrixExponentiation(self, collapseOps = None, decayRates = None):
        self._increaseExponentiationCount()
        hamiltonian = self.superSys.totalHam if hasattr(self.superSys, 'totalHam') else self.superSys.totalHamiltonian #pylint:disable=no-member
        unitary = lio.LiouvillianExp(self._freqCoef * hamiltonian, # pylint: disable=no-member
                                     timeStep=((self.simulation.stepSize*self.ratio)/self.simulation.samples),
                                     collapseOperators=collapseOps, decayRates=decayRates)
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
        super().__init__(_internal=kwargs.pop('_internal', False))
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
        super().__init__(_internal=kwargs.pop('_internal', False))
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
