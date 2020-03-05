from qTools.classes.____Sweep import Sweep
from multiprocessing import Pool, cpu_count
from qTools.classes.extensions.modularSweep import runSimulation
from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
from qTools.classes.QResDict import qResultsContainer
from qTools.classes.QPro import freeEvolution

class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    
    __slots__ = ['Sweep', 'timeDependency',  'qRes', 'delStates', '__finalTime', '__stepSize', '__samples', '__step', 'compute']
    # TODO Same as previous 
    def __init__(self, system=None, **kwargs):
        super().__init__()

        self.Sweep = Sweep(superSys=self)
        self.timeDependency = Sweep(superSys=self)

        self.qRes = qResultsContainer()
        self.delStates = False

        self.__finalTime = None
        self.__stepSize = None
        self.__samples = 1
        self.__step = None

        self.compute = None

        if system is None:
            self.addSubSys(QuantumSystem())

        self._qUniversal__setKwargs(**kwargs)

    @property
    def qSystems(self):
        return (*list(self.subSys.values()),)

    def addQSystems(self, subS, Protocol=None):
        if Protocol is not None:
            self._qUniversal__subSys[Protocol.name] = self._qUniversal__subSys.pop(subS.name)
        elif Protocol is None:
            freeEvol = freeEvolution(superSys=subS)
            self._qUniversal__subSys[freeEvol.name] = self._qUniversal__subSys.pop(subS.name)
        
    def createQSystems(self, subSysClass, Protocol=None, **kwargs):
        newSys = super().createSubSys(subSysClass, **kwargs)
        self.addQSystems(newSys, Protocol)

    def removeQSystems(self, subS):
        for key, subSys in self._qUniversal__subSys.items():
            if subSys == subS:
                del self._qUniversal__subSys[key]
                print(subS.name + ' and its protocol ' + key.name + ' is removed from qSystems of ' + self.name)
       
    def removeProtocol(self, Protocol):
        del self._qUniversal__subSys[Protocol]

    # overwriting methods from qUniversal
    def addSubSys(self, subS, Protocol=None, **kwargs):
        newSys = super().addSubSys(subS, **kwargs)
        self.addQSystems(self, subS, **kwargs)

    def createSubSys(self, subSysClass, Protocol=None, **kwargs):
        newSys = super().createSubSys(subSysClass, **kwargs)
        self.createQSystems(self, newSys, **kwargs)
    
    def removeSubSys(self, subS):
        self.removeQSystems(self, subS)
        
    
    # TODO DECIDE
    def __compute(self, *args):
        states = []
        for qSys in self.subSys.values():
            states.extend(qSys._genericQSys__lastStateList)

        if self.compute is not None:
            self.compute(self, *states)

    @property
    def finalTime(self):
        return self._Simulation__finalTime

    @finalTime.setter
    def finalTime(self, fTime):
        self._Simulation__finalTime = fTime
        self._Simulation__step = int(fTime//self.stepSize + 1)

    @property
    def steps(self):
        return self._Simulation__step

    @steps.setter
    def steps(self, num):
        self._Simulation__step = num
        self._Simulation__stepSize = self.finalTime/num

    @property
    def stepSize(self):
        return self._Simulation__stepSize

    @stepSize.setter
    def stepSize(self, stepsize):
        self._Simulation__stepSize = stepsize
        if self.finalTime is not None:
            self._Simulation__step = int(self.finalTime//stepsize + 1)

    @property
    def samples(self):
        return self._Simulation__samples

    @samples.setter
    def samples(self, num):
        self._Simulation__samples = num

    def __del__(self):
        class_name = self.__class__.__name__

    '''@property
    def qSys(self):
        return self._Simulation__qSys'''

    '''@qSys.setter
    def qSys(self, val):
        self._Simulation__qSys = val
        self.subSys = None
        self.subSys = val'''
    
    def run(self, p=None, coreCount=None):
        for qSys in self.subSys.values():
            if isinstance(self.qSys, QuantumSystem):
                # TODO Check first if constructed
                qSys.constructCompSys()
            
            if isinstance(qSys._genericQSys__unitary, qUniversal):
                qSys._genericQSys__unitary.prepare(self)
            elif isinstance(qSys._genericQSys__unitary, list):
                for protocol in qSys._genericQSys__unitary:
                    protocol.prepare(self)

        self.Sweep.prepare()
        self.qRes.reset()

        _poolMemory.run(self, p, coreCount)

        return self.qRes

    def removeSys(self, sys):
        if isinstance(sys, qUniversal):
            self.removeSweeps(sys)
            del self.subSys[sys.name]
        elif isinstance(sys, str):
            self.removeSweeps(self.subSys[sys])
            del self.subSys[sys]
        return self

    def removeSweeps(self, sys):
        if isinstance(sys, QuantumSystem):
            for qSys in sys.subSys.values():
                for key, val in self.Sweep.sweeps.items():
                    if qSys.name in val.subSys.keys():
                        del self.Loop.sweeps[key]
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