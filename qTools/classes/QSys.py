import qTools.QuantumToolbox.operators as qOps
from qTools.classes.QUni import qUniversal
import qTools.QuantumToolbox.states as qSta
from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from qTools.classes.extensions.QSysDecorators import asignState, addCreateInstance, constructConditions
from qTools.classes.QPro import freeEvolution


class genericQSys(qUniversal):
    instances = 0
    label = 'genericQSys'

    __slots__ = ['__constructed', '__paramUpdated', '__unitary', '__initialState', '__initialStateInput']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__constructed = False
        self.__paramUpdated = True
        self.__unitary = freeEvolution(superSys=self)
        self.__initialState = None
        self.__initialStateInput = None
        self._qUniversal__setKwargs(**kwargs)
        
    @property
    def _paramUpdated(self):
        return self._genericQSys__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._genericQSys__paramUpdated = boolean

    # constructed boolean setter and getter
    @property
    def _constructed(self) -> bool:
        return self._genericQSys__constructed
    
    @_constructed.setter
    def _constructed(self, tf:bool):
        self._genericQSys__constructed = tf
    
    # Unitary property and setter
    # TODO should this always be the freeEvolution
    @property
    def unitary(self):
        if isinstance(self._genericQSys__unitary, qUniversal):
            unitary = self._genericQSys__unitary.createUnitary()
        elif isinstance(self._genericQSys__unitary, list):
            # TODO is list idea the best option ?
            unitary = []
            for protocol in self._genericQSys__unitary:
                unitary.append(protocol.createUnitary())
        self._paramUpdated = False
        return unitary

    @unitary.setter
    def unitary(self, protocols):
        if protocols is not None:
            self._genericQSys__unitary = protocols
        elif protocols is None:
            self._genericQSys__unitary = freeEvolution(superSys=self)

    # initial state
    @property
    def initialState(self):
        return self._genericQSys__initialState


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
        self._qUniversal__setKwargs(**kwargs)

    def add(self, *args):
        for system in args:
            self.addSubSys(system)

    def create(self, n=1, *args):
        # TODO how to use or to use n ?
        for sysClass in args:
            self.addSubSys(sysClass)
    # adding or creating a new sub system to composite system
    @property
    def qSystems(self):
        return self._qUniversal__subSys

    def __addSub(self, subSys):
        for key, subS in self._QuantumSystem__qSystems.items():
            subSys._qSystem__dimsBefore *= subS.dimension
            subS._qSystem__dimsAfter *= subSys.dimension
            
        if subSys._qSystem__Matrix is not None:
            subSys._qSystem__Matrix = None

        self._QuantumSystem__qSystems[subSys.name] = subSys
        subSys.superSys = self
        return subSys

    def addSubSys(self, subSys, **kwargs):
        newSys = super().addSubSys(subSys, **kwargs)
        if isinstance(newSys, qSystem):
            self._QuantumSystem__addSub(newSys)
        elif isinstance(newSys, qCoupling):
            self._QuantumSystem__addCoupling(self._qUniversal__subSys.pop(newSys.name))
        return newSys

    def createSubSys(self, subClass, n=1, **kwargs):
        newSubs = []
        for ind in range(n):
            newSubs.append(self.addSubSys(subClass, **kwargs))
        return (*newSubs,) if n > 1 else newSubs[0]

    # total dimensions, free, coupling, and total Hamiltonians of the composite system
    @property
    def dimension(self):
        sysList = list(self.qSystems.values())
        tDim = (sysList[0]._qSystem__dimsBefore*sysList[0].dimension*sysList[0]._qSystem__dimsAfter)
        return tDim

    @property
    def freeHam(self):
        ham = sum([val.totalHam for val in self.qSystems.values()])
        return ham

    @property
    def totalHam(self):
        return self.freeHam + self.couplingHam

    @property
    def couplingHam(self):
        cham = sum([val.totalHam for val in self.qCouplings.values()])
        return cham

    # adding or creating a new coupling
    @property
    def qCouplings(self):
        return self._QuantumSystem__qCouplings

    def __addCoupling(self, couplingObj, *args, **kwargs):
        self._QuantumSystem__qCouplings[couplingObj.name] = couplingObj
        couplingObj._qUniversal__ind = len(self.qCouplings)
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

        if isinstance(self._genericQSys__unitary, list):
            for protoc in self._genericQSys__unitary:
                protoc.delMatrices()
        else:
            self._genericQSys__unitary.delMatrices()
        
        self._QuantumSystem__keepOld()
        self._constructed = False
        self._paramUpdated = True
        if to is None:
            self._QuantumSystem__qCouplings = {}
            self._genericQSys__unitary = freeEvolution(superSys=self)
            self.couplingName = None
        else:
            self.couplingName = to
            self._QuantumSystem__qCouplings = self._QuantumSystem__kept[to][0]
            self._genericQSys__unitary = self._QuantumSystem__kept[to][1]

    def __keepOld(self):
        name = self.couplingName
        if name in self._QuantumSystem__kept.keys():
            if self._genericQSys__unitary != self._QuantumSystem__kept[name][1]:
                name = len(self._QuantumSystem__kept)
                self._QuantumSystem__kept[name] = [self.qCouplings, self._genericQSys__unitary]
            else:
                return 'nothing'
        else:
            self._QuantumSystem__kept[name] = [self.qCouplings, self._genericQSys__unitary]

    # construct the matrices
    def constructCompSys(self):
        for qSys in self.subSys.values():
            qSys.freeMat = None

        for qSys in self.qCouplings.values():
            qSys.freeMat = None
        self._constructed = True

    # update the dimension of a subSystem
    def updateDimension(self, qSys, newDimVal):
        qSys._qSystem__dimension = newDimVal
        ind = qSys.ind
        for qS in self.qSystems.values():
            if qS.ind < ind:
                dimA = int((qS._qSystem__dimsAfter*newDimVal)/qSys.dimension)
                qS._qSystem__dimsAfter = dimA
            elif qS.ind > ind:
                dimB = int((qS._qSystem__dimsBefore*newDimVal)/qSys.dimension)
                qS._qSystem__dimsBefore = dimB
        self.initialState = self._genericQSys__initialStateInput
        self._paramUpdated = True
        if self._constructed is True:
            self.constructCompSys()
        return qSys

    def copy(self, **kwargs):
        newSys = QuantumSystem(**kwargs)
        for qSys in self.qSystems.values():
            newSys.addSubSys(qSys.copy())
        return newSys

    @genericQSys.initialState.setter
    @asignState(qSta.compositeState)
    def initialState(self, inp):
        pass


