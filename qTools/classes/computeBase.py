from collections import OrderedDict
from qTools.classes.QUni import qUniversal, checkClass
from qTools.classes.QRes import qResults


class _parameter:
    __slots__ = ['_value', '_bound']
    def __init__(self, value):
        self._value = value
        self._bound = None

    def __repr__(self):
        return repr(self.value)

    @property
    def bound(self):
        return self._bound

    @bound.setter
    def bound(self, bound):
        self._bound = bound

    @property
    def value(self):
        if self._bound not in (None, self):
            return self._bound.value
        return self._value

    @value.setter
    def value(self, value):
        self._bound = self
        self._value = value

    def __getattribute__(self, name):
        if name in ['bound', '_bound', 'value', '_value']:
            return object.__getattribute__(self, name)
        return object.__getattribute__(self.value, name)

    def __setattr__(self, name, value):
        if name in ['bound', '_bound', 'value', '_value']:
            object.__setattr__(self, name, value)
        else:
            object.__setattr__(self.value, name, value)

class qBase(qUniversal):
    instances = 0
    label = '_qBase'

    __slots__ = ['__initialState', '__paramUpdated', '__initialStateInput', '__paramBound', 'qRes']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))
        self.__initialState = _parameter(None)
        self.__initialStateInput = _parameter(None)
        self.__paramUpdated = False
        self.__paramBound = OrderedDict()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self.qRes = qResults(superSys=self)

    @property
    def results(self):
        return self.qRes.results

    @property
    def states(self):
        return self.qRes.states

    @checkClass('qBase', '_qBase__paramBound')
    def _createParamBound(self, bound, **kwargs):
        bound._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self._qBase__paramBound[bound.name] = bound

    @checkClass('qBase', '_qBase__paramBound')
    def _breakParamBound(self, bound, **kwargs):
        bound._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        obj = self._qBase__paramBound.pop(bound.name)
        print(obj.name + ' is removed from paramBound of ' + self.name)

    @property
    def _paramUpdated(self):
        return self._qBase__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._qBase__paramUpdated = boolean # pylint: disable=assigning-non-slot
        for sys in self._qBase__paramBound.values():
            if sys is not self:
                if hasattr(sys, '_paramUpdated'):
                    sys._paramUpdated = boolean

    @property
    def initialState(self):
        return self._qBase__initialState.value

    @property
    def _initialStateInput(self):
        return self._qBase__initialStateInput.value


class computeBase(qBase):
    instances = 0
    label = 'computeBase'

    __slots__ = ['__delStates', 'compute', 'calculate']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))

        self.__delStates = _parameter(False)

        self.compute = None
        self.calculate = None

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def getResultByName(self, name):
        return super().getObjByName(name)

    @property
    def delStates(self):
        return self._computeBase__delStates.value

    @delStates.setter
    def delStates(self, boolean):
        self._computeBase__delStates.value = boolean

    def __compute(self, states):
        if callable(self.compute):
            self.compute(self, *states) # pylint: disable=not-callable

    def __calculate(self, systems, evolutions):
        if callable(self.calculate):
            self.calculate(self, systems, evolutions) # pylint: disable=not-callable
