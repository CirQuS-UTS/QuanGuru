import QuantumToolbox.operators as qOps
import QuantumToolbox.Hamiltonians as hams
from datetime import datetime
import copy


class QuantumSystem:
    def __init__(self):
        super().__init__()
        self.subSystems = {}
        self.__cFncs = []
        self.Couplings = {}
        self.__cMatrices = []
        self.Unitaries = None
        self.initialState = None
        self.couplingName = None

    def addSubSys(self, subSys, **kwargs):
        if isinstance(subSys, qSystem):
            if subSys.inComposite == False:
                newSub = self.__addSub(subSys)
                return newSub
            elif subSys.inComposite == True:
                newSub = subSys.createCopy(subSys)
                newSub = self.__addSub(newSub)
                print('the qSytem ' + subSys.name + ' was already in the composite, an exact copy of it is created and included in the composite system (named: ' + newSub.name + ' s)')
                return newSub
        else:
            newSub = subSys(**kwargs)
            self.__addSub(newSub)
            return newSub

    def __addSub(self, subSys):
        subSys._qSystem__ind = len(self.subSystems)
        for key, subS in self.subSystems.items():
            subSys._qSystem__dimsBefore *= subS.dimension
            subS._qSystem__dimsAfter *= subSys.dimension
        subSys.inComposite = True
        subSys.name = subSys._qSystem__name
        self.subSystems[subSys.name] = subSys
        return subSys

    def createSubSys(self, subClass, n=1, **kwargs):
        if isinstance(subClass, qSystem):
            newSub = subClass.createCopy(subClass)
            newSub = self.__addSub(newSub)
            print('Instead of the class, an instance is given, but we are cool')
            for key, value in kwargs.items():
                setattr(newSub, key, value)
            return newSub
        else:
            if n == 1:
                newSub = self.__addSub(subClass(**kwargs))
                return newSub
            else:
                newSubs = []
                for nnn in range(n):
                    newSub = self.__addSub(subClass(**kwargs))
                    newSubs.append(newSub)
                return newSubs

    @property
    def totalDim(self):
        tDim = 1
        for key, subSys in self.subSystems.items():
            tDim *= subSys.dimension
        return tDim

    @property
    def freeHam(self):
        freeHams = []
        for key, val in self.subSystems.items():
            freeHams.append(val.freeHam)
        ham = sum(freeHams)
        return ham

    @property
    def totalHam(self):
        return self.freeHam + self.couplingHam

    @property
    def couplingHam(self):
        if len(self.__cMatrices) == 0:
            coupled = self.__getCoupling(0)
            cHam = self.__cFncs[0][0] * coupled
            self.__cMatrices.append(coupled)
            for ind in range(len(self.__cFncs) - 1):
                coupled = self.__getCoupling(ind + 1)
                cHam += self.__cFncs[ind + 1][0] * coupled
                self.__cMatrices.append(coupled)
            return cHam
        else:
            coupled = self.__cMatrices[0]
            cHam = self.__cFncs[0][0] * coupled
            for ind in range(len(self.__cFncs) - 1):
                coupled = self.__cMatrices[ind + 1]
                cHam += self.__cFncs[ind + 1][0] * coupled
            return cHam

    def addCoupling(self, qsystems, couplingOps, couplingStrength):
        if (self.couplingName == None) or (isinstance(self.couplingName, str) == False):
            self.couplingName = len(self.Couplings)

        orders = []
        for qsys in range(len(qsystems)):
            setattr(self, qsystems[qsys].name + str(self.couplingName) + str(len(self.__cFncs)), couplingOps[qsys])
            orders.append(qsystems[qsys]._qSystem__ind)
        self.__cFncs.append([couplingStrength, orders])
        return 'nothing'

    def coupleBy(self, subSys1, subSys2, cType, cStrength):
        qsystems = [subSys1, subSys2]
        if cType == 'JC':
            self.couplingName = 'JC'
            self.addCoupling(qsystems, [qOps.destroy, qOps.create], cStrength)
            self.addCoupling(qsystems, [qOps.create, qOps.destroy], cStrength)
            return 'nothing'

    def __coupOrdering(self, qts):
        sorted(qts, key=lambda x: x[0], reverse=False)
        oper = qts[0][1]
        for ops in range(len(qts)-1):
            oper = oper @ qts[ops+1][1]
        return oper

    def __getCoupling(self, ind):
        qts = []
        for order in self.__cFncs[ind][1]:
            sys = self.subSystems[str(order)]
            oper = getattr(self, sys.name + str(self.couplingName) + str(ind))
            cHam = hams.compositeOp(oper(sys.dimension), sys._qSystem__dimsBefore, sys._qSystem__dimsAfter)
            ts = [order, cHam]
            qts.append(ts)
        cHam = self.__coupOrdering(qts)
        return cHam

    def reset(self, to=None):
        if to == None:
            self.__keepOld()

            self.__cFncs = []
            self.__cMatrices = []
            self.Unitaries = None
            self.couplingName = None
            return 0
        else:
            self.__keepOld()

            self.couplingName = to
            self.__cFncs = self.Couplings[to][0]
            self.__cMatrices = []
            self.Unitaries = self.Couplings[to][1]
            return 0

    def __keepOld(self):
        name = self.couplingName
        if name in self.Couplings:
            if self.Unitaries != self.Couplings[name][1]:
                name = len(self.Couplings)
                for qs in self.subSystems:
                    ind = qs.ind
                    aaa = 0
                    for order in self.__cFncs[ind][1]:
                        sys = self.subSystems[order]
                        oper = getattr(self, sys.name + str(self.couplingName) + str(ind))
                        setattr(self, qs.name + str(name) + str(aaa), oper)
                        aaa += 1
                self.Couplings[name] = [self.__cFncs, self.Unitaries]
        else:
            self.Couplings[name] = [self.__cFncs, self.Unitaries]

