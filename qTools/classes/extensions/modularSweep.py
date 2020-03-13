from functools import partial
from copy import deepcopy

def runSimulation(qSim, p):
    if len(qSim.Sweep.sweeps) > 0:
        if p is None:
            nonParalEvol(qSim)
        else:
            paralEvol(qSim, p)
    else:
        if len(qSim.timeDependency.sweeps) > 0:
            timeDependent(qSim)
        else:
            __timeEvol(qSim, qSim.steps)


def indicesForSweep(ind, *args):
    remain = 0
    indices = []
    for arg in args:
        #print(ind, arg)
        remain = ind%arg
        ind = (ind-remain)/arg
        indices.insert(0, int(remain))
    return indices


def nonParalEvol(qSim):
    if len(qSim.timeDependency.sweeps) > 0:
        evolFunc = timeDependent
    else:
        evolFunc = _timeEvol

    for ind in range(qSim.Sweep.indMultip):
        _runSweepAndPrep(qSim, ind, evolFunc)
        qSim.qRes._organiseSingleProcRes()


def paralEvol(qSim, p):
    if len(qSim.timeDependency.sweeps) > 0:
        results = p.map(partial(partial(parallelTimeEvol, qSim), timeDependent),range(qSim.Sweep.indMultip))
    else:
        results = p.map(partial(partial(parallelTimeEvol, qSim), _timeEvol),range(qSim.Sweep.indMultip))
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds)

def parallelTimeEvol(qSim, evolFunc, ind):
    _runSweepAndPrep(qSim, ind, evolFunc)
    return deepcopy(qSim.qRes.allResults)

'''def parallelTimeIndep(qSim, ind):
    _runSweepAndPrep(qSim, ind, _timeEvol)
    return deepcopy(qSim.qRes.allResults)'''

def _runSweepAndPrep(qSim, ind, evolFunc):
    qSim.Sweep.runSweep(indicesForSweep(ind, *qSim.Sweep.inds))
    for protoc, qSys in qSim.subSys.items():
        protoc.lastState = qSys.initialState
    qSim.qRes.resetLast()
    evolFunc(qSim, qSim.steps)

def timeDependent(qSim, stepsCount=1):
    qSim.timeDependency.prepare()
    for ind in range(qSim.timeDependency.indMultip):
        qSim.timeDependency.runSweep(indicesForSweep(ind, *qSim.timeDependency.inds))
        _timeEvol(qSim, 1)

def _timeEvol(qSim, stepNumber):
    exponUni(qSim)
    for ii in range(stepNumber):
        __timeEvol(qSim)
        
def exponUni(qSim):
    for protocol in qSim.subSys.keys():
        protocol.createUnitary()

def __timeEvol(qSim):
    for protocol in qSim.subSys.keys():
        qSim._Simulation__compute()
        for ii in range(protocol.samples):
            protocol.lastState = protocol.unitary @ protocol.lastState