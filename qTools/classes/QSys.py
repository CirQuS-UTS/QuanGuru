import qTools.QuantumToolbox.operators as qOps
import qTools.QuantumToolbox.Hamiltonians as hams
from qTools.classes.QUni import qUniversal
import qTools.QuantumToolbox.states as qSta
from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors
import scipy.sparse as sp
from qTools.classes.extensions.QSysDecorators import asignState



class genericQSys(qUniversal):
    instances = 0
    label = 'genericQSys'
    __slots__ = ['__constructed', '__initialState', '__lastState', '__Unitaries']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__constructed = False
        self.__initialState = None
        self.__lastState = None
        self.__Unitaries = None

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
    __slots__ = ['__couplings', 'couplingName', '__kept', '__constructed', '__Unitaries', '__initialState', '__lastState']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__couplings = {}
        self.couplingName = None

        self.__kept = {}
        self.__constructed = False
        # these should not necessarily be in here
        self.__Unitaries = None
        self.__initialState = None
        self.__lastState = None
        self._qUniversal__setKwargs(**kwargs)
        
    # adding or creating a new sub system to composite system
    def addSubSys(self, subSys, **kwargs):
        if isinstance(subSys, qSystem):
            if subSys.superSys is None:
                newSub = self._QuantumSystem__addSub(subSys, **kwargs)
                return newSub
            elif subSys.superSys is self:
                newSub = qUniversal.createCopy(subSys, frequency=subSys.frequency, dimension=subSys.dimension, operator=subSys.operator)
                newSub = self._QuantumSystem__addSub(newSub, **kwargs)
                print('Sub system is already in the composite, copy created and added')
                return newSub
        else:
            newSub = subSys(**kwargs)
            self._QuantumSystem__addSub(newSub)
            return newSub

    def __addSub(self, subSys, **kwargs):
        subSys._qUniversal__setKwargs(**kwargs)
        subSys.ind = len(self.subSystems)
        for key, subS in self.subSystems.items():
            subSys._qSystem__dimsBefore *= subS.dimension
            subS._qSystem__dimsAfter *= subSys.dimension
        # TODO put this into a method that checks all the subs
        if subSys._qSystem__Matrix is not None:
            subSys._qSystem__Matrix = None

        self.subSystems[subSys.name] = subSys
        subSys.superSys = self
        return subSys

    def createSubSys(self, subClass, n=1, **kwargs):
        newSubs = []
        for ind in range(n):
            newSub = newSubs.append(self.addSubSys(subClass, **kwargs))
        return newSubs if n > 1 else newSubs[0]

    # total dimensions, free, coupling, and total Hamiltonians of the composite system
    @property
    def dimension(self):
        tDim = 1
        for key, subSys in self.subSystems.items():
            tDim *= subSys.dimension
        return tDim

    @property
    def freeHam(self):
        ham = sum([val.totalHam for val in self.subSystems.values()])
        return ham

    @property
    def totalHam(self):
        return self.freeHam + self.couplingHam

    @property
    def couplingHam(self):
        cham = sum([val.couplingHam for val in self.couplings.values()])
        return cham

    # adding or creating a new couplings
    @property
    def couplings(self):
        return self._QuantumSystem__couplings

    @couplings.setter
    def couplings(self, coupl):
        if isinstance(coupl, qCoupling):
            self._QuantumSystem__couplings[coupl.name] = coupl
        elif isinstance(coupl, dict):
            self._QuantumSystem__couplings = coupl

    def createSysCoupling(self, *args, **kwargs):
        couplingObj = sysCoupling(*args, **kwargs)
        #couplingObj.addTerm(qsystems, couplingOps)
        couplingObj.ind = len(self.couplings)
        self.couplings[couplingObj.name] = couplingObj
        couplingObj.superSys = couplingObj._qCoupling__qSys
        return couplingObj
        
    def addSysCoupling(self, couplingObj):
        if isinstance(couplingObj, qCoupling):
            self.couplings[couplingObj.name] = couplingObj
        else:
            print('not an instance of qCoupling')
        return couplingObj

    # reset and keepOld
    def reset(self, to=None):
        for coupl in self.couplings.values():
                coupl._qCoupling__cMatrix = None

        for qSys in self.subSystems.values():
            qSys._qSystem__Matrix = None

        self._QuantumSystem__keepOld()

        self._QuantumSystem__constructed = False
        if to is None:
            self.couplings = {}
            self.Unitaries = None
            self.couplingName = None
            return 0
        else:
            self.couplingName = to
            self.couplings = self._QuantumSystem__kept[to][0]
            self.Unitaries = self._QuantumSystem__kept[to][1]
            return 0

    def __keepOld(self):
        name = self.couplingName
        if name in self._QuantumSystem__kept.keys():
            if self.Unitaries != self._QuantumSystem__kept[name][1]:
                name = len(self._QuantumSystem__kept)
                self._QuantumSystem__kept[name] = [self.couplings, self.Unitaries]
            else:
                return 'nothing'
        else:
            self._QuantumSystem__kept[name] = [self.couplings, self.Unitaries]

    # construct the matrices
    def constructCompSys(self):
        for qSys in self.subSystems.values():
            qSys.freeMat = None
        for coupl in self.couplings.values():
            coupl.couplingMat = None
        self._QuantumSystem__constructed = True

    # update the dimension of a subSystem
    def updateDimension(self, qSys, newDimVal):
        ind = qSys.ind
        for qS in self.subSystems.values():
            if qS.ind < ind:
                dimA = int((qS._qSystem__dimsAfter*newDimVal)/qSys.dimension)
                qS._qSystem__dimsAfter = dimA
            elif qS.ind > ind:
                dimB = int((qS._qSystem__dimsBefore*newDimVal)/qSys.dimension)
                qS._qSystem__dimsBefore = dimB

        if self._QuantumSystem__constructed is True:
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
    __slots__ = ['__dimension', '__frequency', '__operator', '__Matrix', '__dimsBefore', '__dimsAfter', '__terms']

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
        self._qUniversal__setKwargs(**kwargs)
        self._qSystem__singleSystem()


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
        self._qSystem__singleSystem()

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

    @totalHam.setter
    def totalHam(self, qOpsFunc):
        self.freeMat = qOpsFunc
        self._qSystem__freeMat = ((1/self.frequency)*(self.freeMat))

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

    def __constructSubMat(self):
        # FIXME Still tries to construcit if dim is None
        for sys in self._qSystem__terms:
            print(self._qSystem__dimsBefore, self._qSystem__dimsAfter)
            sys._qSystem__Matrix = hams.compositeOp(sys.operator(self.dimension), self._qSystem__dimsBefore, self._qSystem__dimsAfter)
        return self._qSystem__Matrix

    def __singleSystem(self):
        # FIXME Find a better way of doing this
        if (self.superSys is None) and (self._qSystem__operator is not None) and (self._qSystem__dimension is not None):
            mat = self._qSystem__constructSubMat()

    def addTerm(self, op, freq):
        copySys = self.copy(operator=op, frequency=freq, superSys=self)
        self._qSystem__terms.append(copySys)
        self._qSystem__singleSystem()
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
        kwargs['dimension'] = 2
        super().__init__(**kwargs)
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
        super().__init__(**kwargs)
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
    
    def __constructSubMat(self):
        # FIXME This does not work, if J Ham has more than one term
        self._qSystem__Matrix = hams.compositeOp(self.operator(self.dimension, isDim=True), self._qSystem__dimsBefore, self._qSystem__dimsAfter)
        return self._qSystem__Matrix


