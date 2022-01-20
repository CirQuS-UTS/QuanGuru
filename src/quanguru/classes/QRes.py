r"""
    Contains qResults, qResBase, and qResBlank classes used in storing various types of simulation results.

    .. currentmodule:: quanguru.classes.QRes

    .. autosummary::

        qResBlank
        qResBase
        qResults

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `qResBlank`                |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `qResBase`                 |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `qResults`                 |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============

"""
from collections import defaultdict

from .base import qBase, aliasDict

__all__ = [
    'qResults'
]

#: used as the slots in :class:`~qResBlank` and :class:`~qResBase`.
resKeys = ['__results', '__states', '__resultsLast', '__statesLast', '__average', '__calculated']

class qResBlank:
    r"""
    This is a simplified version of :class:`~qResBase`, and it is used in time evolution returns of multi-processing
    (pool.map()). Since :class:`~qResBase` inherits from :class:`~named`, they contain a dictionary with :class:`~named`
    instances (incl. quantum system and protocol with large matrices), and multi-processing returns a duplicate/copy
    of each object in the dictionary.
    Introduced to save memory, this class is introduced and :meth:`~qResults._copyAllResBlank` is used in multi-process
    returns to write the results into qResBlank instances, which does not inherit from :class:`~named` (thus no
    duplicate of instances).

    # NOTE There must be a better solution, but enough for the time being
    """
    __slots__ = resKeys
    def __init__(self):
        super().__init__()
        #: Stores the quantities calculated at each step of the time evolution
        self.__results = defaultdict(list)
        #: Stores the time averaged quantities
        self.__average = defaultdict(list)
        #: Stores the last list of results when sweeping parameters
        self.__resultsLast = defaultdict(list)
        #: Stores the time-evolved states
        self.__states = defaultdict(list)
        #: Stores the last list of time-evolved states when sweeping parameters
        self.__statesLast = defaultdict(list)
        #: Stores the quantities calculated by the calculate methods (see :class:`~computeBase`)
        self.__calculated = defaultdict(list)

    @property
    def results(self):
        r"""
        returns the protected attribute ``self._qResBlank__resultsLast``
        """
        return self._qResBlank__resultsLast # pylint: disable=no-member

    @property
    def states(self):
        r"""
        returns the protected attribute ``self._qResBlank__statesLast``
        """
        return self._qResBlank__statesLast # pylint: disable=no-member

