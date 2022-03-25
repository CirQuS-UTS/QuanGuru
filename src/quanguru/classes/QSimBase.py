r"""
    Contains the _parameter class and the parent classes of the Simulation object.

    .. currentmodule:: quanguru.classes.QSimBase

    .. autosummary::

        _parameter

    .. autosummary::

        stateBase
        timeBase

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `_parameter`               |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |x|
      `stateBase`                |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |x|
      `timeBase`                 |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |x|
    =======================    ==================    ================   ===============

"""

from typing import Any, cast

from quanguru.classes.exceptions import checkNotVal
from .baseClasses import computeBase, paramBoundBase
from .tempConfig import classConfig


def setAttr(obj: paramBoundBase, attrStr: str, val: Any) -> None:
    r"""
    a customized setattr that changes the value (and _paramUpdated) if the new value is different than the old/existing.
    Especially useful for multi parameter sweeps (see :class:`~_sweep`).
    """
    oldVal = getattr(obj, attrStr)
    if val != oldVal:
        setattr(obj, attrStr, val)
        setattr(obj, '_paramUpdated', True)

def setAttrParam(obj: paramBoundBase, attrStr: str, val: Any) -> None:
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

    def __init__(self, value: Any = None, _bound: '_parameter' = None) -> None:
        #: the value to be wrapped
        self._value: Any = value #pylint:disable=unsubscriptable-object
        #: bounded _parameter object, self is not bounded to anything when this is None or any other object that does
        #: not have a ``value`` attribute. Assigned to False when a bound is broken (by updating the value).
        self._bound: '_parameter' = _bound

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

class stateBase(computeBase):
    r"""
    Contains attributes and methods for ``initialState`` and a boolean to determine whether to store or
    discard time-evolved states. Since, we can use :meth:`compute <computeBase.compute>` to compute quantities of
    interest at the run-time of simulation, we don't need to keep the states and can discard them to save memory.

    NOTE : This class branches the inheritance started by :class:`paramBoundBase` and extends to
    :class:`Simulation <quanguru.classes.Simulation.Simulation>`.

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

    __slots__ = ['__delStates', '__initialState', '__initialStateInput', '_initialStateSystem']

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
        self._initialStateSystem = None
        r"""
        This system will be used in the initial state creation, i.e. input will be passed to this systems createState
        function. If this is None, it fallbacks to self.superSys, and raises error if self.superSys is also None.
        """
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def initialStateSystem(self):
        if self._initialStateSystem is None:
            self._initialStateSystem=self.superSys if hasattr(self.superSys,'_createAstate') else self.superSys.superSys
        checkNotVal(self._initialStateSystem, None,
                    'Simulation initialStateSystem/superSys is needed for initial state creation')
        return self._initialStateSystem

    @initialStateSystem.setter
    def initialStateSystem(self, qSys):
        checkNotVal(hasattr(qSys, '_createAstate'), False,
                            f"{qSys.name} is not QuantumSystem, Simulation initialStateSystem should be QuantumSystem")
        setAttr(self, '_initialStateSystem', qSys)

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

        if ((self._stateBase__initialState.value is None) or
            (self._stateBase__initialState.value.shape != self.initialStateSystem.dimension)): # pylint: disable=no-member
            # TODO initial state creation has a bug when it relies on .dimension of a protocol
            #  after re-structuring the protocol, this should no longer rely of .dimension of protocol,
            #  which returns 1 and causes this to evaluate everytime anyway.
            #  labels: bug, enhancement
            if isinstance(self._stateBase__initialState._bound, _parameter): # pylint: disable=protected-access
                # might seem redundant, but required to make sure that bound creates its initial state by calling the
                # _createAstate
                self._stateBase__initialState._value = self._timeBase__bound.initialState # pylint: disable=no-member
            else:
                self._stateBase__initialState.value = self.initialStateSystem._createAstate(self._initialStateInput) # pylint: disable=protected-access, no-member, line-too-long # noqa: E501
        return self._stateBase__initialState.value # pylint: disable=no-member

    @initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self._stateBase__initialStateInput.value = inp # pylint: disable=no-member
        self._stateBase__initialState.value = self.initialStateSystem._createAstate(inp) # pylint: disable=protected-access, no-member, line-too-long # noqa: E501

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
        See :meth:`getByNameOrAlias <quanguru.classes.base.named.getByNameOrAlias>` for details.
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
            self._stateBase__initialState._value = None # pylint: disable=no-member, protected-access
            del oldMat
        return _exclude

class timeBase(stateBase):
    r"""
    Implements 3 basic time information, namely total time of simulation (``totalTime``), step size for
    each unitary (``stepSize``), and number of steps (``stepCount = totalTime/stepSize``). Additionally, one more
    parameter, namely, number of samples
    (``samples``) is introduced to be used with time-dependent Hamiltonian, where a continuous parameter
    is discretely changed at every ``stepSize`` and more than one ``samples`` are desired during the ``stepSize``.

    These 4 attributes are all :class:`_parameter <quanguru.classes.computeBase._parameter>` instances and protected
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
        :meth:`_paramUpdated <quanguru.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
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
        :meth:`_paramUpdated <quanguru.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
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
        :meth:`_paramUpdated <quanguru.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
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
        :meth:`_paramUpdated <quanguru.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``.
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
        the intended hierarchical order. For example, when a :class:`quantum system <quanguru.classes.QSys.genericQSys>`
        is added to ``subSys`` of explicitly created :class:`Simulation <quanguru.classes.Simulation.Simulation>`,
        The parameters of any :class:`protocol.simulation <quanguru.classes.QPro.genericProtocol>` for that system will
        be bound to ``(quantum system).simulation`` which will be bound to explicitly created Simulation. This method
        creates such a bound between two ``Simulation`` objects, and it is used in appropriate places of the library.
        Such a bound is broken or not created at all, if a parameter is explicitly assigned for a protocol or system.

        - if self _parameter attributes have bound False (meaning set a value before)

            - copies the value from other, if value in other is not None.
            - is any self _parameter bound is None, and the same value in other is not, sets it and breaks the loop

        - tries bounding if bound is None

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

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        if self not in _exclude:
            _exclude = super().delMatrices(_exclude=_exclude)
            if isinstance(self._timeBase__bound, timeBase):
                _exclude = self._timeBase__bound.delMatrices(_exclude=_exclude)
        return _exclude
