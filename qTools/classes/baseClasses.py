"""
    This module contains some of the base classes and the _parameter class.

    Classes
    -------
    | :class:`_parameter` : This is a simple class to wrap certain parameters (attributes) to create a
        hierarchical dependency.
    | :class:`paramBoundBase` : This class is the start of an inheritance tree that extend to
        :class:`quantum systems <qTools.classes.QSys.genericQSys>`,
        :class:`protocols <qTools.classes.QPro.genericProtocol>`,
        and :class:`Simulation <qTools.classes.Simulation.Simulation>`.
    | :class:`computeBase` : This class contains 3 attributes that are relevant to run-time calculations/computations
        and result storage.
    | :class:`qBaseSim` : This class branches the inheritance started by paramBoundBase, and this branch extends to
        :class:`quantum systems <qTools.classes.QSys.genericQSys>` and
        :class:`protocols <qTools.classes.QPro.genericProtocol>`.
    | :class:`stateBase`: This class branches the inheritance started by paramBoundBase, and this branch extends to
        :class:`Simulation <qTools.classes.Simulation.Simulation>`.
"""
from typing import Any, cast

from collections import OrderedDict

from .base import qUniversal
from .QRes import qResults
# pylint: disable = cyclic-import

class updateBase(qUniversal):
    """
    This class has only two attributes, which are private attributes intended to be used with different properties in
    the ``_sweep`` and ``Update`` classes to enable different terminologies for the same functionality.

    Attributes
    ----------
    key or _updateBase__key or __key : str
        This string value is the name of an attribute for the objects in ``subSys`` dictionary of an instance of
        updateBase, and the value of that attribute is updated by **an update function**.
    _updateBase__function or __function : Callable or None
        This is the aforementioned **update function**. This is not completely implemented in ``Update`` class, but the
        ``_sweep`` class, which will also be updated, has its basic use, which is pointing it to a default method to be
        used in updating the relevant attributes. The goal of making this an attribute is to enable user defined
        functions to be used, if some form of customisation is needed. TODO : cross-reference this to fixed sample-rate
        for varying-step-size demos.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'updateBase'

    #: a list of str (attribute names) to be used with save method, it extends
    #: :attr:`toBeSaved <qTools.classes.QUni.qUniversal.toBeSaved>` list.
    toBeSaved = qUniversal.toBeSaved.extendedCopy(['key'])

    __slots__ = ['__key', '__function', '_aux']

    def __init__(self, **kwargs):
        super().__init__()

        self.__key = None
        self.__function = None
        self._aux = False

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        """
        This method extends the :meth:`save <qTools.classes.QUni.qUniversal.save>` of :class:`qUniversal` by using the
        extended :attr:`toBeSaved <qTools.classes.QUni.qUniversal.toBeSaved>` list and also collecting some of the
        information under a single key.
        """

        saveDict = super().save()
        sysDict = []
        for sys in self.subSys.values():
            sysDict.append(sys.name)
        saveDict['systems'] = sysDict
        return saveDict

    @property
    def key(self):
        """
        The key property:

        - **getter** : ``returns _updateBase__key``
        - **setter** : sets ``_updateBase__key`` string
        - **type** : ``str``
        """

        return self._updateBase__key

    @key.setter
    def key(self, keyStr):
        self._updateBase__key = keyStr # pylint: disable=assigning-non-slot

    @property
    def system(self):
        """
        The system property wraps ``subSys`` dictionary to create new terminology, it basically:

        - **getter** : ``returns subSys[0]`` if there is only one item in it, else ``returns list(subSys.values())``.
        - **setter** : works exactly as :meth:`subSys <qTools.classes.QUni.qUniversal.subSys>` setter.
        """

        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @system.setter
    def system(self, qSys):
        super().addSubSys(qSys)

    def _runUpdate(self, val):
        """
        This simple method sets the attribute (for the given key) of every ``subSys`` to a given value (``val``). It
        returns ``None``.
        """

        for subSys in self.subSys.values():
            try:
                setattr(subSys, self._updateBase__key, val)
            except AttributeError as attrErr:
                if self._aux is True:
                    subSys.aux[self._updateBase__key] = val
                else:
                    raise attrErr

class _parameter: # pylint: disable=too-few-public-methods
    """
    There are two types of parametric bounds/relations in this library,

        1. Value of an attribute of an object is bound to the value of the same attribute in another object, meaning
           it gets its value from its bound.
        2. Not the value of the attribute itself, but any change in its value is important for another object.

    This is a simple class to wrap certain parameters (attributes) to create a hierarchical dependency required for the
    first case. The second case is covered by :class:`paramBoundBase`.

    It is intended to be used with `private attributes` and the corresponding properties returning ``value`` of
    that attribute (which is a _parameter object).

    If a ``_parameter`` is given another ``_parameter`` as its ``_bound``, it returns the ``value`` of its ``_bound``,
    while keeping its ``_value`` unchanged (which is mostly left to be ``None``). So, it keeps calling ``value``
    until the ``_bound`` does not have a ``value`` attribute/property and finally ``returns _value``.

    TODO update this list and add cross-references.
    This class is used in ``stepSize``, ``totalTime``, ``stepCount``, ``initialState`` etc. The goal of having such
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

    Attributes
    ----------
    _value : Optional[Any]
        This is any object to be wrapped (default ``None``).
    _bound : None or False or _parameter
        The object to be used as the bound.
        ``None`` and ``False`` both mean that there is **no bound**, but
        they are used to distinguish between the value being the one given in __init__ method or set later
        by ``value`` property. (default ``None``).
    """

    __slots__ = ['_value', '_bound']

    def __init__(self, value: Any = None, bound: '_parameter' = None) -> None:
        """
        The init for _parameter has two optional arguments _value and _bound, both of them are ``None`` by default.
        """

        self._value = value
        self._bound = bound

    @property
    def value(self) -> Any:
        """
        This a property method with the

        - **getter** : ``returns _value`` of self, if ``bound`` does not have ``value``,
          else ``returns`` the ``value`` of the ``_bound``
          which should be a :class:`_parameter` object or have a ``_value`` &/ ``_bound`` attribute.
        - **setter(value)** : sets the ``_value`` to a given `input value` and ``_bound`` to ``False``
          (signaling its different than the initialisation)
        - **type**: ``Any``
        """

        if hasattr(self._bound, 'value'):
            self._bound = cast(_parameter, self._bound)
            return self._bound.value
        return self._value

    @value.setter
    def value(self, value: Any):
        self._bound = False
        self._value = value


def setAttr(obj, attrStr, val):
    oldVal = getattr(obj, attrStr)
    if val != oldVal:
        setattr(obj, attrStr, val)
        setattr(obj, '_paramUpdated', True)

def setAttrParam(obj, attrStr, val):
    oldVal = getattr(obj, attrStr).value
    if val != oldVal:
        getattr(obj, attrStr).value = val
        setattr(obj, '_paramUpdated', True)

class paramBoundBase(qUniversal):
    """
    There are two types of parametric bounds/relations in this library,

        1. Value of an attribute of an object is bound to the value of same attribute of another object, meaning
           it gets its value from its bound.
        2. Not the value of the attribute itself, but any change in its value is important for another object.

    First case is covered by the :class:`_parameter` and the second case is covered by this class.
    This type of bound is used to make sure that a **protocol** does not re-create (re-exponentiate)
    its **unitary matrix**, unless a relevant parameter is changed. If the ``__paramUpdated`` is ``False``, a protocol
    is not going to re-create its unitary, the ``__paramUpdated`` is set to ``True`` only by an object which contain
    the protocol in its ``__paramBound`` dictionary and changes its ``__paramUpdated`` to ``True`` by calling
    :meth:`_paramUpdated <paramBoundBase._paramUpdated>` property. These sort of dependencies are implemented in the
    library and are not meant for external modifications.

    NOTE : This class is the start of an inheritance tree that extend to
    :class:`quantum systems <qTools.classes.QSys.genericQSys>`,
    :class:`protocols <qTools.classes.QPro.genericProtocol>`,
    and :class:`Simulation <qTools.classes.Simulation.Simulation>`.

    The attributes are private (with name-mangling) and properties &/ methods are used to change their values. Below
    explanations contain property names for such cases with actual attribute names separated by `or`.

    Attributes
    ----------
    _paramUpdated or _paramBoundBase__paramBound or __paramBound: bool
        This is set to ``True`` when a parameter is updated and set back to ``False`` after unitary creation by protocol

        NOTE : protocols check only their own ``_paramUpdated`` for re-creation, so, they only set their own
        ``_paramUpdated`` back after re-creation. This means that the dependency of ``_paramUpdated`` boolean is not
        similar to :class:`_parameter` class.

        The getter of ``_paramUpdated`` simply returns the ``_paramBoundBase__paramBound`` boolean for ``self``. While,
        the setter of ``_paramUpdated``, sets ``_paramBoundBase__paramBound`` boolean for ``self`` and all the other
        objects in ``__paramBound`` dictionary (if they have such an attribute).
    _paramBound or _paramBoundBase__paramBound or __paramBound: dict
        This is a dictionary of objects whose ``_paramUpdated`` boolean value needs to be updated, if ``_paramUpdated``
        of ``self`` is updated (but not the other way around and, unlike :class:`_parameter` setting the ones
        value does not break the relation).
    _paramBoundBase__matrix or __matrix : Matrix
        This is used for storing a relevant matrix in some sub-classes, such as protocols ``__matrix`` is their unitary
        , and single quantum systems use it for their ``freeMat``.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label: str = 'paramBoundBase'

    __slots__ = ['__paramUpdated', '__paramBound', '__matrix']

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__matrix = None
        self.__paramUpdated = True
        self.__paramBound = OrderedDict()
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def _paramBound(self):
        """
        This property ``returns _paramBoundBase__paramBound`` dictionary, and does not have a setter.
        """

        return self._paramBoundBase__paramBound

    # @checkClass('qBase')
    # def _createParamBound(self, bound, **kwargs) -> None:
    #     """[summary]

    #     Parameters
    #     ----------
    #     bound : [type]
    #         [description]
    #     """
    #     bound._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
    #     self._paramBoundBase__paramBound[bound.name] = bound

    # def _breakParamBound(self, bound):
    #     """[summary]

    #     Parameters
    #     ----------
    #     bound : [type]
    #         [description]
    #     """
    #     obj = self._paramBoundBase__paramBound.pop(bound.name)
    #     print(obj.name + ' is removed from paramBound of ' + self.name)

    @property
    def _paramUpdated(self):
        """
        The _paramUpdated property:

        - **getter** : ``returns _paramBoundBase__paramUpdated`` boolean.
        - **setter** : sets ``_paramBoundBase__paramUpdated`` boolean for ``self`` and all the other objects in
          ``__paramBound`` dictionary (if they have such an attribute).
        - **type** : ``bool``
        """

        return self._paramBoundBase__paramUpdated

    @_paramUpdated.setter
    def _paramUpdated(self, boolean):
        self._paramBoundBase__paramUpdated = boolean # pylint: disable=assigning-non-slot
        for sys in self._paramBoundBase__paramBound.values():
            sys._paramUpdated = boolean

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        """
        This method deletes (sets to ``None``) the ``__matrix`` value for self and calls the ``delMatrices`` for on the
        objects in ``__paramBound`` and ``subSys`` dictionaries. Also, calls ``del`` on the old value of ``__matrix``.

        Parameters
        ----------
        _exclude : list, optional
            This is used internally to avoid infinite loops in the cases when an object has another in its
            ``__paramBound``, while it is in ``subSys`` of the other. By default []


        :returns: returns the _exclude list, which should contain references to all the objects whose ``__matrix``
            attribute is set to ``None``
        """

        if self not in _exclude:
            oldMat = self._paramBoundBase__matrix
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
    """
    This class contains 3 attributes that are relevant to run-time calculations/computations and result storage.

    Attributes
    ----------
    qRes : qResults
        This attribute is an instance of :class:`qResults <qTools.classes.QRes.qResults>`, which is used to store
        simulation results and states.
    compute : Callable or None
        This is by default ``None``, but if it is assingned to be a function that is written in a particular format,
        it is called at each step of the time evolution to perform whatever is in its body, which is intended to be
        certain computations on the current state of the system and store them in the ``self.qRes.results``.
        TODO : create a simple demo and a cross-reference
    calculate : Callable or None
        This is by default ``None``, but if it is assingned to be a function that is written in a particular format,
        it is called at certain stages of simulation (like in the beginning of time-evolution etc.), to perform
        some calculation, which are going to be needed in the compute, and store them in the ``self.qRes.calculated``.
        TODO : create a simple demo and a cross-reference
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label: str = 'computeBase'

    __slots__ = ['qRes', 'compute', '__calculate', '__calculateAtStart']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.compute = None
        self.__calculate = None
        self.__calculateAtStart = True
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self.qRes = qResults(superSys=self, _internal=True)

    @property
    def calculate(self):
        return self._computeBase__calculate

    @calculate.setter
    def calculate(self, inp):
        if callable(inp):
            self._computeBase__calculate = inp #pylint: disable=assigning-non-slot
        else:
            if callable(inp[0]):
                self._computeBase__calculate = inp[0] #pylint: disable=assigning-non-slot
                self.calculateAt = inp[1]
            elif callable(inp[1]):
                self._computeBase__calculate = inp[1] #pylint: disable=assigning-non-slot
                self.calculateAt = inp[0]
            else:
                raise TypeError('?')

    @property
    def calculateAt(self):
        if self._computeBase__calculateAtStart: #pylint: disable=assigning-non-slot
            string = 'begining'
        else:
            string = 'start'
        return string

    @calculateAt.setter
    def calculateAt(self, string):
        if string.lower() in ['start', 'begin', 'begining']:
            self._computeBase__calculateAtStart = True #pylint: disable=assigning-non-slot
        elif string.lower() in ['end']:
            self._computeBase__calculateAtStart = False #pylint: disable=assigning-non-slot

    @paramBoundBase.name.setter # pylint: disable=no-member
    def name(self, name):
        """
        This setter extends setter of name property in qUniversal by also
        changing the name of ``qRes``, which is an instance of :class:`qResults <qTools.classes.QRes.qResults>`.
        """

        paramBoundBase.name.fset(self, name) # pylint: disable=no-member
        if self.qRes.superSys is self:
            self.qRes.superSys = self

    def __compute(self, states, ignore=[]):
        """
        This is the actual compute function that is called in the time-evolution, it calls ``self.compute`` is it is a
        callable and does nothing otherwise.
        """
        if self not in ignore:
            if callable(self.compute):
                self.compute(self, *states) # pylint: disable=not-callable
                ignore.append(self)
                # FIXME with calculate
                for qsp in self.subSys.values():
                    if hasattr(qsp, '_computeBase__compute'):
                        qsp._computeBase__compute(states, ignore=ignore)

    def __calculateMeth(self):
        """
        This is the actual calculate function that is called in the time-evolution, it calls ``self.calculate`` is it is
        a callable and does nothing otherwise.
        """

        if callable(self.calculate):
            self._computeBase__calculate(self) # pylint: disable=not-callable
            # FIXME with compute
            for qsp in self.subSys.values():
                if hasattr(qsp, '_computeBase__calculate'):
                    qsp._computeBase__calculateMeth()

    @property
    def results(self):
        """
        This property ``returns results`` attribute of ``qRes``.
        """

        return self.qRes.results

    @property
    def states(self):
        """
        This property ``returns states`` attribute of ``qRes``.
        """

        return self.qRes.states

class qBaseSim(computeBase):
    """
    This class is inhereted by the :class:`quantum systems <qTools.classes.QSys.genericQSys>` and
    :class:`protocols <qTools.classes.QPro.genericProtocol>` and has a
    simulation attribute which is an instance of :class:`Simulation <qTools.classes.Simulation.Simulation>`. The goal
    for such an attribute is to increase possible ways of running a
    :class:`Simulation <qTools.classes.Simulation.Simulation>`.
    TODO : create a simple demo and a cross-reference

    NOTE : This class branches the inheritance started by :class:`paramBoundBase`, and this branch extends to
    :class:`quantum systems <qTools.classes.QSys.genericQSys>` and
    :class:`protocols <qTools.classes.QPro.genericProtocol>`.

    Attributes
    ----------
    simulation or _qBaseSim__simulation or simulation : Simulation
        This an instance of Simulation which can just be run by
        ``self.simulation.run`` without any explicit Simulation creation and/or ``subSys`` addition call.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'qBaseSim'

    __slots__ = ['__simulation']

    def __init__(self, **kwargs):
        from qTools.classes.QSim import Simulation # pylint: disable=import-outside-toplevel
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__simulation = Simulation(_internal=True, superSys=self)
        self._qBaseSim__simulation._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        # self.__openSystem = False

    @property
    def simulation(self):
        """
        This property ``returns _qBaseSim__simulation`` attribute.
        """

        return self._qBaseSim__simulation

    def runSimulation(self, p=None, coreCount=None):
        return self._qBaseSim__simulation.run(p=p, coreCount=coreCount)

    @property
    def simParameters(self):
        return (self.simulation.totalTime, self.simulation.stepSize, self.simulation.stepCount, self.simulation.samples,
                self.simulation.delStates, self.simulation.compute)

    @simParameters.setter
    def simTotalTime(self, fTime):
        self.simulation.totalTime = fTime

    @simParameters.setter
    def simStepSize(self, stepsize):
        self.simulation.stepSize = stepsize

    @simParameters.setter
    def simStepCount(self, num):
        self.simulation.stepCount = num

    @simParameters.setter
    def simSamples(self, num):
        self.simulation.samples = num

    @simParameters.setter
    def simCompute(self, func):
        self.simulation.compute = func

    @simParameters.setter
    def simDelStates(self, boolean):
        self.simulation.delStates = boolean

    @property
    def initialState(self):
        """
            This works by assuming that its setter/s makes sure that _stateBase__initialState.value is not None
             for single systems,
            if its state is set.
            If single system initial state is not set, it will try creating here,
             but single system does not have qSystem,
              so will raise the below error.
        """

        return self.simulation.initialState

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
        """
        This method extends :meth:`delMatrices <paramBoundBase.delMatrices>` of :class:`computeBase` to also call
        :meth:`delMatrices <paramBoundBase.delMatrices>` also on ``self.simulation``.
        """

        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            _exclude = self.simulation.delMatrices(_exclude)
        return _exclude