class qResBase(qBase):
    r"""
    Base class for qResults implements the defaultdict attributes (used to store various quantities) and property/method
    to store quantities in them. `Last` ones store a single time trace (the very last one) and are reset in the
    beginning of each time evolution. At the each time trace, the Last are either moved into full dictionary or copied
    into a :class:`~qResBlank` depending, respectively, on single or multi-process. This class is extended by
    :class:`~qResults` to implement the method dealing with the details of moving the Last into full.
    """
    #: (**class attribute**) class label used in default naming
    label = 'qResBase'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = resKeys
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: Stores the quantities calculated at each step of the time evolution
        self.__results = defaultdict(list)
        #: Stores the time averaged quantities
        self.__average = defaultdict(list)
        #: Stores the last list of results when sweeping parameters
        self.__resultsLast = defaultdict(list)
        #: Stores the time-evolved states
        self.__states = defaultdict(list)
        #: Stores the last list of time-evolved states when sweeping parameters
        self.__statesLast = defaultdict(list)
        #: Stores the quantities calculated by the calculate methods (see :class:`~computeBase`)
        self.__calculated = defaultdict(list)
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def calculated(self):
        r"""
        returns the protected attribute ``self._qResBase__calculated`` and the setter appends the given value into
        the defaultdict from the given (key, val) list/tuple.
        """
        return self._qResBase__calculated # pylint: disable=no-member

    @calculated.setter
    def calculated(self, keyValList):
        self._qResBase__calculated[keyValList[0]].append(keyValList[1]) # pylint: disable=no-member

    @property
    def results(self):
        r"""
        returns the protected attribute ``self._qResBase__resultsLast`` and the setter appends the given value into
        the defaultdict from the given (key, val) list/tuple. Uses the Last, so that it stores the results into proper
        dictionary during time evolution, and other methods in the :class:`~qResults` are called at the end of time
        evolutions to make sure that (by equating this to the regular results dictionary) this returns the full results.
        """
        return self._qResBase__resultsLast # pylint: disable=no-member

    @results.setter
    def result(self, keyValList):
        self._qResBase__resultsLast[keyValList[0]].append(keyValList[1]) # pylint: disable=no-member

    @results.setter
    def resAverage(self, keyValList):
        r"""
        stores the averaged value of given (key, value) pairs.
        # FIXME does not work if storing say ndarray
        """
        valCountPair = self._qResBase__average.pop(keyValList[0], None) # pylint: disable=no-member
        if valCountPair is not None:
            val = valCountPair[0]
            counter = valCountPair[1]
            avg = ((counter*val) + keyValList[1])/(counter + 1)
            self._qResBase__average[keyValList[0]] = [avg, counter+1] # pylint: disable=no-member
            self._qResBase__resultsLast[keyValList[0]] = avg # pylint: disable=no-member
        else:
            val = keyValList[1]
            self._qResBase__average[keyValList[0]] = [val, 1] # pylint: disable=no-member
            self._qResBase__resultsLast[keyValList[0]] = val # pylint: disable=no-member

    def resultsMethod(self, key, value, average=False):
        r"""
        This method also stores results and is an alternative to :py:attr:`~results` property. It is aimed to provide
        enriched syntax. Might also implement average.
        """
        if not average:
            if isinstance(key, str):
                self._qResBase__resultsLast[key].append(value) # pylint: disable=no-member
            elif isinstance(value, str):
                self._qResBase__resultsLast[value].append(key) # pylint: disable=no-member
        #else:
        #    valCountPair = self._qResBase__average.pop(key, None)
        #    if valCountPair is not None:
        #        val = valCountPair[0]
        #        counter = valCountPair[1]
        #        # FIXME does not work if storing say ndarray
        #        avg = ((counter*val) + value)/(counter + 1)
        #        self._qResBase__average

    @property
    def states(self):
        r"""
        returns the _qResBase__statesLast. The states are stored by the simulation objects, so there is no setter.
        Uses the Last, so that it stores the results into proper
        dictionary during time evolution, and other methods in the :class:`~qResults` are called at the end of time
        evolutions to make sure that (by equating this to the regular results dictionary) this returns the full results.
        """
        return self._qResBase__statesLast # pylint: disable=no-member

