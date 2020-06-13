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
from qTools.classes.QUni import checkClass


class genericQSys(qBaseSim):
    instances = 0
    label = 'genericQSys'

    toBeSaved = qBaseSim.toBeSaved.extendedCopy(['dimension'])

    __slots__ = ['__unitary', '__dimension', '__dimsBefore', '__dimsAfter']

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

    @property
    def _dimsBefore(self):
        return self._genericQSys__dimsBefore

    @_dimsBefore.setter
    def _dimsBefore(self, val):
        if not isinstance(val, int):
            raise ValueError('?')
        self._genericQSys__dimsBefore = val # pylint: disable=assigning-non-slot
        for sys in self.subSys.values():
            if isinstance(sys, genericQSys):
                sys._dimsBefore *= val

    @property
    def _dimsAfter(self):
        return self._genericQSys__dimsAfter

    @_dimsAfter.setter
    def _dimsAfter(self, val):
        if not isinstance(val, int):
            raise ValueError('?')
        self._genericQSys__dimsAfter = val # pylint: disable=assigning-non-slot
        for sys in self.subSys.values():
            if isinstance(sys, genericQSys):
                sys._dimsAfter *= val

    @property
    def _totalDim(self):
        return self.dimension * self._dimsBefore * self._dimsAfter#pylint:disable=E1101

    def __init__(self, **kwargs):
        super().__init__()
        self.__unitary = freeEvolution(_internal=True)
        self._genericQSys__unitary.superSys = self # pylint: disable=no-member
        self._qBaseSim__simulation.subSys[self._freeEvol] = self # pylint: disable=no-member
        self.__dimension = None

        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

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

    @property
    def initialState(self):
        """
            This works by assuming that its setter/s makes sure that _stateBase__initialState.value is not None
             for single systems,
            if its state is set.
            If single system initial state is not set, it will try creating here,
             but single system does not have qSystem,
              so will raise the below error.
        """
        if self.simulation._stateBase__initialState.value is None: # pylint: disable=protected-access
            try:
                self.simulation._stateBase__initialState.value =\
                    qSta.tensorProd(*[val.initialState for val in self.qSystems.values()]) # pylint: disable=W0212
            except AttributeError:
                raise ValueError(self.name + ' is not given an initial state')
        return self.simulation._stateBase__initialState.value # pylint: disable=protected-access

    @initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        if self.superSys is not None:
            self.superSys.simulation._stateBase__initialState._value = None
        self.simulation._stateBase__initialStateInput.value = inp # pylint: disable=no-member, protected-access
        if (issparse(inp) or isinstance(inp, ndarray)):
            if inp.shape[0] == self.dimension: # pylint: disable=comparison-with-callable
                self.simulation._stateBase__initialState.value = inp # pylint: disable=protected-access
            else:
                raise ValueError('Dimension mismatch')
        else:
            if isinstance(self, compQSystem):
                for ind, it in enumerate(inp):
                    list(self.qSystems.values())[ind].initialState = it # pylint: disable=no-member
                self.simulation._stateBase__initialState.value = qSta.compositeState(self.subSysDimensions, inp) # pylint: disable=protected-access, no-member
            elif isinstance(self, qSystem):
                self.simulation._stateBase__initialState.value = qSta.compositeState([self.dimension], [inp])
        return self.simulation._stateBase__initialState.value # pylint: disable=protected-access

    def copy(self, **kwargs):  # pylint: disable=arguments-differ
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
            newSys.simulation._stateBase__initialState.value = self.simulation._stateBase__initialState.value
            newSys.simulation._stateBase__initialStateInput.value = self.simulation._stateBase__initialStateInput.value
        newSys._qUniversal__setKwargs(**kwargs)
        return newSys

    def _constructMatrices(self):
        for sys in self.subSys.values():
            sys._constructMatrices() # pylint: disable=protected-access

class QuantumSystem(genericQSys):
    def __new__(cls, sysType='composite', **kwargs):
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

# Composite Quantum system
class compQSystem(genericQSys):
    instances = 0
    label = 'QuantumSystem'

    __slots__ = ['__qCouplings', '__qSystems', 'couplingName']

    def __init__(self, **kwargs):
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

    def removeSubSys(self, subS):
        if isinstance(subS, str):
            subS = self.getObjByName(subS)
        self.updateDimension(subS, newDimVal=1, oldDimVal=subS.dimension)
        super().removeSubSys(subS)

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
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
        self._term__operator = op # pylint: disable=assigning-non-slot

    @property
    def frequency(self):
        return self._term__frequency

    @frequency.setter
    def frequency(self, freq):
        if freq == 0.0:
            freq = 0
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._term__frequency = freq # pylint: disable=assigning-non-slot

    @property
    def order(self):
        return self._term__order

    @order.setter
    def order(self, ordVal):
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._term__order = ordVal # pylint: disable=assigning-non-slot
        if self._paramBoundBase__matrix is not None: # pylint: disable=no-member
            self.freeMat = None

    @property
    def freeMat(self):
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
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

# quantum system objects
class qSystem(genericQSys):
    instances = 0
    label = 'qSystem'

    __slots__ = []
    #@qSystemInitErrors
    def __init__(self, **kwargs):
        super().__init__()

        qSysKwargs = ['terms', 'subSys', 'name', 'superSys']
        for key in qSysKwargs:
            val = kwargs.pop(key, None)
            if val is not None:
                self._qUniversal__setKwargs(key=val) # pylint: disable=no-member

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
        if self.firstTerm._paramBoundBase__matrix is None: # pylint: disable=no-member
            self.firstTerm.freeMat = None
        return self.firstTerm._paramBoundBase__matrix # pylint: disable=no-member

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

    @terms.setter
    def terms(self, subS):
        genericQSys.subSys.fset(self, subS) # pylint: disable=no-member
        for sys in self.subSys.values():
            sys.superSys = self

    def addTerm(self, op, freq, order=1):
        newTerm = super().addSubSys(term, operator=op, frequency=freq, order=order, superSys=self)
        return newTerm

    def removeTerm(self, termObj):
        self.removeSubSys(termObj)
class Spin(qSystem):
    instances = 0
    label = 'Spin'

    __slots__ = ['__jValue']
    def __init__(self, **kwargs):
        super().__init__()
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
        super().__init__()
        kwargs['dimension'] = 2
        self.operator = qOps.Jz
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

class Cavity(qSystem):
    instances = 0
    label = 'Cavity'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
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
            h = [self.couplingStrength * self.freeMat]
            if self.couplingStrength == 0:
                h = []
            self._paramBoundBase__matrix = sum(h) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @property
    def freeMat(self):
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
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

class envCoupling(qCoupling):
    instances = 0
    label = 'envCoupling'

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
