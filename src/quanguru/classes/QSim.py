"""
    Contains :class:`Simulation` and :class:`_poolMemory` classes.

    .. currentmodule:: quanguru.classes.QSim

    .. autosummary::

        Simulation
        _poolMemory

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `Simulation`               |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_poolMemory`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============


"""

import sys
import platform
import multiprocessing

from .base import _recurseIfList, named
from .QSimBase import timeBase
from .QSweep import Sweep
from .modularSweep import runSimulation
from .modularSweep import timeEvolBase
# pylint: disable = cyclic-import

class Simulation(timeBase):
    """
    Simulation class collects all the pieces together to run a simulation. Its ``subSys`` dictionary contains
    :class:`protocols <quanguru.classes.QPro.genericProtocol>`, :class:`quantum systems
    <quanguru.classes.QSys.genericQSys>`
    as ``key:value``, respectively. It has two :class:`sweeps <quanguru.classes.Sweep.Sweep>`, meaning 2 of its
    attributes
    are ``Sweep`` objects. Its ``run`` method, after running some preparations, runs the actual function/s that run
    ``Sweeps`` and evolve the system by calling ``evolFunc`` attribute of ``Simulation`` object, which is a function
    that, by default, calls ``.unitary`` method on protocols, which by default creates the unitary by matrix
    exponentiation, and evolves the system by a matrix multiplication of the ``.unitary`` with the ``.initial state``.

    Avaliable methods of solution in the libray are going to be increased in time, and different methods will be used
    by re-assigning the ``evolFunc``. Additionally, this will be used for interfacing the library with other tools.
    The sweeps just change the value for some system/simulation parameters, which are just object attributes, so they
    are generic and general enough to be independent of ``evolFunc``, and, with this, it is aimed to increase scope of
    sweeps.

    There are 3 cases in :meth:`addProtocol` that raises a ``TypeError``.
    TODO : errors are not properly implemented yet.
    """
    #: (**class attribute**) class label used in default naming
    label = 'Simulation'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0
    #: default evolution method. You can always assign a different evolution method for an instance of Simulation
    #: class, but by re-assigning this class attribute, you can change the evolution method for all the future instances
    _evolFuncDefault = timeEvolBase

    __slots__ = ['Sweep', 'timeDependency', 'evolFunc', '__index']

    # TODO init error decorators or error decorators for some methods
    def __init__(self, system=None, **kwargs):
        #self._reClass = qBaseSim
        super().__init__(_internal=kwargs.pop('_internal', False))

        #: sweep object that contains information about the systems and their parameters to be swept.
        #: TODO create tutorial
        #: This is used to run the simulation for several parameter sets, i.e. sweeping some parameters. This is an
        #: instance of :class:`Sweep <quanguru.classes.Sweep.Sweep>`. The use of this attribute in ``runSimulation``
        #: function is independent of ``evolFunc`` or time-dependent part of the simulation. This is simply to sweep
        #: multiple parameters.
        self.Sweep = Sweep(superSys=self)
        #: sweep object that contains information for parameters that will be changed as a function of time. Note that
        #: this is not the only way to make time-dependent parameters. Actually, the alternative in timeDependency in
        #: term objects is much better solution than this.
        #: TODO create tutorial
        #: This is used to define temporal change of some parameters, i.e. used for time-dependent cases. This attribute
        #: is used when **default** ``evolFunc`` is used with the **default** ``createUnitary`` method of protocols, and
        #: it can be avoided in other cases. This is required in digital simulations, where time dependency is discrete.
        self.timeDependency = Sweep(superSys=self)

        #: this is counter for the number of steps in the time evolution, so this counter times the step size gives the
        #: current time in evolution. this is intended purely for internal use.
        self.__index = -1

        #: default function that implements the actual time evolution in each step. TODO Create tutorial.
        #: This is the default evolution method, which calls ``.unitary`` attribute on protocols and matrix multiply the
        #: resultant unitary with the ``.initialState``. It is possible to use this with other solution methods where
        #: the evolution is obtained by matrix multiplication of state by the unitary, which is not necessarily obtained
        #: by matrix exponentiation or the time-dependency is not incorporated by ``timeDependency``.
        self.evolFunc = Simulation._evolFuncDefault

        if system is not None:
            self.addQSystems(system)

        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def _currentTime(self):
        r"""
        Returns the current time in time evolution, which is equal to the current number of steps in the evolution times
        the step size.
        """
        try:
            if isinstance(self._timeBase__bound, Simulation): # pylint: disable=no-member
                time = self._timeBase__bound._currentTime # pylint: disable=no-member
            else:
                time = self.stepSize*(self.__index+1)
        except: #pylint:disable=bare-except # noqa: E722
            time = 0
        return time

    @property
    def timeList(self):
        r"""
        Returns a list of the time points of the time evolution.
        """
        return [x*self.stepSize for x in range(self.stepCount+1)]

    @property
    def protocols(self):
        """
        Returns a list of protocols (``keys in subSys``) contained in this simulation.
        """
        return list(self.subSys.keys())

    def _freeEvol(self):
        """
        This function is meant purely for internal use. When a quantum system is added to a ``Simulation`` without
        providing a protocol, the key in ``subSys`` dictionary will be the default case inherited from
        :class:`qBase <quanguru.classes.base.qBase>`, i.e. name of the quantum system object. This method
        is called inside the :meth:`run` method to ensure that the key is switched to a ``freeEvolution``. By this
        we ensure that the default evolution is just a free evolution under the given systems Hamiltonian and explicit
        creation of a ``freeEvolution`` object is not required. These are achieved by replacing the ``str`` key by
        the ``freeEvolution`` object that, by default, exists as a parameter for every quantum system.
        The reason for not doing it right away after the meth:`addQSystems` is to create a flexible use, i.e. when a
        :meth:`addProtocol` is called to replace the ``freeEvolution``, there is no need to try reaching internally
        created object but just using the ``system.name`` for ``protocolRemove`` argument of :meth:`addProtocol`.
        """
        keys = self.protocols
        for key in keys:
            qSys = self.subSys[key]
            if not isinstance(key, named):
                self.subSys[qSys._freeEvol] = self.subSys.pop(key) # pylint: disable=protected-access
            else: # this may seem redundant, but this is to keep the order in which the systems are added
                self.subSys[key] = self.subSys.pop(key)

    @property
    def qSystems(self):
        """
        Returns a list of quantum systems (``values in subSys``) contained in this simulation.
        """
        return list(self.subSys.values())

    @property
    def qEvolutions(self):
        """
        The qEvolutions property returns actual protocols rather than simply returning (``keys in subSys``), which
        can be the system name before running the simulation, as in :meth:`protocols` property.
        """
        self._freeEvol()
        qPros = list(self.subSys.keys())
        return qPros if len(qPros) > 1 else qPros[0]

    def addQSystems(self, subS, Protocol=None, **kwargs):
        """
        Quantum systems and the corresponding protocols are, respectively, stored as the values and keys of ``subSys``
        dictionary, so this method extends :meth:`addSubSys <quanguru.classes.QUni.qUniversal>` method by an additional
        argument, i.e. ``Protocol`` to be used as the key, and also by creating the hierarchical

        Parameters
        ----------
        subS : [type]
            [description]
        Protocol : [type], optional
            [description], by default None

        Returns
        -------
        [type]
            [description]
        """
        if isinstance(subS, (list, tuple)):
            for qsys in subS:
                self.addQSystems(qsys, **kwargs)
        else:
            # this horrible solution needs to be fixed!
            if subS not in self._qBase__subSys.values(): # pylint: disable=no-member
                subS = super().addSubSys(subS, **kwargs)
                subS = self._qBase__subSys.pop(subS.name) # pylint: disable=no-member
            #print(subS)
            # TODO print a message, if the same system included more than once without giving a protocol

            if Protocol is not None: # .pop here is to keep the order in  which the systems are added
                self._qBase__subSys[Protocol] = subS # pylint: disable=no-member
            elif subS not in self._qBase__subSys.values(): # pylint: disable=no-member
                self._qBase__subSys[subS.name] = subS # pylint: disable=no-member
            #elif subS not in self._qBase__subSys.values(): # pylint: disable=no-member
            #    subS = super().addSubSys(subS, **kwargs)
            #elif (subS.name != Protocol) and (Protocol is not None):
            #    self._qBase__subSys[Protocol] = self.getByNameOrAlias(subS) # pylint: disable=no-member
            # TODO and above is to avoid recursive calls in _paramUpdated, but it is a temp solution
            # bug in kicked-top
            #if ((subS.simulation is not self) or (subS is not refSys)):
            #print(subS)
            if subS.simulation is not self:
                if self in subS.simulation._paramBound.values():
                    subS.simulation._paramBound.pop(self.name)
                subS.simulation._bound(self) # pylint: disable=protected-access
        return (subS, Protocol)

    def createQSystems(self, subSysClass, Protocol=None, **kwargs):
        r"""
        Create a quantum system of given ``subSysClass`` class and (optional) add a ``Protocol`` for it. ``kwargs`` here
        are used for setting the parameters of newly created quantum system.
        """
        newSys, Protocol = self.addQSystems(subSysClass, Protocol, **kwargs)
        return (newSys, Protocol)

    @_recurseIfList
    def removeQSystems(self, subS):
        r"""
        Remove a quantum system and corresponding sweeps from the simulation.
        """
        #for key, subSys in self._qBase__subSys.items(): # pylint: disable=no-member
        #    if ((subSys is subS) or (subSys.name == subS)):
        super()._removeSubSysExc(subS, _exclude=[]) # pylint: disable=no-member
        #print(subS.name + ' and its protocol ' + key.name + ' is removed from qSystems of ' + self.name)
        self.removeSweep([subS, subS.simulation, subS._freeEvol, subS._freeEvol.simulation])

    @_recurseIfList
    def removeSweep(self, system):
        r"""
        Remove a sweep from the simulation.
        """
        self.Sweep.removeSweep(system)
        self.timeDependency.removeSweep(system)
        if ((isinstance(system, Simulation)) and (system is not self)):
            system.removeSweep(system)

    @_recurseIfList
    def removeProtocol(self, Protocol):
        r"""
        Remove a protocoal and corresponding sweeps from the simulation.
        """
        # FIXME what if freeEvol case, protocol then corresponds to qsys.name before simulation run
        #  or a freeEvol obj after run
        qsys = self._qBase__subSys.pop(Protocol, None) # pylint: disable=no-member
        if qsys is not None:
            self.removeSweep([Protocol, Protocol.simulation])
            if qsys not in self.qSystems:
                self.removeSweep(qsys)

    def addProtocol(self, protocol=None, system=None, protocolRemove=None):
        r"""
        Add a ``protocol`` for the (optional) ``system`` and (optional) remove an existing protocol ``protocolRemove``.
        """
        # TODO Decorate this
        qSysClass = named
        if isinstance(protocol, list):
            # should protocolRemove be a list ?
            for p in protocol:
                protocol = self.addProtocol(protocol=p, system=p.superSys, protocolRemove=protocolRemove)
        elif system is None:
            if isinstance(protocol, qSysClass):
                if isinstance(protocol.superSys, qSysClass):
                    protocol = self.addProtocol(protocol, protocol.superSys, protocolRemove)
                else:
                    raise TypeError('?')
            else:
                raise TypeError('?')
        elif isinstance(protocol.superSys, qSysClass):
            if system is protocol.superSys:
                self.addQSystems(subS=system, Protocol=protocol)
                self.removeProtocol(protocolRemove)
            else:
                raise TypeError('?')
        return protocol

    # overwriting methods from qBase
    def addSubSys(self, subS, Protocol=None, **kwargs): # pylint: disable=arguments-differ,arguments-renamed
        r"""
        Add a quantum system ``subS`` to the simulation and a (optional) ``protocol`` for it. ``kwargs`` can be used for
        setting parameters for the quantum system.
        """
        #newSys = super().addSubSys(subS, **kwargs)
        newSys, Protocol = self.addQSystems(subS, Protocol, **kwargs)
        return newSys

    def createSubSys(self, subSysClass, Protocol=None, **kwargs): # pylint: disable=arguments-differ
        r"""
        Create and add a quantum system of a given class ``subSysClass`` and a (optional) ``protocol`` for it.
        ``kwargs`` can be used for setting parameters for the quantum system.
        """
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.createQSystems(newSys, Protocol)
        return newSys

    @_recurseIfList
    def _removeSubSysExc(self, subSys, _exclude=[]): # pylint: disable=arguments-differ, dangerous-default-value
        r"""
        Remove a quantum system from the simulation.
        """
        self.removeQSystems(subSys)

    def __compute(self): # pylint: disable=dangerous-default-value
        r"""
        Internal compute method that passes the states to all the other compute functions of ``computeBase`` instances.
        """
        states = []
        for protocol in self.subSys.keys():
            states.append(protocol.currentState)
            if protocol.simulation.delStates is False:
                if protocol._internal: #pylint:disable=protected-access
                    self.qRes.states[protocol.superSys.name+'Results'].append(protocol.currentState)
                else:
                    self.qRes.states[protocol.name+'Results'].append(protocol.currentState)
        super()._computeBase__compute(states) # pylint: disable=no-member

    def run(self, p=None, coreCount=None, resetRes=True):
        r"""
        Call this function to run the simulation. It runs certain other preparation before running the simulation.

        Parameters
        ----------
        p : Boolean
            If ``True`` uses multiprocessing to run sweeps
        coreCount: int
            Number of cores used for multiprocessing, uses `` (avaliable number of cores) - 1`` as default.
        resetRes: Boolean
            If ``False``, does not delete the results from the previous run of the simulation. ``True`` by default.
        """
        if len(self.subSys.values()) == 0:
            self.addQSystems(self.superSys)
        self._freeEvol()
        for qSys in self.subSys.values():
            qSys._constructMatrices() # pylint: disable=protected-access
        for protocol in self.subSys.keys():
            protocol.prepare()
        self.Sweep.prepare()
        if resetRes:
            for qres in self.qRes.allResults.values():
                qres._reset() # pylint: disable=protected-access
        _poolMemory.run(self, p, coreCount)
        for key, val in self.qRes.states.items():
            self.qRes.allResults[key]._qResBase__states[key] = val
        # TODO Test this
        sdict = self.states
        return sdict[self.superSys.name+"Results"] if hasattr(self.superSys, 'name') else sdict[self.name+"Results"]

