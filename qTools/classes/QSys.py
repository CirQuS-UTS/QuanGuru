import qTools.QuantumToolbox.operators as qOps
import qTools.QuantumToolbox.Hamiltonians as hams
from qTools.classes.QUni import qUniversal


class QuantumSystem:
    def __init__(self):
        self.subSystems = {}
        self.Couplings = {}
        self.couplingName = None

        self.__kept = {}
        self.__constructed = False
        # these should not necessarily be in here
        self.Unitaries = None
        self.initialState = None
        
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

    # total dimensions, free, coupling, and total hamiltonians of the composite system
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


# quantum coupling object
class qCoupling(qUniversal):
    __slots__ = ['__cFncs', 'couplingStrength', '__cOrders', '__cMatrix', '__qSys']
    def __init__(self, **kwargs):
        super().__init__()
        self.couplingStrength = 0

        self.__cFncs = []
        self.__qSys = []
        self.__cMatrix = None
        self._qUniversal__setKwargs(**kwargs)

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

    def addTerm(self, qsystems, couplingOps):
        self.__cFncs.append(couplingOps)
        self.__qSys.append(qsystems)
        return self


class envCoupling(qCoupling):
    instances = 0
    label = 'EnvironmentCoupling'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs)


class sysCoupling(qCoupling):
    instances = 0
    label = 'SystemCoupling'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs)


# quantum system objects
class qSystem(qUniversal):
    __slots__ = ['__dimension', 'frequency', 'operator', '__Matrix', '__dimsBefore', '__dimsAfter']
    def __init__(self, **kwargs):
        super().__init__()
        self.frequency = 1
        self.operator = None

        self.__dimension = 2
        self.__Matrix = None
        self.__dimsBefore = 1
        self.__dimsAfter = 1

        self._qUniversal__setKwargs(**kwargs)

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
        h = self.frequency * self.freeMat
        return h

    @freeHam.setter
    def freeHam(self, qOpsFunc):
        self.freeMat = qOpsFunc

    @property
    def freeMat(self):
        return self.__Matrix

    @freeMat.setter
    def freeMat(self, qOpsFunc):
        if callable(qOpsFunc):
            self.operator = qOpsFunc
            self.constructSubMat()
        elif qOpsFunc is not None:
            self.__Matrix = qOpsFunc
        else:
            if self.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self.constructSubMat()

    def constructSubMat(self):
        self.__Matrix = hams.compositeOp(self.operator(self.dimension), self.__dimsBefore, self.__dimsAfter)
        return self.__Matrix


class Qubit(qSystem):
    instances = 0
    label = 'Qubit'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.sigmaz
        self._qUniversal__setKwargs(**kwargs)

    @qSystem.freeHam.getter
    def freeHam(self):
        h = qSystem.freeHam.fget(self)
        return h if self.operator is qOps.number else 0.5*h


class Spin(qSystem):
    instances = 0
    label = 'Spin'
    __slots__ = ['_jValue']
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.Jz
        self._jValue = 1
        self._qUniversal__setKwargs(**kwargs)

    @property
    def jValue(self):
        return ((self.dimension-1)/2)

    @jValue.setter
    def jValue(self, value):
        self._jValue = value
        self.dimension = int((2*value) + 1)
    
    def constructSubMat(self):
        self._qSystem__Matrix = hams.compositeOp(self.operator(self.dimension, isDim=True), self._qSystem__dimsBefore, self._qSystem__dimsAfter)
        return self._qSystem__Matrix


class Cavity(qSystem):
    instances = 0
    label = 'Cavity'
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.number
        self._qUniversal__setKwargs(**kwargs)
