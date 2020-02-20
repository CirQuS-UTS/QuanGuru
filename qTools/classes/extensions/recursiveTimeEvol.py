import qTools.QuantumToolbox.liouvillian as lio
from functools import partial
import numpy as np
import sys

# TODO mutable arguments can be used cleverly
def runSimulation(qSim, p, statesList=[], resultsList=[]):
    if len(qSim.whileLoop.sweeps) > 0:
        if len(qSim.whileLoop.sweeps[0].sweepList) > 1500:
            sys.setrecursionlimit(2*len(qSim.whileLoop.sweeps[0].sweepList))
    condition = qSim.beforeLoop.lCount
    runSequence(qSim.beforeLoop)
    res = runLoop(qSim, p)
    if len(qSim.beforeLoop.sweeps) > 0:
        statesList.append(res[0])
        resultsList.append(res[1])
        if condition < (len(qSim.beforeLoop.sweeps[0].sweepList)-1):
            qSim._Simulation__res(qSim.Loop)
            qSim._Simulation__res(qSim.whileLoop)
            return runSimulation(qSim, p)
        else:
            return [statesList, resultsList]
    else:
        return res


def runLoop(qSim, p):
    states = []
    results = []
    if len(qSim.Loop.sweeps) > 0:
        if p is None:
            for ind in range(len(qSim.Loop.sweeps[0].sweepList)-1):
                res = runTime(qSim, ind)
                # FIXME make this more elegent
                st1 = [qSim.qSys.initialState]
                rs1 = [qSim._Simulation__compute(qSim.qSys, qSim.qSys.initialState)]
                for ind0 in range(len(res[0])-1):
                    st1.append(res[0][ind0])
                    rs1.append(res[1][ind0])
                states.append(st1)
                results.append(rs1)
        else:
            res = p.map(partial(runTime, qSim), range(len(qSim.Loop.sweeps[0].sweepList)-1))
            # FIXME make this more elegent
            for ind in range(len(qSim.Loop.sweeps[0].sweepList)-1):
                st1 = [qSim.qSys.initialState]
                rs1 = [qSim._Simulation__compute(qSim.qSys, qSim.qSys.initialState)]
                for ind0 in range(len(res[ind][0])-1):
                    st1.append(res[ind][0][ind0])
                    rs1.append(res[ind][1][ind0])
                states.append(st1)
                results.append(rs1)
    else:
        # TODO improve these parts in general, possibly decorate
        results = [qSim._Simulation__compute(qSim.qSys, qSim.qSys.initialState)]
        states = [qSim.qSys.initialState]
        # TODO going to modify these for better, but take reseting the final state at the start of time evol into account
        qSim.qSys.lastState = qSim.qSys.initialState
        res = runEvolve(qSim, states, results)
        del results[-1]
        del states[-1]
    return [states, results] if len(results) > 2 else res

# TODO work on these to make them more compact
def runTime(qSim, ind):
    for sw in qSim.Loop.sweeps:
        sw.runSweep(ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    qSim._Simulation__res(qSim.whileLoop)
    results = []
    states = []
    res = runEvolve(qSim, states, results)
    return res


def runEvolve(qSim, states, results):
    conditionW = qSim.whileLoop.lCount
    runSequence(qSim.whileLoop)
    res = __timeEvol(qSim)
    for ind in range(qSim.samples):
        results.append(res[1][ind])
        states.append(res[0][ind])
        
    if len(qSim.whileLoop.sweeps) > 0:
        if conditionW < (len(qSim.whileLoop.sweeps[0].sweepList)-1):
            return runEvolve(qSim, states, results)
        else:
            return [states, results]
    else:
        return res


def __timeEvol(qSim):
    # TODO fix this ratio/sample/steps issue
    if qSim.qSys.Unitaries is None:
        unitary = lio.Liouvillian(2 * np.pi * qSim.qSys.totalHam, timeStep=qSim.stepSize/qSim.ratio)
    else:
        unitary = qSim.qSys.Unitaries(qSim.qSys, qSim.stepSize/qSim.ratio)
        
    state = qSim.qSys.lastState
    states = []
    results = []
    for ii in range(qSim.samples):
        state = unitary @ state
        states.append(state)
        result = qSim._Simulation__compute(qSim.qSys, state)
        results.append(result)
        qSim.qSys.lastState = state
    return [states, results]



def runSequence(qSeq):
    for sweep in qSeq.sweeps:
        ind = sweep.lCounts
        sweep.runSweep(ind)
