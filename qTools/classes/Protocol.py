import qTools.QuantumToolbox.liouvillian as lio
from qTools.classes.QUni import qUniversal
import qTools.QuantumToolbox.Hamiltonians as hams
from qTools.classes.extensions.ProtocolDecorators import getAsList, setAsList
import numpy as np
""" under construction """

class Protocol(qUniversal):
    __slots__  = ['steps', 'system']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
            unitary = unitary @ step.unitary
        return unitary

class Step(qUniversal):
    __slots__ = ['__unitary']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__unitary = None
        self._qUniversal__setKwargs(**kwargs)
        
class FreeEvolution(Step):
    __slots__  = ['time', '__system', '__key', '__value', '__unitary']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__system = []
        self.__key = []
        self.__value = []
        self.time = 0
        self._qUniversal__setKwargs(**kwargs)

    # FIXME: There has to be a better way of guaranting the atributes are iterable!
    @property
    def system(self):
        return getAsList(self._FreeEvolution__system)
    
    @system.setter
    def system(self, system):
        self._FreeEvolution__system = setAsList(system)

    @property
    def key(self):
        return getAsList(self._FreeEvolution__key)
    
    @key.setter
    def key(self, key):
        self._FreeEvolution__key = setAsList(key)

    @property
    def value(self):
        return getAsList(self._FreeEvolution__value)
    
    @value.setter
    def value(self, value):
        self._FreeEvolution__value = setAsList(value)

    @property
    def unitary(self):
        memory = []
        for ii, system in enumerate(self.system):
            memory.append(getattr(system, self.key[ii]))
            setattr(system, self.key[ii], self.value[ii])
        
        unitary = lio.Liouvillian(
            2 * np.pi * self.superSys.totalHam, timeStep=self.time)

        for ii, system in enumerate(self.system):
            setattr(system, self.key[ii], memory[ii])
        
        self._Step__unitary = unitary
        return unitary

class Gate(Step):
    __slots__ =  ['operator','unitary']
    def __init__(self, operator, superSys, **kwargs):
        super().__init__(**kwargs)
        self.operator = operator
        self.superSys = superSys
        self.unitary = self.set_unitary()

    def set_unitary(self):
        sys = self.superSys
        unitary = hams.compositeOp(
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

# TODO: figure out how to do the fix
class FixedStep:
    def __init__ (self, step):
        pass
