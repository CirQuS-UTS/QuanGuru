"""
    This module contain two classes related to sweep functionality.

    Classes
    -------
    | :class:`_sweep` : This class is used internally to actually store relevant sweep information for objects/s.
    | :class:`Sweep` : This class can be seen as a container for different ``_sweep`` objects, but it is the one that is
        actually going to be used.

    NOTE : Both of these classes are not actually intended to be instanciated by outside the library.
    :class:`Simulation <qTools.classes.Simulation.Simulation>` objects **has** ``Sweep/s`` as their attributes, and
    ``_sweep/s`` are intended to be created by calling the relevant methods over ``Simulation.Sweep``.
"""

from functools import reduce
from numpy import arange, logspace

from qTools.classes.updateBase import updateBase
from qTools.classes.QUni import qUniversal

__all__ = [
    'Sweep'
]

class _sweep(updateBase): # pylint: disable=too-many-instance-attributes
    """
    This class essentially has a list of values, a dictionary of objects (``subSys``), and a key (name of an attribute).
    The purpose is to use the key to change the value of the corresponding attribute for all the objects to a value from
    the list of values. Rest of the attributes are used to create the list of values in different cases.

    Attributes
    ----------
    sweepList : list
        A list of values can directly be assigned, and the other attributes are not needed in this case.
    sweepMin & sweepMax & sweepStep : float
        These are used to create a list values from ``sweepMin`` to ``sweepMax``. ``sweepStep`` is either number of
        steps from min-to-max or step-size. The first one is used in the case of logarithmic sweeps, and the latter in
        linear.
    logSweep : bool
        If this is true, the list of values will logarithmically (base 10) be separated, in this case ``sweepStep`` has
        to an ``int``.
    multiParam : bool
        This should be set to ``True``, if there are more than one `_sweep` objects exist, but they are not used
        simultaneously instead one is swept while the other is fixed.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = '_sweep'

    #: a list of str (attribute names) to be used with save method, it extends
    #: :attr:`toBeSaved <qTools.classes.QUni.qUniversal.toBeSaved>` list.
    toBeSaved = updateBase.toBeSaved.extendedCopy(['sweepMax', 'sweepMin', 'sweepStep', 'sweepList', 'logSweep',
                                                   'multiParam'])

    __slots__ = ['sweepMax', 'sweepMin', 'sweepStep', '_sweepList', 'logSweep', 'multiParam', 'index']

    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__()

        self._updateBase__function = self._defSweep # pylint: disable=assigning-non-slot

        self.sweepMax = None
        self.sweepMin = None
        self.sweepStep = None
        self._sweepList = None
        self.logSweep = False
        self.multiParam = False
        self.index = None

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def sweepFunction(self):
        """
        The sweepFunction property:

        - **getter** : ``returns _updateBase__function`` which is used in custom sweeps
        - **setter** : sets ``_updateBase__function`` callable
        - **type** : ``callable``
        """

        return self._updateBase__function # pylint: disable=no-member

    @sweepFunction.setter
    def sweepFunction(self, func):
        self._updateBase__function = func # pylint: disable=assigning-non-slot

    @property
    def sweepKey(self):
        """
        The sweepKey property:

        - **getter** : ``returns _updateBase__key`` which is the name of an attribute to be swept, this property exists
          to create terminology
        - **setter** : sets ``_updateBase__key`` string
        - **type** : ``str``
        """

        return self._updateBase__key # pylint: disable=no-member

    @sweepKey.setter
    def sweepKey(self, keyStr):
        self._updateBase__key = keyStr # pylint: disable=assigning-non-slot

    @property
    def sweepList(self):
        """
        The sweepList property:

        - **getter** : ``returns _updateBase__key`` if it is ``not None``, otherwise, creates it using the min-max-step
          informations.
          TODO : this should raise an error, if neither a list nor sufficient/correct information to create a list is
          given.
        - **setter** : sets ``_sweepList`` to a given list
        - **type** : ``list``
        """

        if self._sweepList is None:
            if self.logSweep is False:
                self._sweepList = arange(self.sweepMin, self.sweepMax + self.sweepStep, # pylint: disable=no-member
                                         self.sweepStep) # pylint: disable=no-member
            elif self.logSweep is True:
                self._sweepList = logspace(self.sweepMin, self.sweepMax,
                                           num=self.sweepStep, base=10.0) # pylint: disable=no-member
        return self._sweepList

    @sweepList.setter
    def sweepList(self, sList):
        self._sweepList = sList

    @staticmethod
    def _defSweep(self): # pylint: disable=bad-staticmethod-argument
        """
        This is the default sweep function, see __init__, the ``_timeBase__function`` points to this.

        The method that uses all the objects to do simulations with sweeps uses length of ``sweepList/s`` (stored in
        __inds attribute of :class:`Sweep`) and converts it to a relevant list of indices using modular arithmetic (
        which is introduced for multi-parameter sweeps), and those indices are fed to :meth:`runSweep`, which does
        calls nothing but calls the ``_updateBase__function`` by feeding the ``ind``. So, whatever the
        ``_updateBase__function`` is, it is the actual function to make updates to attribute (given by ``key``).
        This method is the default the ``_updateBase__function``, and it just calls the
        :meth:`_runUpdate <qTools.classes.updateBase.updateBase._runUpdate>` by feeding it the value from the
        ``sweepList`` at the position ``ind``. :meth:`_runUpdate <qTools.classes.updateBase.updateBase._runUpdate>`
        function just sets the attribute (for the given key) of every ``subSys`` to a given value (``val``).

        Parameters
        ----------
        ind : int
            Index of the value from ``sweepList``
        """

        val = self.sweepList[self.index]
        self._runUpdate(val)

    def runSweep(self, ind):
        """
        This method wraps the ``_updateBase__function``, so that this will be the function that is always called to run
        sweeps. This is not essential and could be removed, but it kind of creates a duck-typing with ``Sweep`` class.
        """

        self.index = ind
        self._updateBase__function(self) # pylint: disable=no-member

class Sweep(qUniversal):
    """
    This class can be considered as a container for :class:`_sweep` objects and relevant methods. Instances of this
    class are used as attributes of :class:`Simulation <qTools.classes.Simulation.Simulation>` objects, and those are
    intended to be used for ``_sweep`` creations. This class inherits from
    :class:`qUniversal <qUniversal.classes.QUni.qUniversal>` and stores :class:`_sweep` objects in its ``subSys``
    dictionary, and it has two additional attributes. Againg, the attributes are private and the explanation below
    contain the relevant property, name-mangled attribute , and pure attribute names separated by `or`.

    Attributes
    ----------
    inds or _Sweep__inds or __inds : List[int]
        This is a list of ``sweepList`` length/s of ``_sweep`` **some** of the object/s in ``subSys`` dictionary. The
        reason for **some** is that this list is introduced to be used with multi-parameter sweeps, and the values are
        appended to the list, if it is the first ``sweep`` to be included into ``subSys`` or ``multiParam is True``.
    indMultip or _Sweep__indMultip or __indMultip : int
        This is just the multiplication of all the indices in ``inds``. The actual function that uses all the objects
        to perform a simulation with sweeps, uses values from 0-indMultip as loop counter, and another function using
        some modular arithmetics creates a list of indices from the loop counter to use it for updates.
    """

    #: Total number of instances of the class
    instances: int = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'Sweep'

    __slots__ = ['__inds', '__indMultip']

    # TODO init errors
    def __init__(self, **kwargs):
        super().__init__()

        self.__inds = []
        self.__indMultip = 1

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        """
        This method extends the :meth:`save <qTools.classes.QUni.qUniversal.save>` of :class:`qUniversal` by also
        calling the ``save()`` on the objects in ``subSys`` dictionary.
        """

        saveDict = super().save()
        sweepsDict = {}
        for sw in self.subSys.values():
            sweepsDict[sw.name] = sw.save()
        saveDict['sweeps'] = sweepsDict
        return saveDict

    @property
    def inds(self):
        """
        The ind property:

        - **getter** : ``returns _Sweep__inds``
        - **setter** : there is no setter
        """

        return self._Sweep__inds

    @property
    def indMultip(self):
        """
        The indMultip property:

        - **getter** : ``returns _Sweep__indMultip``
        - **setter** : there is no setter

        NOTE : The reason this property returns a pre-assingned value rather than calculating from the ``inds`` is to
        avoid calculating it over and over again, which could be avoided by checking if ``_Sweep__indMultip is None``,
        but that might create other issues, such as re-running the same simulation after a change in ``sweepList``
        length/s. It still can be improved, and it is possible to avoid such issues and get rid of :meth:`prepare`,
        which is called in ``run`` methods of ``Simulations``, by some modifications in these properties.
        """

        return self._Sweep__indMultip

    @property
    def sweeps(self):
        """
        The sweeps property wraps ``subSys`` dictionary to create new terminology, it basically:

        - **getter** : ``returns subSys`` dictionary.
        - **setter** : works exactly as :meth:`subSys <qTools.classes.QUni.qUniversal.subSys>` setter.
        """

        return self._qUniversal__subSys # pylint: disable=no-member

    @sweeps.setter
    def sweeps(self, sysDict):
        super().addSubSys(sysDict)

    def removeSweep(self, sys):
        """
        A method to remove a ``_sweep`` it self, or all the ``_sweep`` objects that contain a particular ``sys`` in it.

        If the argument ``sys`` is an :class:`_sweep` object, this method calls
        :meth:`removeSubSys <qTools.classes.QUni.qUniversal.removeSubSys>` (since ``_sweep`` objects are stored in
        ``subSys`` dictionary of ``Sweep`` objects).

        Else, it calls the :meth:`removeSubSys <qTools.classes.QUni.qUniversal.removeSubSys>` on every ``_sweep`` in its
        ``subSys`` dictionary (since ``systems`` are stored in ``subSys`` dictionary of ``_sweep`` objects).
        """

        if isinstance(sys, _sweep):
            self.removeSubSys(sys)
        else:
            for sweep in self.subSys.values():
                sweep.removeSubSys(sys)

    def createSweep(self, system=None, sweepKey=None, **kwargs):
        """
        This method creates a new instance of ``_sweep`` and assing its ``system`` and ``sweepKey`` to given system
        and sweepKey arguments of this method. Keyworded arguments are used to set the other attributes of the newly
        created ``_sweep`` object.

        Parameters
        ----------
        system : Any
            Since ``system`` property setter of ``_sweep`` behaves exactly as
            :meth:`subSys <qTools.classes.QUni.qUniversal.subSys>` setter, this can be various things, from a single
            sytems to name of the system, or from a class to name of class, or a list/dict contaning any combination
            of these
        sweepKey : str
            Name of the attribute of system/s that will be swept


        :returns: The new ``_sweep`` instance.
        """

        if system is None:
            system = self.superSys.superSys
            if system is None:
                raise ValueError('?')

        newSweep = _sweep(superSys=self, subSys=system, sweepKey=sweepKey, **kwargs)
        if not isinstance(sweepKey, str):
            newSweep._aux = True #pylint: disable=protected-access
        elif not hasattr(list(newSweep.subSys.values())[0], sweepKey):
            newSweep._aux = True #pylint: disable=protected-access
        elif hasattr(list(newSweep.subSys.values())[0], sweepKey):
            for sys in newSweep.subSys.values():
                if not hasattr(sys, sweepKey):
                    raise AttributeError("?")
        super().addSubSys(newSweep)
        return newSweep

    def prepare(self):
        """
        This method is called inside ``run`` method of ``Simulation`` object/s to update ``inds`` and ``indMultip``
        attributes/properties. The reason for this a bit argued in :meth:`indMultip`, but it is basically to ensure that
        any changes to ``sweepList/s`` or ``multiParam/s`` are accurately used/reflected.
        """

        if len(self.subSys) > 0:
            self._Sweep__inds = [] # pylint: disable=assigning-non-slot
            for indx, sweep in enumerate(self.subSys.values()):
                if ((sweep.multiParam is True) or (indx == 0)):
                    self._Sweep__inds.insert(0, len(sweep.sweepList))
            self._Sweep__indMultip = reduce(lambda x, y: x*y, self._Sweep__inds) # pylint: disable=assigning-non-slot

    def runSweep(self, indList):
        """
        This method is called in proper parts of the actual function running the simulations to run all the ``_sweep``
        objects in a ``Sweep``. indices from a given list ``indList`` are past to the ``runSweep`` method of ``_sweep``
        objects, and it switches to a new index, if the ``multiParam is True``. This means that the ``_sweeps``
        **should be created in an order** such that ``_sweep`` objects that run simultaneously **have to be** added to
        ``subSys`` one after the other.
        """

        indx = 0
        for sweep in self.sweeps.values():
            if sweep.multiParam is True:
                indx += 1
            sweep.runSweep(indList[indx])

    # function used in modular sweep
    @staticmethod
    def _indicesForSweep(ind, *args):
        indices = []
        for arg in args:
            remain = ind%arg
            ind = (ind-remain)/arg
            indices.insert(0, int(remain))
        return indices
