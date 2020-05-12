from multiprocessing import Pool, cpu_count
from qTools.classes.Sweep import Sweep
from qTools.classes.extensions.modularSweep import runSimulation
from qTools.classes.timeBase import timeBase
from qTools.classes.extensions.modularSweep import timeEvolBase

class Simulation(timeBase):
    instances = 0
    _nonInternalInstances = 0
    _internalInstances = 0
    label = 'Simulation'
    simInstances = {}

    __slots__ = ['Sweep', 'timeDependency', 'evolFunc', '__allInstances']

    # TODO init error decorators or error decorators for some methods
    def __init__(self, system=None, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))

        self.Sweep = Sweep(superSys=self)
        self.timeDependency = Sweep(superSys=self)

        self.evolFunc = timeEvolBase

        if system is not None:
            self.addQSystems(system)

        self.__allInstances = Simulation.simInstances

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def save(self):
        saveDict = super().save()
        sysDict = {}
        for pro, sys in self.subSys.items():
            syDict = sys.save()
            syDict[pro.name] = pro.save()
            sysDict[sys.name] = syDict
        saveDict['qSystems'] = sysDict
        saveDict['Sweep'] = self.Sweep.save()
        saveDict['timeDependency'] = self.timeDependency.save()
        return saveDict

    @property
    def protocols(self):
        protocs = list(self.subSys.keys())
        return protocs if len(protocs) > 1 else protocs[0]

    def _freeEvol(self):
        for protocol, qSys in self.subSys.items():
            if isinstance(protocol, str):
                self.subSys[qSys._freeEvol] = self.subSys.pop(protocol) # pylint: disable=protected-access

    @property
    def qSystems(self):
        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @property
    def qEvolutions(self):
        self._freeEvol()
        qPros = list(self.subSys.keys())
        return qPros if len(qPros) > 1 else qPros[0]

    def addQSystems(self, subS, Protocol=None, **kwargs):
        # TODO print a message, if the same system included more than once without giving a protocol
        subS = super().addSubSys(subS, **kwargs)
        self._paramBoundBase__paramBound[subS.name] = subS
        if subS.simulation is not self:
            subS.simulation._bound(self) # pylint: disable=protected-access
        if Protocol is not None:
            self._qUniversal__subSys[Protocol] = self._qUniversal__subSys.pop(subS.name) # pylint: disable=no-member
        return (subS, Protocol)

    def createQSystems(self, subSysClass, Protocol=None, **kwargs):
        newSys, Protocol = self.addQSystems(subSysClass, Protocol, **kwargs)
        return (newSys, Protocol)

    def removeQSystems(self, subS):
        for key, subSys in self._qUniversal__subSys.items(): # pylint: disable=no-member
            if ((subSys is subS) or (subSys.name == subS)):
                self._qUniversal__subSys.pop(key) # pylint: disable=no-member
                print(subS.name + ' and its protocol ' + key.name + ' is removed from qSystems of ' + self.name)
                self.removeSweep(subSys)

    def removeSweep(self, sys):
        self.Sweep.removeSweep(sys)
        self.timeDependency.removeSweep(sys)
        return sys

    # add/remove protocol
    def removeProtocol(self, Protocol):
        # FIXME what if freeEvol case, protocol then corresponds to sys.name before simulation run or a freeEvol obj after run
        self._qUniversal__subSys.pop(Protocol, None) # pylint: disable=no-member

    def addProtocol(self, protocol=None, sys=None, protocolRemove=None):
        # TODO Decorate this
        qSysClass = globals()['qBaseSim']
        if sys is None:
            if isinstance(protocol, qSysClass):
                if isinstance(protocol.superSys, qSysClass):
                    protocol = self.addProtocol(protocol.superSys, protocol, protocolRemove)
                else:
                    raise TypeError('?')
            else:
                raise TypeError('?')
        elif isinstance(protocol.superSys, qSysClass):
            if sys is protocol.superSys:
                self.addQSystems(sys, protocol)
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

    def removeSubSys(self, subS): # pylint: disable=arguments-differ
        self.removeQSystems(subS)

    def __compute(self):
        states = []
        for protocol in self.subSys.keys():
            states.append(protocol.lastState)
            if protocol.simulation.delStates is False:
                self.qRes.states[protocol.name].append(protocol.lastState)
        super()._computeBase__compute(states) # pylint: disable=no-member

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

    @classmethod
    def run(cls, qSim, p, coreCount): # pylint: disable=too-many-branches
        if p is True:
            if coreCount is None:
                if _poolMemory.coreCount is None:
                    _pool = Pool(processes=cpu_count()-1)
                else:
                    _pool = Pool(processes=_poolMemory.coreCount)
            elif isinstance(coreCount, int):
                _pool = Pool(processes=coreCount)
            elif coreCount.lower() == 'all':
                _pool = Pool(processes=cpu_count()-1)
            else:
                # FIXME should raise error
                print('error')
        elif p is False:
            _pool = None
        elif p is not None:
            # FIXME if p is not a pool, this should raise error
            _pool = Pool(processes=p._processes) # pylint: disable=protected-access
        elif p is None:
            if _poolMemory.coreCount is not None:
                _pool = Pool(processes=_poolMemory.coreCount)
            else:
                _pool = None

        runSimulation(qSim, _pool)

        if _pool is not None:
            _poolMemory.coreCount = _pool._processes # pylint: disable=protected-access
            _pool.close()
            _pool.join()
