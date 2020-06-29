from functools import partial


def runSimulation(qSim, p):
    if qSim._computeBase__calculateAtStart in (True, None): #pylint: disable=protected-access
        qSim._computeBase__calculateMeth() # pylint: disable=protected-access

    if p is None:
        nonParalEvol(qSim)
    else:
        paralEvol(qSim, p)

    if qSim._computeBase__calculateAtStart in (False, None): #pylint: disable=protected-access
        qSim._computeBase__calculateMeth() # pylint: disable=protected-access


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
# In the timeDependet case, evolFunc of first function is the second function
def _runSweepAndPrep(qSim, ind):
    if len(qSim.Sweep.inds) > 0:
        qSim.Sweep.runSweep(qSim.Sweep._indicesForSweep(ind, *qSim.Sweep.inds))

    for protocol in qSim.subSys.keys():
        protocol.currentState = protocol.initialState

    qSim.qRes._resetLast(calculateException=qSim.qRes) # pylint: disable=protected-access

    for protocol, system in qSim.subSys.items():
        if protocol._computeBase__calculateAtStart in (True, None): #pylint: disable=protected-access
            protocol._computeBase__calculateMeth() # pylint: disable=protected-access

        if system._computeBase__calculateAtStart in (True, None): #pylint: disable=protected-access
            system._computeBase__calculateMeth() # pylint: disable=protected-access

    timeDependent(qSim)


def timeDependent(qSim):
    td = False
    if len(qSim.timeDependency.sweeps) > 0:
        td = True
        if list(qSim.timeDependency.sweeps.values())[0]._sweepList is not None: #pylint: disable=protected-access
            qSim.timeDependency.prepare()
        else:
            qSim.timeDependency._Sweep__inds = [qSim.stepCount] #pylint: disable=protected-access
        # TODO timeDependency multi-parameter sweep ?
        #qSim._timeBase__stepCount._value = qSim.timeDependency.indMultip # pylint: disable=protected-access
        for pro, sim in qSim.subSys.items(): # pylint: disable=protected-access
            sim.simulation._timeBase__stepCount._value = sim.simulation.timeDependency.indMultip # pylint: disable=protected-access
            pro.simulation._timeBase__stepCount._value = pro.simulation.timeDependency.indMultip # pylint: disable=protected-access
    timeEvolDefault(qSim, td)


# These are the specific solution method, user should define their own timeEvol function to use other solution methods
# This flexibility should be reflected into protocol object

def timeEvolDefault(qSim, td):
    qSim._Simulation__compute() # pylint: disable=protected-access
    for protocol in qSim.subSys.keys():
        qSim.subSys[protocol]._computeBase__compute([protocol.currentState]) # pylint: disable=protected-access
        protocol._computeBase__compute([protocol.currentState]) # pylint: disable=protected-access

    for ind in range(qSim.stepCount):
        qSim._Simulation__index = ind # pylint: disable=protected-access
        if td:
            qSim.timeDependency.runSweep(qSim.timeDependency._indicesForSweep(ind, *qSim.timeDependency.inds))
        qSim.evolFunc(qSim)
        qSim._Simulation__compute() # pylint: disable=protected-access

    for protocol, system in qSim.subSys.items():
        if protocol._computeBase__calculateAtStart in (False, None): #pylint: disable=protected-access
            protocol._computeBase__calculateMeth() # pylint: disable=protected-access

        if system._computeBase__calculateAtStart in (False, None): #pylint: disable=protected-access
            system._computeBase__calculateMeth() # pylint: disable=protected-access

def timeEvolBase(qSim):
    for protocol in qSim.subSys.keys():
        qSim.subSys[protocol]._computeBase__compute([protocol.currentState]) # pylint: disable=protected-access
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