class qResults(qResBase):
    r"""
    Extends the :class:`~qResBase` and introduces methods to reset, organise, copy, etc. for the results/states/etc.
    The results/states/etc are stored in the correspoding Last during time evolution and are appended into a single list
    ,which, at the end of the simulation, is re-shaped by :meth:`~_reShape` method using the sweep.indices.

    The time-evolution methods do not need to return anything (in single process) since every thing is stored in
    qResults objects. However, pool.map() need to return the relevant results out of the pickled program, and it is
    easier and consistent to return the objects storing the results. Due to the, named._allInstacesDict dictionary in
    their attributes, returning qResults out of the map causes duplication of all the named instances incl. quantum
    system and protocols with large matrices. Therefore, an alternative method :meth:`~_copyAllResBlank` is used to
    copy the dictionaries containing the results into :class:`~qResBlank` instances, and duplication of named instances
    is avoided (since qResBlank does not inherit from named, ie. does not contain the _allInstacesDict).
    """
    #: (**class attribute**) class label used in default naming
    label = 'qResults'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    #: (**class attribute**) dictionary to store all the qResults instances, used in several places.
    _allResults = aliasDict()

    __slots__ = ['allResults']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        kwargs.pop('allResults', None)
        #: required to properly pickle _allResults dictionary
        self.allResults = qResults._allResults
        self.allResults[self.name] = self # pylint: disable=no-member
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def _copyAllResBlank(self):
        r"""
        method to copy the dictionaries of all the :class:`~qResults` instances into new :class:`~qResBlank` instances,
        and store them into another dictionary with the name of the corresponding qResults instance. The returned
        dictionary mimics the _allResults dictionary of qResults and is used as the return of the pool.map().
        At the end of the simulation, these dictionaries are used to write back the results into actual _allResults
        by :meth:`~_organiseMultiProcRes`.
        """
        allResCopy = {}
        for sys in self.allResults.values():
            newQRes = qResBlank()
            newQRes._qResBlank__results = sys._qResBase__results # pylint: disable=assigning-non-slot
            newQRes._qResBlank__average = sys._qResBase__average # pylint: disable=assigning-non-slot
            newQRes._qResBlank__states = sys._qResBase__states # pylint: disable=assigning-non-slot
            newQRes._qResBlank__resultsLast = sys._qResBase__resultsLast # pylint: disable=assigning-non-slot
            newQRes._qResBlank__statesLast = sys._qResBase__statesLast # pylint: disable=assigning-non-slot
            newQRes._qResBlank__calculated = sys._qResBase__calculated # pylint: disable=assigning-non-slot
            allResCopy[sys.name] = newQRes
        return allResCopy

    def _reset(self):
        r"""
        Method to empty (creates and assigned them to new defaultdicts) all the previous results/states dicts.
        """
        for qRes in self.allResults.values():
            qRes._qResBase__results = defaultdict(list)
            qRes._qResBase__average = defaultdict(list)
            qRes._qResBase__states = defaultdict(list)
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)
            qRes._qResBase__calculated = defaultdict(list)

    def _resetLast(self):
        r"""
        Method to reset the Last dictionaries only, and it is called before the time evolution to empty the Last. After
        the time evolution (depending on single/multi-process), these are moved to regular results by the corresponding
        methods below. At the end of the simulation, these are made equal to regular, so that the setter/getter
        properties of results/states (returning Last ones) works during and after the simulation to set/get the results.
        """
        for qRes in self.allResults.values():
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)
            qRes._qResBase__average = defaultdict(list)

    def _organiseMultiProcRes(self, results, inds):
        r"""
        multi-processing returns are dictionaries containing :class:`~qResBlank` instances with single time trace
        (see :meth:`~_copyAllResBlank`), this method re-writes the results into corresponding :class:`~qResults` objects
        and re-shapes them into correct sweep and time trace structure. Calls other methods of the class for these.
        """
        for res in results:
            for keyUni, valUni in res.items():
                self._organise(keyUni, valUni)
        self._finaliseAll(inds)

    @classmethod
    def _finaliseAll(cls, inds):
        r"""
        Calls the :meth:`~_finalise` method, which reshapes the results/states list using the given list of indices
        (ie. length of each sweep), on every qResults instances in the _allResults dictionary.
        """
        for qres in cls._allResults.values():
            qres._finalise(inds)

    @staticmethod
    def _organise(keyUni, valUni):
        r"""
        At the end of time evolution, :meth:`~_organise` creates a single list containing all the results/states for
        each key.
        """
        for key, val in valUni.results.items():
            qResults._allResults[keyUni]._qResBase__results[key].append(val) # pylint: disable=no-member

        for key1, val1, in valUni.states.items():
            qResults._allResults[keyUni]._qResBase__states[key1].append(val1) # pylint: disable=no-member

    def _organiseSingleProcRes(self):
        r"""
        organising the single-process results by simply calling :meth:`~_organise` on every qResults instance in
        allResults dictionary. This needs to be finalised, ie. creates a single list containing every sweep, so the list
        has to be reshaped.
        """
        for keyUni, valUni in self.allResults.items():
            self._organise(keyUni, valUni)

    def _finalise(self, inds):
        r"""
        method to reshape the results/states list using the given list of indices (ie. length of each sweep).
        """
        for key, val in self._qResBase__results.items(): # pylint: disable=no-member
            if inds != []:
                self._qResBase__results[key], _ = self._reShape(val, list(reversed(inds))) # pylint: disable=no-member
            else:
                self._qResBase__results[key] = val[0]  # pylint: disable=no-member

        for key1, val1 in self._qResBase__states.items(): # pylint: disable=no-member
            if inds != []:
                self._qResBase__states[key1], _ = self._reShape(val1, list(reversed(inds))) # pylint: disable=no-member
            else:
                self._qResBase__states[key1] = val1[0] # pylint: disable=no-member
        self._qResBase__resultsLast = self._qResBase__results # pylint: disable=assigning-non-slot, no-member
        self._qResBase__statesLast = self._qResBase__states # pylint: disable=assigning-non-slot, no-member

    @staticmethod
    def _reShape(lis, inds, counter=0, totalCount=0):
        r"""
        a recursive method to reshape a list/listOfLists into given indices form.
        """
        newList = []
        if counter < (len(inds)-1):
            counter += 1
            for _ in range(inds[counter-1]):
                nList, totalCount = qResults._reShape(lis, inds, counter, totalCount)
                newList.append(nList)
        else:
            for _ in range(inds[counter]):
                lisToAppend = lis[totalCount]
                if isinstance(lisToAppend, list):
                    if len(lisToAppend) == 1:
                        lisToAppend = lisToAppend[0]
                newList.append(lisToAppend)
                totalCount += 1
            return (newList, totalCount)
        return (newList, totalCount)
