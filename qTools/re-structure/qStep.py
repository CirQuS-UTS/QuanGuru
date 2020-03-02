
class Step(qUniversal):
    instances = 0
    label = 'Step'
    __slots__ = ['__unitary', '__stepSize', '__samples', '__ratio', '__time', '__updates', '__fixed', 'getUnitary', '__bound', 'createUnitary', 'lastState']
    def __init__(self, **kwargs):
        super().__init__()
        self.__unitary = None
        self.__stepSize = None
        self.__samples = None
        self.__ratio = None
        self.__updates = []
        self.__fixed = False
        self.__bound = self
        self.getUnitary = None
        self.createUnitary = self.createUnitaryFunc
        self.lastState = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def updates(self):
       return self._Step__updates

    @property
    def ratio(self):
        return self._Step__ratio

    @ratio.setter
    def ratio(self, val):
        self._Step__ratio = val

    @property
    def fixed(self):
        return self._Step__fixed

    @fixed.setter
    def fixed(self, boolean):
        self._Step__fixed = boolean

    @property
    def stepSize(self):
        return self._Step__stepSize

    @stepSize.setter
    def stepSize(self, val):
        self._Step__stepSize = val

    @property
    def samples(self):
        return self._Step__samples

    @samples.setter
    def samples(self, val):
        self._Step__samples = val

    def createUnitaryFunc(self):
        if self.superSys._paramUpdated is True:
            unitary = self.getUnitary()
        else:
            unitary = self._Step__unitary
        return unitary

    def createUnitaryFixedFunc(self):
        return self._Step__unitary

    @property
    def unitary(self):
        if self._Step__unitary is not None:
            if self.superSys._paramUpdated is False:
                unitary = self._Step__unitary
            else:
                unitary = self.createUnitary()
            return unitary
        else:
            return self.createUnitary()

    def createUpdate(self, **kwargs):
        update = Update(**kwargs)
        self.addUpdate(update)
        return update
    
    def addUpdate(self, *args):
        for update in args:
            self._Step__updates.append(update)

    def prepare(self, obj):
        if self.stepSize is None:
            self._Step__bound = obj

        if self.samples is None:
            self.samples = obj.samples

        if self.ratio is None:
            self.ratio = 1

    @property
    def bound(self):
        return self._Step__bound

class copyStep(Step):
    instances = 0
    label = 'copyStep'
    __slots__ = []
    def __init__(self, superSys):
        self.superSys = superSys
        self.createUnitary = self.unitaryCopy
    
    def unitaryCopy(self):
        return self.superSys._Step__unitary
        
class freeEvolution(Step):
    instances = 0
    label = 'freeEvolution'
    __slots__  = []
    def __init__(self, **kwargs):
        super().__init__()
        self.getUnitary = self.getUnitaryNoUpdate
        self._qUniversal__setKwargs(**kwargs)
    
    @Step.fixed.setter
    def fixed(self, cond):
        if cond:
            self.getUnitary = self.getFixedUnitary
        else:
            if len(self._Step__updates) == 0:    
                self.getUnitary = self.getUnitaryNoUpdate
            else:
                self.getUnitary = self.getUnitaryUpdate
        self._Step__fixed = cond

    def getUnitaryNoUpdate(self):
        unitary = lio.Liouvillian(2 * np.pi * self.superSys.totalHam, timeStep=((self.bound.stepSize*self.ratio)/self.bound.samples))
        self._Step__unitary = unitary
        return unitary
        
    def getUnitaryUpdate(self):
        for update in self._Step__updates:
            update.setup() 
        unitary = self.getUnitaryNoUpdate()
        for update in self._Step__updates:
            update.setback()
        return unitary

    def getFixedUnitary(self):
        return self._Step__unitary

    def addUpdate(self, *args):
        for update in args:
            self._Step__updates.append(update)
        self.getUnitary = self.getUnitaryUpdate

class Gate(Step):
    instances = 0
    label = 'Gate'
    __slots__ =  ['__implementation']
    def __init__(self, **kwargs):
        super().__init__()
        self.__implementation = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def implementation(self):
        return self._Gate__implementation

    @implementation.setter
    def implementation(self, typeStr):
        self._Gate__implementation = typeStr
