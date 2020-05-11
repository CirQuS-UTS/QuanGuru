from numpy import (int64, int32, int16, ndarray)
from scipy.sparse import issparse
import qTools.QuantumToolbox.operators as qOps
import qTools.QuantumToolbox.states as qSta
from qTools.classes.qBaseSim import qBaseSim
from qTools.classes.computeBase import paramBoundBase
from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from qTools.classes.extensions.QSysDecorators import constructConditions
from qTools.classes.QPro import freeEvolution


class genericQSys(qBaseSim):
    instances = 0
    label = 'genericQSys'

    toBeSaved = qBaseSim.toBeSaved.extendedCopy(['dimension'])

    __slots__ = ['__unitary', '__dimension']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__unitary = freeEvolution(_internal=True)
        self._genericQSys__unitary.superSys = self # pylint: disable=no-member
        self._qBaseSim__simulation.subSys[self._freeEvol] = self # pylint: disable=no-member
        self.__dimension = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=no-member, protected-access
            if hasattr(self.simulation._stateBase__initialStateInput.value, 'A'): # pylint: disable=no-member, protected-access
                saveDict['_stateBase__initialStateInput'] = self.simulation._stateBase__initialStateInput.value.A # pylint: disable=no-member, protected-access
            else:
                saveDict['_stateBase__initialStateInput'] = self.simulation._stateBase__initialStateInput.value # pylint: disable=no-member, protected-access
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
    def totalHam(self):
        return None

    # Unitary property and setter
    @property
    def unitary(self):
        unitary = self._genericQSys__unitary.unitary()
        self._paramUpdated = False
        return unitary

    @property
    def _freeEvol(self):
        return self._genericQSys__unitary

    # initial state
    @property
    def initialState(self):
        """
            This works by assuming that its setter/s makes sure that _stateBase__initialState.value is not None for single systems,
            if its state is set.
            If single system initial state is not set, it will try creating here, but single system does not have qSystem,
            so will raise the below error.
        """
        if self.simulation._stateBase__initialState.value is None: # pylint: disable=protected-access
            try:
                self.simulation._stateBase__initialState.value = qSta.tensorProd(*[val.initialState for val in self.qSystems.values()]) # pylint: disable=protected-access
            except AttributeError:
                raise ValueError(self.name + ' is not given an initial state')
        return self.simulation._stateBase__initialState.value # pylint: disable=protected-access

    def dress(self):
        pass

    def copy(self, **kwargs):  # pylint: disable=arguments-differ
        try:
            newSys = super().copy(dimension=self.dimension, frequency=self.frequency, operator=self.operator)
        except AttributeError:
            newSys = super().copy()
        newSys._qUniversal__setKwargs(**kwargs)
        for sys in self.subSys.values():
            if sys is not self:
                newSys.addSubSys(sys.copy())
        return newSys

class universalQSys(genericQSys):
    def __new__(cls, sysType='single', **kwargs):
        if sysType == 'single':
            newCls = qSystem
        elif sysType == 'composite':
            newCls = QuantumSystem
        elif sysType == 'system coupling':
            newCls = qCoupling
        if newCls != cls:
            instance = newCls(**kwargs)
        return instance

    __slots__ = []

