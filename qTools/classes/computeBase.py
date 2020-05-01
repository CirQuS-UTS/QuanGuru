from qTools.classes.QUni import qUniversal, checkClass
from qTools.classes.QRes import qResults


class qBase(qUniversal):
    instances = 0
    label = 'qBase'

    __slots__ = ['__initialState', '__paramUpdated', '__initialStateInput', '__paramBound', 'qRes']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__initialState = None
        self.__initialStateInput = None
        self.__paramUpdated = False
        self.__paramBound = {}
        self._qUniversal__setKwargs(**kwargs)  # pylint: disable=no-member
        self.qRes = qResults(superSys=self)

    @qUniversal.superSys.setter  # pylint: disable=no-member
    def superSys(self, supSys):
        qUniversal.superSys.fset(self, supSys)  # pylint: disable=no-member
        self.qRes.name = self.superSys.name + self.name + 'Results'  # pylint: disable=no-member

    @checkClass('qUniversal')
    def _addParamBound(self, bound, **kwargs):
        bound._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self._qBase__paramBound[bound.name] = bound

    @property
    def _paramUpdated(self):
        return self._qBase__paramUpdated

    @property
    def initialState(self):
        return self._qBase__initialState

    @property
    def _initialStateInput(self):
        return self._qBase__initialStateInput



class computeBase(qBase):
    instances = 0
    label = 'computeBase'

    __slots__ = ['__delStates', 'compute', 'calculate']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))

        self.__delStates = True

        self.compute = None
        self.calculate = None

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def getResultByName(self, name):
        return super().getObjByName(name)

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
