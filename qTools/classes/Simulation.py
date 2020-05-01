from multiprocessing import Pool, cpu_count
from qTools.classes.Sweep import Sweep
from qTools.classes.extensions.modularSweep import runSimulation
from qTools.classes.timeBase import timeBase
from qTools.classes.extensions.modularSweep import timeEvolBase

class Simulation(timeBase):
    instances = 0
    label = 'Simulation'

    __slots__ = ['Sweep', 'timeDependency', 'evolFunc']
    # TODO init error decorators or error decorators for some methods
    def __init__(self, system=None, **kwargs):
        super().__init__(name=kwargs.pop('name', None), samples=1)

        self.Sweep = Sweep(superSys=self)
        self.timeDependency = Sweep(superSys=self)

        self.evolFunc = timeEvolBase

        if system is not None:
            self.addQSystems(system)

        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self._computeBase__delStates = False # pylint: disable=assigning-non-slot

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

    @timeBase.delStates.setter # pylint: disable=no-member
    def delStates(self, boolean):
        timeBase.delStates.fset(self, boolean) # pylint: disable=no-member
        for qres in self.qRes.allResults.values():
            if qres is not self.qRes:
                qres.superSys.delStates = boolean

    @property
    def protocols(self):
        protocs = list(self.subSys.keys())
        return (*protocs,) if len(protocs) > 1 else protocs[0]

    def _freeEvol(self):
        for protocol, qSys in self.subSys.items():
            if isinstance(protocol, str):
                self.subSys[qSys._genericQSys__unitary] = self.subSys.pop(protocol)

    @property
    def qSystems(self):
        '''qSys =  list(self.subSys.values())
        return (*qSys,) if len(qSys) > 1 else qSys[0]'''
        return list(self.subSys.values())

    @property
    def qEvolutions(self):
        '''qPros = list(self.subSys.keys())
        return (*qPros,) if len(qPros) > 1 else qPros[0]'''
        return list(self.subSys.keys())

    def addQSystems(self, subS, Protocol=None):
        # TODO print a message, if the same system included more than once without giving a protocol
        subS = super().addSubSys(subS)
        if Protocol is not None:
            self._qUniversal__subSys[Protocol] = self._qUniversal__subSys.pop(subS.name) # pylint: disable=no-member
        return (subS, Protocol)

    def createQSystems(self, subSysClass, Protocol=None, **kwargs):
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.addQSystems(newSys, Protocol)
        return (newSys, Protocol)

    def removeQSystems(self, subS):
        for key, subSys in self._qUniversal__subSys.items(): # pylint: disable=no-member
            if ((subSys is subS) or (subSys.name == subS)):
                del self._qUniversal__subSys[key] # pylint: disable=no-member
                print(subS.name + ' and its protocol ' + key.name + ' is removed from qSystems of ' + self.name)
                self._updateInd()
                self.removeSweep(subSys)

    def removeSweep(self, sys):
        self.Sweep.removeSweep(sys)
        self.timeDependency.removeSweep(sys)
        return sys

    # add/remove protocol
    def removeProtocol(self, Protocol):
        # FIXME what if freeEvol case, protocol then corresponds to sys.name before simulation run or a freeEvol obj after run
        if isinstance(Protocol, timeBase):
            del self._qUniversal__subSys[Protocol] # pylint: disable=no-member
        else:
            raise ValueError('?')

    def addProtocol(self, protocol=None, sys=None, protocolRemove=None):
        # TODO Decorate this
        qSysClass = globals()['universalQSys']
        if sys is None:
            if isinstance(protocol, timeBase):
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
        newSys, Protocol = self.addQSystems(subS, Protocol, **kwargs)
        return newSys

    def createSubSys(self, subSysClass, Protocol=None, **kwargs): # pylint: disable=arguments-differ
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.createQSystems(newSys, Protocol, **kwargs)
        return newSys

    def removeSubSys(self, subS): # pylint: disable=arguments-differ
        self.removeQSystems(subS)

    def _paramsUsed(self):
        for sys in self.Sweep.sweeps.values():
            for paramUpdateSys in sys.subSys.values():
                try:
                    paramUpdateSys._paramUpdated = False
                except: # pylint: disable=bare-except
                    pass

        for sys in self.timeDependency.sweeps.values():
            for paramUpdateSys in sys.subSys.values():
                try:
                    paramUpdateSys._paramUpdated = False
                except: # pylint: disable=bare-except
                    pass

    def __compute(self):
        states = []
        for protoc in self.subSys.keys():
            states.append(protoc.lastState)
            if ((protoc.simulation.delStates is False) or (self.delStates is False)):
                self.qRes.states[protoc.name].append(protoc.lastState)
        super()._computeBase__compute(states) # pylint: disable=no-member

    def run(self, p=None, coreCount=None):
        self._freeEvol()
        for qSys in self.subSys.values():
            # TODO this will be modified after the structural changes of qSys objects
            if qSys.__class__.__name__ == 'QuantumSystem':
                # TODO Check first if constructed
                qSys.constructCompSys()
        for protoc in self.subSys.keys():
            # TODO tihis will be modified after the structural changes of qPro objects
            protoc.simulation = self
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
