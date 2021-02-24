r"""
    Contains some base classes and the _parameter class.

    .. currentmodule:: qTools.classes.baseClasses

    .. autosummary::

        _parameter

    .. autosummary::

        updateBase
        paramBoundBase
        computeBase
        qBaseSim
        stateBase
        timeBase

"""
from typing import Any, Callable, Dict, List, Union, cast

from .base import named, qBase, addDecorator, _recurseIfList, aliasDict
from .QRes import qResults
from .tempConfig import classConfig
# pylint: disable = cyclic-import

class updateBase(qBase):
    r"""
    Base class for :class:`~_sweep` and :class:`~Update` classes, which are used respectively in parameter sweeps and
    step updates in protocols.
    This class implements a default method to change the value of an attribute (str of the attribute name is
    stored in self.key) of the objects in the subSys dictionary. It can also sweep/update auxiliary dictionary by
    setting the aux boolean to True. The default method
    can be changed to anything by pointing function attribute to any other Callable.
    """
    #: (**class attribute**) class label used in default naming
    label: str = 'updateBase'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__key', '__function', '_aux']

    def __init__(self, **kwargs) -> None:
        super().__init__()
        #: string for an attribute of the objects in ``subSys`` dictionary, used in getattr().
        self.__key: str = None
        #: attribute for custom sweep/update methods. Assigned to some default methods in child, and sweep/update
        #: methods can be customized by re-assigning this.
        self.__function: Callable = None
        #: boolean to switch from subSys attribute sweep/update (False) to auxiliary dictionary key sweep/update (True)
        self._aux: bool = False
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def key(self) -> str:
        r"""
        Gets and sets the  _updateBase__key protected attribute
        """
        return self._updateBase__key

    @key.setter
    def key(self, keyStr: str) -> None:
        self._updateBase__key = keyStr # pylint: disable=assigning-non-slot

    @property
    def system(self) -> Union[List, named]:
        r"""
        system property wraps ``subSys`` dictionary to create a new terminology, it basically:

        gets subSys[0] if there is only one item in it, else  list(subSys.values())
        setter works exactly as :meth:`addSubSys <qTools.classes.base.qBase.addSubSys>` method.
        """
        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @system.setter
    def system(self, qSys: Any) -> None:
        super().addSubSys(qSys)

    def _runUpdate(self, val: Any) -> None:
        r"""
        a simple method to set the attribute (for the given key) of every ``subSys`` to a given value (``val``), if _aux
        bool is False. If _aux True, updates the value for the given key in aux dictionary
        returns ``None``.
        """
        if self._aux is False:
            for subSys in self.subSys.values():
                setattr(subSys, self._updateBase__key, val)
        elif self._aux is True:
            self.aux[self._updateBase__key] = val

