r"""
    Contains two main base classes (for naming and sub/superSys) and their helper classes, functions, decorators.

    .. currentmodule:: quanguru.classes.base

    .. autosummary::
        named
        qBase

    .. autosummary::
        aliasClass
        keySearch
        aliasDict

    .. autosummary::
        _auxiliaryClass
        _recurseIfList
        addDecorator

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `named`                    |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |c|
      `qBase`                    |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |x|
      `aliasClass`               |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |c|
      `keySearch`                |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |c|
      `aliasDict`                |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |c|
      `_auxiliaryClass`          |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_recurseIfList`           |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `addDecorator`             |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============

"""

from functools import wraps
import inspect

import warnings
import weakref
from itertools import chain
from typing import Callable, Hashable, Dict, Optional, List, Union, Any, Tuple, Mapping

from .exceptions import raiseAttrType, checkNotVal, checkCorType

__all__ = [
    'qBase', 'named'
]

def _recurseIfList(func: Callable) -> Callable:
    r"""
    a decorator to call the decorated method recursively for every element of a list/tuple input (and possibly exclude
    certain objects). It is used in various places of the library (exclude is useful/used in some of them to avoid
    infinite recursive calls).
    """
    @wraps(func) # needed for the func.__name__
    def recurse(obj, inp, _exclude=[], **kwargs): # pylint: disable=dangerous-default-value
        r = None # removing this fails test_paramBoundBaseCreateBreakBoundWithList, but only when I run all the tests
        # could not figure out why.
        if isinstance(inp, (list, tuple)):
            for s in inp:
                r = recurse(obj, s, _exclude=_exclude, **kwargs)
        else:
            if "_exclude" in inspect.getfullargspec(func).args:
                r = func(obj, inp, _exclude=_exclude, **kwargs)
            else:
                r = func(obj, inp, **kwargs)
        return r
    return recurse

class aliasClass:
    r"""
    aliasClass is introduced for the naming functionality of the qObjects. It is created to be used as the name
    attribute of qObjects and to work with the extended dictionary :class:`~aliasDict`.
    The default name of qObjects is assigned to be ``__name`` attribute, and the user assigned aliases for a qObject
    are stored in the ``__alias`` list. The string representation and hash value of an aliasClass objects is obtained
    from its name.
    """

    __slots__ = ["__name", "__alias"]

    def __init__(self, name: Optional[str] = None, alias: List[Any] = list) -> None: #pylint:disable=unsubscriptable-object
        checkCorType(name, (str, type(None)), 'name')
        self.__name: Optional[str] = name #pylint:disable=unsubscriptable-object
        r"""
        Protected name attribute of an aliasClass object, set&get through the :py:attr:`~aliasClass.name` property.
        Default is ``None``. It can be set to any string (which cannot be changed later, unless directly overwritting
        ``self._aliasClass__name``).
        """
        #: list of aliases of an aliasClass objects, set&get through the :py:attr:`~aliasClass.alias` property
        self.__alias: List[Any] = [] if isinstance(alias, type) else alias if isinstance(alias, list) else [alias]

    @property
    def name(self) -> Union[str, None]: #pylint:disable=unsubscriptable-object
        r"""
        Getter of the name property, returns ``self.__name``.

        Setter of the name property, sets ``self.__name`` to given ``name`` provided that the ``self.__name is None``
        and the given ``name`` is a string. This means that the name can only be a string and cannot be changed
        once set. Unless, of course, directly overwriting the protected attribute.

        Raises
        ------
        TypeError
            Raised if given name is not string
        """
        return self._aliasClass__name #pylint:disable = no-member

    @name.setter
    @raiseAttrType(str, attrPrintName='name')
    def name(self, name: str) -> None:
        if self._aliasClass__name is None: #pylint:disable = no-member
            self._aliasClass__name = name  #pylint:disable = no-member, assigning-non-slot
        else:
            warnings.warn("name cannot be changed")

    @property
    def alias(self) -> List:
        r"""
        Getter of the alias property, returns the alias list.

        Setter of the alias property, adds a new alias for the aliasClass object (if the given alias is not already
        in the list).
        """
        return self._aliasClass__alias #pylint:disable = no-member

    @alias.setter
    @_recurseIfList
    def alias(self, ali: Any) -> None:
        self._aliasClass__alias.append(ali) #pylint:disable = no-member

    def __members(self) -> Tuple:
        r"""
        :returns: a tuple containing the name and all aliases
        """
        return (self.name, *self._aliasClass__alias) #pylint:disable = no-member

    def _allStringSum(self) -> str:
        r"""
        Adds and returns all the strings in members.

        This is currently used with the saveCSV method to add this string to file name
        """
        return "".join(s for s in self._aliasClass__members() if isinstance(s, str))

    def __repr__(self) -> str:
        r"""
        representation of the object is equal to ``repr(self.name)``.
        """
        return repr(self.name)

    def __str__(self) -> str:
        r"""
        string representation of the object is its name
        """
        return self.name

    @raiseAttrType(str)
    def __radd__(self, other):
        return other + self.name

    @raiseAttrType(str)
    def __add__(self, other):
        return self.name + other

    def __eq__(self, other: Union["aliasClass", str]) -> bool:  #pylint:disable=unsubscriptable-object
        r"""
        Equality of any two aliasClass objects (or an aliasClass object to a string) is determined by comparing their
        names and all
        their aliases (or to given string), if at least one of them are the same (or the same as the given string),
        aliasClass objects (or the aliasClass object and the given string) are considereed to be equal.

        Parameters
        ----------
        other : Union[aliasClass, str]
            aliasClass object or string to check the equality with self
        """
        if type(other) is type(self):
            return any(it in self._aliasClass__members() for it in other._aliasClass__members())#pylint:disable = no-member
        return any(it == other for it in self._aliasClass__members())                #pylint:disable = no-member

    def __hash__(self) -> int:
        r"""
        Hash value of an aliasClass object is equal to hash of its name.
        """
        return hash(self.name)

