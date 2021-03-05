from collections import OrderedDict
from numpy import (int64, int32, int16, ndarray)
from scipy.sparse import issparse

from ..QuantumToolbox import operators as qOps #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox import linearAlgebra as linAlg #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox import states as qSta #pylint: disable=relative-beyond-top-level

from .base import addDecorator, _recurseIfList
from .baseClasses import qBaseSim, paramBoundBase, setAttr
#from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from .QPro import freeEvolution

def _initStDec(_createAstate):
    def wrapper(obj, inp=None):
        if (issparse(inp) or isinstance(inp, ndarray)):
            if inp.shape[0] != obj.dimension:
                raise ValueError('Dimension mismatch')
            state = inp
        else:
            if inp is None:
                inp = obj.simulation._stateBase__initialStateInput.value

            if isinstance(obj.dimension, int):
                state = _createAstate(obj, inp)
            else:
                state = None
        return state
    return wrapper

def _computeDef(sys, state): # pylint: disable=unused-argument
    pass

def _calculateDef(sys): # pylint: disable=unused-argument
    pass

class genericQSys(qBaseSim):
    r"""
    Base class for both single (:class:`~qSystem`) and composite (:class:`~compQSystem`) quantum system classes.
    The ultimate goal is to make those two classes the same by combining them in here. Currently, a proxy
    :class:`~QuantumSystem` is introduced as a temporary solution.
    """
    label = 'genericQSys'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__unitary', '__dimension', '__dimsBefore', '__dimsAfter', '_inpCoef']

    def __init__(self, **kwargs):
        super().__init__()
        #: an internal :class:`~freeEvolution` protocol, this is the default evolution when a simulation is run.
        self.__unitary = freeEvolution(_internal=True)
        self._genericQSys__unitary.superSys = self # pylint: disable=no-member
        self._qBaseSim__simulation.addQSystems(subS=self, Protocol=self._freeEvol) # pylint: disable=no-member
        #: dimension of Hilbert space of the quantum system
        self.__dimension = None
        #: boolean to determine whether initialState inputs contains complex coefficients (the probability amplitudes)
        #: or the populations
        self._inpCoef = False
        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def __add__(self, other):
        if isinstance(self, compQSystem) and isinstance(other, qSystem):
            self.addSubSys(other)
            newComp = self
        elif ((isinstance(self, qSystem) and isinstance(other, qSystem)) or  # noqa: W504
              (isinstance(self, compQSystem) and isinstance(other, compQSystem))):
            newComp = compQSystem()
            # FIXME 'stepCount' getter creates problem with None defaults
            newComp.simulation._copyVals(self.simulation, ['totalTime', 'stepSize', 'delStates'])
            newComp.compute = _computeDef
            newComp.simulation.compute = _computeDef
            #newComp.calculate = _calculateDef
            #newComp.simulation.calculate = _calculateDef
            newComp.addSubSys(self)
            if other is self:
                newComp.addSubSys(other.copy())
            else:
                newComp.addSubSys(other)
        elif isinstance(self, qSystem) and isinstance(other, compQSystem):
            other.addSubSys(self)
            newComp = other
        elif isinstance(other, (float, int)):
            newComp = self
        return newComp

    def __sub__(self, other):
        self.removeSubSys(other, _exclude=[])
        return self

    def __rmul__(self, other):
        newComp = compQSystem()
        newComp.addSubSys(self)
        for _ in range(other - 1):
            newComp.addSubSys(self.copy())
        return newComp

    def copy(self, **kwargs): # pylint: disable=arguments-differ
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
            newSys.initialState = self.simulation._stateBase__initialStateInput.value
        newSys._named__setKwargs(**kwargs)
        return newSys

    @property
    def ind(self):
        ind = 0
        if self.superSys is not None:
            ind += list(self.superSys.subSys.values()).index(self)
            if self.superSys.superSys is not None:
                ind += self.superSys.ind
        return ind

    @property
    def _dimsBefore(self):
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
        return self.dimension * self._dimsBefore * self._dimsAfter#pylint:disable=E1101

    @property
    def _freeEvol(self):
        return self._genericQSys__unitary

    @property
    def unitary(self):
        unitary = self._genericQSys__unitary.unitary
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return unitary

    @qBaseSim.initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        if self.superSys is not None:
            self.superSys.simulation._stateBase__initialState._value = None
        self.simulation.initialState = inp # pylint: disable=no-member, protected-access
        if (isinstance(self, compQSystem) and isinstance(inp, list)):
            for ind, it in enumerate(inp):
                list(self.qSystems.values())[ind].initialState = it # pylint: disable=no-member

    def _constructMatrices(self):
        for sys in self.subSys.values():
            sys._constructMatrices() # pylint: disable=protected-access

    def addProtocol(self, protocol=None, system=None, protocolRemove=None):
        if system is None:
            system = self
        self.simulation.addProtocol(protocol=protocol, system=system, protocolRemove=protocolRemove)

    def _timeDependency(self, time=None):
        if time is None:
            time = self.simulation._currentTime
        for sys in self.subSys.values():
            sys._timeDependency(time)
        return time

