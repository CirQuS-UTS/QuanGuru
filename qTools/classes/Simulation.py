from qTools.classes.Sweep import Sweep
from multiprocessing import Pool, cpu_count
from qTools.classes.extensions.modularSweep import runSimulation
from qTools.classes.QSys import QuantumSystem, genericQSys
from qTools.classes.timeBase import timeBase
from qTools.classes.QPro import freeEvolution
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

        self._qUniversal__setKwargs(**kwargs)

    @timeBase.delStates.setter
    def delStates(self, boolean):
        timeBase.delStates.fset(self, boolean)
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
                self.subSys[freeEvolution(superSys=qSys)] = self.subSys.pop(protocol)

    @property
    def qSystems(self):
        qSys =  list(self.subSys.values())
        return (*qSys,) if len(qSys) > 1 else qSys[0]

    def addQSystems(self, subS, Protocol=None):
        # TODO print a message, if the same system included more than once without giving a protocol
        subS = super().addSubSys(subS)
        if Protocol is not None:
            self._qUniversal__subSys[Protocol] = self._qUniversal__subSys.pop(subS.name)
        return (subS, Protocol)
        
    def createQSystems(self, subSysClass, Protocol=None, **kwargs):
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.addQSystems(newSys, Protocol)
        return (newSys, Protocol)

    def removeQSystems(self, subS):
        for key, subSys in self._qUniversal__subSys.items():
            if ((subSys is subS) or (subSys.name == subS)):
                del self._qUniversal__subSys[key]
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
            del self._qUniversal__subSys[Protocol]
        else:
            raise ValueError('?')

    def addProtocol(self, protocol=None, sys=None, protocolRemove=None):
        # TODO Decorate this
        if sys is None:
            if protocol is None:
                raise TypeError('?')
            elif isinstance(protocol, timeBase):
                if isinstance(protocol.superSys, genericQSys):
                    protocol = self.addProtocol(protocol.superSys, protocol, protocolRemove)
                else:
                    raise TypeError('?')
        elif isinstance(sys, genericQSys):
            if sys is protocol.superSys:
                self.addQSystems(sys, protocol)
                self.removeProtocol(Protocol=protocolRemove)
            else:
                raise TypeError('?')
        return protocol

    # overwriting methods from qUniversal
    def addSubSys(self, subS, Protocol=None, **kwargs):
        newSys = super().addSubSys(subS, **kwargs)
        newSys, Protocol = self.addQSystems(subS, Protocol, **kwargs)
        return newSys

    def createSubSys(self, subSysClass, Protocol=None, **kwargs):
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.createQSystems(newSys, Protocol, **kwargs)
        return newSys
    
    def removeSubSys(self, subS):
        self.removeQSystems(subS)
        
    def __compute(self):
        states = []
        for protoc in self.subSys.keys():
            states.append(protoc.lastState)
            if protoc.delStates is False:
                self.qRes.states[protoc.name].append(protoc.lastState)
        super()._computeBase__compute(states)
            
    def run(self, p=None, coreCount=None):
        self._freeEvol()
        for qSys in self.subSys.values():
            # TODO this will be modified after the structural changes of qSys objects
            if isinstance(qSys, QuantumSystem):
                # TODO Check first if constructed
                qSys.constructCompSys()
        for protoc in self.subSys.keys():
            # TODO tihis will be modified after the structural changes of qPro objects
            protoc.prepare(self)
        self.Sweep.prepare()
        for qres in self.qRes.allResults.values():
            qres._reset()
        _poolMemory.run(self, p, coreCount)
        for key, val in self.qRes.states.items():
            self.qRes.allResults[key]._qResBase__states[key] = val
        return self.qRes

class _poolMemory:
    coreCount = None
    
    @classmethod
    def run(cls, qSim, p, coreCount):
        if p is True:
            if coreCount is None:
                if _poolMemory.coreCount is None:
                    p1 = Pool(processes=cpu_count()-1)
                else:
                    p1 = Pool(processes=_poolMemory.coreCount)
            elif isinstance(coreCount, int):
                p1 = Pool(processes=coreCount)
            elif coreCount.lower() == 'all':
                p1 = Pool(processes=cpu_count())
            else:
                # FIXME should raise error
                print('error')
        elif p is False:
            p1 = None
        elif p is not None:
            # FIXME if p is not a pool, this should raise error
            p1 = Pool(processes=p._processes)
        elif p is None:
            if _poolMemory.coreCount is not None:
                p1 = Pool(processes=_poolMemory.coreCount)
            else:
                p1 = None

        res = runSimulation(qSim, p1)

        if p1 is not None:
            _poolMemory.coreCount = p1._processes
            p1.close()
            p1.join()