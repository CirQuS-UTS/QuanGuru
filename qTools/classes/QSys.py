from collections import OrderedDict
from numpy import (int64, int32, int16, ndarray)
from scipy.sparse import issparse
import qTools.QuantumToolbox.operators as qOps
import qTools.QuantumToolbox.states as qSta
#import qTools.QuantumToolbox.evolution as qEvo
from qTools.classes.computeBase import qBaseSim
from qTools.classes.computeBase import paramBoundBase
#from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from qTools.classes.QPro import freeEvolution
from qTools.classes.QUni import checkClass, _recurseIfList

def _initStDec(_initialState):
    def wrapper(obj, inp=None):
        if (issparse(inp) or isinstance(inp, ndarray)):
            if inp.shape[0] != obj.dimension:
                raise ValueError('Dimension mismatch')
            state = inp
        else:
            if inp is None:
                inp = obj.simulation._stateBase__initialStateInput.value
            state = _initialState(obj, inp)
        return state
    return wrapper

class genericQSys(qBaseSim):
    instances = 0
    label = 'genericQSys'

    toBeSaved = qBaseSim.toBeSaved.extendedCopy(['dimension'])

    __slots__ = ['__unitary', '__dimension', '__dimsBefore', '__dimsAfter']

    def __init__(self, **kwargs):
        super().__init__()
        self.__unitary = freeEvolution(_internal=True)
        self._genericQSys__unitary.superSys = self # pylint: disable=no-member
        self._qBaseSim__simulation.subSys[self._freeEvol] = self # pylint: disable=no-member
        self.__dimension = None

        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def __add__(self, other):
        if isinstance(self, compQSystem) and isinstance(other, qSystem):
            self.addSubSys(other)
            newComp = self
        elif ((isinstance(self, qSystem) and isinstance(other, qSystem)) or
              (isinstance(self, compQSystem) and isinstance(other, compQSystem))):
            newComp = compQSystem()
            newComp.addSubSys(self)
            if other is self:
                newComp.addSubSys(other.copy())
            else:
                newComp.addSubSys(other)
        elif isinstance(self, qSystem) and isinstance(other, compQSystem):
            other.addSubSys(self)
            newComp = other
        return newComp

    def __sub__(self, other):
        self.removeSubSys(other, _exclude=[])
        return self

    @property
    def _dimsBefore(self):
        return self._genericQSys__dimsBefore if self._genericQSys__dimsBefore != 0 else 1

    @_dimsBefore.setter
    def _dimsBefore(self, val):
        self._paramUpdated = True
        if not isinstance(val, int):
            raise ValueError('?')
        oldVal = self._dimsBefore
        self._genericQSys__dimsBefore = val # pylint: disable=assigning-non-slot
        for sys in self.subSys.values():
            if isinstance(sys, genericQSys):
                sys._dimsBefore = int((sys._dimsBefore*val)/oldVal)

    @property
    def _dimsAfter(self):
        return self._genericQSys__dimsAfter if self._genericQSys__dimsAfter != 0 else 1

    @_dimsAfter.setter
    def _dimsAfter(self, val):
        self._paramUpdated = True
        if not isinstance(val, int):
            raise ValueError('?')
        oldVal = self._dimsAfter
        self._genericQSys__dimsAfter = val # pylint: disable=assigning-non-slot
        for sys in self.subSys.values():
            if isinstance(sys, genericQSys):
                sys._dimsAfter = int((sys._dimsAfter*val)/oldVal)

    @property
    def _totalDim(self):
        return self.dimension * self._dimsBefore * self._dimsAfter#pylint:disable=E1101

    @property
    def ind(self):
        ind = 0
        if self.superSys is not None:
            ind += list(self.superSys.subSys.values()).index(self)
            if self.superSys.superSys is not None:
                ind += self.superSys.ind
        return ind

    def save(self):
        saveDict = super().save()
        if self.simulation._stateBase__initialStateInput.value is not None:# pylint: disable=no-member, protected-access
            if hasattr(self.simulation._stateBase__initialStateInput.value, 'A'): # pylint: disable=E1101, W0212
                saveDict['_stateBase__initialStateInput'] =\
                    self.simulation._stateBase__initialStateInput.value.A # pylint: disable=no-member, protected-access
            else:
                saveDict['_stateBase__initialStateInput'] =\
                    self.simulation._stateBase__initialStateInput.value # pylint: disable=no-member, protected-access
        return saveDict

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
    def unitary(self):
        unitary = self._genericQSys__unitary.unitary
        self._paramUpdated = False
        return unitary

    @property
    def _freeEvol(self):
        return self._genericQSys__unitary

    @qBaseSim.initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        if self.superSys is not None:
            self.superSys.simulation._stateBase__initialState._value = None
        self.simulation.initialState = inp # pylint: disable=no-member, protected-access
        if (isinstance(self, compQSystem) and isinstance(inp, list)):
            for ind, it in enumerate(inp):
                list(self.qSystems.values())[ind].initialState = it # pylint: disable=no-member

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
        newSys._qUniversal__setKwargs(**kwargs)
        return newSys

    def _constructMatrices(self):
        for sys in self.subSys.values():
            sys._constructMatrices() # pylint: disable=protected-access

