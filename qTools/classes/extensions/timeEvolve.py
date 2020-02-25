import qTools.QuantumToolbox.liouvillian as lio
from functools import partial
import numpy as np
import copy


def runSimulation(qSim, p):
    if qSim.delState is False:
        if len(qSim.beforeLoop.sweeps) > 0:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        mixedStRes = withBLWnp(qSim)
                    else:
                        mixedStRes = withBLWp(qSim, p)
                else:
                    if p is None:
                        mixedStRes = withBLOnp(qSim)
                    else:
                        mixedStRes = withBLOp(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    mixedStRes = withBOW(qSim)
                else:
                    mixedStRes = withBOO(qSim)
        else:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        mixedStRes = withLWnp(qSim)
                    else:
                        mixedStRes = withLWp(qSim, p)
                else:
                    if p is None:
                        mixedStRes = withLOnp(qSim)
                    else:
                        mixedStRes = withLOp(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    mixedStRes = withW(qSim)
                else:
                    qSim.qSys.lastState = qSim.qSys.initialState
                    unitary = exponUni(qSim)
                    mixedStRes = __timeEvol(qSim, unitary)
        return mixedStRes
    else:
        if len(qSim.beforeLoop.sweeps) > 0:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        results = withBLWnpDel(qSim)
                    else:
                        results = withBLWpDel(qSim, p)
                else:
                    if p is None:
                        results = withBLOnpDel(qSim)
                    else:
                        results = withBLOpDel(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    results = withBOWDel(qSim)
                else:
                    results = withBOODel(qSim)
        else:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        results = withLWnpDel(qSim)
                    else:
                        results = withLWpDel(qSim, p)
                else:
                    if p is None:
                        results = withLOnpDel(qSim)
                    else:
                        results = withLOpDel(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    results = withWDel(qSim)
                else:
                    qSim.qSys.lastState = qSim.qSys.initialState
                    unitary = exponUni(qSim)
                    results = __timeEvolDel(qSim, unitary)
        return results
"""
STAGE 1 POSSIBILITIES
"""
def withBLWnp(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLWnp(qSim)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBLWp(qSim, p):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLWp(qSim, p)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBLOnp(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLOnp(qSim)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBLOp(qSim, p):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLOp(qSim, p)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBOW(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withW(qSim)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBOO(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        st1 = []
        rs1 = []
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            mixedStRes = __timeEvol(qSim, unitary)
            st1.extend(mixedStRes[0])
            rs1.extend(mixedStRes[1])
        states.append(st1)
        results.append(rs1)
    return [states, results]

# with Del
def withBLWnpDel(qSim):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        results.append(withLWnpDel(qSim))
    return results

def withBLWpDel(qSim, p):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        results.append(withLWpDel(qSim, p))
    return results

def withBLOnpDel(qSim):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        results.append(withLOnpDel(qSim))
    return results

def withBLOpDel(qSim, p):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        results.append(withLOpDel(qSim, p))
    return results

def withBOWDel(qSim):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        results.append(withWDel(qSim))
    return results

def withBOODel(qSim):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        runSequence(qSim.beforeLoop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        rs1 = []
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            rs1.extend(__timeEvol(qSim, unitary))
        results.append(rs1)
    return results
     
"""
STAGE 2 POSSIBILITIES
"""
def withLWnp(qSim):
    states = []
    results = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        runSequence(qSim.Loop, ind)
        mixedStRes = withW(qSim)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withLOnp(qSim):
    states = []
    results = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        runSequence(qSim.Loop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        st1 = []
        rs1 = []
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            mixedStRes = __timeEvol(qSim, unitary)
            st1.extend(mixedStRes[0])
            rs1.extend(mixedStRes[1])
        states.append(st1)
        results.append(rs1)
    return [states, results]

def withLWp(qSim, p):
    mixedStRes = p.map(partial(parallelSequenceW, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    states = []
    results = []
    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        st1 = []
        rs1 = []
        for ind1 in range(len(mixedStRes[ind0][0])):
            st1.append(mixedStRes[ind0][0][ind1])
            rs1.append(mixedStRes[ind0][1][ind1])
        states.append(st1)
        results.append(rs1)
    return [states, results]
 
def parallelSequenceW(qSim, ind):
    runSequence(qSim.Loop, ind)
    mixedStRes = withW(qSim)
    return [mixedStRes[0], mixedStRes[1]]

def withLOp(qSim, p):
    mixedStRes = p.map(partial(parallelSequenceO, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    states = []
    results = []
    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        states.append(mixedStRes[ind0][0])
        results.append(mixedStRes[ind0][1])
    return [states, results]

def parallelSequenceO(qSim, ind):
    runSequence(qSim.Loop, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    states = []
    results = []
    unitary = exponUni(qSim)
    for ii in range(qSim.steps):
        mixedStRes = __timeEvol(qSim, unitary)
        states.extend(mixedStRes[0])
        results.extend(mixedStRes[1])
    return [states, results]

# with Del
def withLWnpDel(qSim):
    results = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        runSequence(qSim.Loop, ind)
        results.append(withWDel(qSim))
    return results

def withLOnpDel(qSim):
    results = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        runSequence(qSim.Loop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        result = []
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            result.extend(__timeEvolDel(qSim, unitary))
        results.append(result)
    return results

def withLWpDel(qSim, p):
    results = p.map(partial(parallelSequenceWDel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    return results

def parallelSequenceWDel(qSim, ind):
    runSequence(qSim.Loop, ind)
    results = withWDel(qSim)
    return results
    
def withLOpDel(qSim, p):
    results = p.map(partial(parallelSequenceODel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    return results

def parallelSequenceODel(qSim, ind):
    runSequence(qSim.Loop, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    results = []
    unitary = exponUni(qSim)
    for ii in range(qSim.steps):
        results.extend(__timeEvolDel(qSim, unitary))
    return results

"""
STAGE 3 POSSIBILITIES
"""
def withW(qSim):
    states = []
    results = []
    qSim.qSys.lastState = qSim.qSys.initialState
    for ind in range(len(qSim.whileLoop.sweeps[0].sweepList)):
        runSequence(qSim.whileLoop, ind)
        unitary = exponUni(qSim)
        mixedStRes = __timeEvol(qSim, unitary)
        states.extend(mixedStRes[0])
        results.extend(mixedStRes[1])
    return [states, results]

# with Del
def withWDel(qSim):
    results = []
    qSim.qSys.lastState = qSim.qSys.initialState
    for ind in range(len(qSim.whileLoop.sweeps[0].sweepList)):
        runSequence(qSim.whileLoop, ind)
        unitary = exponUni(qSim)
        results.extend(__timeEvolDel(qSim, unitary))
    return results

"""
TIME EVOLVE
"""
def __timeEvolDel(qSim, unitary):
    results = []
    for ii in range(qSim.samples):
        qSim.qSys.lastState = unitary @ qSim.qSys.lastState
        result = qSim._Simulation__compute(qSim.qSys, qSim.qSys.lastState)
        results.append(result)
    return results

def __timeEvol(qSim, unitary):    
    states = []
    results = []
    for ii in range(qSim.samples):
        qSim.qSys.lastState = unitary @ qSim.qSys.lastState
        states.append(qSim.qSys.lastState)
        result = qSim._Simulation__compute(qSim.qSys, qSim.qSys.lastState)
        results.append(result)
    return [states, results]

def exponUni(qSim):
    if qSim.qSys.Unitaries is None:
        unitary = lio.Liouvillian(2 * np.pi * qSim.qSys.totalHam, timeStep=qSim.stepSize/qSim.samples)
    else:
        unitary = qSim.qSys.Unitaries(qSim.qSys, qSim.stepSize/qSim.samples)
    return unitary

def runSequence(qSeq, ind):
    for sweep in qSeq.sweeps:
        sweep.runSweep(ind)
