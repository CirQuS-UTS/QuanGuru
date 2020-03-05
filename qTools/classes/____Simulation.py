from qTools.classes.____Sweep import Sweep

class Simulation(qUniversal):
    instances = 0
    label = 'Simulation'
    __slots__ = ['__qSys', '__stepSize', '__finalTime', 'compute', '__samples', '__step', 'delState', 'qRes', 'inds', 'indMultip']
    # TODO Same as previous 
    def __init__(self, system=None, **kwargs):
        super().__init__()
        self.__qSys = None

        self.Sweep = Sweep(superSys=self)
        self.timeDependency = Sweep(superSys=self)
        # TODO assign supersys ?
        self.qRes = qResults()
        
        self.delState = False

        self.__finalTime = None
        self.__stepSize = 0.02
        self.__samples = 1
        self.__step = 1

        self.compute = None
        self.inds = []
        self.indMultip = None

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

        if len(self.Loop.sweeps)>0:
            self.inds = [0 for i in range(len(self.Loop.sweeps))]
            for sweep in self.Loop.sweeps.values():
                self.inds[-(sweep.ind+1)] = len(sweep.sweepList)-1
            self.indMultip = reduce(lambda x, y: x*y, self.inds)

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