# Composite Quantum system
class QuantumSystem(genericQSys):
    instances = 0
    label = 'QuantumSystem'

    __slots__ = ['__qCouplings', '__qSystems', 'couplingName', '__kept']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__qCouplings = {}
        self.__qSystems = {}

        self.couplingName = None

        self.__kept = {}
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

    # free, coupling, and total Hamiltonians of the composite system
    @property
    def subSysDimensions(self):
        return [sys.dimension for sys in self.subSys.values()]

    @property
    def freeHam(self):
        ham = sum([val.totalHam for val in self.qSystems.values()])
        return ham

    @genericQSys.totalHam.getter # pylint: disable=no-member
    def totalHam(self): # pylint: disable=invalid-overridden-method
        return self.freeHam + self.couplingHam

    @property
    def couplingHam(self):
        cham = sum([val.totalHam for val in self.qCouplings.values()])
        return cham

    @genericQSys.initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self.simulation._stateBase__initialStateInput.value = inp # pylint: disable=no-member, protected-access
        for ind, it in enumerate(inp):
            list(self.qSystems.values())[ind].initialState = it
        self.simulation._stateBase__initialState.value = self._initialState(inp) # pylint: disable=no-member, protected-access

    def _initialState(self, inp):
        if (issparse(inp) or isinstance(inp, ndarray)):
            if inp.shape[0] == self.dimension: # pylint: disable=comparison-with-callable
                return inp
            raise ValueError('Dimension mismatch')
        return qSta.compositeState(self.subSysDimensions, inp)

    # adding or creating a new sub system to composite system
    def add(self, *args):
        for system in args:
            self.addSubSys(system)

    def create(self, *args, n=1):
        print(n)
        for sysClass in args:
            self.addSubSys(sysClass)

    @property
    def qSystems(self):
        return self._qUniversal__subSys # pylint: disable=no-member

    def addSubSys(self, subSys, **kwargs): # pylint: disable=arguments-differ
        newSys = super().addSubSys(subSys, **kwargs)
        if isinstance(newSys, qCoupling):
            self._QuantumSystem__addCoupling(self._qUniversal__subSys.pop(newSys.name))  # pylint: disable=no-member
        elif isinstance(newSys, genericQSys):
            self._QuantumSystem__addSub(newSys)
        else:
            raise TypeError('?')
        newSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return newSys

    def createSubSys(self, subClass=None, n=1, **kwargs): # pylint: disable=arguments-differ
        if subClass is None:
            subClass = qSystem

        newSubs = []
        for _ in range(n):
            newSubs.append(self.addSubSys(subClass, **kwargs))
        return newSubs if n > 1 else newSubs[0]

    def __addSub(self, subSys):
        for subS in self._QuantumSystem__qSystems.values():
            for sys in subS.subSys.values():
                sys._qSystem__dimsAfter *= subSys.dimension
            for sys in subSys.subSys.values():
                sys._qSystem__dimsBefore *= subS.dimension

        if subSys._paramBoundBase__matrix is not None:
            for sys in subSys.subSys.values():
                sys._paramBoundBase__matrix = None

        self._QuantumSystem__qSystems[subSys.name] = subSys
        for sys in subSys.subSys.values():
            setattr(sys, '_qUniversal__ind', len(self._QuantumSystem__qSystems))
            sys.superSys = self
        return subSys

    # adding or creating a new coupling
    @property
    def qCouplings(self):
        return self._QuantumSystem__qCouplings

    def __addCoupling(self, couplingObj):
        self._QuantumSystem__qCouplings[couplingObj.name] = couplingObj
        couplingObj._qUniversal__ind = len(self.qCouplings)
        couplingObj.superSys = self
        return couplingObj

    def createSysCoupling(self, *args, **kwargs):
        newCoupling = self.addSubSys(qCoupling, **kwargs)
        newCoupling.addTerm(*args)
        return newCoupling

    def addSysCoupling(self, couplingObj):
        self.addSubSys(couplingObj)

    # reset and keepOld
    def reset(self, to=None):
        # TODO make sure that the kept protocols deletes their matrices and different sweeps ? delMatrices
        self.delMatrices(_exclude=[])
        name = self.couplingName
        if name is None:
            name = len(self._QuantumSystem__kept)
        self._QuantumSystem__kept[name] = self.qCouplings
        self._paramUpdated = True
        if to is None:
            self._QuantumSystem__qCouplings = {} # pylint: disable=assigning-non-slot
            self._genericQSys__unitary = freeEvolution() # pylint: disable=assigning-non-slot
            self._genericQSys__unitary.superSys = self # pylint: disable=no-member
            self.couplingName = None
        else:
            self.couplingName = to
            self._QuantumSystem__qCouplings = self._QuantumSystem__kept[to][0] # pylint: disable=assigning-non-slot
            self._genericQSys__unitary = self._QuantumSystem__kept[to][1] # pylint: disable=assigning-non-slot

    # construct the matrices
    def _constructMatrices(self):
        for qSys in self.subSys.values():
            qSys.freeMat = None

        for qSys in self.qCouplings.values():
            qSys.freeMat = None

    # update the dimension of a subSystem
    def updateDimension(self, qSys, newDimVal, oldDimVal=None):
        self._genericQSys__dimension = None # pylint: disable=assigning-non-slot
        if oldDimVal is None:
            oldDimVal = qSys._genericQSys__dimension

        self.delMatrices(_exclude=[])

        qSys._genericQSys__dimension = newDimVal
        ind = qSys.ind
        for qS in self.qSystems.values():
            if qS.ind < ind:
                qS._qSystem__dimsAfter = int((qS._qSystem__dimsAfter*newDimVal)/oldDimVal)
            elif qS.ind > ind:
                qS._qSystem__dimsBefore = int((qS._qSystem__dimsBefore*newDimVal)/oldDimVal)

        if self.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=no-member, protected-access
            self.initialState = self.simulation._stateBase__initialStateInput.value # pylint: disable=no-member, protected-access
        self._paramUpdated = True
        self._constructMatrices()
        for sys in self.subSys.values():
            if sys.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=protected-access
                sys.initialState = sys.simulation._stateBase__initialStateInput.value # pylint: disable=protected-access
        return qSys

