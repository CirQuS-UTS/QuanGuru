from qTools.classes.QUni import qUniversal
from qTools.classes.QResDict import qResults

class computeBase(qUniversal):
    instances = 0
    label = 'computeBase'
    
    __slots__ = ['__delStates', 'compute', 'calculate', 'qRes']
    
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))

        self.__delStates = False

        self.compute = None
        self.calculate = None

        self._qUniversal__setKwargs(**kwargs)
        self.qRes = qResults(superSys=self)
        
    @property
    def delStates(self):
        return self._computeBase__delStates

    @delStates.setter
    def delStates(self, boolean):
        self._computeBase__delStates = boolean

    def __compute(self, states):
        if self.compute is not None:
            self.compute(self, *states)
