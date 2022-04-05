"""
    Contains classes for Quantum systems.

    .. currentmodule:: quanguru.classes.QSys

    .. autosummary::

        genericQSys
        QuantumSystemOld
        compQSystem
        termTimeDep
        term
        qSystem
        qCoupling
        SpinOld
        QubitOld
        CavityOld
        _initStDec
        _computeDef
        _calculateDef

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `genericQSys`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `QuantumSystemOld`         |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `compQSystem`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `termTimeDep`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `term`                     |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `qSystem`                  |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `qCoupling`                |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `SpinOld`                  |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `QubitOld`                 |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `CavityOld`                |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_initStDec`               |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_computeDef`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_calculateDef`            |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============

""" #pylint: disable=too-many-lines

from collections import OrderedDict
from numpy import (int64, int32, int16, ndarray)
from scipy.sparse import issparse

from ..QuantumToolbox import operators as qOps #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox import linearAlgebra as linAlg #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox import states as qSta #pylint: disable=relative-beyond-top-level

from .base import addDecorator, _recurseIfList
from .baseClasses import paramBoundBase
from .QSimComp import QSimComp
from .QSimBase import setAttr
#from quanguru.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from .QPro import freeEvolution

def _initStDec(_createAstate):
    r"""
    Decorater to handle different inputs for initial state creation.
    """
    def wrapper(obj, inp=None):
        if (issparse(inp) or isinstance(inp, ndarray)):
            if inp.shape[0] != obj.dimension:
                raise ValueError('Dimension mismatch')
            state = inp
        else:
            if inp is None:
                inp = obj.simulation._stateBase__initialStateInput.value

            if (issparse(inp) or isinstance(inp, ndarray)):
                if inp.shape[0] != obj.dimension:
                    raise ValueError('Dimension mismatch')
                state = inp
            else:
                if isinstance(obj.dimension, int):
                    state = _createAstate(obj, inp)
                else:
                    state = None
        return state
    return wrapper

def _computeDef(sys, state): # pylint: disable=unused-argument
    r"""
    Dummy compute method used when creating a copy of quantum systems.
    TODO I am not happy with this solution.
    """

def _calculateDef(sys): # pylint: disable=unused-argument
    r"""
    Dummy calculate method used when creating a copy of quantum systems.
    TODO I am not happy with this solution.
    """

