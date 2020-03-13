
# quantum coupling object
class qCoupling(qUniversal):
    instances = 0
    label = 'qCoupling'

    __slots__ = ['__cFncs', '__couplingStrength', '__cOrders', '__Matrix', '__qSys', '__paramUpdated']
    @qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__couplingStrength = None
        self.__cFncs = []
        self.__qSys = []
        self.__Matrix = None
        self.__paramUpdated = True
        self._qUniversal__setKwargs(**kwargs)
        self.addTerm(*args)

    @property
    def _paramUpdated(self):
        return self._qCoupling__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._qCoupling__paramUpdated = boolean

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
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
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