class _parameter: # pylint: disable=too-few-public-methods
    r"""
    _parameter instances can be bound to each other to implement a (value) dependency between them.

    There are two types of parametric bounds/relations/dependencies in this library,

        1. Value of an attribute in an instance is bound to the value of the same attribute in another instance, meaning
           it gets its value from its bound.
        2. Not the value of the attribute itself, but any change in its value is important for another object.

    This class wraps (composition) the value of a parameter (an attribute) to create a hierarchical dependency required
    for the first case. The second case is covered by :class:`~paramBoundBase`.

    It is intended to be used with `private attributes` and the corresponding properties returns the ``value`` of
    that attribute (which is a _parameter object).

    If a ``_parameter`` is given another ``_parameter`` as its ``_bound``, it returns the ``value`` of its ``_bound``,
    while keeping its ``_value`` unchanged (which is mostly left to be ``None``). This is the same for the bound
    one, which means a chain of dependency is achieved by bounding each object to another.

    bounds can be broken by explicitly setting the ``value``.

    TODO update this list and add cross-references.
    Used in ``stepSize``, ``totalTime``, ``stepCount``, ``initialState`` etc. The goal of having such
    dependency is that, for example, when simulating a quantum system simultaneously using more than 1 protocol, we
    can assign an ``initialState`` for the quantum system, and all the protocols ``initialState`` will by default be
    ``_bound`` to quantum systems ``initialState`` and get their value from it.
    If we explicitly assign an ``initialState`` to any protocol, the ``_bound`` will break for that particular protocol,
    which will have its own ``initialState``, but not the others, unless they are also explicitly given an
    ``initialState``. These sort of dependencies are implemented in the library and are not meant for external
    modifications.

    This class can be replaced by a proxy class.
    However, this is intended to be used completely internally (private attributes + properties),
    this simple option should suffice.
    """

    __slots__ = ['_value', '_bound']

    def __init__(self, value: Any = None, bound: '_parameter' = None) -> None:
        assert bound is not self, "cannot bound a _parameter to itself!"
        #: the value to be wrapped
        self._value: Any = value #pylint:disable=unsubscriptable-object
        #: bounded _parameter object, self is not bounded to anything when this is None or any other object that does
        #: not have a ``value`` attribute. Assigned to False when a bound is broken (by updating the value).
        self._bound: "_parameter" = bound

    @property
    def value(self) -> Any:
        r"""
        Property to get the ``_value`` of self, if ``bound`` does not have ``value`` as an attribute,
        else returns the ``value`` of the ``_bound``,
        which should be an instance of :class:`~_parameter` object but can be any other object with an ``_value``
        &/ ``_bound`` attribute.

        Setter assigns the ``_value`` to a given input and ``_bound`` to ``False``
        (meaning the bound to any other object is broken, and value is different than the default, which is None)
        """
        if hasattr(self._bound, 'value'):
            self._bound = cast(_parameter, self._bound)
            return self._bound.value
        return self._value

    @value.setter
    def value(self, value: Any) -> None:
        self._bound = False
        self._value = value

def setAttr(obj: "paramBoundBase", attrStr: str, val: Any) -> None:
    r"""
    a customized setattr that changes the value (and _paramUpdated) if the new value is different than the old/existing.
    Especially useful for multi parameter sweeps (see :class:`~_sweep`).
    """
    oldVal = getattr(obj, attrStr)
    if val != oldVal:
        setattr(obj, attrStr, val)
        setattr(obj, '_paramUpdated', True)

def setAttrParam(obj: "paramBoundBase", attrStr: str, val: Any) -> None:
    r"""
    a customized setattr that changes the value stored as the ``value`` attribute of a _parameter object.
    The value (and _paramUpdated) is changed, if the new value is different than the old/existing. In any case, it
    breaks existing timeBase bounds (bound between :class:`~Simulation` instances).
    Especially useful for multi parameter sweeps (see :class:`~_sweep`).
    """
    oldVal = getattr(obj, attrStr).value
    if obj._timeBase__bound is not None:
        obj._timeBase__bound._paramBoundBase__paramBound.pop(obj.name, None)
        obj._timeBase__bound = None

    if val != oldVal:
        getattr(obj, attrStr).value = val
        setattr(obj, '_paramUpdated', True)

