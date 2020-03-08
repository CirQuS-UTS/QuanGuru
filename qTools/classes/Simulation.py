from qTools.classes.Sweep import Sweep
from multiprocessing import Pool, cpu_count
from qTools.classes.extensions.modularSweep import runSimulation
from qTools.classes.QSys import QuantumSystem, genericQSys
from qTools.classes.timeInfoBase import timeBase
from qTools.classes.QPro import freeEvolution

class Simulation(timeBase):
    instances = 0
    label = 'Simulation'
    
    __slots__ = ['Sweep', 'timeDependency', '__protocols']
    # TODO Same as previous 
    def __init__(self, system=None, **kwargs):
        super().__init__()
        self.__protocols = {}

        self.Sweep = Sweep(superSys=self)
        self.timeDependency = Sweep(superSys=self)

        if system is not None:
            self.addQSystems(system)

        self._qUniversal__setKwargs(**kwargs)
    
    @property
    def protocols(self):
        protocs = list(self._Simulation__protocols.values())
        return (*protocs,) if len(protocs) > 1 else protocs[0]

    @property
    def qSystems(self):
        qSys =  list(self.subSys.values())
        return (*qSys,) if len(qSys) > 1 else qSys[0]

    def addQSystems(self, subS, Protocol=None):
        subS = super().addSubSys(subS)
        '''if Protocol is None:
            Protocol = freeEvolution(superSys=subS)'''
        self._qUniversal__subSys[Protocol] = self._qUniversal__subSys.pop(subS.name)
        # TODO Find a use for this key
        self._Simulation__protocols[Protocol.name] = Protocol
        return (subS, Protocol)
        
    def createQSystems(self, subSysClass, Protocol=None, **kwargs):
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.addQSystems(newSys, Protocol)
        return (newSys, Protocol)

    def removeQSystems(self, subS):
        for key, subSys in self._qUniversal__subSys.items():
            if subSys == subS:
                del self._qUniversal__subSys[key]
                print(subS.name + ' and its protocol ' + key.name + ' is removed from qSystems of ' + self.name)

    # add/remove protocol  
    def removeProtocol(self, Protocol):
        if Protocol is not None:
            del self._qUniversal__subSys[Protocol]

    def addProtocol(self, sys, protocolAdd, protocolRemove=None):
        self.addSubSys(protocolAdd.superSys, protocolAdd)
        self.removeProtocol(Protocol=protocolRemove)
        return protocolAdd

    # overwriting methods from qUniversal
    def addSubSys(self, subS, Protocol=None, **kwargs):
        newSys = super().addSubSys(subS, **kwargs)
        newSys, Protocol = self.addQSystems(subS, Protocol, **kwargs)
        return (newSys, Protocol)

    def createSubSys(self, subSysClass, Protocol=None, **kwargs):
        newSys = super().createSubSys(subSysClass, **kwargs)
        newSys, Protocol = self.createQSystems(newSys, Protocol, **kwargs)
        return (newSys, Protocol)
    
    def removeSubSys(self, subS):
        self.removeQSystems(subS)
        
    # TODO DECIDE
    def __compute(self, *args):
        # TODO avoid this by making last-states the key or storing them in a class attribute list
        states = []
        for protoc in self._Simulation__protocols.values():
            states.append(protoc.lastState)

        if self.compute is not None:
            self.compute(self, *states)

    def run(self, p=None, coreCount=None):
        for protocol, qSys in self.subSys.items():
            if isinstance(qSys, QuantumSystem):
                # TODO Check first if constructed
                qSys.constructCompSys()

            if protocol is None:
                protocol = freeEvolution(superSys=qSys)

        for protoc in self._Simulation__protocols.values():
            protoc.prepare(self)


        self.Sweep.prepare()
        for qres in self.qRes.qResults.values():
            qres.reset()

        _poolMemory.run(self, p, coreCount)

        return self.qRes

    def removeSys(self, sys):
        if isinstance(sys, genericQSys):
            self.removeSweeps(sys)
            del self.subSys[sys.name]
        elif isinstance(sys, str):
            self.removeSweeps(self.subSys[sys])
            del self.subSys[sys]
        return self
    
    # TODO remove a specific sweep
    def removeSweeps(self, sys):
        # TODO type is not valid for single systems
        if isinstance(sys, genericQSys):
            for qSys in sys.subSys.values():
                for key, val in self.Sweep.sweeps.items():
                    if qSys.name in val.subSys.keys():
                        del self.Loop.sweeps[key]
        #elif sys.__class__.__name__ == '_sweep':
        return self


class _poolMemory:
    coreCount = None
    
    @classmethod
    def run(cls, qSim, p, coreCount):
        if p is True:
            if coreCount is None:
                if _poolMemory.coreCount is None:
                    p1 = Pool(processes=cpu_count()-1)
                else:
                    p1 =p1 = Pool(processes=_poolMemory.coreCount)
            elif isinstance(coreCount, int):
                p1 = Pool(processes=coreCount)
            elif coreCount.lower() == 'all':
                p1 = Pool(processes=cpu_count())
        elif p is False:
            p1 = None
        elif p is not None:
            numb = p._processes
            p1 = Pool(processes=numb)
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