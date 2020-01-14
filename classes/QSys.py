import QuantumToolbox.operators as qOps
import QuantumToolbox.Hamiltonians as hams
from datetime import datetime


class QuantumSystem:
    def __init__(self):
        self.subSystems = []
        self.couplings = []
        self.cMatrices = []
        self.Unitaries = None
        self.initialState = None

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
        st = datetime.now()
        ham = self.subSystems[0].freeHam
        for subSys in self.subSystems[1:]:
            ham += subSys.freeHam
        end = datetime.now()
        #print(end-st)
        return ham

    @property
    def totalHam(self):
        return self.freeHam + self.couplingHam

    @property
    def couplingHam(self):
        if len(self.cMatrices) == 0:
            st = datetime.now()
            #print('cF')
            coupled = self.__getCoupling(0)
            cHam = self.couplings[0][0] * coupled
            self.cMatrices.append(coupled)
            for ind in range(len(self.couplings) - 1):
                coupled = self.__getCoupling(ind+1)
                cHam += self.couplings[ind + 1][0] * coupled
                self.cMatrices.append(coupled)
            end = datetime.now()
            #print(end - st)
            return cHam
        else:
            st = datetime.now()
            #print('cL')
            coupled = self.cMatrices[0]
            cHam = self.couplings[0][0] * coupled
            for ind in range(len(self.couplings) - 1):
                coupled = self.cMatrices[ind + 1]
                cHam += self.couplings[ind + 1][0] * coupled
            end = datetime.now()
            #print(end - st)
            return cHam

    def addCoupling(self, qsystems, couplingOps, couplingStrength):
        orders = []
        for qsys in range(len(qsystems)):
            setattr(self, qsystems[qsys].name + str(len(self.couplings)), couplingOps[qsys])
            orders.append(qsystems[qsys].ind)
        self.couplings.append([couplingStrength, orders])
        return 'nothing'


    def __coupOrdering(self, qts):
        sorted(qts, key=lambda x: x[0], reverse=False)
        oper = qts[0][1]
        for ops in range(len(qts)-1):
            oper = oper @ qts[ops+1][1]
        return oper


    def __getCoupling(self, ind):
        qts = []
        for order in self.couplings[ind][1]:
            sys = self.subSystems[order]
            oper = getattr(self, sys.name + str(ind))
            cHam = hams.compositeOp(oper(sys.dimension), sys.dimsBefore, sys.dimsAfter)
            ts = [order, cHam]
            qts.append(ts)
        cHam = self.__coupOrdering(qts)
        return cHam



class qSystem:
    def __init__(self, name=None, **kwargs):
        self.ind = None
        self.name = name
        self.dimension = 2
        self.dimsBefore = 1
        self.dimsAfter = 1
        self.frequency = 1
        self.operator = None
        self.Matrix = None
        for key, value in kwargs.items():
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
            st = datetime.now()
            if self.Matrix != None:
                #print('from Mat')
                h = self.frequency * self.Matrix
                end = datetime.now()
                #print(end - st)
                return h
            else:
                #print('create the Mat')
                h = self.frequency * self.freeMat()
                end = datetime.now()
                #print(end - st)
                return h
        
    def freeMat(self):
        self.Matrix = hams.compositeOp(self.operator(self.dimension), self.dimsBefore, self.dimsAfter)
        return self.Matrix


class Qubit(qSystem):
    def __init__(self,**kwargs):
        super().__init__()
        self.operator = qOps.sigmaz
        for key, value in kwargs.items():
            setattr(self, key, value)


class Cavity(qSystem):
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.number
        for key, value in kwargs.items():
            setattr(self, key, value)