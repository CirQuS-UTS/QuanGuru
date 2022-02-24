r"""
    Contains two classes used for sweep functionalities.
    NOTE : Both of these classes are not intended to be directly instanciated by the user.
    :class:`Simulation <quanguru.classes.Simulation.Simulation>` objects **has** ``Sweep/s`` as their attributes, and
    ``_sweep/s`` are intended to be created by calling the relevant methods over ``Simulation.Sweep``.

    .. currentmodule:: quanguru.classes.QSweep

    .. autosummary::

        _sweep
        Sweep

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `_sweep`                   |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `Sweep`                    |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============

"""

from functools import reduce
from numpy import arange, logspace

from .base import qBase, _recurseIfList
from .baseClasses import updateBase

__all__ = [
    'Sweep'
]

class _sweep(updateBase): # pylint: disable=too-many-instance-attributes
    r"""
    Implements methods and attributes to sweep the value of an attribute for some objects for a list of values.
    The default sweep :meth:`~_defSweep` sweeps the value for a given attribute
    (a string stored in :py:attr:`~_sweep.key`) of objects in ``subSys`` dictionary.
    The list of values (stored in :py:attr:`_sweepList`) to be swept are set either directly
    by giving a ``list`` or the ``sweepMin-sweepMax-sweepStep`` with ``logSweep``.
    Default sweep function can be replaced with any custom method by re-assigning the :py:attr:`~sweepFunction` to the
    function reference. The default sweep method requires the index of the value from the list of values to set the next
    value, this index is provided by the modularSweep and useful for multi-parameter sweeps. It keeps a value fixed
    by re-assigning it using the same index, and the :class:`~paramBoundBase` and  other relevant classes uses the
    custom setattr methods (see :meth:`~setAttr` and :meth:`~setAttrParam`) to make sure that ``paramUpdated`` boolean
    is not set to ``True`` for the same value. This class implements a single sweep, and multi parameter sweep is
    achieved by the :class:`~Sweep` class.
    """
    #: (**class attribute**) class label used in default naming
    label = '_sweep'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['sweepMax', 'sweepMin', 'sweepStep', '_sweepList', 'logSweep', 'multiParam', '_sweepIndex']

    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: protected attribute pointing to a sweep function, by default :meth:`~_defSweep`. This attribute get&set
        #: using the sweepFunction property to replace default with a customized sweep method.
        self._updateBase__function = self._defSweep # pylint: disable=assigning-non-slot
        #: maximum value for the swept parameter, used with other attributes to create the sweepList
        self.sweepMax = None
        #: minimum value for the swept parameter, used with other attributes to create the sweepList
        self.sweepMin = None
        #: corresponds to the step size in a linearly spaced sweepList, or number of steps in logarithmic case,
        #: used with other attributes to create the sweepList
        self.sweepStep = None
        #: protected attribute to store a list of values for the swept parameter. Can be given a full list or
        #: be created using sweepMin-sweepMax-sweepStep values.
        self._sweepList = None
        #: boolean to create either linearly or logarithmically spaced list values (from sweepMin-sweepMax-sweepStep).
        self.logSweep = False
        #: boolean to determine, if two different sweeps are swept simultaneously (same length of list and pair of
        #: values at the same index are swept) or a multi-parameter sweep (fix one sweep the other and repeat).
        self.multiParam = False
        #: stores the index of the value (from the _sweepList) currently being assigned by the sweep function. Used by
        #: the default methods but also useful for custom methods. It is calculated by the modular arithmetic in
        #: modularSweep and passed to here by :class:`~Sweep` object containing self in its subSys. It starts from -1
        #: and the correspoding property returns _sweepIndex+1, while the :meth:`~runSweep` sets it to ind+1 for a given
        #: ind from modularSweep. This whole ordeal is due to make sure that python list indexing and modular arithmetic
        #: properly agrees for the sweep functionality. I feel it can be improved but will leave as it is for now.
        self._sweepIndex = -1
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def index(self):
        r"""
        returns ``self._sweepIndex + 1``. reason for +1 is explained in :py:attr:`~_sweepIndex`. There is no setter,
        the value of _sweepIndex is updated by the :meth:`~runSweep` and is an internal process.
        """
        return self._sweepIndex + 1

    @property
    def sweepFunction(self):
        r"""
        gets and set :py:attr:`~_updateBase__function`, which should point to a Callable.
        """
        return self._updateBase__function # pylint: disable=no-member

    @sweepFunction.setter
    def sweepFunction(self, func):
        self._updateBase__function = func # pylint: disable=assigning-non-slot

    @property
    def sweepKey(self):
        r"""
        gets and sets :py:attr:`~_updateBase__key`, which should be string.
        """
        return self._updateBase__key # pylint: disable=no-member

    @sweepKey.setter
    def sweepKey(self, keyStr):
        self._updateBase__key = keyStr # pylint: disable=assigning-non-slot

    @property
    def sweepList(self):
        r"""
        gets and sets :py:attr:`~_sweepList`. Setter requires a list input, if it is not set, getter tries creating the
        list (and setting :py:attr:`~_sweepList`) using sweepMin-sweepMax-sweepStep attributes.
        """
        if self._sweepList is None:
            try:
                if self.logSweep is False:
                    self._sweepList = arange(self.sweepMin, self.sweepMax + self.sweepStep, # pylint: disable=no-member
                                             self.sweepStep) # pylint: disable=no-member
                elif self.logSweep is True:
                    self._sweepList = logspace(self.sweepMin, self.sweepMax,
                                               num=self.sweepStep, base=10.0) # pylint: disable=no-member
            except: #pylint:disable=bare-except # noqa: E722
                pass
        return self._sweepList

    @sweepList.setter
    def sweepList(self, sList):
        self._sweepList = sList

    @staticmethod
    def _defSweep(self): # pylint: disable=bad-staticmethod-argument
        r"""
        This is the default sweep function, and it just calls the
        :meth:`_runUpdate <quanguru.classes.updateBase.updateBase._runUpdate>` by feeding it the value from the
        ``sweepList`` at the position ``ind``. :meth:`_runUpdate <quanguru.classes.updateBase.updateBase._runUpdate>`
        function just sets the attribute (for the given key) of every ``subSys`` to a given value (``val``).

        The modularSweep methods uses multiplication of length of ``sweepList/s`` (stored in
        __inds attribute of :class:`Sweep` instances) as a loop range, and the current loop counter is used by the
        :meth:`~_indicesForSweep` to calculate which indices of multi _sweep is currently needed.

        Parameters
        ----------
        ind : int
            Index of the value from ``sweepList``
        """

        val = self.sweepList[self.index]
        self._runUpdate(val)

    def runSweep(self, ind):
        r"""
        Wraps the ``_updateBase__function``, so that this will be the function that is always called to run the
        sweeps. This is not essential and could be removed, but it kind of creates a duck-typing with ``Sweep`` class,
        when we might want to use a nested sweep.
        """
        self._sweepIndex = ind-1 # pylint: disable=assigning-non-slot
        self._updateBase__function(self) # pylint: disable=no-member

