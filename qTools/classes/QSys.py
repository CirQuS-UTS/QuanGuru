from numpy import (int64, int32, int16)
import qTools.QuantumToolbox.operators as qOps
import qTools.QuantumToolbox.states as qSta
from qTools.classes.QUni import qUniversal
from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from qTools.classes.extensions.QSysDecorators import InitialStateDecorator, constructConditions
from qTools.classes.QPro import freeEvolution


class universalQSys(qUniversal):
    instances = 0
    label = 'universalQSys'

    __slots__ = ['__constructed', '__paramUpdated']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__constructed = False
        self.__paramUpdated = False
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def _paramUpdated(self):
        return self._universalQSys__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        if hasattr(self.superSys, '_paramUpdated'):
            self.superSys._paramUpdated = boolean
        self._universalQSys__paramUpdated = boolean # pylint: disable=assigning-non-slot

    # constructed boolean setter and getter
    @property
    def _constructed(self) -> bool:
        return self._universalQSys__constructed

    @_constructed.setter
    def _constructed(self, tf: bool):
        self._universalQSys__constructed = tf # pylint: disable=assigning-non-slot

class genericQSys(universalQSys):
    instances = 0
    label = 'genericQSys'

    toBeSaved = qUniversal.toBeSaved.extendedCopy(['dimension'])

    __slots__ = ['__unitary', '__initialState', '__initialStateInput', '__dimension']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__unitary = freeEvolution()
        self._genericQSys__unitary.superSys = self  # pylint: disable=no-member
        self.__initialState = None
        self.__initialStateInput = None
        self.__dimension = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        if self._genericQSys__initialStateInput is not None:
            if hasattr(self._genericQSys__initialStateInput, 'A'):
                saveDict['_genericQSys__initialStateInput'] = self._genericQSys__initialStateInput.A
            else:
                saveDict['_genericQSys__initialStateInput'] = self._genericQSys__initialStateInput
        return saveDict

    @property
    def dimension(self):
        return self._genericQSys__dimension

    @property
    def totalHam(self):
        return None

    # Unitary property and setter
    @property
    def unitary(self):
        unitary = self._genericQSys__unitary.createUnitary()
        self._paramUpdated = False
        return unitary

    # initial state
    @property
    def initialState(self):
        if self._genericQSys__initialState is None:
            try:
                self._genericQSys__initialState = qSta.tensorProd(*[val.initialState for val in self.qSystems.values()]) # pylint: disable=assigning-non-slot
            except AttributeError:
                raise ValueError(self.name + ' is not given an initial state')
        return self._genericQSys__initialState

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
        self._genericQSys__initialState = qSta.compositeState([val.dimension for val in self.subSys.values()], inp) # pylint: disable=assigning-non-slot

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

    def __addSub(self, subSys):
        for subS in self._QuantumSystem__qSystems.values():
            subSys._qSystem__dimsBefore *= subS.dimension
            subS._qSystem__dimsAfter *= subSys.dimension

        if self._genericQSys__dimension is None: # pylint: disable=no-member
            self._genericQSys__dimension = subSys.dimension # pylint: disable=assigning-non-slot
        else:
            self._genericQSys__dimension *= subSys.dimension # pylint: disable=assigning-non-slot, no-member

        if subSys._qSystem__Matrix is not None:
            subSys._qSystem__Matrix = None

        self._QuantumSystem__qSystems[subSys.name] = subSys
        subSys.superSys = self
        return subSys

    def addSubSys(self, subSys, **kwargs): # pylint: disable=arguments-differ
        newSys = super().addSubSys(subSys, **kwargs)
        if isinstance(newSys, qCoupling):
            self._QuantumSystem__addCoupling(self._qUniversal__subSys.pop(newSys.name))  # pylint: disable=no-member
        elif isinstance(newSys, (qSystem, self.__class__)):
            self._QuantumSystem__addSub(newSys)
        else:
            raise TypeError('?')
        return newSys

    def createSubSys(self, subClass=None, n=1, **kwargs): # pylint: disable=arguments-differ
        if subClass is None:
            subClass = qSystem

        newSubs = []
        for _ in range(n):
            newSubs.append(self.addSubSys(subClass, **kwargs))
        return (*newSubs,) if n > 1 else newSubs[0]

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
        newCoupling = self.createSubSys(qCoupling, **kwargs)
        newCoupling.addTerm(*args)
        return newCoupling

    def addSysCoupling(self, couplingObj):
        self.addSubSys(couplingObj)

    # reset and keepOld
    def reset(self, to=None):
        # TODO make sure that the kept protocols deletes their matrices and different sweeps ? delMatrices
        for qSys in self.qSystems.values():
            qSys._qSystem__Matrix = None

        for qCoupl in self.qCouplings.values():
            qCoupl._qCoupling__Matrix = None

        if isinstance(self._genericQSys__unitary, list): # pylint: disable=no-member
            for protoc in self._genericQSys__unitary:  # pylint: disable=no-member
                protoc.delMatrices()
        else:
            self._genericQSys__unitary.delMatrices()  # pylint: disable=no-member

        self._QuantumSystem__keepOld()
        self._constructed = False
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

    def __keepOld(self):
        name = self.couplingName
        if name in self._QuantumSystem__kept.keys():
            if self._genericQSys__unitary != self._QuantumSystem__kept[name][1]: # pylint: disable=no-member
                name = len(self._QuantumSystem__kept)
                self._QuantumSystem__kept[name] = [self.qCouplings, self._genericQSys__unitary] # pylint: disable=no-member
            else:
                pass
        else:
            self._QuantumSystem__kept[name] = [self.qCouplings, self._genericQSys__unitary]  # pylint: disable=no-member

    # construct the matrices
    def constructCompSys(self):
        for qSys in self.subSys.values():
            qSys.freeMat = None

        for qSys in self.qCouplings.values():
            qSys.freeMat = None
        self._constructed = True
        self.initialState # pylint: disable=pointless-statement

    # update the dimension of a subSystem
    def updateDimension(self, qSys, newDimVal, oldDimVal=None):
        if oldDimVal is None:
            oldDimVal = qSys.dimension

        for qSyst in self.qSystems.values():
            qSyst._qSystem__Matrix = None

        for qCoupl in self.qCouplings.values():
            qCoupl._qCoupling__Matrix = None

        qSys._genericQSys__dimension = newDimVal
        self._genericQSys__dimension = newDimVal # pylint: disable=assigning-non-slot, no-member
        #print(newDimVal, oldDimVal)
        ind = qSys.ind
        for qS in self.qSystems.values():
            self._genericQSys__dimension *= qS.dimension # pylint: disable=assigning-non-slot, no-member
            if qS.ind < ind:
                #print((qS._qSystem__dimsAfter*newDimVal)/oldDimVal)
                dimA = int((qS._qSystem__dimsAfter*newDimVal)/oldDimVal)
                qS._qSystem__dimsAfter = dimA
            elif qS.ind > ind:
                #print((qS._qSystem__dimsBefore*newDimVal)/oldDimVal)
                dimB = int((qS._qSystem__dimsBefore*newDimVal)/oldDimVal)
                qS._qSystem__dimsBefore = dimB

        if self._genericQSys__initialStateInput is not None: # pylint: disable=no-member
            self.initialState = self._genericQSys__initialStateInput # pylint: disable=no-member
        self._paramUpdated = True
        self.constructCompSys()
        return qSys