class genericQSys(QSimComp):
    r"""
    Base class for both single (:class:`~qSystem`) and composite (:class:`~compQSystem`) quantum system classes, and I
    hope to combine those two classes in here. Currently, a proxy :class:`~QuantumSystem` is introduced as a
    temporary solution.
    """
    #: (**class attribute**) class label used in default naming
    label = 'genericQSys'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__unitary', '__dimension', '__dimsBefore', '__dimsAfter', '_inpCoef']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: an internal :class:`~freeEvolution` protocol, this is the default evolution when a simulation is run.
        self.__unitary = freeEvolution(_internal=True)
        self._genericQSys__unitary.superSys = self # pylint: disable=no-member
        self._QSimComp__simulation.addQSystems(subS=self, Protocol=self._freeEvol) # pylint: disable=no-member
        #: dimension of Hilbert space of the quantum system
        self.__dimension = None
        #: boolean to determine whether initialState inputs contains complex coefficients (the probability amplitudes)
        #: or the populations
        self._inpCoef = False
        #: Total dimension of the other quantum systems **before** ``self`` in a composite system.
        #: It is 1, when ``self``` is the first system in the composite system or ``self`` is not in a composite system.
        self.__dimsBefore = 1
        #: Total dimension of the other quantum systems **after** ``self`` in a composite system.
        #: It is 1, when ``self`` is the last system in the composite system.
        self.__dimsAfter = 1
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def __add__(self, other):
        r"""
        With this method, ``+`` creates a composite quantum system between ``self`` and the ``other`` quantum system.
        """
        if (isinstance(self, compQSystem) and isinstance(other, qSystem)):
            self.addSubSys(other)
            newComp = self
        elif (isinstance(self, compQSystem) and isinstance(other, compQSystem)):
            if len(self.subSys) == 0:
                newComp = other
            else:
                newComp = compQSystem()
                newComp.addSubSys([self, other.copy() if (other is self) else other])
        elif (isinstance(self, qSystem) and isinstance(other, qSystem)):  # noqa: W504
            newComp = compQSystem()
            # FIXME 'stepCount' getter creates problem with None defaults
            newComp.simulation._copyVals(self.simulation, ['totalTime', 'stepSize', 'delStates'])
            newComp.compute = _computeDef
            newComp.simulation.compute = _computeDef
            #newComp.calculate = _calculateDef
            #newComp.simulation.calculate = _calculateDef
            newComp.addSubSys([self, other.copy() if (other is self) else other])
        elif isinstance(self, qSystem) and isinstance(other, compQSystem):
            other.addSubSys(self)
            newComp = other
        elif isinstance(other, (float, int)):
            newComp = self
        return newComp

    def _hasInSubs(self, other):
        r"""
        Returns True if the given system is in self.subSys or in any other subSys nested inside the self.subSys.
        """
        return (other in self.subSys.values() or any(qs._hasInSubs(other) for qs in self.subSys.values())) # pylint:disable=protected-access

    def __sub__(self, other):
        r"""
        With this method, ``-`` removes the ``other`` from ``self``, which should be the composite quantum system
        containing other.
        """
        self._removeSubSysExc(other, _exclude=[])
        return self

    def __rmul__(self, other):
        r"""
        With this method, ``*`` creates a composite quantum system that contains ``N=other`` many quantum systems with
        the same ``type`` as ``self``.
        """
        newComp = compQSystem()
        newComp.addSubSys(self)
        for _ in range(other - 1):
            newComp.addSubSys(self.copy())
        return newComp

    def copy(self, **kwargs): # pylint: disable=arguments-differ
        r"""
        Create a copy of ``self`` and also change the parameter of the newly created copy with ``kwargs``.
        """
        subSysList = []
        for sys in self.subSys.values():
            subSysList.append(sys.copy())

        if isinstance(self, qSystem):
            newSys = super().copy(dimension=self.dimension, terms=subSysList)
        elif isinstance(self, compQSystem):
            newSys = super().copy()
            for sys in subSysList:
                newSys.addSubSys(sys)

        if self.simulation._stateBase__initialStateInput._value is not None:
            newSys.initialState = self.simulation._stateBase__initialStateInput.value #pylint:disable=assigning-non-slot
        newSys._named__setKwargs(**kwargs) #pylint:disable=no-member
        return newSys

    @property
    def ind(self):
        r"""
        If ``self`` is in a composite quantum system, this return an index representing the position of ``self`` in the
        composite system, else it returns 0.
        Also, the first system in a composite quantum system is at index 0.
        """
        ind = 0
        if self.superSys is not None:
            ind += list(self.superSys.subSys.values()).index(self)
            if self.superSys.superSys is not None:
                ind += self.superSys.ind
        return ind

    @property
    def _dimsBefore(self):
        r"""
        Property to set and get the :attr:`~genericQSys.__dimsBefore`. Getter can be used to get information, but the
        setter is intended purely for internal use.
        """
        return self._genericQSys__dimsBefore if self._genericQSys__dimsBefore != 0 else 1

    @_dimsBefore.setter
    def _dimsBefore(self, val):
        if not isinstance(val, int):
            raise ValueError('?')
        oldVal = self._dimsBefore
        setAttr(self, '_genericQSys__dimsBefore', val)
        for sys in self.subSys.values():
            sys.delMatrices(_exclude=[]) # pylint: disable=protected-access
            if isinstance(sys, genericQSys):
                sys._dimsBefore = int((sys._dimsBefore*val)/oldVal)

    @property
    def _dimsAfter(self):
        r"""
        Property to set and get the :attr:`~genericQSys.__dimsAfter`. Getter can be used to get information, but the
        setter is intended purely for internal use.
        """
        return self._genericQSys__dimsAfter if self._genericQSys__dimsAfter != 0 else 1

    @_dimsAfter.setter
    def _dimsAfter(self, val):
        if not isinstance(val, int):
            raise ValueError('?')
        oldVal = self._dimsAfter
        setAttr(self, '_genericQSys__dimsAfter', val)
        for sys in self.subSys.values():
            sys.delMatrices(_exclude=[]) # pylint: disable=protected-access
            if isinstance(sys, genericQSys):
                sys._dimsAfter = int((sys._dimsAfter*val)/oldVal)

    @property
    def dimension(self):
        r"""
        Property to get the dimension of the quantum system. There is no setter as it is handled internally.
        """
        if self._genericQSys__dimension is None:
            try:
                dims = self.subSysDimensions
                self._genericQSys__dimension = 1 # pylint: disable=assigning-non-slot
                for val in dims:
                    self._genericQSys__dimension *= val # pylint: disable=assigning-non-slot
            except AttributeError:
                print(f'dimension? {self.name}')
        return self._genericQSys__dimension

    @property
    def _totalDim(self):
        r"""
        :attr:`genericQSys.dimension` returns the dimension of a quantum system itself, meaning it does not contain the
        dimensions of the other systems if ``self`` is in a composite system, ``_totalDim`` returns the total dimension
        by also taking the dimensions before and after ``self`` in a composte system.
        """
        return self.dimension * self._dimsBefore * self._dimsAfter#pylint:disable=E1101

    @property
    def _freeEvol(self):
        r"""
        Property to get the ``default`` internal ``freeEvolution`` proptocol.
        """
        return self._genericQSys__unitary

    def unitary(self):
        r"""
        Returns the unitary evolution operator for ``self``.
        """
        unitary = self._genericQSys__unitary.unitary()
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return unitary

    @QSimComp.initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        r"""
        Sets the initial state from a given input ``inp``,
        see :meth:`baseClasses.stateBase.initialState` for different types of inputs.
        """
        if self.superSys is not None:
            self.superSys.simulation._stateBase__initialState._value = None
        self.simulation.initialState = inp # pylint: disable=no-member, protected-access
        if (isinstance(self, compQSystem) and isinstance(inp, list)):
            for ind, it in enumerate(inp):
                list(self.qSystems.values())[ind].initialState = it # pylint: disable=no-member

    def _constructMatrices(self):
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        for sys in self.subSys.values():
            sys._constructMatrices() # pylint: disable=protected-access

    def addProtocol(self, protocol=None, system=None, protocolRemove=None):
        r"""
        adds the given ``protocol`` into ``self.simulation`` and uses ``self`` as ``system`` if it is not given.
        It also can removed a protocol (``protocolRemove``) at the same time.
        """
        if system is None:
            system = self
        self.simulation.addProtocol(protocol=protocol, system=system, protocolRemove=protocolRemove)

    def _timeDependency(self, time=None):
        r"""
        Passes down the current time in evolution to all the ``subSys``, which eventually are either ``term`` or
        ``qCoupling`` objects that are child classes of ``termTimeDep``, which updates the ``frequency`` of the
        corresponding coupling or term using the ``timeDependency`` method created and given by the user.
        TODO Create a demo and hyperlink here.
        """
        if time is None:
            time = self.simulation._currentTime
        for sys in self.subSys.values():
            sys._timeDependency(time)
        return time