def keySearch(obj: Dict, k: Any) -> Hashable:
    r"""
    Method to find a key or any other obj equal to the key in a ``dictionary.keys()``. This method is used in
    :class:`~aliasDict` class (extending ``dict`` class) to find the actual key when using :class:`~aliasClass` as the
    key, which returns equal for a specific
    string (its name) or any other string in its list of aliases.

    Parameters
    ----------
    obj : Dict
        The dictionary to search the key
    k : Any
        The key to search in the dictionary (obj)


    :returns: the key, if the key itself or no equality is found in the dictionary keys. returns the equal key from the
              dictionary, if an equal key is found in the dictionary.
    """
    # NOTE this returns the first match, meaning there can be more than one equality. Example, two string keys in the
    # dictionary and the given key is an aliasClass object with these keys in its members (tuple of its name and
    # aliases)
    if k not in obj.keys():
        for key in obj.keys():
            if k == key:
                k = key
                break
    return k

class aliasDict(dict):
    r"""
    Extending the dictionary class to treat the keys satisfying ``key1 == keys2`` as the same key. This functionality is
    implemented to use
    :class:`~aliasClass` objects as keys and to get the value by using the aliasClass object itself, its name, or any of
    its aliases as the key.

    NOTE no explicit tests for most of the extended methods, be careful in modifications.
    """
    def __getitem__(self, k: Hashable) -> Any:
        r"""
        Gets the value from the dictionary for a given key or any of the keys that is equal to the given key.
        This enables to get a value using an :class:`~aliasClass` object itself, its name, or any any of it aliases.
        """
        k = keySearch(self, k)
        return super().__getitem__(k)

    def get(self, key: Hashable, default: Optional[Any] = None) -> Any: #pylint:disable=unsubscriptable-object
        r"""
        Modified get method to be compatible with extended :meth:`~__getitem__` method.
        """
        try:
            return self.__getitem__(key)
        except: #pylint:disable=bare-except  # noqa: E722
            return default

    def __setitem__(self, k: Hashable, v: Any) -> None:
        r"""
        Updates the value of a key in the dictionary, if the given key exists or any of the keys is equal to given key,
        otherwise creates an item (ie key:value pair) in the dictionary.
        This enables to set a value using an :class:`~aliasClass` object itself, its name, or any any of it aliases.
        """
        # might need to overwrite update and setdefault
        k = keySearch(self, k)
        super().__setitem__(k, v)

    def __delitem__(self, k: Hashable) -> None:
        r"""
        Deletes the item for a given key or any of the keys that is equal to the given key.
        This enables to delete a value using an :class:`~aliasClass` object itself, its name, or any any of it aliases.
        """
        k = keySearch(self, k)
        super().__delitem__(k)

    def __contains__(self, o: Hashable) -> bool:
        r"""
        Returns ``True`` if the key or any object equal to the key exists.
        This enables to ``return True`` for an :class:`~aliasClass` object itself, its name, or any of it aliases.
        """
        return super().__contains__(keySearch(self, o))

    def update(self, mapping: Optional[Mapping] = (), **kwargs) -> None:  #pylint:disable=unsubscriptable-object
        r"""
        update method compatible with the extended get/set methods.
        """
        if hasattr(mapping, "keys"):
            for k in mapping:
                self[k] = mapping[k]
        else:
            for k, v in mapping:
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def setdefault(self, __key: Hashable, __default: Optional[Any] = None) -> Any:
        r"""
        Modified setdefault method to be compatible with extended :meth:`~__setitem__` & :meth:`~__getitem__` methods.
        """
        if not self.__contains__(__key):
            self.__setitem__(__key, __default)
        return self.__getitem__(__key)

    def pop(self, k: Hashable, *args) -> Any:
        r"""
        pop method compatible with the extended methods.
        """
        k = keySearch(self, k)
        return super().pop(k, *args)

    def copy(self) -> "aliasDict":
        r"""
        copy method to make sure the type is correct.
        """
        return type(self)(self)

