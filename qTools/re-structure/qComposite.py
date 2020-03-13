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
        # TODO make sure that the kept protocols deletes their matrices and different sweeps ?
        for qSys in self.qSystems.values():
            qSys._qSystem__Matrix = None

        for qCoupl in self.qCouplings.values():
            qCoupl._qCoupling__Matrix = None
        self._QuantumSystem__keepOld()
        self._genericQSys__constructed = False
        if to is None:
            self.qCouplings = {}
            self._genericQSys__unitary = freeEvolution(superSys=self)
            self.couplingName = None
        else:
            self.couplingName = to
            self.qCouplings = self._QuantumSystem__kept[to][0]
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
        self.initialState = self._genericQSys__initialStateInput
        self._paramUpdated = True
        if self._genericQSys__constructed is True:
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

