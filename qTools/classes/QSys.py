import qTools.QuantumToolbox.operators as qOps
import qTools.QuantumToolbox.Hamiltonians as hams
from qTools.classes.QUni import qUniversal
import qTools.QuantumToolbox.states as qSta
from qTools.classes.exceptions import qSystemInitErrors, qCouplingInitErrors



# Composite Quantum system
class QuantumSystem(qUniversal):
    instances = 0
    label = 'Composite Quantum System'
    __slots__ = ['Couplings', 'couplingName', '__kept', '__constructed', '__Unitaries', '__initialState', '__lastState']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO make these property
        #self.subSystems = {}
        self.Couplings = {}
        self.couplingName = None

        self.__kept = {}
        self.__constructed = False
        # these should not necessarily be in here
        self.__Unitaries = None
        self.__initialState = None
        self.__lastState = None
        self._qUniversal__setKwargs(**kwargs)

    # Unitary property and setter
    @property
    def Unitaries(self):
        return self.__Unitaries

    @Unitaries.setter
    def Unitaries(self, uni):
        self.__Unitaries = uni 
        
    # adding or creating a new sub system to composite system
    def addSubSys(self, subSys, **kwargs):
        if isinstance(subSys, qSystem):
            if subSys.superSys is None:
                newSub = self.__addSub(subSys, **kwargs)
                return newSub
            elif subSys.superSys is self:
                newSub = qUniversal.createCopy(subSys, frequency=subSys.frequency, dimension=subSys.dimension, operator=subSys.operator)
                newSub = self.__addSub(newSub, **kwargs)
                print('Sub system is already in the composite, copy created and added')
                return newSub
        else:
            newSub = subSys(**kwargs)
            self.__addSub(newSub)
            return newSub

    def __addSub(self, subSys, **kwargs):
        subSys.ind = len(self.subSystems)
        for key, subS in self.subSystems.items():
            subSys._qSystem__dimsBefore *= subS.dimension
            subS._qSystem__dimsAfter *= subSys.dimension
        subSys._qUniversal__setKwargs(**kwargs)
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
    def totalDim(self):
        tDim = 1
        for key, subSys in self.subSystems.items():
            tDim *= subSys.dimension
        return tDim

    @property
    def freeHam(self):
        ham = sum([val.freeHam for val in self.subSystems.values()])
        return ham

    @property
    def totalHam(self):
        return self.freeHam + self.couplingHam

    @property
    def couplingHam(self):
        cham = sum([val.couplingHam for val in self.Couplings.values()])
        return cham

    # adding or creating a new couplings
    def createSysCoupling(self, qsystems, couplingOps, couplingStrength, **kwargs):
        couplingObj = sysCoupling(couplingStrength=couplingStrength, **kwargs)
        couplingObj.superSys = self
        couplingObj.addTerm(qsystems, couplingOps)
        couplingObj.ind = len(self.Couplings)
        self.Couplings[couplingObj.name] = couplingObj
        return couplingObj
        
    def addSysCoupling(self, couplingObj):
        if isinstance(couplingObj, qCoupling):
            self.Couplings[couplingObj.name] = couplingObj
        else:
            print('not an instance of qCoupling')
        return couplingObj

    # reset and keepOld
    def reset(self, to=None):
        for coupl in self.Couplings.values():
                coupl._qCoupling__cMatrix = None

        for qSys in self.subSystems.values():
            qSys._qSystem__Matrix = None

        self.__keepOld()

        self.__constructed = False
        if to is None:
            self.Couplings = {}
            self.Unitaries = None
            self.couplingName = None
            return 0
        else:
            self.couplingName = to
            self.Couplings = self.__kept[to][0]
            self.Unitaries = self.__kept[to][1]
            return 0

    def __keepOld(self):
        name = self.couplingName
        if name in self.__kept.keys():
            if self.Unitaries != self.__kept[name][1]:
                name = len(self.__kept)
                self.__kept[name] = [self.Couplings, self.Unitaries]
            else:
                return 'nothing'
        else:
            self.__kept[name] = [self.Couplings, self.Unitaries]

    # construct the matrices
    def constructCompSys(self):
        for qSys in self.subSystems.values():
            qSys.freeMat = None
        for coupl in self.Couplings.values():
            coupl.couplingMat = None
        self.__constructed = True

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

        if self.__constructed is True:
            self.constructCompSys()
        return qSys

    # initial state
    @property
    def initialState(self):
        return self.__initialState

    @initialState.setter
    def initialState(self, inp):
        if len(inp) == len(self.subSystems):
            dims = [val.dimension for val in self.subSystems.values()]
            self.__initialState = qSta.compositeState(dims, inp)

    @property
    def lastState(self):
        return self.__lastState

    @initialState.setter
    def lastState(self, inp):
        self.__lastState = inp


