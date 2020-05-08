from functools import partial


def runSimulation(qSim, p):
    qSim._computeBase__calculate(qSim.qSystems, qSim.qEvolutions) # pylint: disable=protected-access
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
        qSim.qRes._organiseSingleProcRes() # pylint: disable=protected-access
    qSim.qRes._finaliseAll(qSim.Sweep.inds) # pylint: disable=protected-access


# multi-processing functions
def paralEvol(qSim, p):
    if len(qSim.timeDependency.sweeps) > 0:
        results = p.map(partial(partial(parallelTimeEvol, qSim), timeDependent), range(qSim.Sweep.indMultip), chunksize=1)
    else:
        results = p.map(partial(partial(parallelTimeEvol, qSim), qSim.evolFunc), range(qSim.Sweep.indMultip), chunksize=1)
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds) # pylint: disable=protected-access

def parallelTimeEvol(qSim, evolFunc, ind):
    _runSweepAndPrep(qSim, ind, evolFunc)
    return qSim.qRes._copyAllResBlank() # pylint: disable=protected-access


# These two functions, respectively, run Sweep and timeDependent (sweep) parameter updates
# In the timeDependet case, evolFunc of first fuctioon is the second function
def _runSweepAndPrep(qSim, ind, evolFunc):
    qSim.Sweep.runSweep(indicesForSweep(ind, *qSim.Sweep.inds))
    for protoc, qSys in qSim.subSys.items():
        protoc.lastState = qSys.initialState
    qSim.qRes._resetLast(calculateException=qSim.qRes) # pylint: disable=protected-access
    evolFunc(qSim)

def timeDependent(qSim):
    qSim.timeDependency.prepare()
    for ind in range(qSim.timeDependency.indMultip):
        qSim.timeDependency.runSweep(indicesForSweep(ind, *qSim.timeDependency.inds))
        for sim in qSim._Simulation__allInstances: # pylint: disable=protected-access
            sim._timeBase__step.value = 1 # pylint: disable=protected-access
        qSim.evolFunc(qSim)


# These two are the specific solution method, user should define their own timeEvol function to use other solution methods
# This flexibility should be reflected into protocol object
def exponUni(qSim):
    for protocol in qSim.subSys.keys():
        protocol.getUnitary()

def timeEvolBase(qSim):
    exponUni(qSim)
    for _ in range(qSim._timeBase__step.value): # pylint: disable=protected-access
        qSim._Simulation__compute() # pylint: disable=protected-access
        for protocol in qSim.subSys.keys():
            sampleCompute = qSim is protocol.simulation
            for __ in range(int(protocol.simulation._timeBase__step.value/qSim._timeBase__step.value)): # pylint: disable=protected-access
                for ___ in range(protocol.simulation.samples):
                    if not sampleCompute:
                        protocol.simulation._Simulation__compute() # pylint: disable=protected-access
                    protocol.lastState = protocol.unitary @ protocol.lastState