# quantum system objects
class qSystem(genericQSys):
    instances = 0
    label = 'qSystem'

    __slots__ = ['__frequency', '__operator', '__Matrix', '__dimsBefore', '__dimsAfter', '__terms', '__order']
    @qSystemInitErrors
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__frequency = None
        self.__operator = None
        self.__Matrix = None # TODO: make it consistent with pylintrc
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
            if self.dimension is None:
                oldDimVal = newDimVal
            else:
                oldDimVal = self.dimension

        for qSyst in self.subSys.values():
            qSyst._qSystem__Matrix = None
        if not isinstance(newDimVal, (int, int64, int32, int16)):
            raise ValueError('Dimension is not int')
        self._genericQSys__dimension = newDimVal # pylint: disable=assigning-non-slot
        if isinstance(self.superSys, QuantumSystem):
            self.superSys.updateDimension(self, newDimVal, oldDimVal)
        self._paramUpdated = True
        for qPro in self._genericQSys__unitary._allBools:  # pylint: disable=no-member
            # FIXME deletes all, but should not for other sys especially if it has some fixed step
            qPro.delMatrices()
        if self._constructed is True:
            self.initialState = self._genericQSys__initialStateInput # pylint: disable=no-member

    @genericQSys.totalHam.getter # pylint: disable=no-member
    def totalHam(self): # pylint: disable=invalid-overridden-method
        h = sum([(obj.frequency * obj.freeMat) for obj in self.subSys.values()])
        return h

    @property
    def freeMat(self):
        if self._qSystem__Matrix is None:
            self.freeMat = None
        return self._qSystem__Matrix

    @freeMat.setter
    def freeMat(self, qOpsFunc):
        if callable(qOpsFunc):
            self.operator = qOpsFunc
            self._qSystem__constructSubMat()
        elif qOpsFunc is not None:
            self._qSystem__Matrix = qOpsFunc  # pylint: disable=assigning-non-slot
        else:
            if self.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self._qSystem__constructSubMat()

    @genericQSys.initialState.setter # pylint: disable=no-member
    @InitialStateDecorator
    def initialState(self, state):
        self._genericQSys__initialState = qSta.compositeState([self.dimension], [state]) # pylint: disable=assigning-non-slot

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
        self._qSystem__order = ordVal # pylint: disable=assigning-non-slot
        self.freeMat = None

    @property
    def terms(self):
        qSys = list(self.subSys.values())
        return (*qSys,) if len(qSys) > 1 else qSys[0]

    def addTerm(self, op, freq, order=1):
        copySys = super().addSubSys(self.__class__, operator=op, frequency=freq)
        copySys.order = order
        return copySys

    @constructConditions({'dimension': (int, int64, int32, int16), 'operator': qOps.sigmax.__class__})
    def __constructSubMat(self):
        for sys in self.subSys.values():
            try:
                sys._qSystem__Matrix = qOps.compositeOp(sys.operator(self.dimension),
                                                        self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
            except: # pylint: disable=bare-except
                sys._qSystem__Matrix = qOps.compositeOp(sys.operator(), self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
            sys._constructed = True
        return self._qSystem__Matrix

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
        return (self.dimension-1)/2

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
class qCoupling(universalQSys):
    instances = 0
    label = 'qCoupling'

    toBeSaved = qUniversal.toBeSaved.extendedCopy(['couplingStrength'])

    __slots__ = ['__cFncs', '__couplingStrength', '__Matrix', '__qSys']

    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__couplingStrength = None
        self.__cFncs = []
        self.__qSys = []
        self.__Matrix = None
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
        return self._qCoupling__Matrix

    @freeMat.setter
    def freeMat(self, qMat):
        if qMat is not None:
            self._qCoupling__Matrix = qMat # pylint: disable=assigning-non-slot
        else:
            if len(self._qCoupling__cFncs) == 0:
                raise ValueError('No operator is given for coupling Hamiltonian')
            self._qCoupling__Matrix = self._qCoupling__getCoupling() # pylint: disable=assigning-non-slot

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
                cHam = qOps.compositeOp(oper(sys.dimension), sys._qSystem__dimsBefore, sys._qSystem__dimsAfter)
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
            if isinstance(args[counter][0], qSystem):
                qSystems = args[counter]
                if qSystems[0].superSys is not None:
                    qSystems[0].superSys._constructed = False

                if callable(args[counter+1][1]):
                    self._qCoupling__cFncs.append(args[counter + 1])
                    self._qCoupling__qSys.append(qSystems)
                    counter += 2
                # TODO does not have to pass qSystem around
                if counter < len(args):
                    counter = self._qCoupling__addTerm(counter, 1, qSystems, *args)

            # TODO write a generalisation for this one
            # elif isinstance(args[counter][1], qSystem):
            #    qSystems = args[counter]
            #    if qSystems.superSys is not None:
            #        qSystems.superSys._constructed = False

            #    if callable(args[counter+1][1]):
            #        self._qCoupling__cFncs.append(args[counter + 1])
            #        self._qCoupling__qSys.append(qSystems)
            #        counter += 2

            #    if counter < len(args):
            #        self._qCoupling__addTerm(counter, 0, qSystems, *args)
            # TODO generalise this as above
            # elif isinstance(args[counter][0][0],qSystem):
            #    self._qCoupling__cFncs.append(args[counter][1])
            #    self._qCoupling__qSys.append(args[counter][0])
            #    args[counter][0][0].superSys._constructed = False
            #    counter += 1
            # elif isinstance(args[counter][0][1],qSystem):
            #    self._qCoupling__cFncs.append(args[counter][0])
            #    self._qCoupling__qSys.append(args[counter][1])
            #    args[counter][0][1].superSys._constructed = False
            #    counter += 1
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