class _poolMemory: # pylint: disable=too-few-public-methods
    r"""
    handles creation and closing of pools for multi-processing (mp), some other small mp settings (such as setting
    set_start_method to fork etc.), and also calls
    :meth:`~runSimulation: method inside its only method :meth:`~run`.
    This class is introduced to make life a bit easier for user
    (ie. do not need to import multiprocessing or create&close pools) but also to avoid bunch of bugs due to pickling
    etc.
    """
    #: stores the number of cores used in multiprocessing
    coreCount = None
    #: boolean to ensure that the library does not try setting set_start_method to fork when a simulation is re-run.
    reRun = False

    @classmethod
    def run(cls, qSim, p, coreCount): # pylint: disable=too-many-branches
        r"""
        This is the only method in the class, and it carries the tasks described in the class description.
        """
        if ((platform.system() != 'Windows') and (cls.reRun is False)):
            cls.reRun = True
            if sys.version_info[1] >= 8:
                try:
                    #multiprocessing.get_start_method() != 'fork'
                    multiprocessing.set_start_method("fork")
                except: #pylint:disable=bare-except # noqa: E722
                    pass

        if p is True:
            if coreCount is None:
                if _poolMemory.coreCount is None:
                    _pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1) #pylint:disable=consider-using-with
                else:
                    _pool = multiprocessing.Pool(processes=_poolMemory.coreCount) #pylint:disable=consider-using-with
            elif isinstance(coreCount, int):
                _pool = multiprocessing.Pool(processes=coreCount) #pylint:disable=consider-using-with
            elif coreCount.lower() == 'all':
                _pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1) #pylint:disable=consider-using-with
            else:
                # FIXME should raise error
                print('error')
        elif p is False:
            _pool = None
        elif p is not None:
            # FIXME if p is not a pool, this should raise error
            _pool = multiprocessing.Pool(processes=p._processes) # pylint: disable=protected-access,consider-using-with
        elif p is None:
            if _poolMemory.coreCount is not None:
                _pool = multiprocessing.Pool(processes=_poolMemory.coreCount) #pylint:disable=consider-using-with
            else:
                _pool = None
        runSimulation(qSim, _pool)

        if _pool is not None:
            _poolMemory.coreCount = _pool._processes # pylint: disable=protected-access
            _pool.close()
            _pool.join()