class QuantumSystem(genericQSys):
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    def __new__(cls, sysType='composite', **kwargs):
        singleKeys = ['frequency', 'operator', 'order', 'dimension']
        for key in singleKeys:
            if key in kwargs.keys():
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
    label = 'QuantumSystem'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__qCouplings', '__qSystems', 'couplingName']

    def __init__(self, **kwargs):
        if self.__class__.__name__ == 'compQSystem':
            compQSystem._externalInstances = qSystem._instances + compQSystem._instances
        super().__init__()
        self.__qCouplings = OrderedDict()
        self.__qSystems = OrderedDict()
        self.couplingName = None

        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def _timeDependency(self, time=None):
        time = super()._timeDependency(time=time)
        for coupling in self.qCouplings.values():
            coupling._timeDependency(time)

    @property
    def subSysDimensions(self):
        return [sys.dimension for sys in self.subSys.values()]

    @property
    def freeHam(self):
        ham = sum([val.totalHam for val in self.qSystems.values()])
        return ham

    @property
    def totalHam(self): # pylint: disable=invalid-overridden-method
        if ((self._paramUpdated) or (self._paramBoundBase__matrix is None)): # pylint: disable=no-member
            self._paramBoundBase__matrix = self.freeHam + self.couplingHam # pylint: disable=assigning-non-slot
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @property
    def couplingHam(self):
        cham = sum([val.totalHam for val in self.qCouplings.values()])
        return cham

    @property
    def qSystems(self):
        return self._compQSystem__qSystems # pylint: disable=no-member

    @addDecorator
    def addSubSys(self, subSys, **kwargs): # pylint: disable=arguments-differ
        newSys = super().addSubSys(subSys, **kwargs)
        if isinstance(newSys, qCoupling):
            self._compQSystem__addCoupling(self._qBase__subSys.pop(newSys.name))  # pylint: disable=no-member
        elif isinstance(newSys, genericQSys):
            self._compQSystem__addSub(newSys)
        else:
            raise TypeError('?')
        newSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return newSys

    def createSubSys(self, subSysClass, **kwargs):
        return self.addSubSys(subSysClass, **kwargs)

    def __addSub(self, subSys):
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
        return subSys

    @_recurseIfList
    def removeSubSys(self, subS, _exclude=[]):#pylint:disable=arguments-differ,dangerous-default-value,too-many-branches
        if isinstance(subS, str):
            subS = self.getByNameOrAlias(subS)
        couplings = list(self.qCouplings.values())
        for coupling in couplings:
            coupling.removeSubSys(subS, _exclude=_exclude)
            if len(coupling._qBase__subSys) == 0: # pylint: disable=protected-access
                self.qCouplings.pop(coupling.name)

        if subS in list(self.subSys.values()):
            for qS in self.subSys.values():
                qS.simulation._stateBase__initialState._value = None
                if qS.ind < subS.ind:
                    qS._dimsAfter = int(qS._dimsAfter/subS.dimension)
                elif qS.ind > subS.ind:
                    qS._dimsBefore = int(qS._dimsBefore/subS.dimension)
            self.qSystems.pop(subS.name)
            _exclude.append(self)
            super().removeSubSys(subS, _exclude=_exclude)
        elif subS in self.qCouplings.values():
            self.qCouplings.pop(subS.name)

        if self not in _exclude:
            _exclude.append(self)
            if ((self._dimsAfter != 1) or (self._dimsBefore != 1)):
                if self.ind < subS.superSys.ind:
                    self._dimsAfter = int(self._dimsAfter/subS.dimension)
                elif self.ind > subS.superSys.ind:
                    self._dimsBefore = int(self._dimsBefore/subS.dimension)

            for sys in self.subSys.values():
                sys.removeSubSys(subS, _exclude=_exclude)
                #_exclude.append(sys)

        if self.superSys is not None:
            self.superSys.removeSubSys(subS, _exclude=_exclude)
            _exclude.append(self.superSys)

        self.delMatrices(_exclude=[])
        self.simulation._stateBase__initialState._value = None
        self._genericQSys__dimension = None # pylint: disable=assigning-non-slot

    @property
    def qCouplings(self):
        return self._compQSystem__qCouplings

    def __addCoupling(self, couplingObj):
        self._compQSystem__qCouplings[couplingObj.name] = couplingObj
        couplingObj.superSys = self
        return couplingObj

    def createSysCoupling(self, *args, **kwargs):
        newCoupling = self.addSubSys(qCoupling, **kwargs)
        newCoupling.addTerm(*args)
        return newCoupling

    def addSysCoupling(self, couplingObj):
        self.addSubSys(couplingObj)

    @_initStDec
    def _createAstate(self, inp=None):
        if inp is None:
            inp = [qsys._createAstate() for qsys in self.subSys.values()]
        elif isinstance(inp, list):
            inp = [qsys._createAstate(inp[qsys.ind]) for qsys in self.subSys.values()]
        else:
            raise TypeError('?')
        return linAlg.tensorProd(*inp)

    def _constructMatrices(self):
        super()._constructMatrices()
        for sys in self.qCouplings.values():
            sys._constructMatrices() # pylint: disable=protected-access

    def updateDimension(self, qSys, newDimVal, oldDimVal=None, _exclude=[]):#pylint:disable=dangerous-default-value,too-many-branches
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

            if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=no-member
                self.initialState = self.simulation._stateBase__initialStateInput.value # pylint: disable=no-member
            self._paramUpdated = True
            #self._constructMatrices()
            for sys in self.subSys.values():
                if sys.simulation._stateBase__initialStateInput.value is not None:
                    sys.initialState = sys.simulation._stateBase__initialStateInput.value

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
    label = '_timeDep'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['timeDependency', '__frequency', '__order', '__operator']

    def __init__(self, **kwargs):
        super().__init__()
        self.timeDependency = None
        self.__frequency = None
        self.__order = 1
        self.__operator = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def copy(self, **kwargs):  # pylint: disable=arguments-differ
        newSys = super().copy(frequency=self.frequency, operator=self.operator, order=self.order, **kwargs)
        return newSys

    @property
    def operator(self):
        return self._termTimeDep__operator

    @operator.setter
    def operator(self, op):
        self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
        setAttr(self, '_termTimeDep__operator', op)

    @property
    def order(self):
        return self._termTimeDep__order

    @order.setter
    def order(self, ordVal):
        setAttr(self, '_termTimeDep__order', ordVal)
        if self._paramBoundBase__matrix is not None: # pylint: disable=no-member
            self.freeMat = None

    @property
    def frequency(self):
        return self._termTimeDep__frequency

    @frequency.setter
    def frequency(self, freq):
        freq = 0 if freq == 0.0 else freq
        setAttr(self, '_termTimeDep__frequency', freq)

    def _constructMatrices(self):
        pass

    @property
    def totalHam(self):
        return self.frequency*self.freeMat

    @property
    def freeMat(self):
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
        if time is None:
            time = self.superSys.simulation._currentTime

        if callable(self.timeDependency):
            if hasattr(self, 'frequency'):
                self.frequency = self.timeDependency(self, time) # pylint: disable=assigning-non-slot,not-callable
            elif hasattr(self, 'couplingStrength'):
                self.couplingStrength = self.timeDependency(self, time) #pylint:disable=assigning-non-slot,not-callable