class paramBoundBase(qBase):
    r"""
    Implements a mechanism to inform a set of objects when a (relevant) change happens on self.

    There are two types of parametric bounds/relations in this library,

        1. Value of an attribute in an instance is bound to the value of the same attribute in another instance, meaning
           it gets its value from its bound.
        2. Not the value of the attribute itself, but any change in its value is important for another object.

    First case is covered by the :class:`~_parameter` , and the second is by this class.

    Such bound, for example, is used to make sure that a **protocol** does not re-create (re-exponentiate)
    its **unitary matrix**, unless a relevant parameter is changed. If the ``__paramUpdated`` is ``False``, a protocol
    is not going to re-create its unitary, the ``__paramUpdated`` is set to ``True`` only by an object which contain
    the protocol in its ``__paramBound`` dictionary and changes its ``__paramUpdated`` to ``True`` by calling
    :meth:`_paramUpdated <paramBoundBase._paramUpdated>` property. These sort of dependencies are implemented in the
    library and are not meant for external modifications by a user.
    """
    #: (**class attribute**) class label used in default naming
    label: str = 'paramBoundBase'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__paramUpdated', '__paramBound', '__matrix']

    def __init__(self, **kwargs) -> None:
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: This stores a matrix in some sub-classes, e.g. protocols ``__matrix`` store their unitary, single quantum
        #: systems use it for their ``freeMat``
        self.__matrix = None
        #: Signals that a parameter is updated. This is set to ``True`` when a parameter is updated by :meth:`~setAttr`,
        #: :meth:`~setAttrParam` methods, or True/False by another object, if this object is in another paramBound.
        self.__paramUpdated = True
        # NOTE protocols check only their own _paramUpdated for re-creation, so, they only set their own
        # _paramUpdated back after re-creation. This means that the dependency of _paramUpdated boolean is different
        # than :class:`~_parameter` class.

        #: a dictionary of objects whose ``_paramUpdated`` boolean value needs to be updated, if ``_paramUpdated``
        #: of ``self`` is updated (but not the other way around and, unlike :class:`_parameter` setting ones
        #: value does not break the relation).
        self.__paramBound = aliasDict()
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def _paramBound(self) -> Dict:
        r"""
        returns ``_paramBoundBase__paramBound`` dictionary. Since the bound mechanism is meant for internal use, this
        provide an information of the bound structure, but does not have a setter. Creating/breaking a bound has their
        specific methods.
        """
        return self._paramBoundBase__paramBound

    @addDecorator
    def _createParamBound(self, bound: "paramBoundBase", **kwargs) -> "paramBoundBase":
        r"""
        creates a bound to ``self``, ie. given ``bound`` (have to be an :class:`~paramBoundBase` instance) objects
        `__paramUpdated` boolean is updated whenever self updates its.
        """
        assert isinstance(bound, paramBoundBase), "Given object is not an instance of paramBoundBase!"
        bound._named__setKwargs(**kwargs) # pylint: disable=no-member
        self._paramBoundBase__paramBound[bound.name] = bound
        return bound

    @_recurseIfList
    def _breakParamBound(self, bound: "paramBoundBase", _exclude=[]) -> None: # pylint: disable=dangerous-default-value
        r"""
        This method removes the given object from the ``__paramBound`` dictionary.
        """
        if not isinstance(bound, paramBoundBase):
            bound = self.getByNameOrAlias(bound)
        assert isinstance(bound, paramBoundBase), "Given object is not an instance of paramBoundBase!"
        self._paramBoundBase__paramBound.pop(bound.name)

    @property
    def _paramUpdated(self) -> bool:
        r"""
        Gets ``_paramBoundBase__paramUpdated`` boolean, and sets it for ``self`` and all the other objects in
        ``__paramBound`` dictionary.
        """

        return self._paramBoundBase__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean: bool):
        self._paramBoundBase__paramUpdated = boolean # pylint: disable=assigning-non-slot
        for sys in self._paramBoundBase__paramBound.values():
            sys._paramUpdated = boolean

    def delMatrices(self, _exclude: List = []) -> List: # pylint: disable=dangerous-default-value
        r"""
        This method deletes (sets to ``None``) the ``__matrix`` value for self and calls the ``delMatrices`` for the
        objects in ``__paramBound`` and ``subSys`` dictionaries. Also, calls ``del`` on the old value of ``__matrix``.

        Parameters
        ----------

        _exclude : list, optional
            This is used internally to avoid infinite loops in the cases when an object has another in its
            ``__paramBound``, while it is in ``subSys`` of the other. By default []


        :returns: the _exclude list, which should contain references to all the objects whose ``__matrix`` attribute is
            set to ``None``

        """

        if self not in _exclude:
            oldMat = self._paramBoundBase__matrix # noqa: F841
            self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
            del oldMat
            _exclude.append(self)
            for sys in self._paramBoundBase__paramBound.values(): # pylint: disable=no-member
                if hasattr(sys, 'delMatrices'):
                    _exclude = sys.delMatrices(_exclude)
            for sys in self.subSys.values(): # pylint: disable=no-member
                if hasattr(sys, 'delMatrices'):
                    _exclude = sys.delMatrices(_exclude)
        return _exclude

