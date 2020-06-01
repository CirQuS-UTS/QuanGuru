from functools import partial


def runSimulation(qSim, p):
    qSim._computeBase__calculate(qSim.qSystems, qSim.qEvolutions) # pylint: disable=protected-access
    if p is None:
        nonParalEvol(qSim)
    else:
        paralEvol(qSim, p)


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
    for ind in range(qSim.Sweep.indMultip):
        _runSweepAndPrep(qSim, ind)
        qSim.qRes._organiseSingleProcRes() # pylint: disable=protected-access
    qSim.qRes._finaliseAll(qSim.Sweep.inds) # pylint: disable=protected-access


# multi-processing functions
def paralEvol(qSim, p):
    results = p.map(partial(parallelTimeEvol, qSim), range(qSim.Sweep.indMultip), chunksize=1)
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds) # pylint: disable=protected-access


# need this to avoid return part, which is only needed in multi-processing
def parallelTimeEvol(qSim, ind):
    _runSweepAndPrep(qSim, ind)
    return qSim.qRes._copyAllResBlank() # pylint: disable=protected-access


# These two functions, respectively, run Sweep and timeDependent (sweep) parameter updates
# In the timeDependet case, evolFunc of first fuctioon is the second function
def _runSweepAndPrep(qSim, ind):
    if len(qSim.Sweep.inds) > 0:
        qSim.Sweep.runSweep(indicesForSweep(ind, *qSim.Sweep.inds))

    for protocol in qSim.subSys.keys():
        protocol.currentState = protocol.initialState

    qSim.qRes._resetLast(calculateException=qSim.qRes) # pylint: disable=protected-access

    for protocol, system in qSim.subSys.items():
        protocol._computeBase__calculate([system], [protocol]) # pylint: disable=protected-access
        system._computeBase__calculate([system], [protocol]) # pylint: disable=protected-access

    timeDependent(qSim)


def timeDependent(qSim):
    td = False
    if len(qSim.timeDependency.sweeps) > 0:
        td = True
        qSim.timeDependency.prepare()
        qSim._timeBase__stepCount._value = qSim.timeDependency.indMultip # pylint: disable=protected-access
        for pro, sim in qSim.subSys.items(): # pylint: disable=protected-access
            sim.simulation._timeBase__stepCount._value = sim.simulation.timeDependency.indMultip # pylint: disable=protected-access
            pro.simulation._timeBase__stepCount._value = pro.simulation.timeDependency.indMultip # pylint: disable=protected-access
    timeEvolDefault(qSim, td)


# These are the specific solution method, user should define their own timeEvol function to use other solution methods
# This flexibility should be reflected into protocol object

def timeEvolDefault(qSim, td):
    for ind in range(qSim.stepCount):
        if td:
            qSim.timeDependency.runSweep(indicesForSweep(ind, *qSim.timeDependency.inds))
        qSim._Simulation__compute() # pylint: disable=protected-access
        qSim.evolFunc(qSim)

def timeEvolBase(qSim):
    for protocol in qSim.subSys.keys():
        qSim.subSys[protocol]._computeBase__compute(protocol.currentState) # pylint: disable=protected-access
        sampleCompute = qSim is protocol.simulation
        for __ in range(int(protocol.simulation._timeBase__stepCount.value/qSim._timeBase__stepCount.value)): # pylint: disable=protected-access, line-too-long
            for ___ in range(protocol.simulation.samples):
                if not sampleCompute:
                    protocol.simulation._Simulation__compute() # pylint: disable=protected-access

                if protocol.compute is None:
                    protocol.currentState = protocol.unitary @ protocol.currentState
                else:
                    for step in protocol.subSys.values():
                        protocol.currentState = step.unitary @ protocol.currentState
                        protocol._computeBase__compute([protocol.currentState]) # pylint: disable=protected-access
