"""
    This module contains some of the base classes and the _parameter class.

    Classes
    -------
    | **_parameter** : This is a simple class to wrap certain parameters (attributes)
     to create a hierarchical dependency.
"""
from typing import Any, Union, cast

from collections import OrderedDict
from qTools.classes.QUni import qUniversal, checkClass
from qTools.classes.QRes import qResults
# pylint: disable = cyclic-import

class _parameter:
    """
    This is a simple class to wrap certain parameters (attributes) to create a hierarchical dependency.

    It is intended to be used with the private attributes and the corresponding properties returning `value` of
    that attribute.

    If a `_parameter` is given another `_parameter` as its `bound`, it returns the `value` of its `bound`,
    while keeping its `_value` unchanged (which is mostly left to be None).

    This class can be replaced by a proxy class.
    However, this is intended to be used completely internally (private attributes + properties),
    this simple option should suffice.

    Attributes
    ----------
    _value : Any
        This is any object to be wrapped

    _bound : None or False or _parameter
        The object to be used as the bound.
        None and False both mean that there is no bound, but
        they are used to distinguish between the value being the one given in __init__ method or set later
        by value property.

    Methods
    -------
    value :
        This a property method with the

        getter :
            gets/returns the _value of self if bound is None or False,
            or gets/returns the value of bound which should be
                _parameter object or have a _value attribute
        setter(value) : Any
            sets the _value to a given value and _bound to False
                (signaling its different than the initialisation)

    bound :
        This a property method with the

        getter :
            gets/returns the _bound object
        setter(bound) :
            sets the _bound to bound
    """

    #:This does not have function in this class, but it used in naming of instances, and labels in this library are just
    #: the class names
    label: str = '_parameter'

    __slots__ = ['_value', '_bound']

    def __init__(self, value: Any = None, bound: '_parameter' = None) -> None:
        """
        The init for _parameter has two optional arguments

        Parameters
        ----------
        value : any, optional
            value of the parameter, by default None
        bound : _parameter, bool, or None, optional
            The object to be used as the bound.
            None and False both mean that there is no bound, but
            they are used to distinguish between the value being the one given in __init__ method or set later
            by value property. It is by default None
        """
        self._value = value
        self._bound = bound

    @property
    def bound(self) -> Union['_parameter', bool, None]:
        """
        bound property has:

        | **getter** : returns _bound property of the object
        | **setter** : sets the _bound property of the object
        | **type** : _parameter, False, or None
        """
        return self._bound

    @bound.setter
    def bound(self, bound: '_parameter'):
        self._bound = bound

    @property
    def value(self) -> Any:
        """
        value property has:

        | **getter** : returns _bound property of the object
        | **setter** : sets the _bound property of the object
        | **type** : _parameter, False, or None
        """
        if hasattr(self._bound, 'value'):
            self._bound = cast(_parameter, self._bound)
            return self._bound.value
        return self._value

    @value.setter
    def value(self, value: Any):
        self._bound = False
        self._value = value


class paramBoundBase(qUniversal):
    """
    Parambound

    Parameters
    ----------
    qUniversal : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    instances: int = 0
    label: str = 'paramBoundBase'

    __slots__ = ['__paramUpdated', '__paramBound', '__matrix']

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__matrix = None
        self.__paramUpdated = False
        self.__paramBound = OrderedDict()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def _paramBound(self):
        """[summary]

        Returns
        -------
        [type]
            [description]
        """
        return self._paramBoundBase__paramBound

    @checkClass('qBase')
    def _createParamBound(self, bound, **kwargs) -> None:
        """[summary]

        Parameters
        ----------
        bound : [type]
            [description]
        """
        bound._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self._paramBoundBase__paramBound[bound.name] = bound

    def _breakParamBound(self, bound):
        """[summary]

        Parameters
        ----------
        bound : [type]
            [description]
        """
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
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.compute = None
        self.calculate = None
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self.qRes = qResults(superSys=self)

    @paramBoundBase.name.setter # pylint: disable=no-member
    def name(self, name):
        if self.qRes.superSys is self:
            self.qRes.allResults[name] = self.qRes.allResults.pop(self.name)
            self.qRes.name = name + 'Results'
        paramBoundBase.name.fset(self, name) # pylint: disable=no-member

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
    """[summary]

    Arguments:
        computeBase {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    isinstances = 0
    label = 'qBase'

    __slots__ = ['__simulation', '__openSystem']

    def __init__(self, **kwargs):
        from qTools.classes.Simulation import Simulation # pylint: disable=import-outside-toplevel
        super().__init__(_internal=kwargs.pop('_internal', False))
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
    #         self._qBaseSim__simulation = Simulation(_internal=True, superSys=self) #pylint: disable=assigning-non-slot
    #         self._qBaseSim__simulation._paramBoundBase__paramBound[self.name] = self #pylint: disable=protected-access
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
        super().__init__(_internal=kwargs.pop('_internal', False))

        self.__initialState = _parameter()
        self.__initialStateInput = _parameter()
        self.__delStates = _parameter(False)

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def initialState(self):
        if self._stateBase__initialState.value is None: # pylint: disable=no-member
            self._stateBase__initialState.value = list(self.subSys.values())[0]._initialState(self._initialStateInput) # pylint: disable=protected-access, no-member, line-too-long
        return self._stateBase__initialState.value # pylint: disable=no-member

    @initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self._stateBase__initialStateInput.value = inp # pylint: disable=no-member
        self._stateBase__initialState.value = list(self.subSys.values())[0]._initialState(inp) # pylint: disable=protected-access, no-member, line-too-long

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