class computeBase(paramBoundBase):
    r"""
    Implements 3 attributes (and mechanisms) relevant to run-time calculations/computations and result storage.
    """
    #: (**class attribute**) class label used in default naming
    label: str = 'computeBase'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['qRes', 'compute', 'calculateStart', 'calculateEnd']

    def __init__(self, **kwargs) -> None:
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.compute: Callable = None
        r"""
        Function to call at each step of the time evolution, by default ``None``. It needs to be written in the
        appropriate form  TODO create examples/tutorial and link here.
        It is intended to perform computations on the current state of the system and store the results
        in the ``self.qRes.results``.
        """
        self.calculateStart: Callable = None
        r"""
        Function to call at the beginning of time-evolution (or simulation) to perform
        some calculations, which might be needed in the compute, and store them in the ``self.qRes.calculated``.
        This is by default ``None``.
        """
        self.calculateEnd: Callable = None
        r"""
        Function to call at the end of time-evolution (or simulation) to perform
        some calculations, which might be needed in the compute, and store them in the ``self.qRes.calculated``.
        This is by default ``None``.
        """
        self._named__setKwargs(**kwargs) # pylint: disable=no-member
        #: This attribute is an instance of :class:`~qResults`, which is used to store simulation results and states.
        self.qRes: qResults = qResults(superSys=self, _internal=True, alias=self.name.name+"Results")

    def __compute(self, states) -> None: # pylint: disable=dangerous-default-value
        r"""
        This is the actual compute function that is called in the time-evolution, it calls ``self.compute`` if it is a
        callable and does nothing otherwise.
        """
        if callable(self.compute):
            self.compute(self, *states) # pylint: disable=not-callable

    def __calculate(self, where: str = "start") -> None:
        r"""
        This is the actual calculate function that is called in the time-evolution, it calls
        (if callable, does nothing otherwise) ``self.calculateStart``
        or ``self.calculateEnd`` depending on the given string `where`.
        """
        if where == "start":
            meth = self.calculateStart
        elif where == "end":
            meth = self.calculateEnd

        if callable(meth):
            meth(self) # pylint: disable=not-callable

    @paramBoundBase.alias.setter
    def alias(self, ali: str) -> None:
        r"""
        Extends the alias setter to assign an alias (givenAlias + Results) to self.qRes as well.
        """
        named.alias.fset(self, ali) #pylint:disable=no-member
        self.qRes.alias = ali + "Results"

    @property
    def results(self) -> Dict:
        r"""
        returns ``self.qRes.results``.
        """
        return self.qRes.results

    @property
    def states(self) -> Dict:
        r"""
        returns ``stateList if len(list(self.qRes.states.values())) > 1 else stateList[0]`` where stateList is
        ``list(self.qRes.states.values())``.
        """
        #return self.qRes.states
        stateList = list(self.qRes.states.values())
        return stateList if len(list(self.qRes.states.values())) > 1 else stateList[0]

