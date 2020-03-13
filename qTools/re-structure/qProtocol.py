class qProtocol(qUniversal):
    instances = 0
    label = 'qProtocol'
    __slots__  = ['__steps', '__unitary', 'lastState']
    def __init__(self, **kwargs):
        super().__init__()
        self.__steps = []
        self.__unitary = None
        self.lastState = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def steps(self):
        return self._qProtocol__steps

    def addStep(self, *args):
        for ii, step in enumerate(args):
            if step in self.steps:
                self.steps.append(copyStep(step))
            else:
                self.steps.append(step)
                # TODO is this really necessary ?
                if step.superSys is None:
                    step.superSys = self.superSys

    def createStep(self, n=1):
        newSteps = []
        for ind in range(n):
            newSteps.append(Step())
        self._qProtocol__steps.extend(newSteps)
        return newSteps if n > 1 else newSteps[0]

    @property
    def unitary(self):
        if self._qProtocol__unitary is not None:
            return self._qProtocol__unitary
        else:
            return self.createUnitary()

    @unitary.setter
    def unitary(self, uni):
        # TODO generalise this
        if uni is None:
            self.createUnitary()

    def createUnitary(self):
        unitary = identity(self.superSys.dimension)
        for step in self.steps:
            unitary = step.createUnitary() @ unitary
        self._qProtocol__unitary = unitary
        return unitary

    def prepare(self, obj):
        for step in self.steps:
            if not isinstance(step, copyStep):
                step.prepare(obj)
                if step.fixed is True:
                    step.createUnitary()
                    step.createUnitary = step.createUnitaryFixedFunc