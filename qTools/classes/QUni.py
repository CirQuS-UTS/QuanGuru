"""
    Module for the qUniversal, extendedList classes and checkClass decorator.

    Classes
    -------
    | **qUniversal** : This class is inhereted by (almost) all the other classes in this library.
    | **checkClass** : This is a `decorator with arguments and a recursive wrapper`, and it was initially created to be
     used with `subSys` dictionary of `qUniversal` class.
    | **extendedList** : This class extends the built-in class list. It is introduced to be used with `toBeSaved` lists.
"""
from functools import wraps
from collections import OrderedDict

__all__ = [
    'qUniversal'
]

def checkClass(classOf, attribute):
    """
    This is a `decorator with arguments and a recursive wrapper`. It is used in couple of places in the library.
    It decorates the functions to check the `class of (classOf)` a given `input (inp)` then adds it to the `attribute`,
    which is a `dictionary` (mostly ordered).

    This decorater was initially created to be used with `subSys` dictionary of `qUniversal` class, and the idea is to
    cover possible user misuse in `add/create/remove subSys` functions (while also creating flexibility). For example,
    if a user gives the class itself instead of an instance to be included in subSys dictionary, this decorator creates
    a new instance and includes the new instance into the dictionary. This also enable the flexible use of `addSubs` as
    a `createSubSys`. This also covers some other scenarios like giving a list of instances to be included etc.
    This decorator is also used for `paramBound` dictionary of `paramBoundBase` class and
    `envCoupling` of `genericQSys` class.

    **Note** : This decorator assumes that the given object is an instance of qUniversal or its child classes.

    It works by first finding the intended class by using its name (`classOf`) with `global()`.

    0. If the `input (inp)` is an instance of this class (`classOf`), it calls the `addRemoveFunction` (which does the
    actual
    adding/removing). But before that, it changes the `ind` attribute of the instance conditioned on that ind is `None`,
    and the dictionary which it will be included is the `subSys`. `ind` attribute was introduced to keep some order
    information when we were using dictionary, which is not needed since we switched to `OrderedDict`. However, it still
    comes handy when working with the subSys dict (even though it is ordered), so it is kept for some internal uses.

    There are several other cases of input covered by this decorator:
    | 1. input is a `string`
        - name of class : creates and instance of the class and adds the new instance into the attribute dict.
        - name of instance : finds the object from the dict and adds it again (possibly by setting some kwargs)
    | 2. input is a `dictionary`: keys are not used currently, but it calls itself (recursively) for each value in the
    dictionary, meaning anything in this list form 0. to end may be trigerred depending on the type of value.
    | 3. input is `None`: This is used to 'empty' the dictionary, i.e. the `attribute` becomes an empty OrderedDict.
    | 4. input is a class: creates the instance of that class and calls itself with that instance.
    | 5. input is other types of iterable: call itself for every element of the iterable.
    """
    def addDecorator(addRemoveFunction):
        @wraps(addRemoveFunction)
        def wrapper(obj, inp, **kwargs):
            clsDecoArg = globals()[classOf]
            if isinstance(inp, clsDecoArg):
                if ((getattr(inp, '_qUniversal__ind') is None) and (attribute == '_qUniversal__subSys')):
                    if obj is not inp:
                        setattr(inp, '_qUniversal__ind', len(getattr(obj, attribute)))
                addRemoveFunction(obj, inp, **kwargs)
            elif isinstance(inp, str):
                if str in clsDecoArg.instNames.keys():
                    inp = wrapper(obj, clsDecoArg.instNames[inp], **kwargs)
                else:
                    clsInput = globals()[inp]
                    inp = wrapper(obj, clsInput, **kwargs)
            elif isinstance(inp, dict):
                for sys in inp.values():
                    # what to do with the keys?
                    inp = wrapper(obj, sys, **kwargs)
            elif inp is None:
                setattr(obj, attribute, OrderedDict())
                return getattr(obj, attribute, OrderedDict())
            elif inp.__class__ is type:
                newSys = inp()
                inp = wrapper(obj, newSys, **kwargs)
            else:
                for sys in inp:
                    inp = wrapper(obj, sys, **kwargs)
            return inp
        return wrapper
    return addDecorator


