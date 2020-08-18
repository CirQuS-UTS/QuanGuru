"""
    This module contains ``qUniversal`` and ``extendedList`` classes, and ``checkClass`` decorator.

    .. currentmodule:: qTools.classes.base

    .. autosummary::
        :toctree: ../docs/source

        qUniversal
        extendedList
        checkClass

    Classes
    -------
    | :class:`qUniversal` : This class is inhereted by (almost) all the other classes in this library.
    | :class:`extendedList` : This class extends the built-in class ``list``. It is introduced to be used with
     :meth:`toBeSaved <qUniversal.toBeSaved>` lists.

    Decorators
    ----------
    | :func:`checkClass` :
"""

from functools import wraps
from typing import Dict, List
from collections import OrderedDict

__all__ = [
    'qUniversal'
]

def checkClass(classOf):
    """
    This is a **decorator with arguments and a recursive wrapper**, and it was initially created to be used with
    :attr:`~qUniversal.subSys` dictionary of :class:`qUniversal` class.

    Parameters
    ----------
    classOf : str
        name of a class


    This decorater was initially created to be used with :attr:`~qUniversal.subSys` dictionary of
    :class:`qUniversal` (`classOf`) class, and the idea is to cover possible misuse of
    :meth:`add <qUniversal.addSubSys>`/:meth:`create <qUniversal.createSubSys>`/:meth:`remove <qUniversal.removeSubSys>`
    `subSys` methods (while also creating flexibility). For example,
    if  the class itself is given, instead of an instance, to :meth:`addSubSys <qUniversal.addSubSys>` method, this
    decorator creates a new instance and includes the new instance to the dictionary. This also enables the flexible use
    of :meth:`addSubSys <qUniversal.addSubSys>` as :meth:`createSubSys <qUniversal.createSubSys>`. The wrapper covers
    some other scenarios like giving a ``list`` of instances to be included etc. This decorator is also used for
    :meth:`_createParamBound <qTools.classes.computeBase.paramBoundBase._createParamBound>` and
    :meth:`_breakParamBound <qTools.classes.computeBase.paramBoundBase._breakParamBound>` methods for
    :attr:`_paramBound <qTools.classes.computeBase.paramBoundBase._paramBound>` dictionary of
    :class:`paramBoundBase <qTools.classes.computeBase.paramBoundBase>` class.

    **Note** : The wrapper of this decorator assumes that the input (`inp`) to the decorated method is an instance
    of :class:`qUniversal` or :class:`its child classes`. `classOf` argument is used for this purpose. It is
    ``'qUniversal'`` in the most general case, but any other class in the inheritance tree can be used to impose a
    further restriction (as in :attr:`_paramBound <qTools.classes.computeBase.paramBoundBase._paramBound>`).

    The wrapper works by first finding the intended class by using its name (`classOf`) with ``global()``. Then,

    0. If the `input (inp)` is an instance of this class (`classOf`), it calls the `addRemoveFunction`
    (the decorated method, which does the actual adding/removing).

    Other input cases covered by this decorator are

        1. input is a `string`, and it can be

            - name of an `instance` : finds the object from the :attr:`instNames <qUniversal.instNames>` dict
              and makes a recursive call (which will trigger 0., if the object is an instance of `classOf` or `its
              child classes`).
            - name of a `class` : creates an instance of the `class` (which has to be a child-class of `classOf`)
              and makes a recursive call (which will trigger 0., if the `class` is a child-class of `classOf`).

        2. input is a `dictionary`: keys are **not** used currently, but each value in the dictionary is used in a
           recursive call, meaning anything in this list from 0. to 5. may be trigerred again depending on the value
           type.
        3. input is a `class`: creates an instance of the `class` (which has to be a child-class of `classOf`)
           and makes a recursive call (which will trigger 0., if the `class` is a child-class of `classOf`).
        4. input is other types of `iterable`: call itself for every element of the iterable, meaning anything in this
           list from 0. to 5. may be trigerred again depending on the value type.

    TODO : should raise an error if,

            0. the object is not an instance of `classOf` (or `its child-classes`)
            1. given name

                - is in `instNames`, but the object is not an instance of `classOf` or `its child-classes`.
                - corresponds to a class that is not `classOf` or `its child class`.
                - does not correspond to a key in `instNames` or any `class`.

            2. Other cases will raise a relevant error for values of the `dictionary`.
            3. given class is not `classOf` or `its child class`.
            4. Other cases will raise a relevant error for values of the `iterable`.

    """

    def addDecorator(addFunction):
        @wraps(addFunction)
        def wrapper(obj, inp, **kwargs):
            clsDecoArg = globals()[classOf]
            if isinstance(inp, clsDecoArg):
                addFunction(obj, inp, **kwargs)
            elif isinstance(inp, _auxiliaryClass):
                obj._qUniversal__subSys[inp.name] = inp
            elif isinstance(inp, str):
                if inp in clsDecoArg.instNames.keys():
                    inp = wrapper(obj, clsDecoArg.instNames[inp], **kwargs)
                else:
                    clsInput = globals()[inp]
                    inp = wrapper(obj, clsInput, **kwargs)
            elif isinstance(inp, dict):
                for sys in inp.values():
                    # what to do with the keys?
                    inp = wrapper(obj, sys, **kwargs)
            elif inp.__class__ is type:
                newSys = inp()
                inp = wrapper(obj, newSys, **kwargs)
            else:
                for sys in inp:
                    inp = wrapper(obj, sys, **kwargs)
            return inp
        return wrapper
    return addDecorator

