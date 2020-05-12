from collections import OrderedDict
from qTools.classes.QUni import qUniversal, checkClass
from qTools.classes.QRes import qResults

class _parameter:
    label = '_parameter'
    __slots__ = ['_value', '_bound']
    def __init__(self, value, bound=None):
        self._value = value
        self._bound = bound

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
        if self._bound not in (None, False):
            return self._bound.value
        return self._value

    @value.setter
    def value(self, value):
        self._bound = False
        self._value = value

    def __getattribute__(self, name):
        if name in ['bound', '_bound', 'value', '_value', '__getstate__', '__setstate__',
                    '__dict__', '__reduce__', '__reduce_ex__', '__class__']:
            return object.__getattribute__(self, name)
        return object.__getattribute__(self.value, name)

    def __setattr__(self, name, value):
        if name in ['bound', '_bound', 'value', '_value', '__getstate__', '__setstate__',
                    '__dict__', '__reduce__', '__reduce_ex__', '__class__']:
            object.__setattr__(self, name, value)
        else:
            object.__setattr__(self.value, name, value)

    def __getstate__(self):
        return self.__class__, self._value, self._bound

    def __setstate__(self, state):
        self.__class__, self._value, self._bound = state

    def __reduce__(self):
        return (self.__class__, (self._value, self._bound,))

class paramBoundBase(qUniversal):
    instances = 0
    label = 'paramBoundBase'

    __slots__ = ['__paramUpdated', '__paramBound', '__matrix']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))
        self.__matrix = None
        self.__paramUpdated = False
        self.__paramBound = OrderedDict()

    @checkClass('qBase', '_paramBoundBase__paramBound')
    def _createParamBound(self, bound, **kwargs):
        bound._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self._paramBoundBase__paramBound[bound.name] = bound

    @checkClass('qBase', '_paramBoundBase__paramBound')
    def _breakParamBound(self, bound, **kwargs):
        bound._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        obj = self._paramBoundBase__paramBound.pop(bound.name)
        print(obj.name + ' is removed from paramBound of ' + self.name)

    @property
    def _paramUpdated(self):
        return self._paramBoundBase__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._paramBoundBase__paramUpdated = boolean # pylint: disable=assigning-non-slot
        for sys in self._paramBoundBase__paramBound.values():
            if sys is not self:
                if hasattr(sys, '_paramUpdated'):
                    sys._paramUpdated = boolean

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        if self not in _exclude:
            self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
            _exclude.append(self)
            for sys in self._paramBoundBase__paramBound.values(): # pylint: disable=no-member
                if hasattr(sys, 'delMatrices'):
                    _exclude = sys.delMatrices(_exclude)
            for sys in self.subSys.values(): # pylint: disable=no-member
                if hasattr(sys, 'delMatrices'):
                    _exclude = sys.delMatrices(_exclude)
        return _exclude

class computeBase(paramBoundBase):
    instances = 0
    label = '_qBase'

    __slots__ = ['qRes', 'compute', 'calculate']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))
        self.compute = None
        self.calculate = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self.qRes = qResults(superSys=self)

    def __compute(self, states):
        if callable(self.compute):
            self.compute(self, *states) # pylint: disable=not-callable

    def __calculate(self, systems, evolutions):
        if callable(self.calculate):
            self.calculate(self, systems, evolutions) # pylint: disable=not-callable

    @property
    def results(self):
        return self.qRes.results

    @property
    def states(self):
        return self.qRes.states

class qBaseSim(computeBase):
    isinstances = 0
    label = 'qBase'

    __slots__ = ['__simulation', '__openSystem']

    def __init__(self, **kwargs):
        from qTools.classes.Simulation import Simulation
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))
        self.__simulation = Simulation(_internal=True)
        self._qBaseSim__simulation._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        # self.__openSystem = False

    @property
    def simulation(self):
        return self._qBaseSim__simulation

    # @property
    # def _openSystem(self):
    #     return self._qBaseSim__openSystem

    # @_openSystem.setter
    # def _openSystem(self, boolean):
    #     self._qBaseSim__openSystem = True
    #     for sys in self._paramBoundBase__paramBound.values(): # pylint: disable=no-member
    #         if hasattr(sys, '_openSystem'):
    #             sys._openSystem = boolean

    # @simulation.setter
    # def simulation(self, sim):
    #     if ((sim is None) or (sim == 'new')):
    #         self._qBaseSim__simulation = Simulation(_internal=True, superSys=self) # pylint: disable=assigning-non-slot
    #         self._qBaseSim__simulation._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
    #     else:
    #         self._qBaseSim__simulation = sim # pylint: disable=assigning-non-slot
    #         sim._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
    #         for sys in self.subSys.values():
    #             if sys is not self:
    #                 if hasattr(sys, 'simulation'):
    #                     sys.simulation = sim

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            _exclude = self.simulation.delMatrices(_exclude)
        return _exclude

class stateBase(computeBase):
    instances = 0
    label = 'computeBase'

    __slots__ = ['__delStates', '__initialState', '__initialStateInput']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))

        self.__initialState = _parameter(None)
        self.__initialStateInput = _parameter(None)
        self.__delStates = _parameter(False)

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def initialState(self):
        if self._stateBase__initialState.value is None: # pylint: disable=no-member
            self._stateBase__initialState.value = list(self.subSys.values())[0]._initialState(self._initialStateInput) # pylint: disable=protected-access, no-member
        return self._stateBase__initialState.value # pylint: disable=no-member

    @initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self._stateBase__initialStateInput.value = inp # pylint: disable=no-member
        self._stateBase__initialState.value = list(self.subSys.values())[0]._initialState(inp) # pylint: disable=protected-access, no-member

    @property
    def _initialStateInput(self):
        return self._stateBase__initialStateInput.value

    def getResultByName(self, name):
        return super().getObjByName(name)

    @property
    def delStates(self):
        return self._stateBase__delStates.value

    @delStates.setter
    def delStates(self, boolean):
        self._stateBase__delStates.value = boolean

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            self._stateBase__initialState.value = None # pylint: disable=no-member, protected-access
        return _exclude