class QuantumSystemOld(genericQSys):
    r"""
    This class can be used for creating either a composite or a single quantum system depending on the given ``kwargs``,
    if no ``kwargs`` given, it creates a composite system by default.
    """

    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    def __new__(cls, sysType='composite', **kwargs):
        singleKeys = ['frequency', 'operator', 'order', 'dimension']
        for key in singleKeys:
            if key in kwargs:
                sysType = 'single'

        if sysType == 'composite':
            newCls = compQSystem
        elif sysType == 'single':
            newCls = qSystem
        elif sysType == 'system coupling':
            newCls = qCoupling

        if newCls != cls:
            instance = newCls(**kwargs)
        return instance

    __slots__ = []

class compQSystem(genericQSys):
    r"""
    Class for composite quantum systems.
    """

    #: (**class attribute**) class label used in default naming
    label = 'QuantumSystemOld'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__qCouplings', '__qSystems']

    def __init__(self, **kwargs):
        if self.__class__.__name__ == 'compQSystem':
            compQSystem._externalInstances = qSystem._instances + compQSystem._instances
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: an ordered dictionary for the coupling terms
        self.__qCouplings = OrderedDict()
        #: an ordered dictionary for the quantum systems
        self.__qSystems = OrderedDict()

        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def _timeDependency(self, time=None):
        r"""
        Passes down the current time in evolution to all the ``subSys``, which eventually are either ``term`` or
        ``qCoupling`` objects that are child classes of ``termTimeDep``, which updates the ``frequency`` of the
        corresponding coupling or term using the ``timeDependency`` method created and given by the user.
        TODO Create a demo and hyperlink here.
        """
        time = super()._timeDependency(time=time)
        for coupling in self.qCouplings.values():
            coupling._timeDependency(time)

    @property
    def subSysDimensions(self):
        r"""
        Returns a list of dimensions of the quantum systems contained in ``self``, which is a composite system.
        """
        return [sys.dimension for sys in self.subSys.values()]

    @property
    def freeHam(self):
        r"""
        returns the Hamiltonian without the coupling terms.
        """
        ham = sum([val.totalHam for val in self.qSystems.values()])
        return ham

    @property
    def totalHam(self): # pylint: disable=invalid-overridden-method
        r"""
        returns the total Hamiltonian of ``self`` including the coupling terms.
        """
        if ((self._paramUpdated) or (self._paramBoundBase__matrix is None)): # pylint: disable=no-member
            self._paramBoundBase__matrix = self.freeHam + self.couplingHam # pylint: disable=assigning-non-slot
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member, assigning-non-slot

    @property
    def couplingHam(self):
        r"""
        returns only the coupling terms of the Hamiltonian.
        """
        cham = sum([val.totalHam for val in self.qCouplings.values()])
        return cham

    @property
    def qSystems(self):
        r"""
        returns the ordered dictionary that contains the sub-systems.
        """
        return self._compQSystem__qSystems # pylint: disable=no-member

    @addDecorator
    def addSubSys(self, subSys, **kwargs): # pylint: disable=arguments-differ
        r"""
        Add a quantum system to ``self``. Note that composite systems can contain other composite systems as sub-systems
        """
        if subSys not in self.subSys.values():
            subSys = super().addSubSys(subSys, **kwargs)
            if isinstance(subSys, qCoupling):
                self._compQSystem__addCoupling(self._qBase__subSys.pop(subSys.name))  # pylint: disable=no-member
            elif isinstance(subSys, genericQSys):
                self._compQSystem__addSub(subSys)# pylint: disable=no-member
            else:
                raise TypeError('?')
            subSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
            self._paramUpdated = True
        return subSys

    def createSubSys(self, subSysClass, **kwargs):
        r"""
        Create a subsystem of the given ``subSysClass`` class and also set the given ``kwargs`` to newly created system.
        """
        return self.addSubSys(subSysClass, **kwargs)

    def __addSub(self, subSys):
        r"""
        internal method used to update relevant information (such as dimension before/after) for the existing and newly
        added sub-systems. This is purely for internal use.
        """
        for subS in self._compQSystem__qSystems.values():
            subS._dimsAfter *= subSys.dimension
            subSys._dimsBefore *= subS.dimension

        if subSys._paramBoundBase__matrix is not None:
            for sys in subSys.subSys.values():
                sys._paramBoundBase__matrix = None
        # TODO big question here
        subSys.simulation._bound(self.simulation) # pylint: disable=protected-access
        self._compQSystem__qSystems[subSys.name] = subSys
        subSys.superSys = self
        self._genericQSys__dimension = None # pylint: disable=assigning-non-slot
        return subSys

    @_recurseIfList
    def _removeSubSysExc(self, subSys, _exclude=[]):#pylint:disable=arguments-differ,dangerous-default-value,too-many-branches
        r"""
        Removes a quantum system from the composite system ``self`` and updates the relevant information in the
        remaining sub-systems (such as dimension before/after).
        """
        subSys = self.getByNameOrAlias(subSys)
        couplings = list(self.qCouplings.values())
        for coupling in couplings:
            coupling._removeSubSysExc(subSys, _exclude=_exclude)# pylint: disable=protected-access
            if len(coupling._qBase__subSys) == 0: # pylint: disable=protected-access
                self.qCouplings.pop(coupling.name)
        if subSys in list(self.subSys.values()):
            for qS in self.subSys.values():
                qS.simulation._stateBase__initialState._value = None
                if qS.ind < subSys.ind:
                    qS._dimsAfter = int(qS._dimsAfter/subSys.dimension)
                elif qS.ind > subSys.ind:
                    qS._dimsBefore = int(qS._dimsBefore/subSys.dimension)
            self.qSystems.pop(subSys.name)
            _exclude.append(self)
            super()._removeSubSysExc(subSys, _exclude=_exclude)
        elif subSys in self.qCouplings.values():
            self.qCouplings.pop(subSys.name)

        if self not in _exclude:
            _exclude.append(self)
            if ((self._dimsAfter != 1) or (self._dimsBefore != 1)):
                if self.ind < subSys.superSys.ind:
                    self._dimsAfter = int(self._dimsAfter/subSys.dimension)
                elif self.ind > subSys.superSys.ind:
                    self._dimsBefore = int(self._dimsBefore/subSys.dimension)

            for sys in self.subSys.values():
                sys._removeSubSysExc(subSys, _exclude=_exclude) # pylint: disable=protected-access
                #_exclude.append(sys)

        if self.superSys is not None:
            self.superSys._removeSubSysExc(subSys, _exclude=_exclude) # pylint: disable=protected-access
            _exclude.append(self.superSys)

        #subSys.superSys = None
        subSys._dimsAfter = 1
        subSys._dimsBefore = 1
        self.delMatrices(_exclude=[])
        self.simulation._stateBase__initialState._value = None
        self._genericQSys__dimension = None # pylint: disable=assigning-non-slot

    @property
    def qCouplings(self):
        r"""
        returns the ordered dictionary of coupling terms.
        """
        return self._compQSystem__qCouplings

    def __addCoupling(self, couplingObj):
        r"""
        Internal method used when adding a coupling term.
        """
        self._compQSystem__qCouplings[couplingObj.name] = couplingObj
        couplingObj.superSys = self
        return couplingObj

    def createSysCoupling(self, *args, **kwargs):
        r"""
        Creates a coupling term, sets the ``kwargs`` for that coupling, and uses ``args`` for the coupling operators
        and the corresponding operators, see addTerm in qCoupling to understand how args works.
        TODO Create a tutorial and hyperlink here
        """
        newCoupling = self.addSubSys(qCoupling, **kwargs)
        newCoupling.addTerm(*args)
        return newCoupling

    def addSysCoupling(self, couplingObj):
        r"""
        Adds the given coupling term to ``self``.
        TODO Create a tutorial and hyperlink here
        """
        self.addSubSys(couplingObj)

    @_initStDec
    def _createAstate(self, inp=None):
        r"""
        Creates the initial state using the ``inp`` input, and this method is for internal use.
        """
        if inp is None:
            inp = [qsys._createAstate() for qsys in self.subSys.values()]
        elif isinstance(inp, list):
            inp = [qsys._createAstate(inp[ind]) for ind, qsys in enumerate(self.subSys.values())]
        else:
            raise TypeError('?')
        return linAlg.tensorProd(*inp)

    def _constructMatrices(self):
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        super()._constructMatrices()
        for sys in self.qCouplings.values():
            sys._constructMatrices() # pylint: disable=protected-access

    def updateDimension(self, qSys, newDimVal, oldDimVal=None, _exclude=[]):#pylint:disable=dangerous-default-value,too-many-branches
        r"""
        This method is called when the dimension of a subSys ``qSys`` is changed, so that the relevant changes are
        reflected to dimension before/after information for the other systems in the composite system.
        """
        # TODO can be combined with removeSubSys by a decorator or another method to simplfy both
        if oldDimVal is None:
            oldDimVal = qSys._genericQSys__dimension
        self._genericQSys__dimension = None # pylint: disable=assigning-non-slot
        if qSys in self.qSystems.values():
            _exclude.append(self)
            qSys._genericQSys__dimension = newDimVal
            ind = qSys.ind
            for qS in self.qSystems.values():
                if qS.ind < ind:
                    qS._dimsAfter = int((qS._dimsAfter*newDimVal)/oldDimVal)
                elif qS.ind > ind:
                    qS._dimsBefore = int((qS._dimsBefore*newDimVal)/oldDimVal)

            #if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=no-member
            #    self.initialState = self.simulation._stateBase__initialStateInput.value # pylint: disable=no-member
            self._paramUpdated = True
            #self._constructMatrices()
            #for sys in self.subSys.values():
            #    if sys.simulation._stateBase__initialStateInput.value is not None:
            #        sys.initialState = sys.simulation._stateBase__initialStateInput.value

        if self not in _exclude:
            _exclude.append(self)
            if ((self._dimsAfter != 1) or (self._dimsBefore != 1)):
                if self.ind < qSys.superSys.ind:
                    self._dimsAfter = int((self._dimsAfter*newDimVal)/oldDimVal)
                elif self.ind > qSys.superSys.ind:
                    self._dimsBefore = int((self._dimsBefore*newDimVal)/oldDimVal)
            else:
                for sys in self.subSys.values():
                    if sys not in _exclude:
                        _exclude.append(sys)
                        if sys.ind < qSys.superSys.ind:
                            sys._dimsAfter = int((sys._dimsAfter*newDimVal)/oldDimVal)
                        elif sys.ind > qSys.superSys.ind:
                            sys._dimsBefore = int((sys._dimsBefore*newDimVal)/oldDimVal)

        if self.superSys is not None:
            self.superSys.updateDimension(qSys=qSys, newDimVal=newDimVal, oldDimVal=oldDimVal, _exclude=_exclude)
        self.delMatrices(_exclude=[])
        for c in self.qCouplings.values():
            c.delMatrices(_exclude=[])
        return qSys

