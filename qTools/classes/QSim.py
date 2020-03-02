import numpy as np
from qTools.classes.QSys import QuantumSystem
from qTools.classes.QUni import qUniversal
#from qTools.classes.exceptions import sweepInitError
from qTools.classes.extensions.timeEvolve import runSimulation
from qTools.classes.QRes import qResults
from itertools import chain
from multiprocessing import Pool, cpu_count

""" under construction be careful """
class Sweep(qUniversal):
    instances = 0
    label = 'Sweep'
    __slots__ = ['sweepKey', 'sweepMax', 'sweepMin', 'sweepPert', '__sweepList', 'logSweep', '__lCount', 'sweepFunction']
    # FIXME enable this, but not necessarily this way
    #@sweepInitError
    def __init__(self, **kwargs):
        super().__init__()
        # TODO make these properties so that sweepList is dynamic
        self.sweepKey = None
        self.sweepMax = None
        self.sweepMin = None
        self.sweepPert = None
        self.__sweepList = None
        self.logSweep = False
        self.__lCount = 0
        self.sweepFunction = None
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweepList(self):
        return self._Sweep__sweepList

    @sweepList.setter
    def sweepList(self, sList):
        if sList is None:
            if self.logSweep is False:
                self._Sweep__sweepList = np.arange(self.sweepMin, self.sweepMax + self.sweepPert, self.sweepPert)
            elif self.logSweep is True:
                self._Sweep__sweepList = np.logspace(self.sweepMin, self.sweepMax, num=self.sweepPert, base=10.0)
        else:
            self._Sweep__sweepList = sList

    @property
    def lCounts(self):
        self._Sweep__lCount += 1
        return self._Sweep__lCount-1

    @lCounts.setter
    def lCounts(self,val):
        self._Sweep__lCount = val

    def runSweep(self, ind):
        if self.sweepFunction is None:
            val = self.sweepList[ind]
            for subSys in self.subSystems.values():
                setattr(subSys, self.sweepKey, val)
            # TODO Decide if single or multiple subbSys
            #setattr(self.subSystems, self.sweepKey, val)
        else:
            self.sweepFunction(self, self.superSys.superSys)
    # TODO Decide if single or multiple subbSys
    """@qUniversal.subSystems.setter
    def subSystems(self, subS):
        self._qUniversal__subSys = subS"""


class qSequence(qUniversal):
    instances = 0
    label = '_sweep'
    __slots__ = ['__Sweeps', '__swCount']
    # TODO Same as previous 
    def __init__(self, **kwargs):
        super().__init__()
        self.__Sweeps = []
        self.__swCount = 0
        self._qUniversal__setKwargs(**kwargs)

    @property
    def sweeps(self):
        return self._qSequence__Sweeps

    @sweeps.setter
    def sweeps(self, sysDict):
        self._qSequence__Sweeps = {}
        for key, val in sysDict.items():
            self.addSweep(val, key)

    # TODO Change name to create
    def addSweep(self, sys, sweepKey, **kwargs):
        newSweep = Sweep(superSys=self, subSystems=sys, sweepKey=sweepKey, **kwargs)
        self._qSequence__Sweeps.append(newSweep)
        return newSweep

    @property
    def lCount(self):
        self._qSequence__swCount += 1
        return self._qSequence__swCount - 1

    @lCount.setter
    def lCount(self,val):
        self._qSequence__swCount = val


class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    __compute = 0
    __slots__ = ['__qSys', '__stepSize', '__finalTime', 'states', 'beforeLoop', 'Loop', 'whileLoop', 'compute', '__samples', '__step', 'delState', 'qRes', 'pool']
    # TODO Same as previous 
    def __init__(self, system=None, **kwargs):
        super().__init__()
        self.__qSys = None

        self.beforeLoop = qSequence(superSys=self)
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
        self.pool = None

        if ((system is not None) and ('qSys' in kwargs.keys())):
            print('Two qSys given')
        elif ((system is not None) and ('qSys' not in kwargs.keys())):
            kwargs['qSys'] = system
        self._qUniversal__setKwargs(**kwargs)
        if self.__qSys is None:
            self.__qSys = QuantumSystem()
            self.subSystems = self.qSys

    def __compute(self, *args):
        states = []
        for qSys in self.subSystems.values():
            states.extend(qSys._genericQSys__lastStateList)

        if self.compute is not None:
            results = self.compute(self, *states)
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
        self.subSystems = None
        self.subSystems = val
    
    def run(self, p=None, coreNum=None):
        for qSys in self.subSystems.values():
            if isinstance(self.qSys, QuantumSystem):
                # TODO Check first if constructed
                qSys.constructCompSys()
            qSys._genericQSys__unitary.prepare(self)

        self.qRes.reset()
        self.qRes._prepare(self)
        self.qRes._createList()
        
        self._Simulation__res(self.beforeLoop)
        self._Simulation__res(self.Loop)
        self._Simulation__res(self.whileLoop)

        _poolMemory.run(self, p, coreNum)

        self.qRes._unpack()

        return self.qRes

    def removeSys(self, sys):
        if isinstance(sys, qUniversal):
            if isinstance(sys, QuantumSystem):
                for qSys in sys.subSystems.values():
                    for ind, sw in enumerate(self.Loop.sweeps):
                        if qSys.name in sw.subSystems.keys():
                            del self.Loop.sweeps[ind]
            del self.subSystems[sys.name]
        elif isinstance(sys, str):
            del self.subSystems[sys]

    @staticmethod
    def __res(seq):
        seq.lCount = 0
        for sweep in seq.sweeps:
            sweep.lCounts = 0


class _poolMemory:
    pool = None
    
    @classmethod
    def run(cls, qSim, p, coreNum):
        if p is True:
            if coreNum is None:
                if _poolMemory.pool is None:
                    p1 = Pool(processes=cpu_count()-1)
                else:
                    p1 = _poolMemory.pool
            elif isinstance(coreNum, int):
                p1 = Pool(processes=coreNum)
            elif coreNum.lower() == 'all':
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

        res = runSimulation(qSim, p1)

        if p1 is not None:
            numb = p1._processes
            p1.close()
            p1.join()
            _poolMemory.pool = Pool(processes=numb)