class qBaseSim(computeBase):
    r"""
    Inhereted by the :class:`quantum systems <qTools.classes.QSys.genericQSys>` and
    :class:`protocols <qTools.classes.QPro.genericProtocol>` and has a
    simulation attribute which is an instance of :class:`Simulation <qTools.classes.Simulation.Simulation>`. The goal
    for such an attribute is to increase possible ways of running a
    :class:`Simulation <qTools.classes.Simulation.Simulation>`.
    TODO : create a simple demo and a cross-reference

    NOTE : This class branches the inheritance started by :class:`paramBoundBase`, and this branch extends to
    :class:`quantum systems <qTools.classes.QSys.genericQSys>` and
    :class:`protocols <qTools.classes.QPro.genericProtocol>`.
    """
    #: (**class attribute**) class label used in default naming
    label = 'qBaseSim'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__simulation']

    def __init__(self, **kwargs) -> None:
        from qTools.classes.QSim import Simulation # pylint: disable=import-outside-toplevel
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: an instance of Simulation (as a protected attribute) to run
        # ``self.simulation.run`` without any explicit Simulation creation and/or ``subSys`` addition call.
        self.__simulation = Simulation(_internal=True, superSys=self)
        self._qBaseSim__simulation._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        self._named__setKwargs(**kwargs) # pylint: disable=no-member
        # self.__openSystem = False

    @property
    def simulation(self):
        r"""
        ``returns _qBaseSim__simulation`` attribute (an instance of :class:`~Simulation`).
        """
        return self._qBaseSim__simulation

    def runSimulation(self, p=None, coreCount=None):
        r"""
        an alternative to run the simulation, equivalent to ``self.simulation.run()``
        """
        return self._qBaseSim__simulation.run(p=p, coreCount=coreCount)

    @property
    def simParameters(self):
        r"""
        returns a tuple contaning simulation parameters for the self.simulation, which might be bound to some other
        simulation object and getting values from there.

        There are various setters of this property with different names to set the relevant attribute of the simulation.
        # TODO should we include calculate methods into the tuple ? and have a setter for calculates as well ?
        """
        return ('totalTime:', self.simulation.totalTime, 'stepSize:', self.simulation.stepSize, 'stepCount:',
                self.simulation.stepCount, 'samples:', self.simulation.samples, 'delStates:',
                self.simulation.delStates, 'compute:', self.simulation.compute)

    @simParameters.setter
    def simTotalTime(self, fTime):
        r"""
        setter for the totalTime of Simulation, equivalent to ``self.simulation.totalTime = fTime``
        """
        self.simulation.totalTime = fTime

    @simParameters.setter
    def simStepSize(self, stepsize):
        r"""
        setter for the stepSize of Simulation, equivalent to ``self.simulation.stepSize = stepsize``
        """
        self.simulation.stepSize = stepsize

    @simParameters.setter
    def simStepCount(self, num):
        r"""
        setter for the stepCount of Simulation, equivalent to ``self.simulation.stepCount = num``
        """
        self.simulation.stepCount = num

    @simParameters.setter
    def simSamples(self, num):
        r"""
        setter for the samples of Simulation, equivalent to ``self.simulation.samples = num``
        """
        self.simulation.samples = num

    @simParameters.setter
    def simCompute(self, func):
        r"""
        setter for the compute of Simulation, equivalent to ``self.simulation.compute = func``
        """
        self.simulation.compute = func

    @simParameters.setter
    def simDelStates(self, boolean):
        r"""
        setter for the delStates of Simulation, equivalent to ``self.simulation.delStates = boolean``
        """
        self.simulation.delStates = boolean

    @property
    def initialState(self):
        r"""
        Getter for the simulation initial state, equivalent to ``self.simulation.initialState``.
        This works by assuming that its setter/s makes sure that _stateBase__initialState.value is not None
        for single systems (if its state is set).
        """
        return self.simulation.initialState

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        r"""
        This method extends :meth:`delMatrices <paramBoundBase.delMatrices>` of :class:`computeBase` to also call
        :meth:`delMatrices <paramBoundBase.delMatrices>` on ``self.simulation``.
        """
        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            _exclude = self.simulation.delMatrices(_exclude)
        return _exclude