class termTimeDep(paramBoundBase):
    r"""
    Parent class for :class:`~term` and :class:`~qCoupling` and I hope to combine those two in here.
    """
    #: (**class attribute**) class label used in default naming
    label = '_timeDep'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['timeDependency', '__frequency', '__order', '__operator']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: function that can be assigned by the user to update the parameters a function of time. The library passes the
        #: current time to this function
        self.timeDependency = None
        #: frequency of the term, it is is the coupling strength in the case of coupling term
        self.__frequency = None
        # TODO Create a tutorial
        #: the order/power for the operator of the term. The operator is raised to the power in this value
        self.__order = 1
        #: operator for the term
        self.__operator = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def copy(self, **kwargs):  # pylint: disable=arguments-differ
        r"""
        Create a copy ``self`` and change the values of the attributes given in ``kwargs``.
        """
        newSys = super().copy(frequency=self.frequency, operator=self.operator, order=self.order, **kwargs)
        return newSys

    @property
    def operator(self):
        r"""
        Sets and gets the operator for term.
        """
        return self._termTimeDep__operator

    @operator.setter
    def operator(self, op):
        self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
        setAttr(self, '_termTimeDep__operator', op)

    @property
    def order(self):
        r"""
        Sets and gets the order of the operator of the term.
        """
        return self._termTimeDep__order

    @order.setter
    def order(self, ordVal):
        setAttr(self, '_termTimeDep__order', ordVal)
        if self._paramBoundBase__matrix is not None: # pylint: disable=no-member
            self.freeMat = None

    @property
    def frequency(self):
        r"""
        Sets and gets the frequency of the term.
        """
        return self._termTimeDep__frequency

    @frequency.setter
    def frequency(self, freq):
        freq = 0 if freq == 0.0 else freq
        setAttr(self, '_termTimeDep__frequency', freq)

    def _constructMatrices(self):
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        Currently, this is just pass and extended in the child classes, and the goal is to combine those methods in here
        """

    @property
    def totalHam(self):
        r"""
        Return the total Hamiltonian for this term.
        """
        return self.frequency*self.freeMat

    @property
    def freeMat(self):
        r"""
        Gets and sets the free matrix, ie without the frequency (or, equivalently frequency=1) of the term.
        """
        #if ((self._paramBoundBase__matrix is None) or (self._paramUpdated)): # pylint: disable=no-member
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
            self.freeMat = None
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qMat):
        if qMat is not None:
            self._paramBoundBase__matrix = qMat # pylint: disable=no-member, assigning-non-slot
        else:
            #if len(self._qBase__subSys) == 0: # pylint: disable=no-member
            #    raise ValueError('No operator is given for coupling Hamiltonian')
            #if self.operator is None:
            #    raise ValueError('No operator is given for free Hamiltonian')
            self._constructMatrices()

    def _timeDependency(self, time=None):
        r"""
        Internal method that passes the current time to ``timeDependency`` method that needs to be defined by the user
        to update the relevant parameters (such as frequency of the term) as a function of time.
        """
        if time is None:
            time = self.superSys.simulation._currentTime

        if callable(self.timeDependency):
            if hasattr(self, 'frequency'):
                self.frequency = self.timeDependency(self, time) # pylint: disable=assigning-non-slot,not-callable
            elif hasattr(self, 'couplingStrength'):
                self.couplingStrength = self.timeDependency(self, time) #pylint:disable=assigning-non-slot,not-callable

class term(termTimeDep):
    r"""
    Term object for simple (i.e. non-coupling) terms in the Hamiltonian.
    """
    #: (**class attribute**) class label used in default naming
    label = 'term'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []

    @paramBoundBase.superSys.setter
    def superSys(self, supSys):
        r"""
        Extends superSys setter to also add aliases to self.
        New aliases are (any name/alias of superSys) + Term + (number of terms)
        TODO What if there is already a superSys, and also alias list contains user given aliases as well.
        """
        paramBoundBase.superSys.fset(self, supSys) # pylint: disable=no-member
        termCount = len(self.superSys.subSys) if self in self.superSys.subSys.values() else len(self.superSys.subSys)+1 # pylint: disable=no-member,line-too-long # noqa: E501
        self.alias = [na+"Term"+str(termCount) for na in self.superSys.name._aliasClass__members()] # pylint: disable=no-member, protected-access,line-too-long # noqa: E501

    @property
    def _freeMatSimple(self):
        r"""
        Return the matrix corresponding to the operator of the term, but this method does not make it into a composite
        operator even if the term belongs to a system in a composite quantum system.
        """
        h = self._constructMatrices(dimsBefore=1, dimsAfter=1, setMat=False)
        return h

    def _constructMatrices(self, dimsBefore=None, dimsAfter=None, setMat=True): #pylint:disable=arguments-differ
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        if dimsBefore is None:
            dimsBefore = self.superSys._dimsBefore # pylint: disable=no-member

        if dimsAfter is None:
            dimsAfter = self.superSys._dimsAfter # pylint: disable=no-member

        if not (isinstance(self.superSys.dimension, (int, int64, int32, int16)) and callable(self.operator)): # pylint: disable=no-member
            raise TypeError('?')

        dimension = self.superSys._genericQSys__dimension # pylint: disable=no-member
        if self.operator in [qOps.Jz, qOps.Jy, qOps.Jx, qOps.Jm, qOps.Jp, qOps.Js]:
            dimension = 0.5*(dimension-1)

        if self.operator not in [qOps.sigmam, qOps.sigmap, qOps.sigmax, qOps.sigmay, qOps.sigmaz]:
            mat = linAlg._matPower(qOps.compositeOp(self.operator(dimension), #pylint:disable=assigning-non-slot, protected-access
                                   dimsBefore, dimsAfter), self.order)
        else: # pylint: disable=bare-except
            mat = linAlg._matPower(qOps.compositeOp( # pylint: disable=no-member, assigning-non-slot, protected-access
                                   self.operator(), dimsBefore, dimsAfter), self.order)

        if setMat:
            self._paramBoundBase__matrix = mat #pylint:disable=assigning-non-slot
        return mat

class qSystem(genericQSys):
    r"""
    Class for single quantum systems, used as the parent for :class:`~Cavity`, :class:`~Spin`, and :class:`~Qubit`.
    """
    #: (**class attribute**) class label used in default naming
    label = 'QuantumSystemOld'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    #@qSystemInitErrors
    def __init__(self, **kwargs):
        if self.__class__.__name__ == 'qSystem':
            qSystem._externalInstances = qSystem._instances + compQSystem._instances
        super().__init__(_internal=kwargs.pop('_internal', False))
        # TODO
        qSysKwargs = ['terms', 'subSys', 'name', 'superSys', 'dimension', 'alias']
        for key in qSysKwargs:
            val = kwargs.pop(key, None)
            if val is not None:
                setattr(self, key, val)

        if len(self.subSys) == 0:
            self.addSubSys(term(superSys=self, **kwargs))
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    # @genericQSys.name.setter #pylint: disable=no-member
    # def name(self, name):
    #     oldName = self.name
    #     genericQSys.name.fset(self, name) # pylint: disable=no-member
    #     for ii, sys in enumerate(self.subSys.values()):
    #         if sys.name == (oldName + 'term' + str(ii)):
    #             sys.name = self.superSys.name + 'term' + str(ii+1) # pylint: disable=no-member

    @genericQSys.dimension.setter # pylint: disable=no-member
    def dimension(self, newDimVal):
        r"""
        Setter for the dimension of single quantum system. It deletes the existing matrices for the operators, unitaries
        etc, that uses the previous dimension information. It also takes care of updating the dimension before/after
        information for the other quantum system systems if ``self`` is in a composite system.
        """
        if not isinstance(newDimVal, (int, int64, int32, int16)):
            raise ValueError('Dimension is not int')

        oldDimVal = self._genericQSys__dimension # pylint: disable=no-member

        for sys in self.subSys.values():
            sys.delMatrices(_exclude=[]) # pylint: disable=protected-access

        setAttr(self, '_genericQSys__dimension', newDimVal)
        # FIXME these should be called only if oldDim != newDim
        #if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=protected-access
        #    self.initialState = self.simulation._stateBase__initialStateInput.value # pylint: disable=protected-access

        if isinstance(self.superSys, compQSystem):
            self.superSys.updateDimension(self, newDimVal, oldDimVal, _exclude=[]) # pylint: disable=no-member

    @property
    def totalHam(self): # pylint: disable=invalid-overridden-method
        r"""
        Returns the total Hamiltonian of the single quantum system.
        """
        if ((self._paramUpdated) or (self._paramBoundBase__matrix is None)): # pylint: disable=no-member
            h = sum([(obj.frequency * obj.freeMat) for obj in self.subSys.values()])
            self._paramBoundBase__matrix = h # pylint: disable=assigning-non-slot
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @property
    def _totalHamSimple(self):
        r"""
        returns the total Hamiltonian of the single quantum system, but this method does not take the dimension
        before/after into account even if ``self`` is a sub-system of a composite system.
        """
        return sum([(obj.frequency * obj._freeMatSimple) for obj in self.subSys.values()])#pylint:disable=protected-access

    @property
    def freeMat(self):
        r"""
        returns the free (i.e. no frequency or, equivalently frequency=1) matrix for the operator of the first term in
        its Hamiltonian.
        """
        return self.firstTerm.freeMat # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qOpsFunc):
        r"""
        Setter for the freeMat. This is used internally in construct matrices methods.
        """
        if callable(qOpsFunc):
            self.firstTerm.operator = qOpsFunc
            self.firstTerm._constructMatrices() # pylint: disable=protected-access
        elif qOpsFunc is not None:
            self.firstTerm._paramBoundBase__matrix = qOpsFunc  # pylint: disable=assigning-non-slot
        else:
            if self.firstTerm.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self.firstTerm._constructMatrices() # pylint: disable=protected-access

    @property
    def operator(self):
        r"""
        Gets a list of the operators for the terms in its Hamiltonian, and sets the operator only for the first term.
        """
        operators = [obj._termTimeDep__operator for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return operators if len(operators) > 1 else operators[0]

    @operator.setter
    def operator(self, op):
        self.firstTerm.operator = op

    @property
    def frequency(self):
        r"""
        Setter and getter of the frequency of the first term in its Hamiltonian.
        """
        #frequencies = [obj._termTimeDep__frequency for obj in list(self.subSys.values())] # pylint: disable=protected-access
        #return frequencies if len(frequencies) > 1 else frequencies[0]
        return self.firstTerm.frequency

    @frequency.setter
    def frequency(self, freq):
        self.firstTerm.frequency = freq

    @property
    def order(self):
        r"""
        Sets and gets the order/power of the operator of the first term in its Hamiltonian.
        """
        orders = [obj._termTimeDep__order for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return orders if len(orders) > 1 else orders[0]

    @order.setter
    def order(self, ordVal):
        self.firstTerm.order = ordVal

    @property
    def firstTerm(self):
        r"""
        Returns the first term in its Hamiltonian
        """
        return list(self.subSys.values())[0]

    @property
    def terms(self):
        r"""
        returns a list of the term objects used for its Hamiltonian.
        """
        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @addDecorator
    def addSubSys(self, subSys, **kwargs):
        r"""
        extends the addSubSys method from the parent classes and uses it add terms to its Hamiltonian.
        """
        if not isinstance(subSys, term):
            raise TypeError('?')
        kwargs['superSys'] = self
        newS = super().addSubSys(subSys, **kwargs)
        # FIXME use setAttr, check also for operator
        self._paramUpdated = True
        newS._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return subSys

    @_recurseIfList
    def _removeSubSysExc(self, subSys, _exclude=[]): # pylint: disable=arguments-differ, dangerous-default-value
        r"""
        Method to remove a term from its Hamiltonian.
        """
        if self not in _exclude:
            _exclude.append(self)
            subSys = self.getByNameOrAlias(subSys)
            if self.superSys is not None:
                self.superSys._removeSubSysExc(subSys, _exclude=_exclude) # pylint: disable=protected-access

            if subSys in self.subSys.values():
                super()._removeSubSysExc(subSys, _exclude=_exclude)

    @terms.setter
    def terms(self, subSys):
        r"""
        add terms to its Hamiltonian with this setter.
        """
        genericQSys.subSys.fset(self, subSys) # pylint: disable=no-member
        for sys in self.subSys.values():
            sys.superSys = self

    def addTerm(self, operator, frequency=0, order=1):
        r"""
        Calls the addSubSys to add terms, this method is created to provide a more intuitive name than addSubSys
        """
        newTerm = self.addSubSys(term(operator=operator, frequency=frequency, order=order, superSys=self))
        return newTerm

    @_recurseIfList
    def removeTerm(self, termObj):
        r"""
        Calls the removeSubSys to remove terms, this method is created to provide a more intuitive name than
        removeSubSys
        """
        self._removeSubSysExc(termObj, _exclude=[])

    @_initStDec
    def _createAstate(self, inp=None):
        r"""
        Internal method to create initial states.
        """
        if inp is None:
            raise ValueError(self.name + ' is not given an initial state')
        return qSta.superPos(self.dimension, inp, not self._inpCoef)

class SpinOld(qSystem): # pylint: disable=too-many-ancestors
    r"""
    Object for a single Spin system with spin j (jValue).
    """
    #: (**class attribute**) class label used in default naming
    label = 'SpinOld'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__jValue']
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None),
                         _internal=kwargs.pop('_internal', False))
        #: operator for (the first term in) its Hamiltonian
        self.operator = qOps.Jz
        #: spin quantum number
        self.__jValue = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def jValue(self):
        r"""
        Gets and sets the spin quantum number
        """
        return (self._genericQSys__dimension-1)/2 # pylint: disable=no-member

    @jValue.setter
    def jValue(self, value):
        self._SpinOld__jValue = value # pylint: disable=assigning-non-slot
        self.dimension = int((2*value) + 1)

class QubitOld(SpinOld): # pylint: disable=too-many-ancestors
    r"""
    Spin 1/2 special case of Spin class, i.e. a Qubit.
    """
    #: (**class attribute**) class label used in default naming
    label = 'QubitOld'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None),
                         _internal=kwargs.pop('_internal', False))
        kwargs['dimension'] = 2
        self.operator = qOps.Jz
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

class CavityOld(qSystem): # pylint: disable=too-many-ancestors
    r"""
    Cavity class, the only difference from a generic quantum object is that, by default, its operator is the number
    operator.
    """
    #: (**class attribute**) class label used in default naming
    label = 'CavityOld'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None),
                         _internal=kwargs.pop('_internal', False))
        self.operator = qOps.number
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

class qCoupling(termTimeDep):
    r"""
    Class to create coupling terms between quantum systems.
    """
    #: (**class attribute**) class label used in default naming
    label = 'qCoupling'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []

    #@qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._named__setKwargs(**kwargs) # pylint: disable=no-member
        self.addTerm(*args)

    # TODO might define setters
    @property
    def couplingOperators(self):
        r"""
        returns a list of coupling operators stored in this coupling term
        """
        ops = []
        for co in self._qBase__subSys.values(): # pylint: disable=no-member
            ops.append(co[1])
        return ops

    @property
    def coupledSystems(self):
        r"""
        returns the list of coupled systems by this coupling term
        """
        ops = []
        for co in self._qBase__subSys.values(): # pylint: disable=no-member
            ops.append(co[0])
        return ops

    @property
    def couplingStrength(self):
        r"""
        Gets and sets the coupling strength for this coupling. This is simply an alternative terminology for frequency.
        """
        return self.frequency

    @couplingStrength.setter
    def couplingStrength(self, strength):
        self.frequency = strength

    def __coupOrdering(self, qts): # pylint: disable=no-self-use
        r"""
        method used internally to make some sorting of the operators. This is implemented so that there are some
        flexibilities for user when creating coupling.
        """
        qts = sorted(qts, key=lambda x: x[0], reverse=False)
        oper = qts[0][1]
        for ops in range(len(qts)-1):
            oper = oper @ qts[ops+1][1]
        return oper

    def _constructMatrices(self):
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        cMats = []
        for ind in range(len(self._qBase__subSys)): # pylint: disable=no-member
            qts = []
            for indx in range(len(list(self._qBase__subSys.values())[ind])): # pylint: disable=no-member
                sys = list(self._qBase__subSys.values())[ind][0][indx] # pylint: disable=no-member
                order = sys.ind
                oper = list(self._qBase__subSys.values())[ind][1][indx] # pylint: disable=no-member
                if oper in [qOps.sigmam, qOps.sigmap, qOps.sigmax, qOps.sigmay, qOps.sigmaz]:
                    cHam = qOps.compositeOp(oper(), sys._dimsBefore, sys._dimsAfter)
                else:
                    dimension = sys._genericQSys__dimension
                    if oper in [qOps.Jz, qOps.Jy, qOps.Jx, qOps.Jm, qOps.Jp, qOps.Js]:
                        dimension = 0.5*(dimension-1)
                    cHam = qOps.compositeOp(oper(dimension), sys._dimsBefore, sys._dimsAfter)
                ts = [order, cHam]
                qts.append(ts)
            cMats.append(self._qCoupling__coupOrdering(qts))
        #h = []
        #if ((self.couplingStrength != 0) or (self.couplingStrength is not None)):
        #    h = [self.couplingStrength * sum(cMats)]
        self._paramBoundBase__matrix = sum(cMats) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def __addTerm(self, count, ind, sys, *args):
        r"""
        used internally when adding terms to the coupling.
        """
        if callable(args[count][ind]):
            lo = len(self.subSys)
            self._qBase__subSys[str(lo)] = (sys, tuple(args[count])) # pylint: disable=no-member
            count += 1
            if count < len(args):
                count = self.__addTerm(count, ind, sys, *args)
        return count

    def addTerm(self, *args):
        r"""
        method to add terms to the coupling.
        """
        counter = 0
        while counter in range(len(args)):
            # TODO write a generalisation for this one
            if isinstance(self.getByNameOrAlias(args[counter][0]), qSystem):
                qSystems = [self.getByNameOrAlias(obj) for obj in args[counter]]
                for qsys in qSystems:
                    qsys._paramBoundBase__paramBound[self.name] = self
                if callable(args[counter+1][1]):
                    #if tuple(args[counter + 1]) in self._qBase__subSys.keys(): # pylint: disable=no-member
                    #    print(tuple(args[counter + 1]), 'already exists')
                    lo = len(self.subSys)
                    self._qBase__subSys[str(lo)] = (qSystems, tuple(args[counter + 1])) # pylint: disable=no-member
                    counter += 2
                # TODO does not have to pass qSystem around
                if counter < len(args):
                    counter = self._qCoupling__addTerm(counter, 1, qSystems, *args)
            else:
                # TODO raise a meaningful error
                break
        self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
        return self

    @_recurseIfList
    def removeSysCoupling(self, sys):
        r"""
        method to remove terms from the coupling, simply calls removeSubSys, this method is to create terminology
        """
        self._removeSubSysExc(sys, _exclude=[])

    @_recurseIfList
    def _removeSubSysExc(self, subSys, _exclude=[]): # pylint: disable=dangerous-default-value
        r"""
        method to remove terms from the coupling
        """
        vals = self._qBase__subSys.values() # pylint: disable=no-member
        for ind, val in enumerate(vals):
            systs = val[0]
            if subSys in systs:
                self._qBase__subSys.pop(str(ind)) # pylint: disable=no-member