class extendedList(list):
    """
    This class extends the built-in class list. It is introduced to be used with `toBeSaved` lists, which contain
    contain the keys for `the attributes to be saved` into a `txt and hdf5 attributes`. The `toBeSaved` is a class
    attribute and extending through the inheritance tree is achieved by this `extendedCopy` method.

    Current saving methods are going to be improved, so, in future, this class might not be needed.
    """
    def extendedCopy(self, iterable):
        """
        This methods returns a new instance of extendedList by concatenating the ``self`` with a given ``iterable``.

        Parameters
        ----------
        iterable : list, tuple, or extendedList
            Existing iterable is extended by this.

        Returns
        -------
        :returns: extendedList
            A new instance of extendedList
        """
        baseList = extendedList()
        for it in self:
            baseList.append(it)
        for exIt in iterable:
            baseList.append(exIt)
        return baseList


class qUniversal:
    """
    This class is inhereted by (almost) all the other classes in this library. It is best understood by considering
    its attributes.

    Note: Some attributes are private (with name mangling) and reached/modified by a property getter/setter. The
    attribute explanations below uses the property names for such cases together with the name-mangled and
    pure attribute names separated by `or`. The reason behind the use of properties is to ensure some
    internal functionalties are maintained especially in the sub-classes that extend the properties. For example,
    uniqueness of object name is achieved by the .name setter calling another method.

    Attributes
    ----------
    name or _qUniversal__name or __name: str
        Every-object inheriting from qUniversal will have a `unique` name.

        Default names for internally (by the library) and externally (by the user) created objects differ by an
        underscore. Default names are always the class `label` (a class attribute and always the same as class
        name) or `_label` plus, respectively, the number of external or internal instances, which are also kept as
        class attributes. Note that the `default` name for an object will
        always be `label` +number of instances. For example, if this is the list of name for existing instances
        ``['qUniversal1, 'bob', 'alice']`` , name of the next instance will be ``'qUniversal4'`` (not qUniversal2).

        Special names can be assigned by ``obj.name = 'new Name'`` after object creation or
        by ``obj = qUniversal(name='new Name')`` while instantiation. The special names also has to be unique. If a
        duplicate name is assigned to another object, it is changed to
        ``'new Name' + (number of external instances)``.
    _internal : bool
        This a boolean to distinguish between internally (True) and externally (False) created objects. Mainly used
        for naming.
    _qUniversal__allInstances or __allInstances : dict
        This is an instance attribute pointing to class attribute `instNames`. This exist to `properly` access any
        object using the method `getObjByName` **during multi-processing**.
    superSys or _qUniversal__superSys or __superSys : Any
        This is used in many places in the library to share information between objects. `superSys` is
        (almost for all classes) is a `single system`. This mainly introduced to be used when an object needs to use
        `several attribute values` of another object.
    subSys or _qUniversal__subSys or __subSys: OrderedDict
        The purpose is, same as `superSys`, to share information, but this is a dictionary of systems, and it is
        mainly introduced to be used when an object needs the `same attribute value/s` from `several` other objects.

        Note: subSys-superSys **DOES NOT** define a hierarchy, meaning that if an object A is in `subSys` of B, this
        **does not** mean B is `superSys` of A. Even further, A can even be the superSys of B at the same time.
        If needed, such a hierarchy, needs to be introduced explicitly in the sub-classes, which already exist in
        QuantumSystem class.
    ind or _qUniversal__ind or __ind: int
        It was introduced to keep some order information when we were using dictionary, and it is not strictly
        needed since we switched to `OrderedDict`. However, it still comes handy when working with the subSys dict
        (even though it is ordered), so it is kept for some internal uses. It is set as the current length of subSys
        dictionary by the checkClass decorator and (should only be) updated by removeSubSys method, when an object is
        removed from the `subSys` dictionary.
    """
    #: Total number of instances of the class = `_internalInstances` + `_externalInstances`
    instances = 0
    #: Together with `_externalInstances` and `_internalInstances`, `label` is used in `default` naming of the objects.
    #: It is the same as class name, and the default names for the objects explicitly created by the user are
    #: `label+_externalInstances`, and the object created internally are named as `_label+_internalInstances`
    label = 'qUniversal'
    #: This is a dictionary with keys as object names and values as objects. This is kept to ensure that the names are
    #: unique, but it is conveniently used for other purposes, such as reaching an object from any part of the code just
    #: by using its name.
    instNames = {}
    #: This is the number of instances that are explicitly created by the user.
    _externalInstances = 0
    #: This is the number of instances that are created internally by the library.
    _internalInstances = 0
    #: a list of str (attribute names) to be used with save method.
    toBeSaved = extendedList(['name'])

    __slots__ = ['__name', '__superSys', '__ind', '__subSys', '__allInstances', '_internal']

    def __init__(self, **kwargs):
        super().__init__()
        self._internal = kwargs.pop('_internal', False)
        self._incrementInstances(self._internal)
        self.__name = self._qUniversal__namer()
        self.__superSys = None
        self.__subSys = OrderedDict()
        self.__ind = None
        self.__allInstances = qUniversal.instNames
        self._qUniversal__setKwargs(**kwargs)

    #def __del__(self):
    #    class_name = self.__class__.__name__

    def save(self):
        """
        This method creates & **returns** a dictionary with keys from `toBeSaved` (a class attribute) list and
        the values from the corresponding attribute values of the object.

        This is used to collect the same relevant information for all the instances and use the resultant dictionary
        with some other format specific save method. For example, this is currently used with ``saveH5``
        and ``writeToTxt`` methods.
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
        This method finds & **returns** the instance of qUniversal (or its child classes) with the given name.

        Parameters
        ----------
        name : str
            name of the object to be returned.
        """
        return self._qUniversal__allInstances[name]

    def __setKwargs(self, **kwargs):
        """
        This is used to set the attributes of the object from the given keywords and values.
        It is introduced to be used while instantiation of the object.

        Parameters
        ----------
        kwargs : Any
            Any attribute from the __slots__ (should take namemangling into account, if used by a child class) or
            the name of corresponding property with an appropriate value.


        :returns: None
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def resetSubSys(self):
        """
        This is a trivial method. It just sets the `subSys` dict to a new empty OrderedDict. There are two reasons
        leading to its introduction:
            | 1. The __subSys is a private attribute and the subSys setter is more useful when
             used to add new system rather than assigning a whole new OrderedDict.
            | 2. Complement add/create/removeSubSys methods.

        :returns: None
        """
        setattr(self, '_qUniversal__subSys', OrderedDict())

    @property
    def subSys(self):
        """
        The subSys property:

        | **getter** : returns __subSys OrderedDict
        | **setter** : adds the given object/s to __subSys OrderedDict. It calls the addSubSys, so it can used to add a
         single system, list/dict/tuple/orderedDict of systems, by giving the name of the system, or giving class name
         to add a new instance of that class.
        | **type** : list/dict/tuple/orderedDict
        """
        return self._qUniversal__subSys

    @subSys.setter
    def subSys(self, subS):
        self.addSubSys(subS)

    @checkClass('qUniversal', '_qUniversal__subSys')
    def addSubSys(self, subS, **kwargs):
        """
        The main body of this method just adds the given object into `subSys` dictionary and calls __setKwargs on the
        object for the given keyworded arguments.

        However, this method is decorated by `checkClass, so it can do much more than that is in the main body.
        See the decorator docstrings of `checkClass` for more detail.

        Parameters
        ----------
        subS: qUniversal
            The object to add into subSys dictionary
        kwargs: Any
            Keyworded arguments to be used with __setKwargs to set some attributes of the given subS.


        :returns: subS (an instance of qUniversal or its child classes)
        """
        subS._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        self._qUniversal__subSys[subS.name] = subS

    @checkClass('qUniversal', '_qUniversal__subSys')
    def createSubSys(self, subSysClass, **kwargs):
        """
        The main body of this method just adds the given object into `subSys` dictionary and calls __setKwargs on the
        object for the given keyworded arguments. (Same as addSubSys)

        However, this method is decorated by `checkClass, so it can do much more than that is in the main body.
        See the decorator docstrings of `checkClass` for more detail.

        Parameters
        ----------
        subS: qUniversal
            The object to add into subSys dictionary
        kwargs: Any
            Keyworded arguments to be used with __setKwargs to set some attributes of the given subS.


        :returns: subS (an instance of qUniversal or its child classes)
        """
        subSysClass._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        self._qUniversal__subSys[subSysClass.name] = subSysClass

    #@checkClass('qUniversal', '_qUniversal__subSys')
    def removeSubSys(self, subS, **kwargs):
        """
        This method calls __setKwargs on the object for the given keyworded arguments, then removes the given object
        from the `subSys` dictionary, and, finally, updates `ind` of the remaining objects in the `subSys`.
        """
        subS._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        obj = self._qUniversal__subSys.pop(subS.name)
        self._updateInd()
        print(obj.name + ' is removed from subSys of ' + self.name)

    def _updateInd(self):
        """
        This method updates the value of `__ind` attribute. This attribute should be equal to the position value of
        the object in the `subSys` dictionary for some parts of the library to work properly. So, this method basically
        re-assigns it to the objects position in `subSys`.

        This would/should not change anything when called arbitrarily, but it is introduced to be used when an object is
        removed (See removeSubSys) for subSys.
        """
        for ind, obj in enumerate(self._qUniversal__subSys):
            obj.ind = ind

    @property
    def superSys(self):
        """
        The superSys property:

        | **getter** : returns __superSys attribute value
        | **setter** : sets the __superSys attribute value
        """
        return self._qUniversal__superSys

    @superSys.setter
    def superSys(self, supSys):
        setattr(self, '_qUniversal__superSys', supSys)

    @property
    def ind(self):
        """
        The superSys property:

        | **getter** : returns __ind attribute value
        | **setter** : no setter, this should not be modified externally.
        """
        return self._qUniversal__ind

    @property
    def name(self):
        """
        The name property:

        | **getter** : returns __name attribute value
        | **setter** : after calling updateNames method of qUniversal class to
         ensure the uniqueness of names, sets the __name attribute value to `name`.
        | **types** : str
        """
        return self._qUniversal__name

    @name.setter
    def name(self, name):
        name = qUniversal.updateNames(self, name)
        setattr(self, '_qUniversal__name', name)

    @classmethod
    def updateNames(cls, obj, name):
        """
        This class method ensures that an objects name is unique, and the `insNames` dictionary contains the correct
        name as the key, meaning not the old name or more than 1 keys for the same object.

        This is a recursive method that calls itself if the given `name` exists in `instNames` keys and the value is
        not the `obj`.

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

    def copy(self, n=1, **kwargs):
        """
        This is a method to create n `empty` copies of an object. This method is introduced here to be extended in child
        class. In here, it ** does not copy ** the object, but creates n new objects of the same class and sets the
        given kwargs.


        :returns: a single object of the same class if n = 1 else Tuple with `n` objects
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
        This is the naming method used internally for default names. It uses class label and correspoding number of
        instances (internal or external).

        To get the cls label and the corresponding number of instances for internal/external, it calls class methods
        `clsLabel` and `clsInstances` with the `_internal` boolean value.

        :returns: str
            the name string
        """
        if self._internal is False:
            name = self.clsLabel() + str(self.clsInstances(self._internal))
        else:
            name = '_' + self.clsLabel() + str(self.clsInstances(self._internal))
        qUniversal.instNames[name] = self
        return name

    @classmethod
    def _incrementInstances(cls, boolean=False):
        """
        This method is called inside __init__ to increase total the number of instances and internal/external number
        of instances depending on the `boolean`.
        """
        cls.instances += 1
        if boolean is False:
            cls._externalInstances += 1
        elif boolean is True:
            cls._internalInstances += 1

    @classmethod
    def clsInstances(cls, _internal=None):
        """
        This class method **returns** the number of instances:
            | 1. Total number, if `_internal` is `None`
            | 2. internal, if `_internal` is `True`
            | 3. external, if `_internal` is `False`
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
