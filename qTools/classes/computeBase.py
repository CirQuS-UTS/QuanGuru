from qTools.classes.QUni import qUniversal
from qTools.classes.QRes import qResults


class computeBase(qUniversal):
    instances = 0
    label = 'computeBase'

    __slots__ = ['__delStates', 'compute', 'calculate', 'qRes']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))

        self.__delStates = True

        self.compute = None
        self.calculate = None

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self.qRes = qResults(superSys=self)

    def getResultByName(self, name):
        return super().getObjByName(name)

    @qUniversal.superSys.setter  # pylint: disable=no-member
    def superSys(self, supSys):
        qUniversal.superSys.fset(self, supSys)  # pylint: disable=no-member
        self.qRes.name = self.superSys.name + self.name + 'Results'  # pylint: disable=no-member

    @property
    def delStates(self):
        return self.__delStates

    @delStates.setter
    def delStates(self, boolean):
        self.__delStates = boolean

    def __compute(self, states):
        if callable(self.compute):
            self.compute(self, *states) # pylint: disable=not-callable

    def __calculate(self, systems, evolutions):
        if callable(self.calculate):
            self.calculate(self, systems, evolutions) # pylint: disable=not-callable