class Cavity(qSystem):
    instances = 0
    label = 'Cavity'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.operator = qOps.number
        self._qUniversal__setKwargs(**kwargs)


# quantum coupling object
class qCoupling(qUniversal):
    instances = 0
    label = 'qCoupling'
    __slots__ = ['__cFncs', '__couplingStrength', '__cOrders', '__cMatrix', '__qSys']

    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.__couplingStrength = None
        self.__cFncs = []
        self.__qSys = []
        self.__cMatrix = None
        self._qUniversal__setKwargs(**kwargs)
        self.addTerm(*args)


    # TODO might define setters
    @property
    def couplingOperators(self):
        return self._qCoupling__cFncs

    @property
    def coupledSystems(self):
        return self._qCoupling__qSys

    @qUniversal.superSys.setter
    def superSys(self, sys):
        self._qUniversal__superSys = sys

    # FIXME all the below explicitly or implicitly assumes that this is a system coupling,
    # so these should be generalised and explicit ones moved into sysCoupling
    @property
    def couplingStrength(self):
        return self._qCoupling__couplingStrength

    @couplingStrength.setter
    def couplingStrength(self, strength):
        self._qCoupling__couplingStrength = strength

    @property
    def couplingMat(self):
        """if self._qCoupling__cMatrix is None:
            self.couplingMat = None"""
        return self._qCoupling__cMatrix

    @couplingMat.setter
    def couplingMat(self, qMat):
        if qMat is not None:
            self._qCoupling__cMatrix = qMat
        else:
            if len(self._qCoupling__cFncs) == 0:
                raise ValueError('No operator is given for coupling Hamiltonian')
            self._qCoupling__cMatrix = self._qCoupling__getCoupling()

    @property
    def couplingHam(self):
        h = self.couplingStrength * self.couplingMat
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
                cHam = hams.compositeOp(oper(sys.dimension), sys._qSystem__dimsBefore, sys._qSystem__dimsAfter)
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
            else:
                return count


    def addTerm(self, *args):
        counter = 0
        while counter in range(len(args)):
            # TODO write this better with a decorator possibly
            if isinstance(args[counter][0], qSystem):
                qSystems = args[counter]
                if qSystems[0].superSys is not None:
                    qSystems[0].superSys._QuantumSystem__constructed = False

                if callable(args[counter+1][1]):
                    self._qCoupling__cFncs.append(args[counter + 1])
                    self._qCoupling__qSys.append(qSystems)
                    counter += 2
                # TODO does not have to pass qSystem around
                if counter < len(args):
                    counter = self._qCoupling__addTerm(counter, 1, qSystems, *args)

            # TODO write a generalisation for this one
            elif isinstance(args[counter][1], qSystem):
                qSystems = args[counter]
                if qSystems.superSys is not None:
                    qSystems.superSys._QuantumSystem__constructed = False

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
                args[counter][0][0].superSys._QuantumSystem__constructed = False
                counter += 1
            elif isinstance(args[counter][0][1],qSystem):
                self._qCoupling__cFncs.append(args[counter][0])
                self._qCoupling__qSys.append(args[counter][1])
                args[counter][0][1].superSys._QuantumSystem__constructed = False
                counter += 1
        return self


class envCoupling(qCoupling):
    instances = 0
    label = 'envCoupling'
    __slots__ = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._qUniversal__setKwargs(**kwargs)


class sysCoupling(qCoupling):
    instances = 0
    label = 'sysCoupling'
    __slots__ = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._qUniversal__setKwargs(**kwargs)