class QuantumSystem(genericQSys):
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
    @_initStDec
    def _initialState(self, inp=None):
        if inp is None:
            inp = [qsys._initialState() for qsys in self.subSys.values()]
        elif isinstance(inp, list):
            inp = [qsys._initialState(inp[qsys.ind]) for qsys in self.subSys.values()]
        else:
            raise TypeError('?')
        return qSta.tensorProd(*inp)

    instances = 0
    label = 'QuantumSystem'

    __slots__ = ['__qCouplings', '__qSystems', 'couplingName']

    def __init__(self, **kwargs):
        if self.__class__ == compQSystem:
            self._incrementInstances(val=qSystem.instances)
        super().__init__()
        self.__qCouplings = OrderedDict()
        self.__qSystems = OrderedDict()
        self.couplingName = None

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        qsys = {}
        for sys in self.subSys.values():
            qsys[sys.name] = sys.save()
        saveDict['qSystems'] = qsys
        qcou = {}
        for cou in self.qCouplings.values():
            qcou[cou.name] = cou.save()
        saveDict['qCouplings'] = qcou
        return saveDict

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
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @property
    def couplingHam(self):
        cham = sum([val.totalHam for val in self.qCouplings.values()])
        return cham

    @property
    def qSystems(self):
        return self._compQSystem__qSystems # pylint: disable=no-member

    @checkClass('qUniversal')
    def addSubSys(self, subSys, **kwargs): # pylint: disable=arguments-differ
        newSys = super().addSubSys(subSys, **kwargs)
        if isinstance(newSys, qCoupling):
            self._compQSystem__addCoupling(self._qUniversal__subSys.pop(newSys.name))  # pylint: disable=no-member
        elif isinstance(newSys, genericQSys):
            self._compQSystem__addSub(newSys)
        else:
            raise TypeError('?')
        newSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return newSys

    def createSubSys(self, subSysClass, **kwargs):
        return self.addSubSys(subSysClass, **kwargs)

    @_recurseIfList
    def removeSubSys(self, subS, _exclude=[]):#pylint:disable=arguments-differ,dangerous-default-value,too-many-branches
        if isinstance(subS, str):
            subS = self.getObjByName(subS)
        couplings = list(self.qCouplings.values())
        for coupling in couplings:
            coupling.removeSubSys(subS, _exclude=_exclude)
            if len(coupling._qUniversal__subSys) == 0: # pylint: disable=protected-access
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

    def __addSub(self, subSys):
        for subS in self._compQSystem__qSystems.values():
            subS._dimsAfter *= subSys.dimension
            subSys._dimsBefore *= subS.dimension

        if subSys._paramBoundBase__matrix is not None:
            for sys in subSys.subSys.values():
                sys._paramBoundBase__matrix = None
        subSys.simulation._bound(self.simulation) # pylint: disable=protected-access
        self._compQSystem__qSystems[subSys.name] = subSys
        subSys.superSys = self
        return subSys

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

    def _constructMatrices(self):
        super()._constructMatrices()
        for sys in self.qCouplings.values():
            sys._constructMatrices() # pylint: disable=protected-access

    def updateDimension(self, qSys, newDimVal, oldDimVal=None):
        self._genericQSys__dimension = None # pylint: disable=assigning-non-slot
        if oldDimVal is None:
            oldDimVal = qSys._genericQSys__dimension
        self.delMatrices(_exclude=[])
        qSys._genericQSys__dimension = newDimVal
        ind = qSys.ind
        for qS in self.qSystems.values():
            if qS.ind < ind:
                qS._dimsAfter = int((qS._dimsAfter*newDimVal)/oldDimVal)
            elif qS.ind > ind:
                qS._dimsBefore = int((qS._dimsBefore*newDimVal)/oldDimVal)

        if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=no-member, W0212
            self.initialState = self.simulation._stateBase__initialStateInput.value # pylint: disable=no-member, W0212
        self._paramUpdated = True
        self._constructMatrices()
        for sys in self.subSys.values():
            if sys.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=protected-access
                sys.initialState = sys.simulation._stateBase__initialStateInput.value # pylint: disable=protected-access
        return qSys

