import QuantumToolbox.operators as qOps
import QuantumToolbox.Hamiltonians as hams
from datetime import datetime


class QuantumSystem:
    def __init__(self):
        self.subSystems = []
        self.__cFncs = []
        self.Couplings = {}
        self.__cMatrices = []
        self.Unitaries = None
        self.initialState = None
        self.couplingName = None

    def addSubSys(self, subSys, **kwargs):
        if isinstance(subSys, qSystem):
            newSub = self.__addSub(subSys)
        else:
            newSub = subSys(**kwargs)
            self.__addSub(newSub)
        return newSub

    def __addSub(self, subSys):
        subSys.ind = len(self.subSystems)
        for subS in self.subSystems:
            subSys.dimsBefore *= subS.dimension
            subS.dimsAfter *= subSys.dimension
        self.subSystems.append(subSys)
        return subSys

    def createSubSys(self, subClass, n=1, **kwargs):
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
        for subSys in self.subSystems:
            tDim *= subSys.dimension
        return tDim

    @property
    def freeHam(self):
        ham = self.subSystems[0].freeHam
        for subSys in self.subSystems[1:]:
            ham += subSys.freeHam
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
            orders.append(qsystems[qsys].ind)
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
            sys = self.subSystems[order]
            oper = getattr(self, sys.name + str(self.couplingName) + str(ind))
            cHam = hams.compositeOp(oper(sys.dimension), sys.dimsBefore, sys.dimsAfter)
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



class qSystem:
    def __init__(self, name=None, **kwargs):
        self.__ind = None
        self.name = name

        self.dimension = 2
        self.frequency = 1

        self.operator = None
        self.__Matrix = None

        self.__dimsBefore = 1
        self.__dimsAfter = 1

        for key, value in kwargs.items():
            if hasattr(self, key) is False:
                print('New attribute added:' + key)
            setattr(self, key, value)

        if self.name is None:
            self.name = str(datetime.timestamp(datetime.now()))

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


class Qubit(qSystem):
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.sigmaz
        for key, value in kwargs.items():
            setattr(self, key, value)

class Spin(qSystem):
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
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.number
        for key, value in kwargs.items():
            setattr(self, key, value)