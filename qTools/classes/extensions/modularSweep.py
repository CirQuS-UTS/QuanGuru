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
            #timeEvolBase(qSim, qSim.steps)
            qSim.evolFunc(qSim)


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
        evolFunc = timeEvolBase

    for ind in range(qSim.Sweep.indMultip):
        _runSweepAndPrep(qSim, ind, evolFunc)
        qSim.qRes._organiseSingleProcRes()
    qSim.qRes._finaliseAll(qSim.Sweep.inds)


def paralEvol(qSim, p):
    if len(qSim.timeDependency.sweeps) > 0:
        results = p.map(partial(partial(parallelTimeEvol, qSim), timeDependent),range(qSim.Sweep.indMultip))
    else:
        results = p.map(partial(partial(parallelTimeEvol, qSim), timeEvolBase),range(qSim.Sweep.indMultip))
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds)

def parallelTimeEvol(qSim, evolFunc, ind):
    _runSweepAndPrep(qSim, ind, evolFunc)
    return deepcopy(qSim.qRes.allResults)

def _runSweepAndPrep(qSim, ind, evolFunc):
    qSim.Sweep.runSweep(indicesForSweep(ind, *qSim.Sweep.inds))
    for protoc, qSys in qSim.subSys.items():
        protoc.lastState = qSys.initialState
    qSim.qRes._resetLast()
    evolFunc(qSim, qSim.steps)

def timeDependent(qSim, steps):
    qSim.timeDependency.prepare()
    for ind in range(qSim.timeDependency.indMultip):
        qSim.timeDependency.runSweep(indicesForSweep(ind, *qSim.timeDependency.inds))
        #exponUni(qSim)
        #timeEvolBase(qSim)
        qSim.evolFunc(qSim, 1)

'''def _timeEvol(qSim):
    qSim.evolFunc(qSim, qSim.steps)'''
        
def exponUni(qSim):
    for protocol in qSim.subSys.keys():
        protocol.createUnitary()

def timeEvolBase(qSim, steps):
    exponUni(qSim)
    for ii in range(steps):
        for protocol in qSim.subSys.keys():
            qSim._Simulation__compute()
            for ii in range(protocol.samples):
                protocol.lastState = protocol.unitary @ protocol.lastState