class term(termTimeDep):
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
        h = self._constructMatrices(dimsBefore=1, dimsAfter=1, setMat=False)
        return h

    def _constructMatrices(self, dimsBefore=None, dimsAfter=None, setMat=True): #pylint:disable=arguments-differ
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
            mat = qOps.compositeOp(self.operator(dimension), #pylint:disable=assigning-non-slot
                                   dimsBefore, dimsAfter)**self.order
        else: # pylint: disable=bare-except
            mat = qOps.compositeOp( # pylint: disable=no-member, assigning-non-slot
                self.operator(), dimsBefore, dimsAfter)**self.order

        if setMat:
            self._paramBoundBase__matrix = mat #pylint:disable=assigning-non-slot
        return mat

class qSystem(genericQSys):
    label = 'QuantumSystem'
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
        super().__init__()
        qSysKwargs = ['terms', 'subSys', 'name', 'superSys', 'dimension']
        for key in qSysKwargs:
            val = kwargs.pop(key, None)
            if val is not None:
                setattr(self, key, val)
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

        if len(self.subSys) == 0:
            self.addSubSys(term(superSys=self, **kwargs))

    # @genericQSys.name.setter #pylint: disable=no-member
    # def name(self, name):
    #     oldName = self.name
    #     genericQSys.name.fset(self, name) # pylint: disable=no-member
    #     for ii, sys in enumerate(self.subSys.values()):
    #         if sys.name == (oldName + 'term' + str(ii)):
    #             sys.name = self.superSys.name + 'term' + str(ii+1) # pylint: disable=no-member

    @genericQSys.dimension.setter # pylint: disable=no-member
    def dimension(self, newDimVal):
        if not isinstance(newDimVal, (int, int64, int32, int16)):
            raise ValueError('Dimension is not int')

        oldDimVal = self._genericQSys__dimension # pylint: disable=no-member

        for sys in self.subSys.values():
            sys.delMatrices(_exclude=[]) # pylint: disable=protected-access

        setAttr(self, '_genericQSys__dimension', newDimVal)
        # FIXME these should be called only if oldDim != newDim
        if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=protected-access
            self.initialState = self.simulation._stateBase__initialStateInput.value # pylint: disable=protected-access

        if isinstance(self.superSys, compQSystem):
            self.superSys.updateDimension(self, newDimVal, oldDimVal, _exclude=[]) # pylint: disable=no-member

    @property
    def totalHam(self): # pylint: disable=invalid-overridden-method
        if ((self._paramUpdated) or (self._paramBoundBase__matrix is None)): # pylint: disable=no-member
            h = sum([(obj.frequency * obj.freeMat) for obj in self.subSys.values()])
            self._paramBoundBase__matrix = h # pylint: disable=assigning-non-slot
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @property
    def _totalHamSimple(self):
        return sum([(obj.frequency * obj._freeMatSimple) for obj in self.subSys.values()])#pylint:disable=protected-access

    @property
    def freeMat(self):
        return self.firstTerm.freeMat # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qOpsFunc):
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
        operators = [obj._termTimeDep__operator for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return operators if len(operators) > 1 else operators[0]

    @operator.setter
    def operator(self, op):
        self.firstTerm.operator = op

    @property
    def frequency(self):
        #frequencies = [obj._termTimeDep__frequency for obj in list(self.subSys.values())] # pylint: disable=protected-access
        #return frequencies if len(frequencies) > 1 else frequencies[0]
        return self.firstTerm.frequency

    @frequency.setter
    def frequency(self, freq):
        self.firstTerm.frequency = freq

    @property
    def order(self):
        orders = [obj._termTimeDep__order for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return orders if len(orders) > 1 else orders[0]

    @order.setter
    def order(self, ordVal):
        self.firstTerm.order = ordVal

    @property
    def firstTerm(self):
        return list(self.subSys.values())[0]

    @property
    def terms(self):
        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @addDecorator
    def addSubSys(self, subS, **kwargs):
        if not isinstance(subS, term):
            raise TypeError('?')
        kwargs['superSys'] = self
        newS = super().addSubSys(subS, **kwargs)
        # FIXME use setAttr, check also for operator
        self._paramUpdated = True
        newS._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return subS

    @_recurseIfList
    def removeSubSys(self, subS, _exclude=[]): # pylint: disable=arguments-differ, dangerous-default-value
        if self not in _exclude:
            _exclude.append(self)
            if self.superSys is not None:
                self.superSys.removeSubSys(subS, _exclude=_exclude)
            super().removeSubSys(subS, _exclude=_exclude)

    @terms.setter
    def terms(self, subS):
        genericQSys.subSys.fset(self, subS) # pylint: disable=no-member
        for sys in self.subSys.values():
            sys.superSys = self

    def addTerm(self, operator, frequency=0, order=1):
        newTerm = self.addSubSys(term(operator=operator, frequency=frequency, order=order, superSys=self))
        return newTerm

    @_recurseIfList
    def removeTerm(self, termObj):
        self.removeSubSys(termObj, _exclude=[])

    @_initStDec
    def _createAstate(self, inp=None):
        if inp is None:
            raise ValueError(self.name + ' is not given an initial state')
        return qSta.superPos(self.dimension, inp, not self._inpCoef)

class Spin(qSystem): # pylint: disable=too-many-ancestors
    label = 'Spin'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__jValue']
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None))
        self.operator = qOps.Jz
        self.__jValue = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def jValue(self):
        return (self._genericQSys__dimension-1)/2 # pylint: disable=no-member

    @jValue.setter
    def jValue(self, value):
        self._Spin__jValue = value # pylint: disable=assigning-non-slot
        self.dimension = int((2*value) + 1)

