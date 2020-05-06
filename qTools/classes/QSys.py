from numpy import (int64, int32, int16)
import qTools.QuantumToolbox.operators as qOps
import qTools.QuantumToolbox.states as qSta
from qTools.classes.qBaseSim import qBaseSim
from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from qTools.classes.extensions.QSysDecorators import InitialStateDecorator, constructConditions
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
        self.__dimension = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        if self._qBase__initialStateInput is not None: # pylint: disable=no-member
            if hasattr(self._qBase__initialStateInput, 'A'): # pylint: disable=no-member
                saveDict['_qBase__initialStateInput'] = self._qBase__initialStateInput.A # pylint: disable=no-member
            else:
                saveDict['_qBase__initialStateInput'] = self._qBase__initialStateInput # pylint: disable=no-member
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
            This works by assuming that its setter/s makes sure that _qBase__initialState is not None for single systems,
            if its state is set.
            If single system initial state is not set, it will try creating here, but single system does not have qSystem,
            so will raise the below error.
        """
        if self._qBase__initialState is None: # pylint: disable=no-member
            try:
                self._qBase__initialState = qSta.tensorProd(*[val.initialState for val in self.qSystems.values()]) # pylint: disable=assigning-non-slot
            except AttributeError:
                raise ValueError(self.name + ' is not given an initial state')
        return self._qBase__initialState # pylint: disable=no-member

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
    @InitialStateDecorator
    def initialState(self, inp):
        if inp != 'sparse':
            for ind, it in enumerate(inp):
                list(self.qSystems.values())[ind].initialState = it
            self._qBase__initialState = qSta.compositeState([val.dimension for val in self.subSys.values()], inp) # pylint: disable=assigning-non-slot

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
        elif isinstance(newSys, (qSystem, self.__class__)):
            self._QuantumSystem__addSub(newSys)
        else:
            raise TypeError('?')
        newSys._qBase__paramBound[self.name] = self # pylint: disable=protected-access
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
            subSys._qSystem__dimsBefore *= subS._genericQSys__dimension
            subS._qSystem__dimsAfter *= subSys._genericQSys__dimension

        if subSys._qUniversal__matrix is not None:
            subSys._qUniversal__matrix = None

        self._QuantumSystem__qSystems[subSys.name] = subSys
        setattr(subSys, '_qUniversal__ind', len(self._QuantumSystem__qSystems))
        subSys.superSys = self
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
        self.delMatrices()
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

        self.delMatrices()

        qSys._genericQSys__dimension = newDimVal
        ind = qSys.ind
        for qS in self.qSystems.values():
            if qS.ind < ind:
                qS._qSystem__dimsAfter = int((qS._qSystem__dimsAfter*newDimVal)/oldDimVal)
            elif qS.ind > ind:
                qS._qSystem__dimsBefore = int((qS._qSystem__dimsBefore*newDimVal)/oldDimVal)

        if self._qBase__initialStateInput is not None: # pylint: disable=no-member
            self.initialState = self._qBase__initialStateInput # pylint: disable=no-member
        self._paramUpdated = True
        self._constructMatrices()
        for sys in self.subSys.values():
            if sys._qBase__initialStateInput is not None: # pylint: disable=protected-access
                sys.initialState = sys._qBase__initialStateInput # pylint: disable=protected-access
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
            sys.delMatrices() # pylint: disable=protected-access
            if sys._qBase__initialStateInput is not None: # pylint: disable=protected-access
                sys.initialState = sys._qBase__initialStateInput # pylint: disable=protected-access
            sys._paramUpdated = True

        if isinstance(self.superSys, QuantumSystem):
            self.superSys.updateDimension(self, newDimVal, oldDimVal) # pylint: disable=no-member

    @genericQSys.totalHam.getter # pylint: disable=no-member
    def totalHam(self): # pylint: disable=invalid-overridden-method
        h = sum([(obj.frequency * obj.freeMat) for obj in self.subSys.values()])
        return h

    @property
    def freeMat(self):
        if self._qUniversal__matrix is None: # pylint: disable=no-member
            self.freeMat = None
        return self._qUniversal__matrix # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qOpsFunc):
        if callable(qOpsFunc):
            self.operator = qOpsFunc
            self._constructMatrices()
        elif qOpsFunc is not None:
            self._qUniversal__matrix = qOpsFunc  # pylint: disable=assigning-non-slot
        else:
            if self.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self._constructMatrices()

    @genericQSys.initialState.setter # pylint: disable=no-member
    @InitialStateDecorator
    def initialState(self, state):
        if state != 'sparse':
            for sys in self.subSys.values():
                sys._qBase__initialStateInput = state # pylint: disable=protected-access
            self._qBase__initialState = qSta.compositeState([self._genericQSys__dimension], [state]) # pylint: disable=assigning-non-slot, no-member

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
        copySys = super().addSubSys(self.__class__, operator=op, frequency=freq)
        copySys.order = order
        return copySys

    @constructConditions({'dimension': (int, int64, int32, int16), 'operator': qOps.sigmax.__class__})
    def _constructMatrices(self):
        for sys in self.subSys.values():
            try:
                sys._qUniversal__matrix = qOps.compositeOp(sys.operator(self._genericQSys__dimension), # pylint: disable=no-member
                                                           self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
            except: # pylint: disable=bare-except
                sys._qUniversal__matrix = qOps.compositeOp(sys.operator(), # pylint: disable=no-member
                                                           self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
        return self._qUniversal__matrix # pylint: disable=no-member

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
class qCoupling(genericQSys):
    instances = 0
    label = 'qCoupling'

    toBeSaved = qBaseSim.toBeSaved.extendedCopy(['couplingStrength'])

    __slots__ = ['__cFncs', '__couplingStrength', '__qSys']

    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__couplingStrength = None
        self.__cFncs = []
        self.__qSys = []
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
        return self._qCoupling__cFncs

    @property
    def coupledSystems(self):
        return self._qCoupling__qSys

    # FIXME all the below explicitly or implicitly assumes that this is a system coupling,
    # so these should be generalised and explicit ones moved into sysCoupling
    @property
    def totalHam(self):
        h = self.couplingStrength * self.freeMat
        return h

    @property
    def freeMat(self):
        return self._qUniversal__matrix # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qMat):
        if qMat is not None:
            self._qUniversal__matrix = qMat # pylint: disable=no-member, assigning-non-slot
        else:
            if len(self._qCoupling__cFncs) == 0:
                raise ValueError('No operator is given for coupling Hamiltonian')
            self._qUniversal__matrix = self._qCoupling__getCoupling() # pylint: disable=no-member, assigning-non-slot

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
        for ind in range(len(self._qCoupling__cFncs)):
            qts = []
            for indx in range(len(self._qCoupling__qSys[ind])):
                sys = self._qCoupling__qSys[ind][indx]
                order = sys.ind
                oper = self._qCoupling__cFncs[ind][indx]
                cHam = qOps.compositeOp(oper(sys._genericQSys__dimension), sys._qSystem__dimsBefore, sys._qSystem__dimsAfter)
                ts = [order, cHam]
                qts.append(ts)
            cMats.append(self._qCoupling__coupOrdering(qts))
        cHam = sum(cMats)
        return cHam

    def __addTerm(self, count, ind, sys, *args):
        if callable(args[count][ind]):
            self._qCoupling__cFncs.append(args[count])
            self._qCoupling__qSys.append(sys)
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
                    self._qCoupling__cFncs.append(args[counter + 1])
                    self._qCoupling__qSys.append(qSystems)
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

class sysCoupling(qCoupling):
    instances = 0
    label = 'sysCoupling'

    __slots__ = []

    def __init__(self, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
