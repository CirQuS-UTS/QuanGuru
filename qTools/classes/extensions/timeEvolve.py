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
                        qSim.qRes.indB = 0
                        mixedStRes = withLWnp(qSim)
                    else:
                        qSim.qRes.indB = 0
                        mixedStRes = withLWp(qSim, p)
                else:
                    if p is None:
                        qSim.qRes.indB = 0
                        mixedStRes = withLOnp(qSim)
                    else:
                        qSim.qRes.indB = 0
                        mixedStRes = withLOp(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    mixedStRes = withW(qSim)
                else:
                    qSim.qSys.lastState = qSim.qSys.initialState
                    unitary = exponUni(qSim)
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
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
                        qSim.qRes.indB = 0
                        results = withLWnpDel(qSim)
                    else:
                        qSim.qRes.indB = 0
                        results = withLWpDel(qSim, p)
                else:
                    if p is None:
                        qSim.qRes.indB = 0
                        results = withLOnpDel(qSim)
                    else:
                        qSim.qRes.indB = 0
                        results = withLOpDel(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    results = withWDel(qSim)
                else:
                    qSim.qSys.lastState = qSim.qSys.initialState
                    unitary = exponUni(qSim)
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    results = __timeEvolDel(qSim, unitary)
        return results
"""
STAGE 1 POSSIBILITIES
"""
def withBLWnp(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLWnp(qSim)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBLWp(qSim, p):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLWp(qSim, p)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBLOnp(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLOnp(qSim)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBLOp(qSim, p):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLOp(qSim, p)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBOW(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withW(qSim)
        states.append(mixedStRes[0])
        results.append(mixedStRes[1])
    return [states, results]

def withBOO(qSim):
    states = []
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
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
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        results.append(withLWnpDel(qSim))
    return results

def withBLWpDel(qSim, p):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        results.append(withLWpDel(qSim, p))
    return results

def withBLOnpDel(qSim):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        results.append(withLOnpDel(qSim))
    return results

def withBLOpDel(qSim, p):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        results.append(withLOpDel(qSim, p))
    return results

def withBOWDel(qSim):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        results.append(withWDel(qSim))
    return results

def withBOODel(qSim):
    results = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
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
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        states.append(withW(qSim))
    return states

def withLOnp(qSim):
    states = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        st1 = []
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            st1.extend(__timeEvol(qSim, unitary))
        states.append(st1)
    return states

def withLWp(qSim, p):
    mixedStRes = p.map(partial(parallelSequenceW, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    states = []
    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        st1 = []
        for ind1 in range(len(mixedStRes[ind0][0])):
            st1.append(mixedStRes[ind0][0][ind1])
        qSim.qRes.results[qSim.qRes.indB][ind0] = mixedStRes[ind0][1]
        states.append(st1)
    return states
 
def parallelSequenceW(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    mixedStRes = withW(qSim)
    return [mixedStRes[0], qSim.qRes.results[qSim.qRes.indB][ind]]

def withLOp(qSim, p):
    mixedStRes = p.map(partial(parallelSequenceO, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    states = []
    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        states.append(mixedStRes[ind0][0])
        qSim.qRes.results[qSim.qRes.indB][ind0] = mixedStRes[ind0][1]
    return states

def parallelSequenceO(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    states = []
    results = []
    unitary = exponUni(qSim)
    for ii in range(qSim.steps):
        mixedStRes = __timeEvol(qSim, unitary)
        states.extend(mixedStRes[0])
        results.extend(mixedStRes[1])
    return [states, qSim.qRes.results[qSim.qRes.indB][ind]]

# with Del
def withLWnpDel(qSim):
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        withWDel(qSim)

def withLOnpDel(qSim):
    results = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            __timeEvolDel(qSim, unitary)

def withLWpDel(qSim, p):
    results = p.map(partial(parallelSequenceWDel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    qSim.qRes.results[qSim.qRes.indB] = results

def parallelSequenceWDel(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    results = withWDel(qSim)
    return qSim.qRes.results[qSim.qRes.indB][ind]
    
def withLOpDel(qSim, p):
    results = p.map(partial(parallelSequenceODel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    qSim.qRes.results[qSim.qRes.indB] = results

def parallelSequenceODel(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    unitary = exponUni(qSim)
    for ii in range(qSim.steps):
        __timeEvolDel(qSim, unitary)
    return qSim.qRes.results[qSim.qRes.indB][ind]

"""
STAGE 3 POSSIBILITIES
"""
def withW(qSim):
    states = []
    qSim.qSys.lastState = qSim.qSys.initialState
    for ind in range(len(qSim.whileLoop.sweeps[0].sweepList)):
        runSequence(qSim.whileLoop, ind)
        unitary = exponUni(qSim)
        states.extend(__timeEvol(qSim, unitary))
    return states

# with Del
def withWDel(qSim):
    qSim.qSys.lastState = qSim.qSys.initialState
    for ind in range(len(qSim.whileLoop.sweeps[0].sweepList)):
        runSequence(qSim.whileLoop, ind)
        unitary = exponUni(qSim)
        __timeEvolDel(qSim, unitary)

"""
TIME EVOLVE
"""
def __timeEvolDel(qSim, unitary):
    for ii in range(qSim.samples):
        qSim.qSys.lastState = unitary @ qSim.qSys.lastState
        qSim.qRes._qResults__resCount = 0
        qSim._Simulation__compute(qSim.qSys, qSim.qSys.lastState)
        qSim.qRes._qResults__prevRes = True
        

def __timeEvol(qSim, unitary):    
    states = []
    for ii in range(qSim.samples):
        qSim.qSys.lastState = unitary @ qSim.qSys.lastState
        states.append(qSim.qSys.lastState)
        qSim.qRes._qResults__resCount = 0
        qSim._Simulation__compute(qSim.qSys, qSim.qSys.lastState)
        qSim.qRes._qResults__prevRes = True
    return states

def exponUni(qSim):
    if qSim.qSys.Unitaries is None:
        unitary = lio.Liouvillian(2 * np.pi * qSim.qSys.totalHam, timeStep=qSim.stepSize/qSim.samples)
    else:
        unitary = qSim.qSys.Unitaries(qSim.qSys, qSim.stepSize/qSim.samples)
    return unitary

def runSequence(qSeq, ind):
    for sweep in qSeq.sweeps:
        sweep.runSweep(ind)