class term(paramBoundBase):
    instances = 0
    label = 'term'

    __slots__ = ['__frequency', '__operator', '__order']

    def __init__(self, **kwargs):
        super().__init__()
        self.__frequency = None
        self.__operator = None
        self.__order = 1
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @paramBoundBase.superSys.setter
    def superSys(self, supSys):
        paramBoundBase.superSys.fset(self, supSys) # pylint: disable=no-member
        for i in range(self.instances + 1):
            if self.name == str('term' + str(i)):
                name = self.superSys.name + 'term' + str(len(self.superSys.subSys)+1) # pylint: disable=no-member
                self.name = name
                self.superSys.terms = list(self.superSys.subSys.values()) # pylint: disable=no-member
                break

    @property
    def operator(self):
        return self._term__operator

    @operator.setter
    def operator(self, op):
        self._paramUpdated = True
        self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
        self._term__operator = op # pylint: disable=assigning-non-slot

    @property
    def frequency(self):
        return self._term__frequency

    @frequency.setter
    def frequency(self, freq):
        if freq == 0.0:
            freq = 0
        self._paramUpdated = True
        self._term__frequency = freq # pylint: disable=assigning-non-slot

    @property
    def order(self):
        return self._term__order

    @order.setter
    def order(self, ordVal):
        self._paramUpdated = True
        self._term__order = ordVal # pylint: disable=assigning-non-slot
        if self._paramBoundBase__matrix is not None: # pylint: disable=no-member
            self.freeMat = None

    @property
    def freeMat(self):
        if ((self._paramBoundBase__matrix is None) or (self._paramUpdated)): # pylint: disable=no-member
            self.freeMat = None
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qOpsFunc):
        if callable(qOpsFunc):
            self.operator = qOpsFunc
            self._constructMatrices()
        elif qOpsFunc is not None:
            self._paramBoundBase__matrix = qOpsFunc  # pylint: disable=assigning-non-slot
        else:
            if self.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self._constructMatrices()

    def _constructMatrices(self):
        if not (isinstance(self.superSys.dimension, (int, int64, int32, int16)) and callable(self.operator)): # pylint: disable=no-member
            raise TypeError('?')

        dimension = self.superSys._genericQSys__dimension # pylint: disable=no-member
        if self.operator in [qOps.Jz, qOps.Jy, qOps.Jx, qOps.Jm, qOps.Jp, qOps.Js]:
            dimension = 0.5*(dimension-1)

        try:
            self._paramBoundBase__matrix = qOps.compositeOp(self.operator(dimension), #pylint:disable=assigning-non-slot
                                                            self.superSys._dimsBefore, # pylint: disable=no-member
                                                            self.superSys._dimsAfter)**self.order # pylint: disable=no-member
        except: # pylint: disable=bare-except
            self._paramBoundBase__matrix = qOps.compositeOp( # pylint: disable=no-member, assigning-non-slot
                self.operator(),
                self.superSys._dimsBefore, # pylint: disable=no-member
                self.superSys._dimsAfter)**self.order # pylint: disable=no-member
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def copy(self, **kwargs):  # pylint: disable=arguments-differ
        newSys = super().copy(frequency=self.frequency, operator=self.operator, order=self.order, **kwargs)
        return newSys