class stateBase(computeBase):
    r"""
    Contains attributes and methods for ``initialState`` and a boolean to determine whether to store or
    discard time-evolved states. Since, we can use :meth:`compute <computeBase.compute>` to compute quantities of
    interest at the run-time of simulation, we don't need to keep the states and can discard them to save memory.

    NOTE : This class branches the inheritance started by :class:`paramBoundBase` and extends to
    :class:`Simulation <qTools.classes.Simulation.Simulation>`.

    NOTE : All three attributes of this class (and all 4 of timeBase) are instances of :class:`_parameter`, so they have
    a corresponding property.
    """
    #: (**class attribute**) class label used in default naming
    label = 'stateBase'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__delStates', '__initialState', '__initialStateInput']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: This attribute is a :class:`~_parameter` and value stores the ``initialState`` matrix
        self.__initialState = _parameter()
        self.__initialStateInput = _parameter()
        r"""
        Input used in the creation of the ``initialState``, there are various ways to create ``initialState``, so its
        value changes depending on the case. This information is kept so that it can be used in cases where a new
        reconstruction of ``initialState`` is required, e.g. when system dimension is swept or changed.
        """
        self.__delStates = _parameter(classConfig['delStates'])
        r"""
        This boolean determines if we delete/discard (``True``) time-evolved states (to save memory) and keep only
        the ``initialState`` and ``currentState`` of the system. By default, it is ``False`` and states will be stored
        in the corresponding protocols ``qRes.states``.
        """
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def initialState(self):
        r"""
        The initialState property ``returns _stateBase__initialState.value`` if it is not ``None``. Otherwise, uses
        first element in its ``subSys`` dictionary values to create and assign its value. This assumes that, to be able
        to assign a state to a Simulation, it needs at least one quantum system in its ``subSys`` dictionary, and the
        subSys have method to create the state (``_createAstate``). This requirement, by default, is satisfied by the
        internally created Simulation objects that are attributes of quantum systems and protocols.

        Setter sets ``_stateBase__initialState.value`` matrix for ``self`` by using the first element of ``subSys``
        dictionary values.
        """

        if self._stateBase__initialState.value is None: # pylint: disable=no-member
            if isinstance(self._stateBase__initialState._bound, _parameter): # pylint: disable=protected-access
                # might seem redundant, but required to make sure that bound creates its initial state by calling the
                # _createAstate
                self._stateBase__initialState._value = self._timeBase__bound.initialState # pylint: disable=no-member
            else:
                self._stateBase__initialState.value = list(self.subSys.values())[0]._createAstate(self._initialStateInput) # pylint: disable=protected-access, no-member, line-too-long # noqa: E501
        return self._stateBase__initialState.value # pylint: disable=no-member

    @initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self._stateBase__initialStateInput.value = inp # pylint: disable=no-member
        self._stateBase__initialState.value = list(self.subSys.values())[0]._createAstate(inp) # pylint: disable=protected-access, no-member, line-too-long # noqa: E501

    @property
    def _initialStateInput(self):
        r"""
        ``returns _stateBase__initialStateInput.value``.
        """
        return self._stateBase__initialStateInput.value

    def getResultByNameOrAlias(self, name):
        r"""
        This method exists to enrich the terminology, it just ``returns super().getByNameOrAlias(name)``, which returns
        the object with the given `name`.
        See :meth:`getByNameOrAlias <qTools.classes.base.named.getByNameOrAlias>` for details.
        """
        return super().getByNameOrAlias(name)

    @property
    def delStates(self):
        r"""
        gets and sets ``_stateBase__delStates.value`` boolean
        """
        return self._stateBase__delStates.value

    @delStates.setter
    def delStates(self, boolean):
        self._stateBase__delStates.value = boolean

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        r"""
        This method extends :meth:`delMatrices <paramBoundBase.delMatrices>` to also set
        the ``_stateBase__initialState.value`` to ``None`` and del the old value.
        """
        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            oldMat = self._stateBase__initialState.value  # noqa: 841
            self._stateBase__initialState.value = None # pylint: disable=no-member, protected-access
            del oldMat
        return _exclude

