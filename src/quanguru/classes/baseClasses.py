r"""
    Contains some base classes.

    .. currentmodule:: quanguru.classes.baseClasses

    .. autosummary::

        updateBase
        paramBoundBase
        computeBase

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `updateBase`               |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |c|
      `paramBoundBase`           |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |x|
      `computeBase`              |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |x|
    =======================    ==================    ================   ===============

"""
from typing import Any, Callable, Dict, List, Union

from .exceptions import attrNotValWarn, raiseAttrType, checkCorType, checkNotVal
from .base import named, qBase, addDecorator, _recurseIfList, aliasDict
from .QRes import qResults
# pylint: disable = cyclic-import

class updateBase(qBase):
    r"""
    Base class for :class:`~_sweep` and :class:`~Update` classes, which are used in parameter sweeps and step updates in
    protocols, respectively.
    This class implements a default method to change the value of an attribute (``str`` of the attribute name is
    stored in ``self.key``) of the objects in the ``subSys`` dictionary.
    It can also sweep/update auxiliary dictionary by setting the ``aux`` boolean to ``True``.
    The default method can be changed to anything by pointing the ``function`` attribute to any other ``Callable``.
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
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: string for an attribute of the objects in ``subSys`` dictionary, used in getattr().
        self.__key: str = None
        #: attribute for custom sweep/update methods. Assigned to some default methods in child, and sweep/update
        #: methods can be customized by re-assigning this.
        self.__function: Callable = None
        #: boolean to switch from subSys attribute sweep/update (False) to auxiliary dictionary key sweep/update (True)
        self._aux: bool = checkCorType(kwargs.pop('_aux', False), bool, '_aux')
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def key(self) -> str:
        r"""
        Gets and sets the  _updateBase__key protected attribute
        """
        return self._updateBase__key

    @key.setter
    @raiseAttrType(str, attrPrintName='key')
    def key(self, keyStr: str) -> None:
        self._updateBase__key = keyStr # pylint: disable=assigning-non-slot

    @property
    def system(self) -> Union[List, named]:
        r"""
        system property wraps ``subSys`` dictionary to create a new terminology, it basically:

        gets subSys[0] if there is only one item in it, else  list(subSys.values())
        setter works exactly as :meth:`addSubSys <quanguru.classes.base.qBase.addSubSys>` method.
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
            self.auxDict[self._updateBase__key] = val

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
        checkNotVal(bound, self, 'Cannot bound an object to itself')
        checkCorType(bound, paramBoundBase, '_createParamBound')
        bound._named__setKwargs(**kwargs) # pylint: disable=no-member
        self._paramBoundBase__paramBound[bound.name] = bound
        return bound

    @_recurseIfList
    def _breakParamBound(self, bound: "paramBoundBase", _exclude=[]) -> None: # pylint: disable=dangerous-default-value
        r"""
        This method removes the given object from the ``__paramBound`` dictionary.
        """
        bound = checkCorType(self.getByNameOrAlias(bound), paramBoundBase, '_breakParamBound')
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
        kwargs.pop('qRes', None)
        #: This attribute is an instance of :class:`~qResults`, which is used to store simulation results and states.
        self.qRes: qResults = qResults(superSys=self, _internal=True, alias=self.name+"Results")
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

    def __compute(self, states, *args, **kwargs) -> None: # pylint: disable=dangerous-default-value
        r"""
        This is the actual compute function that is called in the time-evolution, it calls ``self.compute`` if it is a
        callable and does nothing otherwise.
        """
        if callable(self.compute):
            return self.compute(self, states, *args, **kwargs) # pylint: disable=not-callable
        return attrNotValWarn(self.compute, None, 'compute should be callable but '+str(type(self.compute))+'is given')

    def __calculate(self, where: str, *args, **kwargs) -> None:
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
            return meth(self, *args, **kwargs) # pylint: disable=not-callable
        return attrNotValWarn(meth, None, 'calculate'+where+' should be a callable but ' + str(type(meth)) + 'is given')

    @paramBoundBase.alias.setter
    def alias(self, ali: str) -> None:
        r"""
        Extends the alias setter to assign an alias (givenAlias + Results) to self.qRes as well.
        """
        named.alias.fset(self, ali) #pylint:disable=no-member
        if isinstance(ali, str):
            self.qRes.alias = ali + "Results"
        elif isinstance(ali, list):
            self.qRes.alias = [a+"Results" for a in ali if isinstance(a, str)]

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
        return self.qRes.states
        # stateList = list(self.qRes.states.values())
        # return stateList if len(list(self.qRes.states.values())) > 1 else stateList[0]
