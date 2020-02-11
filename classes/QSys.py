import QuantumToolbox.operators as qOps
import QuantumToolbox.Hamiltonians as hams
from classes.QUni import qUniversal


class QuantumSystem:
    def __init__(self):
        super().__init__()
        self.subSystems = {}
        self.Couplings = {}

        self.couplingName = None
        self.__kept = {}

        # these should not necessarily be in here
        self.Unitaries = None
        self.initialState = None
        
    # adding or creating a new sub system to composite system
    def addSubSys(self, subSys, **kwargs):
        if isinstance(subSys, qSystem):
            if subSys._qSystem__inComposite is False:
                newSub = self.__addSub(subSys, **kwargs)
                return newSub
            elif subSys._qSystem__inComposite is True:
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
        subSys._qSystem__inComposite = True
        subSys._qUniversal__setKwargs(**kwargs)
        self.subSystems[subSys.name] = subSys
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
        couplingObj._qCoupling__cFncs.append(couplingOps)
        couplingObj._qCoupling__qSys.append(qsystems)
        couplingObj.ind = len(self.Couplings)
        self.Couplings[couplingObj.name] = couplingObj
        return couplingObj
        
    def addSysCoupling(self, couplingObj):
        if isinstance(couplingObj, qCoupling):
            self.Couplings[couplingObj.name] = couplingObj
        else:
            print('not an instance of qCoupling')
        return couplingObj

    def coupleBy(self, subSys1, subSys2, cType, cStrength):
        '''
        These options should be located in a  seperate file, in which case
        cType would be a function
        '''
        qsystems = [subSys1, subSys2]
        if cType == 'JC':
            self.couplingName = 'JC'
            if subSys2.operator == qOps.sigmaz:
                print('sigmaz')
                couplingObj = self.createSysCoupling(qsystems, [qOps.destroy, qOps.sigmap], cStrength)
                # below line can be replaced with add_term, but lets keep as it is for the moment
                couplingObj._qCoupling__cFncs.append([qOps.create, qOps.sigmam])
            else:
                print('number')
                couplingObj = self.createSysCoupling(qsystems, [qOps.destroy, qOps.create], cStrength)
                couplingObj._qCoupling__cFncs.append([qOps.create, qOps.destroy])
            couplingObj._qCoupling__qSys.append(qsystems)
            couplingObj.name = 'JCcoupling'
        return couplingObj

    # reset and keepOld
    def reset(self, to=None):
        if to is None:
            self.__keepOld()
            self.Couplings = {}
            self.Unitaries = None
            self.couplingName = None
            return 0
        else:
            self.__keepOld()
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
    def constructSystem(self):
        for qSys in self.subSystems.values():
            qSys.freeMat = qSys._qSystem__Matrix
        for coupl in self.Couplings.values():
            coupl.couplingMat = coupl._qCoupling__cMatrix



# quantum coupling object
class qCoupling(qUniversal):
    __slots__ = ['__cFncs', 'couplingStrength', '__cOrders', '__cMatrix', '__qSys']
    def __init__(self, name=None, **kwargs):
        super().__init__()
        self._qUniversal__name = name
        self.__cFncs = []
        self.__qSys = []
        self.couplingStrength = 0
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
    __slots__ = ['label']
    def __init__(self, **kwargs):
        super().__init__()
        self.label = 'Environment Coupling'
        self._qUniversal__setKwargs(**kwargs)

class sysCoupling(qCoupling):
    __slots__ = ['label']
    def __init__(self, **kwargs):
        super().__init__()
        self.label = 'System Coupling'
        self._qUniversal__setKwargs(**kwargs)


# quantum system objects
class qSystem(qUniversal):
    __slots__ = ['dimension', 'frequency', 'operator', '__Matrix', '__dimsBefore', '__dimsAfter', '__inComposite']
    def __init__(self, name=None, **kwargs):
        super().__init__()
        self._qUniversal__name = name

        self.dimension = 2
        self.frequency = 1
        self.operator = None

        self.__Matrix = None
        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self.__inComposite = False

        self._qUniversal__setKwargs(**kwargs)

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
            self.__createMat()
        elif qOpsFunc is not None:
            self.__Matrix = qOpsFunc
        else:
            if self.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self.__createMat()

    def __createMat(self):
        self.__Matrix = hams.compositeOp(self.operator(self.dimension), self.__dimsBefore, self.__dimsAfter)

class Qubit(qSystem):
    __slots__ = ['label']
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.sigmaz
        self.label = 'Qubit'
        self._qUniversal__setKwargs(**kwargs)

    @qSystem.freeHam.getter
    def freeHam(self):
        h = qSystem.freeHam.fget(self)
        return h if self.operator is qOps.number else 0.5*h


class Spin(qSystem):
    __slots__ = ['jValue', 'label']
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.Jz
        self.jValue = 1
        self.label = 'Spin'
        self._qUniversal__setKwargs(**kwargs)
        self.dimension = ((2*self.jValue) + 1)

    def _qSystem__createMat(self):
        self._qSystem__Matrix = hams.compositeOp(self.operator(self.jValue), self._qSystem__dimsBefore, self._qSystem__dimsAfter)

class Cavity(qSystem):
    __slots__ = ['label']
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.number
        self.label = 'Cavity'
        self._qUniversal__setKwargs(**kwargs)