class qSystem(genericQSys):
    @_initStDec
    def _initialState(self, inp=None):
        if inp is None:
            raise ValueError(self.name + ' is not given an initial state')
        return qSta.superPos(self.dimension, inp)

    instances = 0
    label = 'QuantumSystem'

    __slots__ = []
    #@qSystemInitErrors
    def __init__(self, **kwargs):
        if self.__class__ == qSystem:
            self._incrementInstances(val=compQSystem.instances)
        super().__init__()
        qSysKwargs = ['terms', 'subSys', 'name', 'superSys']
        for key in qSysKwargs:
            val = kwargs.pop(key, None)
            if val is not None:
                setattr(self, key, val)
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

        if len(self.subSys) == 0:
            self.addSubSys(term(superSys=self, **kwargs))

    def save(self):
        saveDict = super().save()
        qsys = {}
        for sys in self.subSys.values():
            qsys[sys.operator.__name__] = {
                'frequency': sys.frequency,
                'operator': sys.operator.__name__,
                'order': sys.order
            }
        saveDict['terms'] = qsys
        return saveDict

    @genericQSys.dimension.setter # pylint: disable=no-member
    def dimension(self, newDimVal):
        if self._genericQSys__dimension is not None: # pylint: disable=no-member
            oldDimVal = self._genericQSys__dimension # pylint: disable=no-member

            if not isinstance(newDimVal, (int, int64, int32, int16)):
                raise ValueError('Dimension is not int')
            self._genericQSys__dimension = newDimVal # pylint: disable=assigning-non-slot
            for sys in self.subSys.values():
                sys.delMatrices(_exclude=[]) # pylint: disable=protected-access

            if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=protected-access
                self.initialState = self.simulation._stateBase__initialStateInput.value # pylint: disable=protected-access
            self._paramUpdated = True

            if isinstance(self.superSys, compQSystem):
                self.superSys.updateDimension(self, newDimVal, oldDimVal) # pylint: disable=no-member
        elif self._genericQSys__dimension is None: # pylint: disable=no-member
            self._genericQSys__dimension = newDimVal # pylint: disable=assigning-non-slot

    @property
    def totalHam(self): # pylint: disable=invalid-overridden-method
        if ((self._paramUpdated) or (self._paramBoundBase__matrix is None)): # pylint: disable=no-member
            h = sum([(obj.frequency * obj.freeMat) for obj in self.subSys.values() if obj.frequency != 0])
            self._paramBoundBase__matrix = h # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

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
        operators = [obj._term__operator for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return operators if len(operators) > 1 else operators[0]

    @operator.setter
    def operator(self, op):
        self._paramUpdated = True
        firstTerm = self.firstTerm
        setattr(firstTerm, '_paramBoundBase__matrix', None)
        setattr(firstTerm, '_term__operator', op)

    @property
    def frequency(self):
        frequencies = [obj._term__frequency for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return frequencies if len(frequencies) > 1 else frequencies[0]

    @frequency.setter
    def frequency(self, freq):
        if freq == 0.0:
            freq = 0
        self._paramUpdated = True
        setattr(self.firstTerm, '_term__frequency', freq)

    @property
    def order(self):
        orders = [obj._term__order for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return orders if len(orders) > 1 else orders[0]

    @order.setter
    def order(self, ordVal):
        self._paramUpdated = True
        setattr(self.firstTerm, '_term__order', ordVal)
        self.firstTerm.freeMat = None

    @property
    def firstTerm(self):
        return list(self.subSys.values())[0]

    @property
    def terms(self):
        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @checkClass('qUniversal')
    def addSubSys(self, subS, **kwargs):
        kwargs.pop('superSys', None)
        if not isinstance(subS, term):
            raise TypeError('?')
        newS = super().addSubSys(subS, superSys=self, **kwargs)
        newS._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access

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

    def addTerm(self, op, freq, order=1):
        newTerm = super().addSubSys(term, operator=op, frequency=freq, order=order, superSys=self)
        return newTerm

    @_recurseIfList
    def removeTerm(self, termObj):
        self.removeSubSys(termObj, _exclude=[])

class Spin(qSystem):
    instances = 0
    label = 'Spin'

    __slots__ = ['__jValue']
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None))
        self.operator = qOps.Jz
        self.__jValue = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def jValue(self):
        return (self._genericQSys__dimension-1)/2 # pylint: disable=no-member

    @jValue.setter
    def jValue(self, value):
        self._Spin__jValue = value # pylint: disable=assigning-non-slot
        self.dimension = int((2*value) + 1)

class Qubit(Spin): # pylint: disable=too-many-ancestors
    instances = 0
    label = 'Qubit'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None))
        kwargs['dimension'] = 2
        self.operator = qOps.Jz
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

class Cavity(qSystem):
    instances = 0
    label = 'Cavity'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None))
        self.operator = qOps.number
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