class Qubit(Spin): # pylint: disable=too-many-ancestors
    label = 'Qubit'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None))
        kwargs['dimension'] = 2
        self.operator = qOps.Jz
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

class Cavity(qSystem): # pylint: disable=too-many-ancestors
    label = 'Cavity'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None))
        self.operator = qOps.number
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

class qCoupling(termTimeDep):
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
        super().__init__()
        self._named__setKwargs(**kwargs) # pylint: disable=no-member
        self.addTerm(*args)

    # TODO might define setters
    @property
    def couplingOperators(self):
        ops = []
        for co in self._qBase__subSys.values(): # pylint: disable=no-member
            ops.append(co[1])
        return ops

    @property
    def coupledSystems(self):
        ops = []
        for co in self._qBase__subSys.values(): # pylint: disable=no-member
            ops.append(co[0])
        return ops

    @property
    def couplingStrength(self):
        return self.frequency

    @couplingStrength.setter
    def couplingStrength(self, strength):
        self.frequency = strength

    def __coupOrdering(self, qts): # pylint: disable=no-self-use
        qts = sorted(qts, key=lambda x: x[0], reverse=False)
        oper = qts[0][1]
        for ops in range(len(qts)-1):
            oper = oper @ qts[ops+1][1]
        return oper

    def _constructMatrices(self):
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
        if callable(args[count][ind]):
            lo = len(self.subSys)
            self._qBase__subSys[str(lo)] = (sys, tuple(args[count])) # pylint: disable=no-member
            count += 1
            if count < len(args):
                count = self.__addTerm(count, ind, sys, *args)
        return count

    def addTerm(self, *args):
        counter = 0
        while counter in range(len(args)):
            # TODO write a generalisation for this one
            if isinstance(args[counter][0], qSystem):
                qSystems = args[counter]
                if callable(args[counter+1][1]):
                    #if tuple(args[counter + 1]) in self._qBase__subSys.keys(): # pylint: disable=no-member
                    #    print(tuple(args[counter + 1]), 'already exists')
                    lo = len(self.subSys)
                    self._qBase__subSys[str(lo)] = (qSystems, tuple(args[counter + 1])) # pylint: disable=no-member
                    counter += 2
                # TODO does not have to pass qSystem around
                if counter < len(args):
                    counter = self._qCoupling__addTerm(counter, 1, qSystems, *args)
        self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
        return self

    @_recurseIfList
    def removeSysCoupling(self, sys):
        self.removeSubSys(sys, _exclude=[])

    @_recurseIfList
    def removeSubSys(self, subS, _exclude=[]): # pylint: disable=dangerous-default-value
        vals = self._qBase__subSys.values() # pylint: disable=no-member
        for ind, val in enumerate(vals):
            systs = val[0]
            if subS in systs:
                self._qBase__subSys.pop(str(ind)) # pylint: disable=no-member
