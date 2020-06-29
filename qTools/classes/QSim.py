"""
    This module contain :class:`Simulation` and :class:`_poolMemory` classes.
"""
import sys
import platform
import multiprocessing

from .base import _recurseIfList
from .baseClasses import timeBase
from .QSweep import Sweep
from .extensions.modularSweep import runSimulation
from .extensions.modularSweep import timeEvolBase
# pylint: disable = cyclic-import

class Simulation(timeBase):
    """
    Simulation class collects all the pieces together to run a simulation. Its ``subSys`` dictionary contain
    :class:`protocols <qTools.classes.QPro.genericProtocol>`, :class:`quantum systems <qTools.classes.QSys.genericQSys>`
    as ``key:value``, respectively. It has two :class:`sweeps <qTools.classes.Sweep.Sweep>`, meaning 2 of its attributes
    are ``Sweep`` objects. Its ``run`` method, after running some preparations, runs the actual function/s that run
    ``Sweeps`` and evolve the system by calling ``evolFunc`` attribute of ``Simulation`` object, which is a function
    that, by default, calls ``.unitary`` method on protocols, which by default creates the unitary by matrix
    exponentiation, and evolves the system by a matrix multiplication of the ``.unitary`` with the ``.initial state``.

    Avaliable methods of solution in the libray are going to be increased in time, and different methods will be used
    by re-assigning the ``evolFunc``. Additionally, this will be used for interfacing the library with other tools.
    The sweeps just change the value for some system/simulation parameters, which are just object attributes, so they
    are generic and general enough to be independent of ``evolFunc``, and, with this, it is aimed to increase scope of
    sweeps.


    Attributes
    ----------
    Sweep : ``Sweep``
        This is used to run the simulation for several parameter sets, i.e. sweeping some parameters. This is an
        instance of :class:`Sweep <qTools.classes.Sweep.Sweep>`. The use of this attribute in ``runSimulation`` function
        is independent of ``evolFunc`` or time-dependent part of the simulation. This is simply to sweep multiple
        parameters.
    timeDependency: ``Sweep``
        This is used to define temporal change of some parameters, i.e. used for time-dependent cases. This attribute
        is used when **default** ``evolFunc`` is used with the **default** ``createUnitary`` method of protocols, and it
        can be avoided in other cases. This is required in digital simulations, where time dependency is discrete.
    evolFunc: ``Callable``
        This is the default evolution method, which calls ``.unitary`` attribute on protocols and matrix multiply the
        resultant unitary with the ``.initialState``. It is possible to use this with other solution methods where
        the evolution is obtained by matrix multiplication of state by the unitary, which is not necessarily obtained
        by matrix exponentiation or the time-dependency is not incorporated by ``timeDependecy``.


    Raises
    ------
    TypeError
        There are 3 cases in :meth:`addProtocol` that raises a ``TypeError``.
        TODO : errors are not properly implemented yet.
    """

    #: This is the number of instances that are explicitly created by the user.
    _externalInstances: int = 0

    #: This is the number of instances that are created internally by the library.
    _internalInstances: int = 0

    #: Total number of instances of the class = ``_internalInstances + _externalInstances```
    instances = 0

    #: Used in default naming of objects. See :attr:`label <qTools.classes.QUni.qUniversal.label>`.
    label = 'Simulation'

    __slots__ = ['Sweep', 'timeDependency', 'evolFunc', '__index']

    # TODO init error decorators or error decorators for some methods
    def __init__(self, system=None, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))

        self.Sweep = Sweep(superSys=self)
        self.timeDependency = Sweep(superSys=self)

        #self.timeDependent = False
        self.__index = -1

        self.evolFunc = timeEvolBase

        if system is not None:
            self.addQSystems(system)

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        """
        This method extends the :meth:`save <qTools.classes.QUni.qUniversal.save>` of :class:`qUniversal` by calling the
        ``save`` method on the ``keys()`` (protocols) and ``values()`` (quantum systems) of its ``subSys`` dictionary,
        ``Sweep``, and ``timeDependency`` attributes, and then using the resultant dictionaries to extend ``saveDict``.
        """

        saveDict = super().save()
        sysDict = {}
        for pro, system in self.subSys.items():
            syDict = system.save()
            syDict[pro.name] = pro.save()
            sysDict[system.name] = syDict
        saveDict['qSystems'] = sysDict
        saveDict['Sweep'] = self.Sweep.save()
        saveDict['timeDependency'] = self.timeDependency.save()
        saveDict['timeList'] = self.timeList
        return saveDict

    @property
    def _currentTime(self):
        return self.stepSize*(self.__index+1)

    @property
    def timeList(self):
        return [x*self.stepSize for x in range(self.stepCount+1)]

    @property
    def protocols(self):
        """
        The protocols property returns the protocols (``keys in subSys``) as a ``list``.
        """

        return list(self.subSys.keys())

    def _freeEvol(self):
        """
        This function is meant purely for internal use. When a quantum system is added to a ``Simulation`` without
        providing a protocol, the key in ``subSys`` dictionary will be the default case inherited from
        :class:`qUniversal <qTools.classes.QUni.qUniversal>`, i.e. name of the quantum system object. This method
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
            if isinstance(key, str):
                self.subSys[qSys._freeEvol] = self.subSys.pop(key) # pylint: disable=protected-access
            else:
                self.subSys[key] = self.subSys.pop(key)

    @property
    def qSystems(self):
        """
        The qSystems property returns the quantum systems (``values in subSys``) as a ``list``.
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
        dictionary, so this method extends :meth:`addSubSys <qTools.classes.QUni.qUniversal>` method by an additional
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

        # TODO print a message, if the same system included more than once without giving a protocol
        subS = super().addSubSys(subS, **kwargs)
        self._paramBoundBase__paramBound[subS.name] = subS # pylint: disable=no-member
        if subS.simulation is not self:
            subS.simulation._bound(self) # pylint: disable=protected-access
        if Protocol is not None:
            self._qUniversal__subSys[Protocol] = self._qUniversal__subSys.pop(subS.name) # pylint: disable=no-member
        return (subS, Protocol)

    def createQSystems(self, subSysClass, Protocol=None, **kwargs):
        newSys, Protocol = self.addQSystems(subSysClass, Protocol, **kwargs)
        return (newSys, Protocol)

    @_recurseIfList
    def removeQSystems(self, subS):
        for key, subSys in self._qUniversal__subSys.items(): # pylint: disable=no-member
            if ((subSys is subS) or (subSys.name == subS)):
                super().removeSubSys(key, _exclude=[]) # pylint: disable=no-member
                print(subS.name + ' and its protocol ' + key.name + ' is removed from qSystems of ' + self.name)
                self.removeSweep([subSys, subSys.simulation, subSys._freeEvol, subSys._freeEvol.simulation])

    @_recurseIfList
    def removeSweep(self, system):
        self.Sweep.removeSweep(system)
        self.timeDependency.removeSweep(system)
        if ((isinstance(system, Simulation)) and (system is not self)):
            system.removeSweep(system)

    @_recurseIfList
    def removeProtocol(self, Protocol):
        # FIXME what if freeEvol case, protocol then corresponds to qsys.name before simulation run
        #  or a freeEvol obj after run
        qsys = self._qUniversal__subSys.pop(Protocol, None) # pylint: disable=no-member
        self.removeSweep([Protocol, Protocol.simulation])
        if qsys not in self.qSystems:
            self.removeSweep(qsys)

    def addProtocol(self, protocol=None, system=None, protocolRemove=None):
        # TODO Decorate this
        qSysClass = globals()['qBaseSim']
        if system is None:
            if isinstance(protocol, qSysClass):
                if isinstance(protocol.superSys, qSysClass):
                    protocol = self.addProtocol(protocol.superSys, protocol, protocolRemove)
                else:
                    raise TypeError('?')
            else:
                raise TypeError('?')
        elif isinstance(protocol.superSys, qSysClass):
            if system is protocol.superSys:
                self.addQSystems(system, protocol)
                self.removeProtocol(Protocol=protocolRemove)
            else:
                raise TypeError('?')
        return protocol

    # overwriting methods from qUniversal
    def addSubSys(self, subS, Protocol=None, **kwargs): # pylint: disable=arguments-differ
        newSys = super().addSubSys(subS, **kwargs)
        newSys, Protocol = self.addQSystems(newSys, Protocol)
        return newSys

    def createSubSys(self, subSysClass, Protocol=None, **kwargs): # pylint: disable=arguments-differ
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.createQSystems(newSys, Protocol)
        return newSys

    @_recurseIfList
    def removeSubSys(self, subS, _exclude=[]): # pylint: disable=arguments-differ, dangerous-default-value
        self.removeQSystems(subS)

    def __compute(self): # pylint: disable=dangerous-default-value
        states = []
        for protocol in self.subSys.keys():
            states.append(protocol.currentState)
            if protocol.simulation.delStates is False:
                self.qRes.states[protocol.name+'Results'].append(protocol.currentState)
        super()._computeBase__compute(states, sim=True) # pylint: disable=no-member

    def run(self, p=None, coreCount=None):
        if len(self.subSys.values()) == 0:
            self.addQSystems(self.superSys)
        self._freeEvol()
        for qSys in self.subSys.values():
            qSys._constructMatrices() # pylint: disable=protected-access
        for protocol in self.subSys.keys():
            protocol.prepare()
        self.Sweep.prepare()
        for qres in self.qRes.allResults.values():
            qres._reset() # pylint: disable=protected-access
        _poolMemory.run(self, p, coreCount)
        for key, val in self.qRes.states.items():
            self.qRes.allResults[key]._qResBase__states[key] = val
        return self.qRes