def _recurseIfList(func):
    def recurse(obj, sys, _exclude=[]): # pylint: disable=dangerous-default-value
        if isinstance(sys, list):
            for s in sys:
                r = recurse(obj, s, _exclude=_exclude)
        else:
            try:
                r = func(obj, sys, _exclude=_exclude)
            except TypeError:
                r = func(obj, sys)
        return r
    return recurse

class extendedList(list):
    """
    This class extends the built-in ``list`` class. It is introduced to be used with
    :attr:`toBeSaved <qUniversal.toBeSaved>` lists of every class that inherits from :class:`qUniversal`.
    These lists contain the keys for `the attributes to be saved` (currently into a `txt and hdf5 attributes`).
    :attr:`toBeSaved <qUniversal.toBeSaved>` is a class attribute and extending it through the inheritance tree is
    achieved by `extendedCopy` method of this class.

    Current saving methods are going to be improved, so, in future, this class might not be needed.
    """

    def extendedCopy(self, iterable):
        """
        This methods returns a new instance of extendedList by concatenating the ``self`` with a given ``iterable``.

        Parameters
        ----------
        iterable : list, tuple, or extendedList
            Existing iterable is extended by this.


        :returns: A new instance of extendedList
        """

        baseList = extendedList()
        for it in self:
            baseList.append(it)
        for exIt in iterable:
            baseList.append(exIt)
        return baseList


class _auxiliaryClass:#pylint:disable=too-few-public-methods
    def __init__(self):
        self.name = 'auxObj'
        super().__init__()