# quantum system objects
class qSystem(genericQSys):
    instances = 0
    label = 'qSystem'

    __slots__ = ['__dimension', '__frequency', '__operator', '__Matrix', '__dimsBefore', '__dimsAfter', '__terms', '__order']
    @qSystemInitErrors
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__frequency = None
        self.__operator = None
        self.__dimension = None
        self.__Matrix = None
        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self.__terms = [self]
        self.__order = 1
        self._qUniversal__setKwargs(**kwargs)

    @property
    def order(self):
        return self._qSystem__order

    @order.setter
    def order(self, ordVal):
        self._qSystem__order = ordVal
        self.freeMat = None

    @property
    def terms(self):
        if not isinstance(self.superSys, qSystem):
            return self._qSystem__terms
        else:
            print('This is a term in ', self.superSys)

    @genericQSys.initialState.setter
    @asignState(qSta.superPos)
    def initialState(self, state):
        pass

    @property
    def frequency(self):
        return self._qSystem__frequency

    @frequency.setter
    def frequency(self, freq):
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._qSystem__frequency = freq

    @property
    def operator(self):
        return self._qSystem__operator

    @operator.setter
    def operator(self, op):
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._qSystem__operator = op

    @property
    def dimension(self):
        return self._qSystem__dimension

    @dimension.setter
    def dimension(self, newDimVal):
        if not isinstance(newDimVal, int):
            raise ValueError('Dimension is not int')
        self._qSystem__dimension = newDimVal
        if isinstance(self.superSys, QuantumSystem):
            QuantumSystem.updateDimension(self.superSys, self, newDimVal)
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        if self._constructed is True:
            self.initialState = self._genericQSys__initialStateInput
            
    @property
    def totalHam(self):
        h = sum([(obj.frequency * obj.freeMat) for obj in self._qSystem__terms])
        return h

    # I'm not sure on keeping this, freeMat setter covers all the cases and this one does not make much sense
    """@totalHam.setter
    def totalHam(self, qOpsFunc):
        self.freeMat = qOpsFunc
        self._qSystem__freeMat = ((1/self.frequency)*(self.freeMat))"""

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
            self._qSystem__Matrix = qOpsFunc
        else:
            if self.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self._qSystem__constructSubMat()

    @constructConditions({'dimension':int,'operator':qOps.sigmax.__class__})
    def __constructSubMat(self):
        for sys in self._qSystem__terms:
            sys._qSystem__Matrix = qOps.compositeOp(sys.operator(self.dimension), self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
            sys._constructed = True
        return self._qSystem__Matrix

    def addTerm(self, op, freq, order=1):
        copySys = self.copy(operator=op, frequency=freq, superSys=self)
        copySys.order = order
        self._qSystem__terms.append(copySys)
        return copySys

    def copy(self, **kwargs):
        # TODO should copy the terms as well
        if 'superSys' in kwargs.keys():
            copySys = super().copy(superSys=kwargs['superSys'], dimension = self.dimension, frequency = self.frequency, operator = self.operator)
        else:
            copySys = super().copy(dimension = self.dimension, frequency = self.frequency, operator = self.operator)

        copySys._qUniversal__setKwargs(**kwargs)
        return copySys


class Qubit(qSystem):
    instances = 0
    label = 'Qubit'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        kwargs['dimension'] = 2
        self.operator = qOps.sigmaz
        self._qUniversal__setKwargs(**kwargs)

    @qSystem.totalHam.getter
    def totalHam(self):
        h = qSystem.totalHam.fget(self)
        return h if self.operator is qOps.number else 0.5*h


class Spin(qSystem):
    instances = 0
    label = 'Spin'

    __slots__ = ['__jValue']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.operator = qOps.Jz
        self.__jValue = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def jValue(self):
        return ((self.dimension-1)/2)

    @jValue.setter
    def jValue(self, value):
        self._Spin__jValue = value
        self.dimension = int((2*value) + 1)


class Cavity(qSystem):
    instances = 0
    label = 'Cavity'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.operator = qOps.number
        self._qUniversal__setKwargs(**kwargs)


# quantum coupling object
class qCoupling(qUniversal):
    instances = 0
    label = 'qCoupling'

    __slots__ = ['__cFncs', '__couplingStrength', '__cOrders', '__Matrix', '__qSys', '__paramUpdated']

    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__couplingStrength = None
        self.__cFncs = []
        self.__qSys = []
        self.__Matrix = None
        self.__paramUpdated = True
        self._qUniversal__setKwargs(**kwargs)
        self.addTerm(*args)

    @property
    def _paramUpdated(self):
        return self._qCoupling__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._qCoupling__paramUpdated = boolean

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
    def couplingStrength(self):
        return self._qCoupling__couplingStrength

    @couplingStrength.setter
    def couplingStrength(self, strength):
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._qCoupling__couplingStrength = strength

    @property
    def freeMat(self):
        return self._qCoupling__Matrix

    @freeMat.setter
    def freeMat(self, qMat):
        if qMat is not None:
            self._qCoupling__Matrix = qMat
        else:
            if len(self._qCoupling__cFncs) == 0:
                raise ValueError('No operator is given for coupling Hamiltonian')
            self._qCoupling__Matrix = self._qCoupling__getCoupling()

    @property
    def totalHam(self):
        h = self.couplingStrength * self.freeMat
        return h

    def __coupOrdering(self, qts):
        sorted(qts, key=lambda x: x[0], reverse=False)
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

            """# TODO write a generalisation for this one
            elif isinstance(args[counter][1], qSystem):
                qSystems = args[counter]
                if qSystems.superSys is not None:
                    qSystems.superSys._constructed = False

                if callable(args[counter+1][1]):
                    self._qCoupling__cFncs.append(args[counter + 1])
                    self._qCoupling__qSys.append(qSystems)
                    counter += 2
                    
                if counter < len(args):
                    self._qCoupling__addTerm(counter, 0, qSystems, *args)
            # TODO generalise this as above
            elif isinstance(args[counter][0][0],qSystem):
                self._qCoupling__cFncs.append(args[counter][1])
                self._qCoupling__qSys.append(args[counter][0])
                args[counter][0][0].superSys._constructed = False
                counter += 1
            elif isinstance(args[counter][0][1],qSystem):
                self._qCoupling__cFncs.append(args[counter][0])
                self._qCoupling__qSys.append(args[counter][1])
                args[counter][0][1].superSys._constructed = False
                counter += 1"""
        return self


class envCoupling(qCoupling):
    instances = 0
    label = 'envCoupling'

    __slots__ = []
    def __init__(self, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs)


class sysCoupling(qCoupling):
    instances = 0
    label = 'sysCoupling'
    __slots__ = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs)