import qTools.QuantumToolbox.operators as qOps
from qTools.classes.QUni import qUniversal
import qTools.QuantumToolbox.states as qSta
from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
from qTools.classes.extensions.QSysDecorators import asignState, addCreateInstance, constructConditions


class genericQSys(qUniversal):
    instances = 0
    label = 'genericQSys'
    
    __slots__ = ['__constructed', '__initialState', '__lastState', '__Unitaries']
    def __init__(self, **kwargs):
        super().__init__()
        self.__constructed = False
        self.__initialState = None
        self.__lastState = None
        self.__Unitaries = None
        self._qUniversal__setKwargs(**kwargs)

    # constructed boolean setter and getter
    @property
    def constructed(self):
        return self._genericQSys__constructed
    
    @constructed.setter
    def constructed(self, tf):
        self._genericQSys__constructed = tf
    
    # Unitary property and setter
    @property
    def Unitaries(self):
        return self._genericQSys__Unitaries

    @Unitaries.setter
    def Unitaries(self, uni):
        self._genericQSys__Unitaries = uni

    # initial state
    @property
    def initialState(self):
        return self._genericQSys__initialState

    @property
    def lastState(self):
        return self._genericQSys__lastState

    @lastState.setter
    def lastState(self, inp):
        self._genericQSys__lastState = inp


# Composite Quantum system
class QuantumSystem(genericQSys):
    instances = 0
    label = 'QuantumSystem'

    __slots__ = ['__qCouplings', '__qSystems', 'couplingName', '__kept']
    def __init__(self, **kwargs):
        super().__init__()
        self.__qCouplings = {}
        self.__qSystems = {}

        self.couplingName = None

        self.__kept = {}
        self._qUniversal__setKwargs(**kwargs)

    def add(self, *args):
        for system in args:
            if isinstance(system, qSystem):
                self.addSubSys(system)
            elif isinstance(system, sysCoupling):
                self.addSysCoupling(system)
            elif isinstance(system, envCoupling):
                print('Enviroment coupling currently not supported')
            else:
                print('Object not valid.')

    # adding or creating a new sub system to composite system
    @property
    def qSystems(self):
        return self._QuantumSystem__qSystems

    def __addSub(self, subSys, **kwargs):
        subSys.ind = len(self._QuantumSystem__qSystems)
        for key, subS in self._QuantumSystem__qSystems.items():
            subSys._qSystem__dimsBefore *= subS.dimension
            subS._qSystem__dimsAfter *= subSys.dimension
            
        if subSys._qSystem__Matrix is not None:
            subSys._qSystem__Matrix = None

        self._QuantumSystem__qSystems[subSys.name] = subSys
        return subSys

    @addCreateInstance(_QuantumSystem__addSub)
    def addSubSys(self, subSys, **kwargs):
        pass

    def createSubSys(self, subClass, n=1, **kwargs):
        newSubs = []
        for ind in range(n):
            newSub = newSubs.append(self.addSubSys(subClass, **kwargs))
        return newSubs if n > 1 else newSubs[0]

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

    @qCouplings.setter
    def qCouplings(self, coupl):
        self._QuantumSystem__addCoupling(coupl)
        

    def __addCoupling(self, couplingObj, *args, **kwargs):
        if isinstance(couplingObj, qCoupling):
            self._QuantumSystem__qCouplings[couplingObj.name] = couplingObj
            couplingObj.ind = len(self.qCouplings)
        elif isinstance(couplingObj, dict):
            self._QuantumSystem__qCouplings = couplingObj
        elif couplingObj == 'qCoupling':
            couplingObj = qCoupling(*args, **kwargs)
            couplingObj = self._QuantumSystem__addCoupling(couplingObj)
        return couplingObj

    @addCreateInstance(_QuantumSystem__addCoupling)
    def createSysCoupling(self, *args, **kwargs):
        pass
        
    @addCreateInstance(_QuantumSystem__addCoupling)
    def addSysCoupling(self, couplingObj):
        pass

    # reset and keepOld
    def reset(self, to=None):
        for qSys in self.qSystems.values():
            qSys._qSystem__Matrix = None

        for qCoupl in self.qCouplings.values():
            qCoupl._qCoupling__Matrix = None
        self._QuantumSystem__keepOld()
        self._genericQSys__constructed = False
        if to is None:
            self.qCouplings = {}
            self.Unitaries = None
            self.couplingName = None
            return 0
        else:
            self.couplingName = to
            self.qCouplings = self._QuantumSystem__kept[to][0]
            self.Unitaries = self._QuantumSystem__kept[to][1]
            return 0

    def __keepOld(self):
        name = self.couplingName
        if name in self._QuantumSystem__kept.keys():
            if self.Unitaries != self._QuantumSystem__kept[name][1]:
                name = len(self._QuantumSystem__kept)
                self._QuantumSystem__kept[name] = [self.qCouplings, self.Unitaries]
            else:
                return 'nothing'
        else:
            self._QuantumSystem__kept[name] = [self.qCouplings, self.Unitaries]

    # construct the matrices
    def constructCompSys(self):
        for qSys in self.subSystems.values():
            qSys.freeMat = None
        self._genericQSys__constructed = True

    # update the dimension of a subSystem
    def updateDimension(self, qSys, newDimVal):
        ind = qSys.ind
        for qS in self.qSystems.values():
            if qS.ind < ind:
                dimA = int((qS._qSystem__dimsAfter*newDimVal)/qSys.dimension)
                qS._qSystem__dimsAfter = dimA
            elif qS.ind > ind:
                dimB = int((qS._qSystem__dimsBefore*newDimVal)/qSys.dimension)
                qS._qSystem__dimsBefore = dimB

        if self._genericQSys__constructed is True:
            self.constructCompSys()
        return qSys

    @genericQSys.initialState.setter
    @asignState(qSta.compositeState)
    def initialState(self, inp):
        pass