class timeBase(stateBase):
    r"""
    Implements 3 basic time information, namely total time of simulation (``totalTime``), step size for
    each unitary (``stepSize``), and number of steps (``stepCount = totalTime/stepSize``). Additionally, one more
    parameter, namely, number of samples
    (``samples``) is introduced to be used with time-dependent Hamiltonian, where a continuous parameter
    is discretely changed at every ``stepSize`` and more than one ``samples`` are desired during the ``stepSize``.

    These 4 attributes are all :class:`_parameter <qTools.classes.computeBase._parameter>` instances and protected
    attributes, meaning they are modified by the corresponding properties. One other functionality of
    property is to create flexible use of these attributes. For example, not all 3 of ``stepSize``, ``totalTime``, and
    ``stepCount`` are need to be explicitly defined, any of these two would be sufficient, since the 3rd can be
    calculated using the two. So, property setters&getters also covers such cases. Another flexibility ensured by the
    properties is when ``_bound`` are broken.
    """
    #: (**class attribute**) class label used in default naming
    label = 'timeBase'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__totalTime', '__stepSize', '__samples', '__stepCount', '__bound']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: _parameter storing the total time of simulation
        self.__totalTime = _parameter()
        #: _parameter storing the step size of simulation
        self.__stepSize = _parameter()
        #: _parameter storing number of samples in each step, by default 1.
        self.__samples = _parameter(1)
        #: _parameter storing the number of steps, i.e totalTime/stepSize.
        self.__stepCount = _parameter()
        #: if bound to another object, meaning the _parameters of this gets their value from the others _parameters,
        #: this attribute is a reference to another. Else None.
        self.__bound = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def totalTime(self):
        r"""
        gets and sets ``_timeBase__totalTime.value``, and also sets the ``_timeBase__stepCount.value``
        conditioned on that ``stepSize`` is not ``None``. It also sets
        :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
        these, it sets ``_timeBase__stepSize._value`` to ``_timeBase__stepSize._bound._value``, if
        ``_timeBase__stepSize._bound`` is not ``None or False``. This is introduced to provide a flexible
        use of these parameters, such as not forcing to define at least 2 of 3 timeBase parameters, if it already
        has a ``_bound`` and can obtain the second one from the ``_bound``.
        """
        return self._timeBase__totalTime.value

    @totalTime.setter
    def totalTime(self, fTime):
        if self._timeBase__stepSize._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__stepSize._value = self._timeBase__stepSize._bound._value # pylint: disable=protected-access
        setAttrParam(self, '_timeBase__totalTime', fTime)
        if self.stepSize is not None:
            self._timeBase__stepCount.value = int((fTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot

    @property
    def stepCount(self):
        r"""
        gets and sets ``_timeBase__stepCount.value``. getter also try seting the ``totalTime`` if it is ``None``.
        Setter also sets ``_timeBase__stepSize.value`` conditioned on that ``totalTime`` is not ``None``. It also sets
        :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
        these, it sets ``_timeBase__totalTime._value`` to ``_timeBase__totalTime._bound._value``, if
        ``_timeBase__totalTime._bound`` is not ``None or False``. This is introduced to provide a flexible
        use of these parameters, such as not forcing to define at least 2 of 3 timeBase parameters, if it already
        has a ``_bound`` and can obtain the second one from the ``_bound``.
        """
        if self.totalTime is None:
            if not ((self.stepSize is None) and (self._timeBase__stepCount.value is None)):
                self._timeBase__totalTime.value = self._timeBase__stepCount.value * self.stepSize # pylint: disable=E0237

        try:
            self._timeBase__stepCount.value = int((self.totalTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot
        except:  # noqa: E722
            raise ValueError('?') # pylint: disable=raise-missing-from
        return self._timeBase__stepCount.value

    @stepCount.setter
    def stepCount(self, num):
        if self._timeBase__totalTime._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__totalTime._value = self._timeBase__totalTime._bound._value# pylint: disable=protected-access
        setAttrParam(self, '_timeBase__stepCount', num)
        if self.totalTime is not None:
            self._timeBase__stepSize.value = self.totalTime/num # pylint: disable=assigning-non-slot

    @property
    def stepSize(self):
        r"""
        gets and sets ``_timeBase__stepSize.value``, and also ``_timeBase__stepCount.value`` conditioned on that
        ``totalTime`` is not ``None``. It also sets
        :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
        these, it sets ``_timeBase__totalTime._value`` to ``_timeBase__totalTime._bound._value``, if
        ``_timeBase__totalTime._bound`` is not ``None or False``. This is introduced to provide a flexible
        use of these parameters, such as not forcing to define at least 2 of 3 timeBase parameters, if it already
        has a ``_bound`` and can obtain the second one from the ``_bound``.
        """
        return self._timeBase__stepSize.value

    @stepSize.setter
    def stepSize(self, stepsize):
        if self._timeBase__totalTime._bound not in (None, False):# pylint: disable=protected-access
            self._timeBase__totalTime._value = self._timeBase__totalTime._bound._value# pylint: disable=protected-access
        setAttrParam(self, '_timeBase__stepSize', stepsize)
        if self.totalTime is not None:
            self._timeBase__stepCount.value = int((self.totalTime//stepsize) + 1) # pylint: disable=assigning-non-slot

    @property
    def samples(self):
        r"""
        gets and sets ``_timeBase__samples.value`` and also sets
        :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``.
        """

        return self._timeBase__samples.value

    @samples.setter
    def samples(self, num):
        setAttrParam(self, '_timeBase__samples', num)

    def _copyVals(self, other, keys):
        r"""
        Method to copy the values for given attributes (as keys) from ``other`` to ``self``.
        """
        for key in keys:
            val = getattr(other, key)
            if val is not None:
                setattr(self, key, val)

    @staticmethod
    def _boundTree(osys, tree=None):
        r"""
        Creates a tree of bound instances starting from the given ``osys``. A primitive method used in debugging and to
        be improved.
        """
        if tree is None:
            tree = []
        bSys = osys._timeBase__bound
        if bSys is not None:
            tree.append(bSys)
            tree = bSys._boundTree(bSys, tree)
        return tree

    def _bound(self, other, # pylint: disable=dangerous-default-value
               params=['_stateBase__delStates', '_stateBase__initialState', '_stateBase__initialStateInput'],
               re=False):
        r"""
        This method is used internally at appropriate places to create bound between different simulation instances in
        the intended hierarchical order. For example, when a :class:`quantum system <qTools.classes.QSys.genericQSys>`
        is added to ``subSys`` of explicitly created :class:`Simulation <qTools.classes.Simulation.Simulation>`,
        The parameters of any :class:`protocol.simulation <qTools.classes.QPro.genericProtocol>` for that system will
        be bound to ``(quantum system).simulation`` which will be bound to explicitly created Simulation. This method
        creates such a bound between two ``Simulation`` objects, and it is used in appropriate places of the library.
        Such a bound is broken or not created at all, if a parameter is explicitly assigned for a protocol or system.

        NOTE : This method is intended purely for internal uses!

        Parameters
        ----------
        other : Simulation
            The other Simulation (or timeBase) class to bound the parameters of self
        re : bool, optional
            This boolean used (internally) to **re-bound** a simulation object to another one, by default False. So,
            re-calling this method to bound a simulation object to another will not work unless ``re=True``.
        param: List[str]
            This is a list of strings for attributes (which are also _parameter objects) other than time parameters, for
            which the same bound will be created. The difference between ``param`` and ``timeBase`` parameters is that
            the latter ones has a functional dependency to each other, meaning a break in one of them should
            appropriately be reflected to the others.
        """

        if self not in self._boundTree(osys=other): #pylint: disable=too-many-nested-blocks
            other._paramBoundBase__paramBound[self.name] = self
            self._timeBase__bound = other # pylint: disable=assigning-non-slot
            keys = ['_timeBase__stepSize', '_timeBase__totalTime', '_timeBase__stepCount']
            keysProp = ['stepSize', 'totalTime', 'stepCount']
            bounding = True
            for ind, key in enumerate(keys):
                if getattr(self, key)._bound is False: # pylint: disable=protected-access
                    if getattr(other, key)._value is not None: # pylint: disable=protected-access
                        setattr(self, keysProp[ind], getattr(self, key)._value) # pylint: disable=protected-access

                    if bounding:
                        for i, k in enumerate(keys):
                            if ((getattr(self, k)._bound is None) and # pylint: disable=protected-access # noqa: W504
                                    (getattr(other, k)._value is not None)): # pylint: disable=protected-access
                                setattr(self, keysProp[i], getattr(other, k)._value) # pylint: disable=protected-access
                                break
                        bounding = False

            for key in (*keys, *params, '_timeBase__samples'):
                try:
                    if ((getattr(self, key)._bound is None) or re): # pylint: disable=protected-access
                        getattr(self, key)._bound = getattr(other, key) # pylint: disable=protected-access
                except AttributeError:
                    print('not bounding', key)
