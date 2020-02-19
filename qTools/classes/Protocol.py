import qTools.QuantumToolbox.liouvillian as lio
from qTools.classes.QUni import qUniversal
import numpy as np
""" under construction """


class Protocol(qUniversal):
    __slots__  = ['steps']
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.steps = []
        self._qUniversal__setKwargs(**kwargs)

    def add_step(self, step):
        step.superSys = self
        self.steps.append(step)

    def free_evol(self, system=[], key=[], value=[], time=0):
        free_evol = FreeEvolution(system=system, key=key, value=value, time=time, superSys=self)
        self.steps.append(free_evol)
        return  free_evol

    @property
    def unitary(self):
        unitary = self.steps[0].unitary
        for step in self.steps[1:]:
            unitary = unitary @ step.unitary
        return unitary

    #TODO: add a function which returns a schematic of the protocol


class FreeEvolution(qUniversal):
    __slots__  = ['time', '__system', '__key', '__value']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__system = []
        self.__key = []
        self.__value = []
        self.time = 0
        self._qUniversal__setKwargs(**kwargs)

    # FIXME: There has to be a better way of guaranting the atributed are iterable!
    @property
    def system(self):
        return self.__system
    
    @system.setter
    def system(self, system):
        if not hasattr(system, '__iter__'):
            self.__system = [system]
        else:
            self.__system = system
    
    @system.getter
    def system(self):
        if len(self.__system)==1:
            return self.__system[0]
        else:
            return self.__system

    @property
    def key(self):
        return self.__key
    
    @key.setter
    def key(self, key):
        if not hasattr(key, '__iter__'):
            self.__key = [key]
        else:
            self.__key = key

    @key.getter
    def key(self):
        if len(self.__key)==1:
            return self.__key[0]
        else:
            return self.__key

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if not hasattr(value, '__iter__'):
            self.__value = [value]
        else:
            self.__value = value
    
    @value.getter
    def value(self):
        if len(self.__value)==1:
            return self.__value[0]
        else:
            return self.__value

    @property
    def unitary(self):
        memory = []
        for ii, system in enumerate(self.system):
            memory = getattr(system, self.key[ii])
            setattr(system, self.key[ii], self.value[ii])

        unitary = lio.Liouvillian(
            2 * np.pi * self.superSys.superSys.totalHam, timeStep=self.time)
       
        for ii, system in enumerate(self.system):
            setattr(system, self.key[ii], memory[ii])

        return unitary