class named:
    r"""
    Implements a name attribute and a naming standard. It is inhereted by all the other qObjects so that
    they have unique default names, and users are able to assign aliases for any object. It uses the
    :class:`~aliasClass` for its name attribute to enable this.

    Default naming is ``(_)class.label (same as class name) + number of instances created in a session``.
    The optional _ in the name is to distinguish between the objects created internally which is not trivially known
    by the user. The objects explicitly created by the user does not have an underscore in their names.
    There are 4 class attribute to achieve these, 1 the label and 3 for keeping number of (internal, external, and
    total number of) instances.
    One last counter is the total number of instances of the classes inherited from named.
    """
    #: (**class attribute**) class label used in default naming
    label: str = 'named'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    #: (**class attribute**) total number of instances including named and all the child classes
    _totalNumberOfInst: int = 0
    #: (**class attribute**) a weakValue dictionary to store a weakref to every instance.
    #: This is used to reach any instance by its name or
    #: alias using the :class:`getByName` method
    #: _allInstacesDict = weakref.WeakValueDictionary() (could not pickle, so, for now, uses aliasDict which
    #: has problems with garbage collection in jupyter sessions)
    _allInstacesDict = aliasDict()

    __slots__ = ["__name", "_internal", "__weakref__", "_allInstaces"]

    @classmethod
    def _findInSlots(cls, k):
        if hasattr(cls, "__slots__"):
            if k in cls.__slots__:
                k =  "_" + cls.__name__
            elif cls.__base__ != object:
                k = cls.__base__._findInSlots(k) # pylint: disable=no-member,protected-access
        return k

    def __getstate__(self):
        for k, v in self._allInstaces.items(): # pylint: disable=protected-access
            if ((not isinstance(v, named)) and (v is not None)):
                self._allInstaces[k] = v() # pylint: disable=protected-access
        state = {}
        slots = chain.from_iterable(getattr(cls, '__slots__', []) for cls in self.__class__.__mro__)
        for k in slots:
            if k == '__weakref__':
                continue

            if (k.startswith("__") and (not k.endswith("__"))):
                k = self._findInSlots(k) + k
                state[k] = getattr(self, k)
            else:
                state[k] = getattr(self, k)
        return state

    def __setstate__(self, state):
        for slot in state:
            setattr(self, slot, state[slot])

        for k, v in self._allInstaces.items(): # pylint: disable=protected-access
            if isinstance(v, named):
                self._allInstaces[k] = weakref.ref(v, None) # pylint: disable=protected-access

    def __init__(self, **kwargs) -> None:
        #: boolean to distinguish internally and explicitly created instances.
        self._internal: bool = checkCorType(kwargs.pop('_internal', False), bool, '_internal')
        super().__init__()
        self._incrementInstances()
        #: protected name attribute is an instance of :class:`~named` class
        self.__name: aliasClass = aliasClass(name=self._named__namer())
        self._named__setKwargs(**kwargs)
        named._allInstacesDict[self.name] = weakref.ref(self, None)
        #: used in :meth:`~named.getByNameOrAlias` to properly pickle and reach updated objects during multi-processing
        self._allInstaces = named._allInstacesDict

    def __str__(self) -> str:
        r"""
        string representation of the object is the default name
        """
        return f'{self.name}'

    def getByNameOrAlias(self, name: Union[str, aliasClass]) -> "named": #pylint:disable=unsubscriptable-object
        r"""
        Returns a reference for an object using its name or any alias.

        Raises ValueError if it cannot find any object for the given name (or alias).
        """
        if isinstance(name, named):
            return name
        obj = checkNotVal(self._allInstaces.get(name), None,
                           "No object with the given name/alias is found!")
        return obj if isinstance(obj, named) else obj()

    def _incrementInstances(self) -> None:
        r"""
        Method used inside __init__ to increase internal/external and total number of instances.
        """
        named._totalNumberOfInst += 1
        self.__class__._instances += 1
        if self._internal is False:
            self.__class__._externalInstances += 1
        elif self._internal is True:
            self.__class__._internalInstances += 1

    def __namer(self) -> str:
        r"""
        Generates the default names.

        :returns: the default name
        """
        if self._internal is False:
            name = self.clsLabel() + str(self.clsInstances(self._internal))
        else:
            name = '_' + self.clsLabel() + str(self.clsInstances(self._internal))
        return name

    @property
    def name(self) -> aliasClass:
        r"""
        Getter of the name property  ``returns __name`` protected attribute. There is no setter, names are not allowed
        to be changed but can assign an alias.
        """
        return self._named__name

    @property
    def alias(self) -> List:
        r"""
        alias property gets the list of aliases.

        Sets (adds/extends into the list) alias (single/list of alias). Does not allow duplicate alias.
        """
        return self._named__name.alias

    @alias.setter
    @_recurseIfList
    def alias(self, ali: str) -> None:
        for k, v in self._allInstacesDict.items():
            wv = v if not isinstance(v, weakref.ReferenceType) else v()
            checkNotVal((k == ali) and (wv != self), True,
                         f"Given alias ({ali}) already exist and is assigned to: {k.name}")
        self._named__name.alias = ali

    @classmethod
    def clsLabel(cls) -> str:
        r"""
        Returns the class label.
        """
        return cls.label

    @classmethod
    def clsInstances(cls, _internal: Optional[bool] = None) -> int: #pylint:disable=unsubscriptable-object
        r"""
        This class method **returns** the number of instances:

            1. Total number, ``if _internal is None``
            2. internal, ``if _internal is True``
            3. external, ``if _internal is False``
        """
        if _internal is None:
            insCount = cls._instances
        elif _internal is True:
            insCount = cls._internalInstances
        elif _internal is False:
            insCount = cls._externalInstances
        return insCount

    @classmethod
    def _resetAllSubProc(cls):
        cls._externalInstances = 0 # pylint:disable=protected-access
        cls._internalInstances = 0 # pylint:disable=protected-access
        cls._instances = 0 # pylint:disable=protected-access
        for otherCLS in cls.__subclasses__():
            otherCLS._resetAllSubProc() # pylint:disable=protected-access

    @classmethod
    def _resetAll(cls) -> None:
        r"""
        Resets the counters and empties the weakref dictionary. Goal is to make this an equivalent to restarting a
        script or notebook.
        """
        named._totalNumberOfInst = 0
        named._allInstacesDict = aliasDict() # pylint:disable=protected-access
        named._resetAllSubProc() # pylint:disable=protected-access
        #self.__class__._allInstacesDict = weakref.WeakValueDictionary() # pylint:disable=protected-access

    def __setKwargs(self, **kwargs) -> None:
        r"""
        Method to set the attributes of the object from the given keywords and values.
        It is introduced to be used while instantiation of the object so that the protected attributes are set through
        the correspoding properties.

        Parameters
        ----------
        kwargs : Any
            Any attribute from the __slots__ (should take name-mangling into account, if used by a child class) or
            the name of corresponding property with an appropriate value type.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

class _auxiliaryClass:#pylint:disable=too-few-public-methods
    r"""
    an auxiliary class used to instantiate a dummy object for the :attr:`~qBase._auxiliaryObj` attribute.
    """
    def __init__(self) -> None:
        self.name = 'auxObj'
        super().__init__()

    def _named__setKwargs(self, **kwargs) -> None: #pylint:disable=invalid-name
        r"""
        Method to set the attributes of the object from the given keywords and values.
        It is introduced to be used while instantiation of the object so that the protected attributes are set through
        the correspoding properties.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