# quantum system objects
class qSystem(genericQSys):
    instances = 0
    label = 'qSystem'

    __slots__ = ['__dimension', '__frequency', '__operator', '__Matrix', '__dimsBefore', '__dimsAfter', '__terms', 'order']
    @qSystemInitErrors
    def __init__(self, **kwargs):
        super().__init__()
        self.__frequency = None
        self.__operator = None
        self.__dimension = None
        self.__Matrix = None
        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self.__terms = [self]
        self.order = 1
        self._qUniversal__setKwargs(**kwargs)

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
        self._qSystem__frequency = freq

    @property
    def operator(self):
        return self._qSystem__operator

    @operator.setter
    def operator(self, op):
        self._qSystem__operator = op

    @property
    def dimension(self):
        return self._qSystem__dimension

    @dimension.setter
    def dimension(self, newDimVal):
        if not isinstance(newDimVal, int):
            raise ValueError('Dimension is not int')

        if isinstance(self.superSys, QuantumSystem):
            QuantumSystem.updateDimension(self.superSys, self, newDimVal)

        self._qSystem__dimension = newDimVal
            
    @property
    def totalHam(self):
        h = sum([(obj.frequency * obj.freeMat) for obj in self._qSystem__terms])
        return h

    # I'm not sure to keep this, freeMat setter covers all the cases and this one does not make much sense
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
            sys._genericQSys__constructed = True
        return self._qSystem__Matrix

    def addTerm(self, op, freq, order=1):
        copySys = self.copy(operator=op, frequency=freq, superSys=self)
        copySys.order = order
        self._qSystem__terms.append(copySys)
        return copySys

    def copy(self, **kwargs):
        if 'superSys' in kwargs.keys():
            copySys = qUniversal.createCopy(self, superSys=kwargs['superSys'], dimension = self.dimension, 
            frequency = self.frequency, operator = self.operator)
        else:
            copySys = qUniversal.createCopy(self, dimension = self.dimension, 
            frequency = self.frequency, operator = self.operator)
        copySys._qUniversal__setKwargs(**kwargs)
        return copySys


class Qubit(qSystem):
    instances = 0
    label = 'Qubit'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
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
        super().__init__()
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
        super().__init__()
        self.operator = qOps.number
        self._qUniversal__setKwargs(**kwargs)


# quantum coupling object
class qCoupling(qUniversal):
    instances = 0
    label = 'qCoupling'

    __slots__ = ['__cFncs', '__couplingStrength', '__cOrders', '__Matrix', '__qSys']
    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__couplingStrength = None
        self.__cFncs = []
        self.__qSys = []
        self.__Matrix = None
        self._qUniversal__setKwargs(**kwargs)
        self.addTerm(*args)

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
                    qSystems[0].superSys._genericQSys__constructed = False

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
                    qSystems.superSys._genericQSys__constructed = False

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
                args[counter][0][0].superSys._genericQSys__constructed = False
                counter += 1
            elif isinstance(args[counter][0][1],qSystem):
                self._qCoupling__cFncs.append(args[counter][0])
                self._qCoupling__qSys.append(args[counter][1])
                args[counter][0][1].superSys._genericQSys__constructed = False
                counter += 1"""
        return self


class envCoupling(qCoupling):
    instances = 0
    label = 'envCoupling'

    __slots__ = []
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs)


class sysCoupling(qCoupling):
    instances = 0
    label = 'sysCoupling'
    __slots__ = []
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs)