class qCoupling(object):
     __slots__ = ['name']
    def __init__(self):
        super().__init__()
        self.name = None

class envCoupling(qCoupling):
     __slots__ = ['superOp']
    def __init__(self):
        super().__init__()
        self.superOp = 'yes'

class sysCoupling(qCoupling):
     __slots__ = ['coupling']
    def __init__(self):
        super().__init__()
        self.coupling = 'yes'

class qSystem(object):
    __slots__ = ['__ind', 'name', 'dimension', 'frequency', 'operator', '__Matrix', '__dimsBefore', '__dimsAfter', 'inComposite']
    def __init__(self, name=None, **kwargs):
        super().__init__()
        self.__ind = None
        self.name = name

        self.dimension = 2
        self.frequency = 1

        self.operator = None
        self.__Matrix = None

        self.__dimsBefore = 1
        self.__dimsAfter = 1
        self.inComposite = False

        for key, value in kwargs.items():
            if hasattr(self, key) is False:
                print('New attribute added:' + key)
            setattr(self, key, value)

    def __del__(self):
        class_name = self.__class__.__name__

    @property
    def freeHam(self):
        if self.operator is None:
            raise ValueError('No operator is given for free Hamiltonian')
        else:
            if self.__Matrix != None:
                h = self.frequency * self.__Matrix
                return h
            else:
                h = self.frequency * self.freeMat
                return h
        
    @property
    def freeMat(self):
        if self.__Matrix == None:
            self.__Matrix = hams.compositeOp(self.operator(self.dimension), self.__dimsBefore, self.__dimsAfter)
            return self.__Matrix
        else:
            return self.__Matrix

    @property
    def __name(self):
        if self.name == None:
            return str(self.__ind)
        else:
            return self.name

    @staticmethod
    def createCopy(qSystem):
        sysClass = qSystem.__class__
        newSub = sysClass()
        newSub.frequency = qSystem.frequency
        newSub.dimension = qSystem.dimension
        newSub.operator = qSystem.operator
        return newSub


class Qubit(qSystem):
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.sigmaz
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def freeHam(self):
        if self._qSystem__Matrix != None:
            h = self.frequency * self._qSystem__Matrix
            return 0.5*h
        else:
            h = self.frequency * self.freeMat
            return 0.5*h

class Spin(qSystem):
    __slots__ = ['jValue']
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.Jz
        self.jValue = 1
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.dimension = ((2*self.jValue) + 1)

    @property
    def freeMat(self):
        if self._qSystem__Matrix == None:
            self._qSystem__Matrix = hams.compositeOp(self.operator(self.jValue), self._qSystem__dimsBefore, self._qSystem__dimsAfter)
            return self._qSystem__Matrix
        else:
            return self.__Matrix

class Cavity(qSystem):
    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.number
        for key, value in kwargs.items():
            setattr(self, key, value)