def addDecorator(addFunction):
    r"""
    A recursive decorator for methods like addSubSys which add items into dictionaries (eg. subSys dictionary).

    It is initially created to be used with :attr:`~qBase.subSys` dictionary of
    :class:`~qBase` class, and the idea is to cover possible misuse of
    :meth:`add <qBase.addSubSys>`/:meth:`create <qBase.createSubSys>`
    `subSys` methods (while also creating flexibility).

    For example,
    if, instead of an instance, the class itself is given to :meth:`addSubSys <qBase.addSubSys>` method, this
    decorator creates a new instance and includes the new instance to the dictionary.
    This also enables the flexible use
    of :meth:`addSubSys <qBase.addSubSys>` as replacement for :meth:`createSubSys <qBase.createSubSys>`.

    The wrapper is also decorated with the :meth:`~_recurseIfList` to make it recursive for list/tuple inputs.

    This decorator is also used for
    :meth:`_createParamBound <quanguru.classes.computeBase.paramBoundBase._createParamBound>` and
    :meth:`_breakParamBound <quanguru.classes.computeBase.paramBoundBase._breakParamBound>` methods for
    :attr:`_paramBound <quanguru.classes.computeBase.paramBoundBase._paramBound>` dictionary of
    :class:`paramBoundBase <quanguru.classes.computeBase.paramBoundBase>` class.

    1. If the `input (inp)` is an instance of :class:`~named`, it calls the `addFunction`
    (the decorated method that does the actual adding) and its added into the relevant dictionary.

    Other input cases covered by this decorator are

        2. If the input is a `string`, i.e. name/alias of an `instance`: finds the object from the
           :attr:`instNames <named._allInstacesDict>` dict and calls the `addFunction`.
        3. If the input is a `class`, creates an instance of the `class` (has to be a child-class of :class:`~named` )
           and makes a recursive call (which will trigger 1).
        4. If the input is a `list` or `tuple`: makes a recursive call, which is handled by the :meth:`~_recurseIfList``
           to iterate over every element of the given iterable, meaning anything in this
           list from 1. to 4. may be trigerred again depending on the value of the element in the iterable.
           (this can be combined with dict type to create nested dictionaries)
        5. raises an error if the object to be added is not an instance of :class:`~named`.
    """
    @wraps(addFunction)
    @_recurseIfList
    def wrapper(obj, inp, **kwargs):
        if isinstance(inp, (named, _auxiliaryClass)):
            inp = addFunction(obj, inp, **kwargs)
        elif isinstance(inp, (str, aliasClass)):
            inp = addFunction(obj, obj.getByNameOrAlias(inp), **kwargs) # pylint:disable=protected-access
        elif inp.__class__ is type:
            inp = wrapper(obj, inp(), **kwargs)
        elif isinstance(inp, (list, tuple)):
            inp = wrapper(obj, inp, **kwargs)
        else:
            raise TypeError("Add function does not support " + f"{inp.__class__} types")
        return inp
    return wrapper