# quantum system objects
class qSystem(genericQSys):
    instances = 0
    label = 'qSystem'

    __slots__ = ['__frequency', '__operator', '__dimsBefore', '__dimsAfter', '__terms', '__order']
    @qSystemInitErrors
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__frequency = None
        self.__operator = None
        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self.addSubSys(self)
        self.__order = 1
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        qsys = {}
        for sys in self.subSys.values():
            qsys[sys.operator.__name__] = {
                'frequency': sys.frequency,
                'operator': sys.operator.__name__,
                'order': sys.order,
                'ind': sys.ind
            }
        saveDict['terms'] = qsys
        return saveDict

    @genericQSys.dimension.setter # pylint: disable=no-member
    def dimension(self, newDimVal, oldDimVal=None):
        if oldDimVal is None:
            if self._genericQSys__dimension is None: # pylint: disable=no-member
                oldDimVal = newDimVal
            else:
                oldDimVal = self._genericQSys__dimension # pylint: disable=no-member

        if not isinstance(newDimVal, (int, int64, int32, int16)):
            raise ValueError('Dimension is not int')

        for sys in self.subSys.values():
            sys._genericQSys__dimension = newDimVal # pylint: disable=assigning-non-slot
            sys.delMatrices(_exclude=[]) # pylint: disable=protected-access
            if sys.simulation._stateBase__initialStateInput.value is not None: # pylint: disable=protected-access
                sys.initialState = sys.simulation._stateBase__initialStateInput.value # pylint: disable=protected-access
            sys._paramUpdated = True

        if isinstance(self.superSys, QuantumSystem):
            self.superSys.updateDimension(self, newDimVal, oldDimVal) # pylint: disable=no-member

    @genericQSys.totalHam.getter # pylint: disable=no-member
    def totalHam(self): # pylint: disable=invalid-overridden-method
        h = sum([(obj.frequency * obj.freeMat) for obj in self.subSys.values() if obj.frequency != 0])
        return h

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

    @genericQSys.initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        # self.simulation._stateBase__initialStateInput.value = inp # pylint: disable=no-member, protected-access
        # if not (issparse(inp) or isinstance(inp, ndarray)):
        for sys in self.subSys.values():
            sys.simulation._stateBase__initialStateInput.value = inp # pylint: disable=protected-access
            sys.simulation._stateBase__initialState.value = sys._initialState(inp) # pylint: disable=protected-access

    def _initialState(self, inp):
        if (issparse(inp) or isinstance(inp, ndarray)):
            if inp.shape[0] == self.dimension: # pylint: disable=comparison-with-callable
                return inp
            raise ValueError('Dimension mismatch')
        return qSta.compositeState([self.dimension], [inp]) # pylint: disable=no-member

    @property
    def operator(self):
        return self._qSystem__operator

    @operator.setter
    def operator(self, op):
        self._paramUpdated = True
        self._qSystem__operator = op # pylint: disable=assigning-non-slot

    @property
    def frequency(self):
        return self._qSystem__frequency

    @frequency.setter
    def frequency(self, freq):
        if freq == 0.0:
            freq = 0
        self._paramUpdated = True
        self._qSystem__frequency = freq # pylint: disable=assigning-non-slot

    @property
    def order(self):
        return self._qSystem__order

    @order.setter
    def order(self, ordVal):
        self._paramUpdated = True
        self._qSystem__order = ordVal # pylint: disable=assigning-non-slot
        self.freeMat = None

    @property
    def terms(self):
        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    def addTerm(self, op, freq, order=1):
        copySys = super().addSubSys(self.__class__, operator=op, frequency=freq, _qSystem__dimsBefore=self._qSystem__dimsBefore, 
                                    _qSystem__dimsAfter=self._qSystem__dimsAfter)
        copySys.order = order
        return copySys

    @constructConditions({'dimension': (int, int64, int32, int16), 'operator': qOps.sigmax.__class__})
    def _constructMatrices(self):
        for sys in self.subSys.values():
            try:
                sys._paramBoundBase__matrix = qOps.compositeOp(sys.operator(self._genericQSys__dimension), # pylint: disable=no-member
                                                               self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
            except: # pylint: disable=bare-except
                sys._paramBoundBase__matrix = qOps.compositeOp(sys.operator(), # pylint: disable=no-member
                                                               self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
        return self._paramBoundBase__matrix # pylint: disable=no-member

class Qubit(qSystem):
    instances = 0
    label = 'Qubit'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        kwargs['dimension'] = 2
        self.operator = qOps.sigmaz
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @qSystem.totalHam.getter # pylint: disable=no-member
    def totalHam(self):
        h = qSystem.totalHam.fget(self) # pylint: disable=no-member
        return h if self.operator is qOps.number else 0.5*h

class Spin(qSystem):
    instances = 0
    label = 'Spin'

    __slots__ = ['__jValue']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
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

class Cavity(qSystem):
    instances = 0
    label = 'Cavity'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.operator = qOps.number
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

# quantum coupling object
class qCoupling(paramBoundBase):
    instances = 0
    label = 'qCoupling'

    toBeSaved = qBaseSim.toBeSaved.extendedCopy(['couplingStrength'])

    __slots__ = ['__couplingStrength']

    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
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
        h = [self.couplingStrength * self.freeMat]
        return sum(h) if self.couplingStrength != 0 else sum([])

    @property
    def freeMat(self):
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qMat):
        if qMat is not None:
            self._paramBoundBase__matrix = qMat # pylint: disable=no-member, assigning-non-slot
        else:
            if len(self._qUniversal__subSys) == 0: # pylint: disable=no-member
                raise ValueError('No operator is given for coupling Hamiltonian')
            self._paramBoundBase__matrix = self._qCoupling__getCoupling() # pylint: disable=no-member, assigning-non-slot

    @property
    def couplingStrength(self):
        return self._qCoupling__couplingStrength

    @couplingStrength.setter
    def couplingStrength(self, strength):
        self._paramUpdated = True
        self._qCoupling__couplingStrength = strength # pylint: disable=assigning-non-slot

    def __coupOrdering(self, qts): # pylint: disable=no-self-use
        qts = sorted(qts, key=lambda x: x[0], reverse=False)
        oper = qts[0][1]
        for ops in range(len(qts)-1):
            oper = oper @ qts[ops+1][1]
        return oper

    def __getCoupling(self):
        cMats = []
        for ind in range(len(self._qUniversal__subSys)): # pylint: disable=no-member
            qts = []
            for indx in range(len(list(self._qUniversal__subSys.values())[ind])): # pylint: disable=no-member
                sys = list(self._qUniversal__subSys.values())[ind][indx] # pylint: disable=no-member
                order = sys.ind
                oper = list(self._qUniversal__subSys.keys())[ind][indx] # pylint: disable=no-member
                cHam = qOps.compositeOp(oper(sys._genericQSys__dimension), sys._qSystem__dimsBefore, sys._qSystem__dimsAfter)
                ts = [order, cHam]
                qts.append(ts)
            cMats.append(self._qCoupling__coupOrdering(qts))
        cHam = sum(cMats)
        return cHam

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
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