class qUniversal:
    """
    This class is inhereted by (almost) all the other classes in this library. It is best understood by considering
    its attributes.

    Note: Most attributes are `private` (with name mangling) and reached/modified by a `property getter/setter`. The
    attribute explanations below uses the property names for such cases together with the name-mangled and
    pure attribute names separated by `or`. The reason behind the use of properties is to ensure that some
    internal functionalties are maintained, especially in the child-classes that extend these properties. For example,
    uniqueness of object name is achieved by the .name setter calling another method.

    Attributes
    ----------
    name or _qUniversal__name or __name: ``str``
        Every-object inheriting from qUniversal will have a `unique` name.

        Default names for internally (by the library) and externally (by the user) created objects differ by an
        underscore. Default names are always the class `label` (a class attribute and always the same as class
        name) or `_label` plus, respectively, the number of external or internal instances, which are also kept as
        class attributes. Note that the `default` name for an object will
        always be `label` +number of instances. For example, if this is the list of name for existing instances
        ``['qUniversal1, 'bob', 'alice']`` , name of the next instance will be ``'qUniversal4'`` (not `qUniversal2`).

        Special names can be assigned by ``obj.name = 'new Name'`` after object creation or
        by ``obj = qUniversal(name='new Name')`` while instantiation. The special names also has to be unique. If a
        duplicate name is assigned to another object, it is changed to
        ``'new Name' + (number of external instances)``.
    _internal : ``bool``
        This is a boolean to distinguish between internally (``True``) and externally (``False``) created objects.
        Mainly usedfor naming.
    _qUniversal__allInstances or __allInstances : ``dict``
        This is an instance attribute pointing to class attribute :attr:`instNames <qUniversal.instNames>`. This exist
        to `ensure a proper access` to any object using the method :meth:`getObjByName <qUniversal.getObjByName>`
        **during multi-processing**.
    superSys or _qUniversal__superSys or __superSys : ``Any``
        This is used in many places in the library to share information between objects. `superSys` is
        (almost for all classes) is a `single system`. This is mainly introduced to be used when an object needs to use
        `several attribute values` of another object.
    subSys or _qUniversal__subSys or __subSys: ``OrderedDict``
        The purpose is, same as `superSys`, to share information, but this is a dictionary of objects, and it is
        mainly introduced to be used when an object needs the `same attribute value/s` from `several` other objects.

        Note: `subSys-superSys` **DOES NOT** define a hierarchy, meaning that if an object A is in `subSys` of B, this
        **does not** mean B is `superSys` of A. Even further, A can even be the superSys of B at the same time.
        If needed, such a hierarchy, needs to be introduced explicitly in the sub-classes.
    """

    label: str = 'qUniversal'
    """
    Together with :attr:`_externalInstances <qUniversal._externalInstances>`
    and :attr:`_internalInstances <qUniversal._internalInstances>`,
    `label` is used in `default` naming of the objects.
    It is the same as class name, and the default names for the objects explicitly created by the user are
    ``label+_externalInstances``, and the object created internally are named as ``_label+_internalInstances``
    """

    instNames: Dict = {}
    """
    This is a dictionary with keys as instance names and values as instances. This is kept to ensure that the names are
    unique, but it is conveniently used for other purposes, such as reaching an object from any part of the code just
    by using its name. NOTE : It contains instances of ``qUniversal`` and ``all its child classes``.
    """

    #: This is the number of instances that are explicitly created by the user.
    _externalInstances: int = 0

    #: This is the number of instances that are created internally by the library.
    _internalInstances: int = 0

    #: Total number of instances of the class = ``_internalInstances + _externalInstances```
    instances = 0

    _totalInst = 0

    #: aux
    _auxiliary = {}
    _auxiliaryObj = _auxiliaryClass()

    #: a list of str (attribute names) to be used with save method.
    toBeSaved: List[str] = extendedList(['name'])

    __slots__ = ['__name', '__superSys', '__subSys', '__allInstances', '_internal', '__aux', '__auxObj']

    def __init__(self, **kwargs):
        super().__init__()
        self._internal = kwargs.pop('_internal', False)
        self._incrementInstances(self._internal)
        self.__name = self._qUniversal__namer()
        self.__superSys = None
        self.__subSys = OrderedDict()
        self.__allInstances = qUniversal.instNames
        self.__aux = qUniversal._auxiliary
        self.__auxObj = qUniversal._auxiliaryObj
        self._qUniversal__setKwargs(**kwargs)

    @property
    def aux(self):
        return self._qUniversal__aux

    @aux.setter
    def aux(self, dictionary):
        setattr(self, '_qUniversal__aux', dictionary)

    @property
    def auxObj(self):
        return self._qUniversal__auxObj

    def save(self):
        """
        This method creates & ``returnss`` a dictionary with keys from :attr:`toBeSaved <qUniversal.toBeSaved>` list and
        the values from the corresponding values of the object.

        This is used to collect the same relevant information for all the instances and use the resultant dictionary
        with some other (format specific) save method. For example, this is currently used with
        :meth:`saveH5 <qTools.classes.extensions.saveReadH5.saveH5>`
        and :meth:`writeToTxt <qTools.classes.extensions.saveReadH5.writeToTxt>` methods.

        TODO : **This is introduced as a quick solution for saving and will be improved/changed**.
        """

        saveDict = {}
        for k in self.toBeSaved:
            val = getattr(self, k)
            if val is not None:
                saveDict[k] = val
        saveDict['class'] = self.__class__.__name__
        return saveDict

    def getObjByName(self, name):
        """
        This method finds & ``returnss`` the instance of qUniversal (or its child classes) with the given name.

        Parameters
        ----------
        name : str
            name of the object to be returned.
        """

        return self._qUniversal__allInstances[name]

    def __setKwargs(self, **kwargs):
        """
        This is used to set the attributes of the object from the given keywords and values.
        It is introduced to be used while instantiation of the object. It ``returns None``.

        Parameters
        ----------
        kwargs : Any
            Any attribute from the __slots__ (should take name-mangling into account, if used by a child class) or
            the name of corresponding property with an appropriate value type.
        """

        for key, value in kwargs.items():
            setattr(self, key, value)

    def resetSubSys(self):
        """
        This is a trivial method. It just sets the ``subSys`` dict to a new empty ``OrderedDict``. There are two reasons
        leading to its introduction:

            1. The ``__subSys`` is a private attribute and the `subSys setter` is more useful when
               used for adding new system rather than assigning a whole new ``OrderedDict``.
            2. To complement :meth:`add <qUniversal.addSubSys>`/:meth:`create <qUniversal.createSubSys>`/
               :meth:`remove <qUniversal.removeSubSys>` SubSys methods.

        It ``returns None``.
        """

        oldDict = self._qUniversal__subSys
        setattr(self, '_qUniversal__subSys', OrderedDict())
        del oldDict

    @property
    def subSys(self):
        """
        The subSys property:

        - **getter** : ``returns __subSys`` an ``OrderedDict``.
        - **setter** : adds the given object/s to ``__subSys``. It calls the :meth:`addSubSys <qUniversal.addSubSys>`,
          so it can used to add a single object, `list/dict/tuple/orderedDict` of objects, by giving the name of the
          system, or giving class name to add a new instance of that class.
        - **type** : ``list or dict or tuple or orderedDict``
        """

        return self._qUniversal__subSys

    @subSys.setter
    def subSys(self, subS):
        self.resetSubSys()
        self.addSubSys(subS)

    @checkClass('qUniversal')
    def addSubSys(self, subS, **kwargs):
        """
        The main body of this method just adds the given object into ``__subSys`` dictionary and
        calls :meth:`__setKwargs <qUniversal._qUniversal__setKwargs>` on the object for the given keyworded arguments.

        However, this method is decorated by :func:`checkClass`, so it does much more than that is the main body.
        See the decorator docstrings of :func:`checkClass` for more detail.

        Parameters
        ----------
        subS: qUniversal
            The object to add into ``__subSys`` dictionary
        kwargs: Any
            Keyworded arguments to be used with :meth:`__setKwargs <qUniversal._qUniversal__setKwargs>` to set some
            attributes of the given `subS`.


        :returns: `subS` (an instance of qUniversal or its child classes)
        """

        subS._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        self._qUniversal__subSys[subS.name] = subS

    @checkClass('qUniversal')
    def createSubSys(self, subSysClass, **kwargs):
        """
        The main body and functionality of this method are exactly the same as :meth:`addSubSys <qUniversal.addSubSys>`.
        """

        subSysClass._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        self._qUniversal__subSys[subSysClass.name] = subSysClass


    def _remFromDict(self, subS, dictName):
        dictSelf = getattr(self, dictName)
        if subS in dictSelf.keys():
            obj = dictSelf.pop(subS)
            print(obj, ' is removed from of ' + self.name)
        elif isinstance(subS, qUniversal):
            if subS.name in dictSelf.keys():
                obj = dictSelf.pop(subS.name)
                print(obj, ' is removed from of ' + self.name)
            else:
                keys = list(dictSelf.keys())
                vals = list(dictSelf.values())
                for ind, key in enumerate(keys):
                    if vals[ind] is subS:
                        obj = dictSelf.pop(key, None)
                        print(obj, ' is removed from of ' + self.name)


    @_recurseIfList
    def removeSubSys(self, subS, _exclude=[]): # pylint: disable=dangerous-default-value
        """
        This method removes the given object from the ``__subSys`` dictionary.

        TODO Cover if the given key of obj or str is not in subSys dict.
        """

        self._remFromDict(subS, '_qUniversal__subSys')

    @property
    def superSys(self):
        """
        The superSys property:

        - **getter** : ``returns __superSys`` attribute value
        - **setter** : sets the ``__superSys`` attribute value
        """

        return self._qUniversal__superSys

    @superSys.setter
    def superSys(self, supSys):
        setattr(self, '_qUniversal__superSys', supSys)

    @property
    def name(self):
        """
        The name property:

        - **getter** : ``returns __name`` attribute value
        - **setter** : after calling :meth:`updateNames <qUniversal.updateNames>` method of qUniversal class to
          ensure the uniqueness of names, sets the ``__name`` attribute value to `name`.
        - **types** : ``str``
        """

        return self._qUniversal__name

    @name.setter
    def name(self, name):
        name = qUniversal.updateNames(self, name)
        setattr(self, '_qUniversal__name', name)

    def copy(self, n=1, **kwargs):
        """
        This is a method to create n `empty` copies of an object. This method is introduced here to be extended in child
        class. In here, it ** does not copy ** the object, but creates n new objects of the same class and sets the
        given kwargs.


        :returns: a single object of the same class if n = 1 else ``Tuple`` with `n` objects
        """

        newSystems = []
        for ind in range(n): # pylint: disable=W0612
            sysClass = self.__class__
            newSystems.append(sysClass(**kwargs))

        if len(newSystems) == 1:
            newS = newSystems[0]
        else:
            newS = (*newSystems,)
        return newS

    def __namer(self):
        """
        This is the naming method used internally for default names. It uses class `label` and correspoding number of
        instances (internal or external).

        To get the cls label and the corresponding number of instances for internal/external, it calls class methods
        :meth:`clsLabel` and :meth:`clsInstances` with the :attr:`_internal` boolean value.

        :returns:
            the name string
        """

        if self._internal is False:
            name = self.clsLabel() + str(self.clsInstances(self._internal))
        else:
            name = '_' + self.clsLabel() + str(self.clsInstances(self._internal))
        qUniversal.instNames[name] = self
        return name

    @classmethod
    def updateNames(cls, obj, name):
        """
        This ``classmethod`` ensures that an objects name is unique, and the :attr:`instNames <qUniversal.instNames>`
        dictionary contains the correct name as the key, meaning not an old name or more than 1 keys for the same object

        This is a **recursive** method that calls itself if the given `name` exists in
        :attr:`instNames <qUniversal.instNames>` keys and the value is not the `obj`.

        Parameters
        ----------
        obj : qUniversal
            The object to be renamed
        name : str
            New name for the `obj`


        :returns: `name`
        """

        if name in cls.instNames.keys():
            if obj is cls.instNames[name]:
                cls.instNames[name] = cls.instNames.pop(obj.name)
            else:
                print(f'A duplicate name {name} is given,')
                name += str(obj.__class__._externalInstances) # pylint: disable=protected-access
                print(f'it is changed to {name}')
                return cls.updateNames(obj, name)
        else:
            if obj in cls.instNames.values():
                # can skip this and keep two keys for a system?
                cls.instNames[name] = cls.instNames.pop(obj.name)
            else:
                cls.instNames[name] = obj
        return name

    @classmethod
    def _incrementInstances(cls, boolean=False, val=1):
        """
        This method is called inside __init__ to increase internal/external number
        of instances depending on the `boolean`.
        """

        qUniversal._totalInst += 1
        cls.instances += val
        if boolean is False:
            cls._externalInstances += val
        elif boolean is True:
            cls._internalInstances += val

    @classmethod
    def clsInstances(cls, _internal=None):
        """
        This class method **returns** the number of instances:

            1. Total number, ``if _internal is None``
            2. internal, ``if _internal is True``
            3. external, ``if _internal is False``
        """

        if _internal is None:
            insCount = cls.instances
        elif _internal is True:
            insCount = cls._internalInstances
        elif _internal is False:
            insCount = cls._externalInstances
        return insCount

    @classmethod
    def clsLabel(cls):
        """
        This method **returns** the class label.
        """

        return cls.label