class qBase(named):
    r"""
    Implements the sub/super-system attributes, auxiliary object and dictionary, and copy method.
    """
    #: (**class attribute**) class label used in default naming
    label: str = 'qBase'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    #: (**class attribute**) aux dictionary to store auxiliary things as items to reach from any instance
    _auxiliaryDict: Dict = {}
    #: (**class attribute**) aux object to store auxiliary things as attributes to reach from any instance
    _auxiliaryObj: _auxiliaryClass = _auxiliaryClass()

    __slots__ = ['__superSys', '__subSys', '__auxDict', '__auxObj']

    def __init__(self, **kwargs) -> None:
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: protected attribute for super system property
        self.__superSys: Any = None
        #: protected attribute for sub-system dictionary
        self.__subSys: Dict = aliasDict()
        #: attribute for the class attribute _auxiliary (this is required due to pickling in multi-processing)
        self.__auxDict = qBase._auxiliaryDict
        #: attribute for the class attribute _auxiliaryObj (this is required due to pickling in multi-processing)
        self.__auxObj = qBase._auxiliaryObj
        self._named__setKwargs(**kwargs) # pylint:disable=no-member

    @property
    def auxDict(self) -> Dict:
        r"""
        property to get and set auxiliary items into auxiliary dictionary. The setter updates the existing dictionary
        (instead of an single element into the existing dictionary) with a given one, ie. adds key:value pair for the
        non-existing keys and changes the value for existing keys.
        """
        return self._qBase__auxDict

    @auxDict.setter
    def auxDict(self, dictionary: Dict) -> None:
        self._qBase__auxDict.update(dictionary)

    @property
    def auxObj(self) -> _auxiliaryClass:
        r"""
        property to reach and set auxiliary attributes into auxiliary object
        """
        return self._qBase__auxObj

    @property
    def superSys(self) -> Any:
        r"""
        superSys property get/sets __superSys protected attribute
        """
        return self._qBase__superSys

    @superSys.setter
    def superSys(self, supSys: Any) -> None:
        setattr(self, '_qBase__superSys', supSys)

    @property
    def subSys(self) -> Dict:
        r"""
        subSys property gets the subSystem dictionary.

        Setter resets the existing dictionary and adds the given object/s to ``__subSys`` dictionary.
        It calls the :meth:`addSubSys <qBase.addSubSys>`,
        so it can used to add a single object, `list/tuple` of objects, by giving the name of the
        system, or giving class name to add a new instance of that class. Be aware that the setter resets the existing.
        """
        return self._qBase__subSys

    @subSys.setter
    def subSys(self, subS: Any) -> None:
        self.resetSubSys()
        self.addSubSys(subS)

    @addDecorator
    def addSubSys(self, subSys: named, **kwargs) -> named:
        r"""
        Adds sub-system/s into subSys dictionary and works with instances, their name/alias, class themselves (creates
        an instance and adds), and list/tuple containing any combination of these.
        """
        # TODO add examples for addSubSys
        #  and link this to a tutorial
        subSys._named__setKwargs(**kwargs) # pylint: disable=W0212
        self._qBase__subSys[subSys.name] = subSys
        return subSys

    def createSubSys(self, subSysClass: Any, **kwargs) -> named:
        r"""
        Simply calls and returns the :meth:`~qBase.addSubSys` method, which is decorated to also cover creation.
        """
        return self.addSubSys(subSysClass, **kwargs)

    @_recurseIfList
    def _removeSubSysExc(self, subSys: Any, _exclude=[]) -> None: # pylint: disable=dangerous-default-value
        r"""
        Internal method that actually removes the sub-system, the removeSubSys is a wrapper around this function.
        This is introduced to avoid users interaction with _exclude, which needs to be empty for each removeSubSys call.
        """
        subSys = self.getByNameOrAlias(subSys)
        checkCorType(subSys, (named, _auxiliaryClass), 'removeSubSys')
        self.subSys.pop(subSys.name)

    @_recurseIfList
    def removeSubSys(self, subSys: Any) -> None: # pylint: disable=dangerous-default-value
        r"""
        Removes an object from the subSys dictionary and works with the object itself, its name, or any alias. Will
        raise regular keyError if the object is not in the dictionary, or typeError if the object is not an instance of
        named class.
        """
        self._removeSubSysExc(subSys, _exclude=[])

    def resetSubSys(self) -> None:
        r"""
        clear() the subSys dictionary.
        """
        self._qBase__subSys.clear()

    def copy(self, **kwargs) -> "qBase":
        r"""
        Creates an `empty` copy of `self`. This method is introduced here to be extended in child class.
        In here, it ** does not copy ** the object, but creates a new object of the same class and sets the given kwargs
        """
        sysClass = self.__class__
        return sysClass(**kwargs)