class stateBase(computeBase):
    """
    This base class contains relevant attributes and methods for ``initialState`` and a boolean to determine to keep or
    discard time-evolved states. Since, we can use :meth:`compute <computeBase.compute>` to compute quantities of
    interest at the run-time of simulation, we don't need to keep the states and can save memory.

    NOTE : This class branches the inheritance started by :class:`paramBoundBase`, and this branch extends to
    :class:`Simulation <qTools.classes.Simulation.Simulation>`.

    NOTE : All three attributes of this class (and all 4 of timeBase) are instances of :class:`_parameter`, so they have
    a corresponding property.

    Attributes
    ----------
    delState or _stateBase__delStates or __delStates : bool
        This boolean is used to determine delete/discard (``True``) time-evolved states (to save memory) and keep only
        the ``initialState`` and ``currentState`` of the system. By default, it is ``False`` and states will be stored
        in the corresponding protocols ``qRes.states``.
    initialState or _stateBase__initialState or __initialState: Matrix
        This _parameter object attributes value is set to be ``initialState`` matrix
    _initialStateInput or _stateBase__initialStateInput or __initialStateInput :
        This is the input used to create ``initialState``, there are various ways to create ``initialState``, so its
        value is changes depending on the case. This information is kept so that it can be used in cases where a new
        reconstruction of ``initialState`` is required, e.g. when system dimension is swept or changed.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'stateBase'

    __slots__ = ['__delStates', '__initialState', '__initialStateInput']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))

        self.__initialState = _parameter()
        self.__initialStateInput = _parameter()
        self.__delStates = _parameter(False)

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def initialState(self):
        """
        The initialState property:

        - **getter** : ``returns _stateBase__initialState.value`` if it is not ``None``. Otherwise, uses first element
          in its ``subSys`` dictionary values to create and assign its value. This assumes that, to be able to assign
          a state to a Simulation, it needs at least one quantum system in its ``subSys`` dictionary. This requirement
          is by default satisfied by the internally created Simulation objects, which are attributes of quantum systems
          and protocols.
        - **setter** : sets ``_stateBase__initialState.value`` matrix for ``self`` by using the first element of
          ``subSys`` dictionary values.
        - **type** : ``Matrix``
        """

        if self._stateBase__initialState.value is None: # pylint: disable=no-member
            if isinstance(self._stateBase__initialState._bound, _parameter): # pylint: disable=protected-access
                self._stateBase__initialState._value = self._timeBase__bound.initialState # pylint: disable=no-member
            else:
                self._stateBase__initialState.value = list(self.subSys.values())[0]._createAstate(self._initialStateInput) # pylint: disable=protected-access, no-member, line-too-long
        return self._stateBase__initialState.value # pylint: disable=no-member

    @initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        self._stateBase__initialStateInput.value = inp # pylint: disable=no-member
        self._stateBase__initialState.value = list(self.subSys.values())[0]._createAstate(inp) # pylint: disable=protected-access, no-member, line-too-long

    @property
    def _initialStateInput(self):
        """
        This property ``returns _stateBase__initialStateInput.value``.
        """

        return self._stateBase__initialStateInput.value

    def getResultByName(self, name):
        """
        This method exists to enrich the terminology, it just ``returns super().getObjByName(name)``, which returns the
        object with the given `name`.
        See :meth:`getObjByName <qTools.classes.QUni.qUniversal.getObjByName>` for details.
        """

        return super().getObjByName(name)

    @property
    def delStates(self):
        """
        The delStates property:

        - **getter** : ``returns _stateBase__delStates.value``
        - **setter** : sets ``_stateBase__delStates.value`` boolean
        - **type** : ``boolean``
        """

        return self._stateBase__delStates.value

    @delStates.setter
    def delStates(self, boolean):
        self._stateBase__delStates.value = boolean

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        """
        This method extends :meth:`delMatrices <paramBoundBase.delMatrices>` to also set
        the ``_stateBase__initialState.value`` to ``None`` and del the old value.
        """

        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            oldMat = self._stateBase__initialState.value
            self._stateBase__initialState.value = None # pylint: disable=no-member, protected-access
            del oldMat
        return _exclude

class timeBase(stateBase):
    """
    This base class contain 3 basis time information, namely total time of simulation (``totalTime``), step size for
    each unitary (``stepSize``), and number of steps (``stepCount = totalTime/stepSize``). Additionally, one more
    parameter, namely, number of samples
    (``samples``) is introduced to be used with time-dependent Hamiltonians, where a continuous parameter
    is discretely changed at every ``stepSize`` and more than one ``samples`` are desired during the ``stepSize``.

    These 4 attributes are all :class:`_parameter <qTools.classes.computeBase._parameter>` objects and private
    attributes, so they are modified by the corresponding properties (names here are property names). One other use of
    property is to create flexible use of these attributes. For example, not all 3 of ``stepSize``, ``totalTime``, and
    ``stepCount`` are need to be explicitly defined, any of these two would be sufficient, since the 3rd can be
    calculated using the two. So, property setters&getters also covers such cases. Another flexibility ensured by the
    properties is when ``_bound`` are broken.

    Attribute names and these explanations are enough to understand the basics for these 4 paramaters of timeBase class.
    See below for more details on the corresponding properties.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'timeBase'

    __slots__ = ['__totalTime', '__stepSize', '__samples', '__stepCount', '__bound']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__totalTime = _parameter()
        self.__stepSize = _parameter()
        self.__samples = _parameter(1)
        self.__stepCount = _parameter()
        self.__bound = None

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        """
        This method extends the :meth:`save <qTools.classes.QUni.qUniversal.save>` of :class:`qUniversal`. This one uses
        an alternative approach to :attr:`toBeSaved <qTools.classes.QUni.qUniversal.toBeSaved>` list, which is defining
        the list inside the function as opposed to being a class attribute. There are advantages and disadvantages for
        both approaches, but these methods are temporary anyway.
        """

        keys = ['stepSize', 'totalTime', 'samples', 'stepCount']
        try:
            saveDict = super().save()
        except TypeError:
            saveDict = {}

        if self.superSys is not None:
            saveDict['superSys'] = self.superSys.name # pylint: disable=no-member

        for key in keys:
            saveDict[key] = getattr(self, key)
        return saveDict

    @property
    def totalTime(self):
        """
        The totalTime property:

        - **getter** : ``returns _timeBase__totalTime.value``.
        - **setter** : sets ``_timeBase__totalTime.value``, and also ``_timeBase__stepCount.value`` conditioned on that
          ``stepSize`` is not ``None``. It also sets
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
        """
        The stepCount property:

        - **getter** : ``returns _timeBase__stepCount.value`` but also sets ``totalTime`` if it is ``None``.
        - **setter** : sets ``_timeBase__stepCount.value`` and also ``_timeBase__stepSize.value`` conditioned on that
          ``totalTime`` is not ``None``. It also sets
          :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``. Additionally to
          these, it sets ``_timeBase__totalTime._value`` to ``_timeBase__totalTime._bound._value``, if
          ``_timeBase__totalTime._bound`` is not ``None or False``. This is introduced to provide a flexible
          use of these parameters, such as not forcing to define at least 2 of 3 timeBase parameters, if it already
          has a ``_bound`` and can obtain the second one from the ``_bound``.
        """

        if self.totalTime is None:
            self._timeBase__totalTime.value = self._timeBase__stepCount.value * self.stepSize # pylint: disable=E0237
        self._timeBase__stepCount.value = int((self.totalTime//self.stepSize) + 1) # pylint: disable=assigning-non-slot
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
        """
        The stepSize property:

        - **getter** : ``returns _timeBase__stepSize.value``.
        - **setter** : sets ``_timeBase__stepSize.value`` and also ``_timeBase__stepCount.value`` conditioned on that
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
        """
        The samples property:

        - **getter** : ``returns _timeBase__samples.value``.
        - **setter** : sets ``_timeBase__samples.value`` and also
          :meth:`_paramUpdated <qTools.classes.computeBase.paramBoundBase._paramUpdated>` to ``True``.
        """

        return self._timeBase__samples.value

    @samples.setter
    def samples(self, num):
        setAttrParam(self, '_timeBase__samples', num)

    def _copyVals(self, other, keys):
        for key in keys:
            setattr(self, key, getattr(other, key))

    def _bound(self, other, # pylint: disable=dangerous-default-value
               params=['_stateBase__delStates', '_stateBase__initialState', '_stateBase__initialStateInput'],
               re=False):
        """
        This method is used internally at appropriate places to create bound between different simulation instances in
        the intended hierarchical order. Meaning, when a :class:`quantum system <qTools.classes.QSys.genericQSys>` is
        added to ``subSys`` of explicitly created :class:`Simulation <qTools.classes.Simulation.Simulation>`.
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


        :returns: None
        """

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
                        if ((getattr(self, k)._bound is None) and # pylint: disable=protected-access
                                (getattr(other, k)._value is not None)): # pylint: disable=protected-access
                            setattr(self, keysProp[i], getattr(other, k)._value) # pylint: disable=protected-access
                            break
                    bounding = False

        for key in (*keys, *params, '_timeBase__samples'):
            try:
                if ((getattr(self, key)._bound is None) or re): # pylint: disable=protected-access
                    if getattr(other, key)._bound in (None, False): # pylint: disable=protected-access
                        getattr(self, key)._bound = getattr(other, key) # pylint: disable=protected-access
                    elif isinstance(getattr(other, key)._bound, _parameter): # pylint: disable=protected-access
                        getattr(self, key)._bound = getattr(other, key)._bound # pylint: disable=protected-access
            except AttributeError:
                print('not bounding', key)
