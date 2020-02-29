import qTools.QuantumToolbox.liouvillian as lio
from qTools.classes.QUni import qUniversal
from qTools.QuantumToolbox.operators import compositeOp
import numpy as np
""" under construction """

class Protocol(qUniversal):
    __slots__  = ['steps', 'system']
    def __init__(self, **kwargs):
        super().__init__()
        self.steps = []
        self._qUniversal__setKwargs(**kwargs)

    def add(self, *args):
        for ii, step in enumerate(args):
            if step in self.steps:
                self.steps.append(CopyStep(step))
            else:
                step.superSys = self.superSys
                self.steps.append(step)

    def unitary(self):
        unitary = self.steps[0].unitary
        for step in self.steps[1:]:
            unitary = step.unitary @ unitary
        return unitary

class Step(qUniversal):
    __slots__ = ['__unitary']
    def __init__(self, **kwargs):
        super().__init__()
        self.__unitary = None
        self._qUniversal__setKwargs(**kwargs)
        
class FreeEvolution(Step):
    __slots__  = ['time', 'updates', 'getUnitary', '__fixed']
    def __init__(self, **kwargs):
        super().__init__()
        self.time = 0
        self.updates =  []
        self.__fixed = False
        self.getUnitary = self.getUnitaryNoUpdate
        self._qUniversal__setKwargs(**kwargs)

    def getUnitaryNoUpdate(self):
        unitary = lio.Liouvillian(
            2 * np.pi * self.superSys.totalHam, timeStep=self.time)
        self._Step__unitary = unitary
        return unitary
        
    def getUnitaryUpdate(self):
        for update in self.updates:
            update.setup() 

        unitary = lio.Liouvillian(
            2 * np.pi * self.superSys.totalHam, timeStep=self.time)

        for update in self.updates:
            update.setback()

        self._Step__unitary = unitary
        return unitary

    def getFixedUnitary(self):
        return self._Step__unitary
        
    @property
    def fixed(self):
        return self._FreeEvolution__fixed
    
    @fixed.setter
    def fixed(self, boollean):
        if boollean:
            self.getUnitary = self.getFixedUnitary
        else:
            if len(self.updates)==0:    
                self.getUnitary = self.getUnitaryNoUpdate
            else:
                self.getUnitary = self.getUnitaryUpdate
        self._FreeEvolution__fixed = boollean

    def createUpdate(self, **kwargs):
        update = Update(**kwargs)
        self.addUpdate(update)
        return update
    
    def addUpdate(self, *args):
        for update in args:
            self.updates.append(update)
        self.getUnitary = self.getUnitaryUpdate

    @property
    def unitary(self):
        return self.getUnitary()

class Gate(Step):
    __slots__ =  ['operator','unitary']
    def __init__(self, superSys, operator, **kwargs):
        super().__init__()
        self.operator = operator
        self.superSys = superSys
        self.unitary = self.setUnitary()
        self._qUniversal__setKwargs(**kwargs)

    def setUnitary(self):
        sys = self.superSys
        unitary = compositeOp(
            self.operator(sys.dimension),
            sys._qSystem__dimsBefore,
            sys._qSystem__dimsAfter)
        self._Step__unitary = unitary
        return unitary
        
class CopyStep:
    def __init__(self, superSys):
        self.superSys = superSys
    
    @property
    def unitary(self):
        return self.superSys._Step__unitary

class Update(qUniversal):
    slots = ['system', 'key', 'value', 'memory']
    def __init__ (self, **kwargs):
        super().__init__()
        self.system = None
        self.key = None
        self.value = None
        self.memory = None
        self._qUniversal__setKwargs(**kwargs)

    def setup(self):
        self.memory = getattr(self.system, self.key)
        setattr(self.system, self.key, self.value)
    
    def setback(self):
        setattr(self.system, self.key, self.memory)