class Sweep(qBase):
    r"""
    A container class for :class:`_sweep` objects and relevant methods for creating/removing and carrying
    multi-parameter sweeps. It stores :class:`_sweep` objects in its ``subSys``
    dictionary, and it has two additional private attributes to store sweep lengths and their multiplications, which are
    used in modularSweep and by :meth:`~_indicesForSweep` to carry multi parameter sweeps.
    Instances of this
    class are used as attributes of :class:`Simulation <quanguru.classes.Simulation.Simulation>` objects, and those are
    intended to be used for ``_sweep`` creations.
    """
    #: Used in default naming of objects. See :attr:`label <quanguru.classes.QUni.qUniversal.label>`.
    label = 'Sweep'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__inds', '__indMultip']

    # TODO init errors
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__inds = []
        r"""
        a list of ``sweepList`` length/s of multi-parameter ``_sweep`` object/s in ``subSys`` dictionary, meaning the
        length for simultaneously swept ``_sweep`` objects are not repeated. the values are
        appended to the list, if it is the first ``sweep`` to be included into ``subSys`` or ``multiParam is True``.
        """
        self.__indMultip = 1
        r"""
        the multiplication of all the indices in ``inds``. This value is used as the loop range by modularSweep.
        """
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def inds(self):
        r"""
        ``returns _Sweep__inds`` and there is no setter
        """
        return self._Sweep__inds

    @property
    def indMultip(self):
        r"""
        ``returns _Sweep__indMultip``, and there is no setter

        NOTE : The reason this property returns a pre-assingned value rather than calculating from the ``inds`` is to
        avoid calculating it over and over again, which could be avoided by checking if ``_Sweep__indMultip is None``,
        but that might create other issues, such as re-running the same simulation after a change in ``sweepList``
        length/s. It still can be improved, and it is possible to avoid such issues and get rid of :meth:`prepare`,
        which is called in ``run`` methods of ``Simulations``, by some modifications in these properties.
        """
        return self._Sweep__indMultip

    @property
    def sweeps(self):
        r"""
        The sweeps property wraps ``subSys`` dictionary to create new terminology, it works exactly as
        :meth:`subSys <quanguru.classes.base.qBase.subSys>`.
        """
        return self._qBase__subSys # pylint: disable=no-member

    @sweeps.setter
    def sweeps(self, sysDict):
        super().addSubSys(sysDict)

    @_recurseIfList
    def removeSweep(self, sys):
        r"""
        Removes a ``_sweep`` it self, or all the ``_sweep`` objects that contain a particular ``sys`` in it.
        Since, it uses :meth:`removeSubSys <quanguru.classes.base.qBase.removeSubSys>`, it works exactly the same,
        meaning
        names/aliases/objects/listOfObjects can be used to remove.

        If the argument ``sys`` is an :class:`_sweep` object, this method calls
        :meth:`removeSubSys <quanguru.classes.base.qBase.removeSubSys>` (since ``_sweep`` objects are stored in
        ``subSys`` dictionary of ``Sweep`` objects).

        Else, it calls the :meth:`removeSubSys <quanguru.classes.base.qBase.removeSubSys>` on every ``_sweep`` in its
        ``subSys`` dictionary (since ``systems`` are stored in ``subSys`` dictionary of ``_sweep`` objects).
        """
        if isinstance(sys, _sweep):
            super()._removeSubSysExc(sys, _exclude=[])
        else:
            sweeps = list(self.subSys.values())
            for sweep in sweeps:
                sweep._removeSubSysExc(sys, _exclude=[]) #pylint:disable=protected-access
                if len(sweep.subSys) == 0:
                    super()._removeSubSysExc(sweep, _exclude=[])

    def createSweep(self, system=None, sweepKey=None, **kwargs):
        r"""
        Creates a instance of ``_sweep`` and assing its ``system`` and ``sweepKey`` to given system
        and sweepKey arguments of this method. Keyworded arguments are used to set the other attributes of the newly
        created ``_sweep`` object.

        Parameters
        ----------
        system : Any
            Since ``system`` property setter of ``_sweep`` behaves exactly as
            :meth:`subSys <quanguru.classes.base.qBase.subSys>` setter, this can be various things, from a single
            system to name/alias of the system, or from a class to a list/tuple contaning any combination
            of these.
        sweepKey : str
            Name of the attribute of system/s that will be swept


        :returns: The new ``_sweep`` instance.
        """
        if system is None:
            system = self.superSys.superSys
            if system is None:
                raise ValueError('?')

        newSweep = _sweep(superSys=self, subSys=system, sweepKey=sweepKey, **kwargs)
        if system is not self.auxObj:
            if not isinstance(sweepKey, str):
                raise ValueError("key")
                # newSweep._aux = True #pylint: disable=protected-access

            if hasattr(list(newSweep.subSys.values())[0], sweepKey):
                for sys in newSweep.subSys.values():
                    if not hasattr(sys, sweepKey):
                        raise AttributeError("?")
            else:
                # FIXME if the system does not have the given attribute and that is an error
                # (eg wrong attr name/typo given), this still works without an error. this should be an explicit setting
                newSweep._aux = True #pylint: disable=protected-access
            # ignores when object is given with a key it does not have
            #elif not hasattr(list(newSweep.subSys.values())[0], sweepKey):
            #    newSweep._aux = True #pylint: disable=protected-access
        super().addSubSys(newSweep)
        return newSweep

    def prepare(self):
        r"""
        This method is called inside ``run`` method of ``Simulation`` object/s to update ``inds`` and ``indMultip``
        attributes/properties. The reason for this a bit argued in :meth:`indMultip`, but it is basically to ensure that
        any changes to ``sweepList/s`` or ``multiParam/s`` are accurately used/reflected (especially on re-runs).
        """
        if len(self.subSys) > 0:
            self._Sweep__inds = [] # pylint: disable=assigning-non-slot
            for indx, sweep in enumerate(self.subSys.values()):
                if ((sweep.multiParam is True) or (indx == 0)):
                    self._Sweep__inds.insert(0, len(sweep.sweepList))
            self._Sweep__indMultip = reduce(lambda x, y: x*y, self._Sweep__inds) # pylint: disable=assigning-non-slot

    def runSweep(self, indList):
        r"""
        called in modularSweep to run all the ``_sweep``
        objects in a ``Sweep``. indices from a given list ``indList`` are used by the ``runSweep`` method of ``_sweep``
        objects, and it switches to a new index, if the ``multiParam is True``. This means that the ``_sweeps``
        **should be created in an order** such that ``_sweep`` objects that run simultaneously **have to be** added to
        ``subSys`` one after the other. Also, for nested Sweeps, the indList should be a properly nested list.
        """
        indx = 0
        for sweep in self.sweeps.values():
            if sweep.multiParam is True:
                indx += 1
            sweep.runSweep(indList[indx])

    # function used in modular sweep
    @staticmethod
    def _indicesForSweep(ind, *args):
        r"""
        method used in modularSweep to calculate indices for each sweepList from the loop counter ``ìnd`` using the
        total lengths ``*args``. It is hard to describe the exact calculation in words, but it is trivial to see from
        the math (TODO) which i will do later.

        the loop counter can at max be :math:`(\prod_{i = 1}^{len(args)} args[i]) - 1`, and multi-parameter
        sweeps loops the first sweepList while fixing the others. So, at each inp = args[0] the first list should
        start from zero, and the second list moves to next item, and this relation goes up in the chain, e.g. at each
        inp = args[0]*args[1], the index of the third need to be increased, and so on. Therefore, the current index for
        the first sweepList simply is the reminder of inp with args[0].
        """
        indices = []
        for arg in args:
            remain = ind%arg
            ind = (ind-remain)/arg
            indices.insert(0, int(remain))
        return indices
