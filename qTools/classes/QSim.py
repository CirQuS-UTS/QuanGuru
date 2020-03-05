import numpy as np
from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
#from qTools.classes.exceptions import sweepInitError
from qTools.classes.extensions.timeEvolve import runSimulation
from qTools.classes.QResDict import qResults
from itertools import chain
from multiprocessing import Pool, cpu_count
import qTools.classes.extensions.modularSweep as modularRun
from functools import reduce

class Sweep(qUniversal):
    instances = 0
    label = '_sweep'
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepStep', '__sweepList', 'logSweep', 'sweepFunction']
    # FIXME enable this, but not necessarily this way
    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__()
        # TODO make these properties so that sweepList is dynamic
        self.sweepKey = None
        self.sweepMax = None
        self.sweepMin = None
        self.sweepStep = None
        self.__sweepList = None
        self.logSweep = False
        self.sweepFunction = None
        self._qUniversal__setKwargs(**kwargs)

    @qUniversal.subSys.setter
    def subSys(self, subSys):
        super().addSubSys(subSys)

    @property
    def sweepList(self):
        return self._Sweep__sweepList

    @sweepList.setter
    def sweepList(self, sList):
        if sList is None:
            if self.logSweep is False:
                self._Sweep__sweepList = arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)
            elif self.logSweep is True:
                self._Sweep__sweepList = logspace(self.sweepMin, self.sweepMax, num=self.sweepPert, base=10.0)
        else:
            self._Sweep__sweepList = sList

    def runSweep(self, ind):
        if self.sweepFunction is None:
            val = self.sweepList[ind]
            for subSys in self.subSys.values():
                setattr(subSys, self.sweepKey, val)
        else:
            self.sweepFunction(self, self.superSys.superSys)


class qSequence(qUniversal):
    instances = 0
    label = 'Sweep'
    __slots__ = ['__inds', '__indMultip', 'compute', 'calculate']
    # TODO init errors
    def __init__(self, **kwargs):
        super().__init__()
        self.compute = None
        # TODO Behaviour of calculate ?
        self.calculate = None
        self.__inds = []
        self.__indMultip = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def inds(self):
        return self._qSequence__inds

    @property
    def indMultip(self):
        return self._qSequence__indMultip

    @property
    def sweeps(self):
        return self._qUniversal__subSys

    @sweeps.setter
    def sweeps(self, sysDict):
        super().subSys = sysDict

    def createSweep(self, sys, sweepKey, **kwargs):
        newSweep = Sweep(superSys=self, subSys=sys, sweepKey=sweepKey, **kwargs)
        super().addSubSys(newSweep)
        return newSweep

    def prepare(self):
        if len(self.subSys) > 0:
            self._qSequence__inds = [0 for i in range(len(self.subSys))]
            for sweep in self.subSys.values():
                self._qSequence__inds[-(sweep.ind+1)] = len(sweep.sweepList)-1
            self._qSequence__indMultip = reduce(lambda x, y: x*y, self._qSequence__inds)


class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    __slots__ = ['__qSys', '__stepSize', '__finalTime', 'states', 'beforeLoop', 'Loop', 'whileLoop', 'compute', '__samples', '__step', 'delState', 'qRes']
    # TODO Same as previous 
    def __init__(self, system=None, **kwargs):
        super().__init__()
        self.__qSys = None

        self.Loop = qSequence(superSys=self)
        self.whileLoop = qSequence(superSys=self)
        # TODO assign supersys ?
        self.qRes = qResults()
        
        self.delState = False

        self.__finalTime = None
        self.__stepSize = 0.02
        self.__samples = 1
        self.__step = 1

        self.compute = None

        if ((system is not None) and ('qSys' in kwargs.keys())):
            print('Two qSys given')
        elif ((system is not None) and ('qSys' not in kwargs.keys())):
            kwargs['qSys'] = system
        self._qUniversal__setKwargs(**kwargs)
        if self.__qSys is None:
            self.__qSys = QuantumSystem()
            self.subSys = self.qSys

    
    #def __compute(self, results, *args):
    def __compute(self, *args):
        states = []
        for qSys in self.subSys.values():
            states.extend(qSys._genericQSys__lastStateList)

        if self.compute is not None:
            results = self.compute(self, *states)
            #results = self.compute(self,results, *states)
        else:
            # FIXME assumed this is going to return a thing a that will be appended, if not ?
            results = None
        return results

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
            # TODO print a message here
            self._Simulation__step = int(self.finalTime//stepsize + 1)

    @property
    def samples(self):
        return self._Simulation__samples

    @samples.setter
    def samples(self, num):
        self._Simulation__samples = num

    def __del__(self):
        class_name = self.__class__.__name__

    @property
    def qSys(self):
        #self._Simulation__qSys.superSys = self
        return self._Simulation__qSys

    @qSys.setter
    def qSys(self, val):
        """if isinstance(val, QuantumSystem):
            QuantumSystem.constructCompSys(val)"""
        self._Simulation__qSys = val
        self.subSys = None
        self.subSys = val
    
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

        self.Loop.prepare()

        self.qRes.reset()


        _poolMemory.run(self, p, coreCount)

        #self.qRes._unpack()

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
                for ind, sw in enumerate(self.Loop.sweeps):
                    if qSys.name in sw.subSys.keys():
                        del self.Loop.sweeps[ind]
        return self


class _poolMemory:
    pool = None
    
    @classmethod
    def run(cls, qSim, p, coreCount):
        if p is True:
            if coreCount is None:
                if _poolMemory.pool is None:
                    p1 = Pool(processes=cpu_count()-1)
                else:
                    p1 = _poolMemory.pool
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
            if _poolMemory.pool is not None:
                numb = _poolMemory.pool._processes
                p1 = Pool(processes=numb)
            else:
                p1 = _poolMemory.pool
        _poolMemory.pool = p1

        res = modularRun.runSimulation(qSim, p1)
        #res = runSimulation(qSim, p1)

        if p1 is not None:
            numb = p1._processes
            p1.close()
            p1.join()
            _poolMemory.pool = Pool(processes=numb)