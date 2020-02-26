import qTools.QuantumToolbox.liouvillian as lio
from functools import partial
import numpy as np
from copy import deepcopy


def runSimulation(qSim, p):
    if qSim.delState is False:
        if len(qSim.beforeLoop.sweeps) > 0:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        states = withBLWnp(qSim)
                    else:
                        states = withBLWp(qSim, p)
                else:
                    if p is None:
                        states = withBLOnp(qSim)
                    else:
                        states = withBLOp(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    states = withBOW(qSim)
                else:
                    states = withBOO(qSim)
        else:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        qSim.qRes.indB = 0
                        states = withLWnp(qSim)
                    else:
                        qSim.qRes.indB = 0
                        states = withLWp(qSim, p)
                else:
                    if p is None:
                        qSim.qRes.indB = 0
                        states = withLOnp(qSim)
                    else:
                        qSim.qRes.indB = 0
                        states = withLOp(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    states = withW(qSim)
                else:
                    qSim.qSys.lastState = qSim.qSys.initialState
                    unitary = exponUni(qSim)
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    states = __timeEvol(qSim, unitary)
        return states
    else:
        if len(qSim.beforeLoop.sweeps) > 0:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        withBLWnpDel(qSim)
                    else:
                        withBLWpDel(qSim, p)
                else:
                    if p is None:
                        withBLOnpDel(qSim)
                    else:
                        withBLOpDel(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    withBOWDel(qSim)
                else:
                    withBOODel(qSim)
        else:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        qSim.qRes.indB = 0
                        withLWnpDel(qSim)
                    else:
                        qSim.qRes.indB = 0
                        withLWpDel(qSim, p)
                else:
                    if p is None:
                        qSim.qRes.indB = 0
                        withLOnpDel(qSim)
                    else:
                        qSim.qRes.indB = 0
                        withLOpDel(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    withWDel(qSim)
                else:
                    qSim.qSys.lastState = qSim.qSys.initialState
                    unitary = exponUni(qSim)
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    __timeEvolDel(qSim, unitary)
        return None
"""
STAGE 1 POSSIBILITIES
"""
def withBLWnp(qSim):
    states = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        states.append(withLWnp(qSim))
    return states

def withBLWp(qSim, p):
    states = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        states.append(withLWp(qSim, p))
    return states

def withBLOnp(qSim):
    states = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        states.append(withLOnp(qSim))
    return states

def withBLOp(qSim, p):
    states = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        mixedStRes = withLOp(qSim, p)
        states.append(mixedStRes[0])
    return states

def withBOW(qSim):
    states = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        states.append(withW(qSim))
    return states

def withBOO(qSim):
    states = []
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        st1 = []
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            st1.extend(__timeEvol(qSim, unitary))
        states.append(st1)
    return states

# with Del
def withBLWnpDel(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLWnpDel(qSim)

def withBLWpDel(qSim, p):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLWpDel(qSim, p)

def withBLOnpDel(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLOnpDel(qSim)

def withBLOpDel(qSim, p):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLOpDel(qSim, p)

def withBOWDel(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withWDel(qSim)

def withBOODel(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            __timeEvol(qSim, unitary)
     
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
    for ind in range(len(mixedStRes[0][1])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))

    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        states.append(mixedStRes[ind0][0])
        for ind1 in range(len(mixedStRes[ind0][1])):
            qSim.qRes._qResults__multiResults[ind1][qSim.qRes.indB][ind0] = mixedStRes[ind0][1][ind1]
    return states
 
def parallelSequenceW(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    mixedStRes = withW(qSim)
    return [mixedStRes[0], qSim.qRes._qResults__last]

def withLOp(qSim, p):
    mixedStRes = p.map(partial(parallelSequenceO, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    states = []
    for ind in range(len(mixedStRes[0][1])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))

    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        states.append(mixedStRes[ind0][0])
        for ind1 in range(len(mixedStRes[ind0][1])):
            qSim.qRes._qResults__multiResults[ind1][qSim.qRes.indB][ind0] = mixedStRes[ind0][1][ind1]
    return states

def parallelSequenceO(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    states = []
    unitary = exponUni(qSim)
    for ii in range(qSim.steps):
        mixedStRes = __timeEvol(qSim, unitary)
        states.extend(mixedStRes[0])
    return [states, qSim.qRes._qResults__last]

# with Del
def withLWnpDel(qSim):
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        withWDel(qSim)

def withLOnpDel(qSim):
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        qSim.qSys.lastState = qSim.qSys.initialState
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            __timeEvolDel(qSim, unitary)

def withLWpDel(qSim, p):
    results = p.map(partial(parallelSequenceWDel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    for ind in range(len(results[0])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))
        
    for ind0 in range(results[0]):
        for ind1 in range(len(qSim.Loop.sweeps[0].sweepList)):
            qSim.qRes._qResults__multiResults[ind0][qSim.qRes.indB][ind1] = results[ind0][ind1]

def parallelSequenceWDel(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    withWDel(qSim)
    return qSim.qRes._qResults__last
    
def withLOpDel(qSim, p):
    results = p.map(partial(parallelSequenceODel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    for ind in range(len(results[0])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))

    for ind0 in range(results[0]):
        for ind1 in range(len(qSim.Loop.sweeps[0].sweepList)):
            qSim.qRes._qResults__multiResults[ind0][qSim.qRes.indB][ind1] = results[ind0][ind1]


def parallelSequenceODel(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    qSim.qSys.lastState = qSim.qSys.initialState
    unitary = exponUni(qSim)
    for ii in range(qSim.steps):
        __timeEvolDel(qSim, unitary)
    return qSim.qRes._qResults__last

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