# quantum coupling object
class qCoupling(paramBoundBase):
    instances = 0
    label = 'qCoupling'

    toBeSaved = qBaseSim.toBeSaved.extendedCopy(['couplingStrength'])

    __slots__ = ['__couplingStrength']

    #@qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__couplingStrength = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self.addTerm(*args)

    def save(self):
        saveDict = super().save()
        qsys = {}
        for idx, sys in enumerate(self.coupledSystems):
            qsys['term' + str(idx)] = [[op.__name__ for op in self.couplingOperators[idx]], [sy.name for sy in sys]]
        saveDict['terms'] = qsys
        return saveDict

    # TODO might define setters
    @property
    def couplingOperators(self):
        return list(self._qUniversal__subSys.keys()) # pylint: disable=no-member

    @property
    def coupledSystems(self):
        return list(self._qUniversal__subSys.values()) # pylint: disable=no-member

    @property
    def totalHam(self):
        if ((self._paramUpdated) or (self._paramBoundBase__matrix is None)): # pylint: disable=no-member
            h = []
            if self.couplingStrength != 0:
                h = [self.couplingStrength * self.freeMat]
            self._paramBoundBase__matrix = sum(h) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @property
    def freeMat(self):
        if ((self._paramBoundBase__matrix is None) or (self._paramUpdated)): # pylint: disable=no-member
            self.freeMat = None
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qMat):
        if qMat is not None:
            self._paramBoundBase__matrix = qMat # pylint: disable=no-member, assigning-non-slot
        else:
            if len(self._qUniversal__subSys) == 0: # pylint: disable=no-member
                raise ValueError('No operator is given for coupling Hamiltonian')
            self._constructMatrices()

    @property
    def couplingStrength(self):
        return self._qCoupling__couplingStrength

    @couplingStrength.setter
    def couplingStrength(self, strength):
        if strength == 0.0:
            strength = 0
        self._paramUpdated = True
        self._qCoupling__couplingStrength = strength # pylint: disable=assigning-non-slot

    def __coupOrdering(self, qts): # pylint: disable=no-self-use
        qts = sorted(qts, key=lambda x: x[0], reverse=False)
        oper = qts[0][1]
        for ops in range(len(qts)-1):
            oper = oper @ qts[ops+1][1]
        return oper

    def _constructMatrices(self):
        cMats = []
        for ind in range(len(self._qUniversal__subSys)): # pylint: disable=no-member
            qts = []
            for indx in range(len(list(self._qUniversal__subSys.values())[ind])): # pylint: disable=no-member
                sys = list(self._qUniversal__subSys.values())[ind][indx] # pylint: disable=no-member
                order = sys.ind
                oper = list(self._qUniversal__subSys.keys())[ind][indx] # pylint: disable=no-member
                cHam = qOps.compositeOp(oper(sys._genericQSys__dimension), sys._dimsBefore, sys._dimsAfter)
                ts = [order, cHam]
                qts.append(ts)
            cMats.append(self._qCoupling__coupOrdering(qts))
        self._paramBoundBase__matrix = sum(cMats) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def __addTerm(self, count, ind, sys, *args):
        if callable(args[count][ind]):
            self._qUniversal__subSys[tuple(args[count])] = sys # pylint: disable=no-member
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
                    if tuple(args[counter + 1]) in self._qUniversal__subSys.keys(): # pylint: disable=no-member
                        print(tuple(args[counter + 1]), 'already exists')
                    self._qUniversal__subSys[tuple(args[counter + 1])] = qSystems # pylint: disable=no-member
                    counter += 2
                # TODO does not have to pass qSystem around
                if counter < len(args):
                    counter = self._qCoupling__addTerm(counter, 1, qSystems, *args)
        return self

    @_recurseIfList
    def removeSysCoupling(self, sys):
        self.removeSubSys(sys, _exclude=[])

    @_recurseIfList
    def removeSubSys(self, subS, _exclude=[]): # pylint: disable=dangerous-default-value
        _exclude.append(self)
        subSysVals = self.coupledSystems
        subSysKeys = self.couplingOperators
        for ind, sysList in enumerate(subSysVals):
            if subS in sysList:
                super().removeSubSys(subSysKeys[ind], _exclude=_exclude)

class envCoupling(qCoupling):
    instances = 0
    label = 'envCoupling'

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