# quantum coupling object
class qCoupling(qUniversal):
    instances = 0
    label = 'qCoupling'
    __slots__ = ['__cFncs', '__couplingStrength', '__cOrders', '__cMatrix', '__qSys']

    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.__couplingStrength = None
        # TODO functions and systems are not available to outside, make them!
        self.__cFncs = []
        self.__qSys = []
        self.__cMatrix = None
        self._qUniversal__setKwargs(**kwargs)
        # FIXME if nor args given should not create a problem
        self.addTerm(*args)


    # FIXME all the below explicitly or implicitly assumes that this is a system coupling,
    # so these should be generalised and explicit ones moved into sysCoupling
    @property
    def couplingStrength(self):
        return self.__couplingStrength

    @couplingStrength.setter
    def couplingStrength(self, strength):
        self.__couplingStrength = strength

    @property
    def couplingMat(self):
        return self.__cMatrix

    @couplingMat.setter
    def couplingMat(self, qMat):
        if qMat is not None:
            self.__cMatrix = qMat
        else:
            if len(self.__cFncs) == 0:
                raise ValueError('No operator is given for coupling Hamiltonian')
            self.__cMatrix = self.__getCoupling()

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
        for ind in range(len(self.__cFncs)):
            qts = []
            for indx in range(len(self.__qSys[ind])):
                sys = self.__qSys[ind][indx]
                order = sys.ind
                oper = self.__cFncs[ind][indx]
                cHam = hams.compositeOp(oper(sys.dimension), sys._qSystem__dimsBefore, sys._qSystem__dimsAfter)
                ts = [order, cHam]
                qts.append(ts)
            cMats.append(self.__coupOrdering(qts))
        cHam = sum(cMats)
        return cHam

    # TODO make it as in qSystem for possiblity of differnet g acd copy
    def addTerm(self, *args):
        # TODO might be turn into 0-1 independent
        if len(args) > 0:
            self.__cFncs.append(args[1])
            self.__qSys.append(args[0])
            self.superSys._QuantumSystem__constructed = False
        return self


class envCoupling(qCoupling):
    instances = 0
    label = 'EnvironmentCoupling'
    __slots__ = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._qUniversal__setKwargs(**kwargs)


class sysCoupling(qCoupling):
    instances = 0
    label = 'SystemCoupling'
    __slots__ = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._qUniversal__setKwargs(**kwargs)


# quantum system objects
class qSystem(qUniversal):
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
        self.__singleSystem()
        
    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, freq):
        self.__frequency = freq

    @property
    def operator(self):
        return self.__operator

    @operator.setter
    def operator(self, op):
        self.__operator = op
        self.__singleSystem()

    @property
    def dimension(self):
        return self.__dimension

    @dimension.setter
    def dimension(self, newDimVal):
        if not isinstance(newDimVal, int):
            raise ValueError('Dimension is not int')

        if self.superSys is None:
            self.__dimension = newDimVal
        elif isinstance(self.superSys, QuantumSystem):
            QuantumSystem.updateDimension(self.superSys, self, newDimVal)
            self.__dimension = newDimVal
            
    @property
    def freeHam(self):
        h = sum([(obj.frequency * obj.freeMat) for obj in self.__terms])
        return h

    @freeHam.setter
    def freeHam(self, qOpsFunc):
        self.freeMat = qOpsFunc
        self.__freeMat = ((1/self.frequency)*(self.freeMat))

    @property
    def freeMat(self):
        return self.__Matrix

    @freeMat.setter
    def freeMat(self, qOpsFunc):
        if callable(qOpsFunc):
            self.operator = qOpsFunc
            self.__constructSubMat()
        elif qOpsFunc is not None:
            self.__Matrix = qOpsFunc
        else:
            if self.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self.__constructSubMat()

    def __constructSubMat(self):
        self.__Matrix = hams.compositeOp(self.operator(self.dimension), self.__dimsBefore, self.__dimsAfter)
        return self.__Matrix

    def __singleSystem(self):
        if (self.superSys is None) and (self.__operator is not None):
            mat = self.__constructSubMat()

    def addTerm(self, op, freq):
        copySys = self.copy(operator=op, frequency=freq)
        self.__terms.append(copySys)
        self.__singleSystem()
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
        super().__init__(dimension=2, **kwargs)
        self.operator = qOps.sigmaz
        self._qUniversal__setKwargs(**kwargs)

    @qSystem.freeHam.getter
    def freeHam(self):
        h = qSystem.freeHam.fget(self)
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
        self.__jValue = value
        self.dimension = int((2*value) + 1)
    
    def __constructSubMat(self):
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
