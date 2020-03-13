import qTools.QuantumToolbox.liouvillian as lio
from qTools.classes.QUni import qUniversal
from functools import partial
import numpy as np
from copy import deepcopy


def runSimulation(qSim, p):
    if qSim.delState is False:
        if len(qSim.beforeLoop.sweeps) > 0:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        withBLWnp(qSim)
                    else:
                        withBLWp(qSim, p)
                else:
                    if p is None:
                        withBLOnp(qSim)
                    else:
                        withBLOp(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    withBOW(qSim)
                else:
                    withBOO(qSim)
        else:
            if len(qSim.Loop.sweeps) > 0:
                if len(qSim.whileLoop.sweeps) > 0:
                    if p is None:
                        qSim.qRes.indB = 0
                        withLWnp(qSim)
                    else:
                        qSim.qRes.indB = 0
                        withLWp(qSim, p)
                else:
                    if p is None:
                        qSim.qRes.indB = 0
                        withLOnp(qSim)
                    else:
                        qSim.qRes.indB = 0
                        withLOp(qSim, p)
            else:
                if len(qSim.whileLoop.sweeps) > 0:
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    withW(qSim)
                else:
                    for qSys in qSim.subSystems.values():
                        qSys._genericQSys__prepareLastStateList()
                    unitary = exponUni(qSim)
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    __timeEvol(qSim, unitary)
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
                    for qSys in qSim.subSystems.values():
                        qSys._genericQSys__prepareLastStateList()
                    unitary = exponUni(qSim)
                    qSim.qRes.indB = 0
                    qSim.qRes.indL = 0
                    __timeEvolDel(qSim, unitary)

# STAGE 1 POSSIBILITIES
def withBLWnp(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLWnp(qSim)

def withBLWp(qSim, p):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLWp(qSim, p)

def withBLOnp(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLOnp(qSim)

def withBLOp(qSim, p):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withLOp(qSim, p)

def withBOW(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        withW(qSim)

def withBOO(qSim):
    for ind in range(len(qSim.beforeLoop.sweeps[0].sweepList)):
        qSim.qRes.indB = ind
        runSequence(qSim.beforeLoop, ind)
        for qSys in qSim.subSystems.values():
            qSys._genericQSys__prepareLastStateList()
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            __timeEvol(qSim, unitary)

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
        for qSys in qSim.subSystems.values():
            qSys._genericQSys__prepareLastStateList()
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            __timeEvol(qSim, unitary)
     
# STAGE 2 POSSIBILITIES
def withLWnp(qSim):
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        withW(qSim)

def withLOnp(qSim):
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes.indL = ind
        runSequence(qSim.Loop, ind)
        for qSys in qSim.subSystems.values():
            qSys._genericQSys__prepareLastStateList()
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            __timeEvol(qSim, unitary)

def withLWp(qSim, p):
    mixedStRes = p.map(partial(parallelSequenceW, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    for ind in range(len(mixedStRes[0][1])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))

    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes._qResults__states[qSim.qRes.indB][ind0] = mixedStRes[ind0][0]
        for ind1 in range(len(mixedStRes[ind0][1])):
            qSim.qRes._qResults__multiResults[ind1][qSim.qRes.indB][ind0] = mixedStRes[ind0][1][ind1]
 
def parallelSequenceW(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    qSim.qRes._qResults__last = []
    qSim.qRes._qResults__prevRes = False
    qSim.qRes._qResults__resTotCount = 0
    withW(qSim)
    return [qSim.qRes._qResults__states, qSim.qRes._qResults__last]

def withLOp(qSim, p):
    mixedStRes = p.map(partial(parallelSequenceO, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    for ind in range(len(mixedStRes[0][1])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))

    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        qSim.qRes._qResults__states[qSim.qRes.indB][ind0] = mixedStRes[ind0][0]
        for ind1 in range(len(mixedStRes[ind0][1])):
            qSim.qRes._qResults__multiResults[ind1][qSim.qRes.indB][ind0] = mixedStRes[ind0][1][ind1]

def parallelSequenceO(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    for qSys in qSim.subSystems.values():
        qSys._genericQSys__prepareLastStateList()
    unitary = exponUni(qSim)
    qSim.qRes._qResults__last = []
    qSim.qRes._qResults__prevRes = False
    qSim.qRes._qResults__resTotCount = 0
    for ii in range(qSim.steps):
        __timeEvol(qSim, unitary)
    return [qSim.qRes._qResults__states, qSim.qRes._qResults__last]

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
        for qSys in qSim.subSystems.values():
            qSys._genericQSys__prepareLastStateList()
        unitary = exponUni(qSim)
        for ii in range(qSim.steps):
            __timeEvolDel(qSim, unitary)

def withLWpDel(qSim, p):
    results = p.map(partial(parallelSequenceWDel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    for ind in range(len(results[0])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))
        
    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        for ind1 in range(len(results[ind0])):
            qSim.qRes._qResults__multiResults[ind1][qSim.qRes.indB][ind0] = results[ind0][ind1]

def parallelSequenceWDel(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    qSim.qRes._qResults__last = []
    qSim.qRes._qResults__prevRes = False
    qSim.qRes._qResults__resTotCount = 0
    withWDel(qSim)
    return qSim.qRes._qResults__last
    
def withLOpDel(qSim, p):
    results = p.map(partial(parallelSequenceODel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    for ind in range(len(results[0])):
        qSim.qRes._qResults__multiResults.append(deepcopy(qSim.qRes._qResults__results))

    for ind0 in range(len(qSim.Loop.sweeps[0].sweepList)):
        for ind1 in range(len(results[ind0])):
            qSim.qRes._qResults__multiResults[ind1][qSim.qRes.indB][ind0] = results[ind0][ind1]

def parallelSequenceODel(qSim, ind):
    qSim.qRes.indL = ind
    runSequence(qSim.Loop, ind)
    for qSys in qSim.subSystems.values():
        qSys._genericQSys__prepareLastStateList()
    unitary = exponUni(qSim)
    qSim.qRes._qResults__last = []
    qSim.qRes._qResults__prevRes = False
    qSim.qRes._qResults__resTotCount = 0
    for ii in range(qSim.steps):
        __timeEvolDel(qSim, unitary)
    return qSim.qRes._qResults__last

# STAGE 3 POSSIBILITIES
def withW(qSim):
    for qSys in qSim.subSystems.values():
        qSys._genericQSys__prepareLastStateList()

    for ind in range(len(qSim.whileLoop.sweeps[0].sweepList)):
        runSequence(qSim.whileLoop, ind)
        unitary = exponUni(qSim)
        __timeEvol(qSim, unitary)

# with Del
def withWDel(qSim):
    for qSys in qSim.subSystems.values():
        qSys._genericQSys__prepareLastStateList()

    for ind in range(len(qSim.whileLoop.sweeps[0].sweepList)):
        runSequence(qSim.whileLoop, ind)
        unitary = exponUni(qSim)
        __timeEvolDel(qSim, unitary)

# TIME EVOLVE
def __timeEvolDel(qSim, unitaryList):
    for ii in range(qSim.samples):
        for idx, qSys in enumerate(qSim.subSystems.values()):
            for ind, unitary in enumerate(unitaryList[idx]):
                qSys._genericQSys__lastStateList[ind] = unitary @ qSys._genericQSys__lastStateList[ind]
        qSim.qRes._qResults__resCount = 0
        qSim._Simulation__compute()
        qSim.qRes._qResults__prevRes = True
        
def __timeEvol(qSim, unitaryList):
    for ii in range(qSim.samples):
        for idx, qSys in enumerate(qSim.subSystems.values()):
            for ind, unitary in enumerate(unitaryList[idx]):
                qSys._genericQSys__lastStateList[ind] = unitary @ qSys._genericQSys__lastStateList[ind]
            qSim.qRes.state = qSys._genericQSys__lastStateList
        qSim.qRes._qResults__resCount = 0
        qSim._Simulation__compute()
        qSim.qRes._qResults__prevRes = True

def exponUni(qSim):
    unitary = []
    for qSys in qSim.subSystems.values():
        subUni = qSys.unitary
        if not isinstance(subUni, list):
            unitary.append([subUni])
        else:
            unitary.append(subUni)
    return unitary

def runSequence(qSeq, ind):
    for sweep in qSeq.sweeps:
        sweep.runSweep(ind)