class _poolMemory: # pylint: disable=too-few-public-methods
    coreCount = None
    reRun = False

    @staticmethod
    def systemCheck():
        return platform.system()

    @staticmethod
    def pythonSubVersion():
        return sys.version_info[1]

    @classmethod
    def run(cls, qSim, p, coreCount): # pylint: disable=too-many-branches
        if ((cls.systemCheck() != 'Windows') and (cls.reRun is False)):
            cls.reRun = True
            if cls.pythonSubVersion() == 8:
                multiprocessing.set_start_method("fork")

        if p is True:
            if coreCount is None:
                if _poolMemory.coreCount is None:
                    _pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1)
                else:
                    _pool = multiprocessing.Pool(processes=_poolMemory.coreCount)
            elif isinstance(coreCount, int):
                _pool = multiprocessing.Pool(processes=coreCount)
            elif coreCount.lower() == 'all':
                _pool = multiprocessing.Pool(processes=multiprocessing.cpu_count()-1)
            else:
                # FIXME should raise error
                print('error')
        elif p is False:
            _pool = None
        elif p is not None:
            # FIXME if p is not a pool, this should raise error
            _pool = multiprocessing.Pool(processes=p._processes) # pylint: disable=protected-access
        elif p is None:
            if _poolMemory.coreCount is not None:
                _pool = multiprocessing.Pool(processes=_poolMemory.coreCount)
            else:
                _pool = None
        runSimulation(qSim, _pool)

        if _pool is not None:
            _poolMemory.coreCount = _pool._processes # pylint: disable=protected-access
            _pool.close()
            _pool.join()
