import QuantumToolbox.operators as qOps
import QuantumToolbox.Hamiltonians as hams
from datetime import datetime

""" *** under construction *** """

class QuantumSystem:
    """
    An object for a composite Quantum System
    """
    def __init__(self):
        self.subSystems = []
        self.__cFncs = []
        self.Couplings = {}
        self.__cMatrices = []
        self.Unitaries = None
        self.initialState = None
        self.couplingName = None

    def addSubSys(self, subSys, **kwargs):
        """
        function to add the given subSys or an instance of the given subSystem class
        :param subSys: either an instance of subSystem classes or the class itself
        :param kwargs: variables to be changed from the default values or included in the new instance
        :return: the new subSystem
        """
        if isinstance(subSys, qSystem):
            newSub = self.__addSub(subSys)
        else:
            newSub = subSys(**kwargs)
            self.__addSub(newSub)
        return newSub

    def __addSub(self, subSys):
        """
        an internal function to update the subSystems and self accordingly with the newly added subSys
        :param subSys: an instance of the new subSys
        :return: the new subSys
        """
        subSys.ind = len(self.subSystems)
        for subS in self.subSystems:
            subSys.dimsBefore *= subS.dimension
            subS.dimsAfter *= subSys.dimension
        self.subSystems.append(subSys)
        return subSys

    def createSubSys(self, subClass, n=1, **kwargs):
        """
        A function to create and add n number of new subSystems from a given class
        :param subClass: class for the new subSystem/s
        :param n: how many copies of the new subSystem is added
        :param kwargs: variables to be changed from the default values or included in the new instance
        :return: the new subSys or list of new subSystems
        """
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
        """
        :return: total dimension of the composite system Hilbert space
        """
        tDim = 1
        for subSys in self.subSystems:
            tDim *= subSys.dimension
        return tDim

    @property
    def freeHam(self):
        """
        :return: free Hamiltonian (i.e. no coupling) of the composite system
        """
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
        if len(self.__cMatrices) == 0:
            st = datetime.now()
            coupled = self.__getCoupling(0)
            cHam = self.__cFncs[0][0] * coupled
            self.__cMatrices.append(coupled)
            for ind in range(len(self.__cFncs) - 1):
                coupled = self.__getCoupling(ind + 1)
                cHam += self.__cFncs[ind + 1][0] * coupled
                self.__cMatrices.append(coupled)
            end = datetime.now()
            # print(end - st)
            return cHam
        else:
            st = datetime.now()
            coupled = self.__cMatrices[0]
            cHam = self.__cFncs[0][0] * coupled
            for ind in range(len(self.__cFncs) - 1):
                coupled = self.__cMatrices[ind + 1]
                cHam += self.__cFncs[ind + 1][0] * coupled
            end = datetime.now()
            # print(end - st)
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
        if self.Matrix == None:
            self.Matrix = hams.compositeOp(self.operator(self.dimension), self.dimsBefore, self.dimsAfter)
            return self.Matrix
        else:
            return self.Matrix


class Qubit(qSystem):
    def __init__(self, **kwargs):
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