from functools import partial
from copy import deepcopy

def runSimulation(qSim, p):
    qSim._computeBase__calculate(qSim.qSystems, qSim.qEvolutions)
    if len(qSim.Sweep.sweeps) > 0:
        if p is None:
            nonParalEvol(qSim)
        else:
            paralEvol(qSim, p)
    else:
        if len(qSim.timeDependency.sweeps) > 0:
            timeDependent(qSim)
        else:
            qSim.evolFunc(qSim)


# function used in modular sweep
def indicesForSweep(ind, *args):
    indices = []
    for arg in args:
        remain = ind%arg
        ind = (ind-remain)/arg
        indices.insert(0, int(remain))
    return indices


# This is the single process function
def nonParalEvol(qSim):
    if len(qSim.timeDependency.sweeps) > 0:
        evolFunc = timeDependent
    else:
        evolFunc = timeEvolBase

    for ind in range(qSim.Sweep.indMultip):
        _runSweepAndPrep(qSim, ind, evolFunc)
        qSim.qRes._organiseSingleProcRes()
    qSim.qRes._finaliseAll(qSim.Sweep.inds)


# multi-processing functions
def paralEvol(qSim, p):
    if len(qSim.timeDependency.sweeps) > 0:
        results = p.map(partial(partial(parallelTimeEvol, qSim), timeDependent), range(qSim.Sweep.indMultip))
    else:
        results = p.map(partial(partial(parallelTimeEvol, qSim), qSim.evolFunc), range(qSim.Sweep.indMultip))
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds)

def parallelTimeEvol(qSim, evolFunc, ind):
    _runSweepAndPrep(qSim, ind, evolFunc)
    return qSim.qRes._copyAllResBlank()


# These two functions, respectively, run Sweep and timeDependent (sweep) parameter updates
# In the timeDependet case, evolFunc of first fuctioon is the second function
def _runSweepAndPrep(qSim, ind, evolFunc):
    qSim.Sweep.runSweep(indicesForSweep(ind, *qSim.Sweep.inds))
    for protoc, qSys in qSim.subSys.items():
        protoc.lastState = qSys.initialState
    qSim.qRes._resetLast(calculateException=qSim.qRes)
    qSim.Sweep._computeBase__calculate(qSim.qSystems, qSim.qEvolutions)
    evolFunc(qSim)

def timeDependent(qSim):
    qSim.timeDependency.prepare()
    for ind in range(qSim.timeDependency.indMultip):
        qSim.timeDependency.runSweep(indicesForSweep(ind, *qSim.timeDependency.inds))
        qSim.timeDependency._computeBase__calculate(qSim.qSystems, qSim.qEvolutions)
        qSim._timeBase__step = 1
        qSim.evolFunc(qSim)
        

# These two are the specific solution method, user should define their own timeEvol function to use other solution methods
# This flexibility should be reflected into protocol object
def exponUni(qSim):
    for protocol in qSim.subSys.keys():
        protocol.getUnitary()
    qSim._paramsUsed()

def timeEvolBase(qSim):
    exponUni(qSim)
    for ii in range(qSim._timeBase__step):
        qSim._Simulation__compute()
        for protocol in qSim.subSys.keys():
            for jj in range(protocol.samples):
                protocol.lastState = protocol.unitary @ protocol.lastState