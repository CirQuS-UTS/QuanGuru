# quantum system objects
class qSystem(genericQSys):
    instances = 0
    label = 'qSystem'

    __slots__ = ['__dimension', '__frequency', '__operator', '__Matrix', '__dimsBefore', '__dimsAfter', '__terms', 'order']
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
        self.order = 1
        self._qUniversal__setKwargs(**kwargs)

    @property
    def terms(self):
        if not isinstance(self.superSys, qSystem):
            return self._qSystem__terms
        else:
            print('This is a term in ', self.superSys)

    @genericQSys.initialState.setter
    @asignState(qSta.superPos)
    def initialState(self, state):
        pass

    @property
    def frequency(self):
        return self._qSystem__frequency

    @frequency.setter
    def frequency(self, freq):
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._qSystem__frequency = freq

    @property
    def operator(self):
        return self._qSystem__operator

    @operator.setter
    def operator(self, op):
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        self._qSystem__operator = op

    @property
    def dimension(self):
        return self._qSystem__dimension

    @dimension.setter
    def dimension(self, newDimVal):
        if not isinstance(newDimVal, int):
            raise ValueError('Dimension is not int')
        self._qSystem__dimension = newDimVal
        if isinstance(self.superSys, QuantumSystem):
            QuantumSystem.updateDimension(self.superSys, self, newDimVal)
        self._paramUpdated = True
        if self.superSys is not None:
            self.superSys._paramUpdated = True
        if self.constructed is True:
            self.initialState = self._genericQSys__initialStateInput
            
    @property
    def totalHam(self):
        h = sum([(obj.frequency * obj.freeMat) for obj in self._qSystem__terms])
        return h

    # I'm not sure to keep this, freeMat setter covers all the cases and this one does not make much sense
    """@totalHam.setter
    def totalHam(self, qOpsFunc):
        self.freeMat = qOpsFunc
        self._qSystem__freeMat = ((1/self.frequency)*(self.freeMat))"""

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

    @constructConditions({'dimension':int,'operator':qOps.sigmax.__class__})
    def __constructSubMat(self):
        for sys in self._qSystem__terms:
            sys._qSystem__Matrix = qOps.compositeOp(sys.operator(self.dimension), self._qSystem__dimsBefore, self._qSystem__dimsAfter)**sys.order
            sys._genericQSys__constructed = True
        return self._qSystem__Matrix

    def addTerm(self, op, freq, order=1):
        copySys = self.copy(operator=op, frequency=freq, superSys=self)
        copySys.order = order
        self._qSystem__terms.append(copySys)
        return copySys

    def copy(self, **kwargs):
        # TODO should copy the terms as well
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
        print(kwargs)
        super().__init__()
        kwargs['dimension'] = 2
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
        super().__init__()
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


class Cavity(qSystem):
    instances = 0
    label = 'Cavity'

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__()
        self.operator = qOps.number
        self._qUniversal__setKwargs(**kwargs)
