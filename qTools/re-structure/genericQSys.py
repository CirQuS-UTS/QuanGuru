class genericQSys(qUniversal):
    instances = 0
    label = 'genericQSys'
    __slots__ = ['__constructed', '__initialState', '__lastState', '__unitary', '__initialStateInput', '__paramUpdated', '__lastStateList']
    def __init__(self, **kwargs):
        super().__init__()
        self.__constructed = False
        self.__initialState = None
        self.__lastState = None
        self.__unitary = freeEvolution(superSys=self)
        self.__initialStateInput = None
        self.__paramUpdated = True
        self.__lastStateList = []
        self._qUniversal__setKwargs(**kwargs)
        
    @property
    def _paramUpdated(self):
        return self._genericQSys__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._genericQSys__paramUpdated = boolean

    # constructed boolean setter and getter
    @property
    def constructed(self):
        return self._genericQSys__constructed
    
    @constructed.setter
    def constructed(self, tf):
        self._genericQSys__constructed = tf
    
    # Unitary property and setter
    @property
    def unitary(self):
        if isinstance(self._genericQSys__unitary, qUniversal):
            unitary = self._genericQSys__unitary.createUnitary()
        elif isinstance(self._genericQSys__unitary, list):
            unitary = []
            for protocol in self._genericQSys__unitary:
                unitary.append(protocol.createUnitary())
        self._paramUpdated = False
        return unitary

    @unitary.setter
    def unitary(self, protocols):
        self._genericQSys__unitary = protocols

    # initial state
    @property
    def initialState(self):
        return self._genericQSys__initialState

    @property
    def lastState(self):
        return self._genericQSys__lastState

    @lastState.setter
    def lastState(self, inp):
        self._genericQSys__lastState = inp

    def __prepareLastStateList(self):
        self._genericQSys__lastStateList = []
        if isinstance(self._genericQSys__unitary, qUniversal):
            self._genericQSys__lastStateList.append(self.initialState)
        elif isinstance(self._genericQSys__unitary, list):
            for ind in range(len(self.unitary)):
                self._genericQSys__lastStateList.append(self.initialState)