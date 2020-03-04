from functools import partial
import numpy as np
import datetime


def runSimulation(qSim, p):
    '''if qSim.delState is False:
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
                for qSys in qSim.subSys.values():
                    qSys._genericQSys__prepareLastStateList()
                unitary = exponUni(qSim)
                qSim.qRes.indB = 0
                qSim.qRes.indL = 0
                __timeEvol(qSim, unitary)
    else:'''
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
            for qSys in qSim.subSys.values():
                qSys._genericQSys__prepareLastStateList()
            unitary = exponUni(qSim)
            qSim.qRes.indB = 0
            qSim.qRes.indL = 0
            __timeEvolDel(qSim, unitary)


def indicesForSweep(ind, *args):
    remain = 0
    indices = []
    for arg in args:
        #print(ind, arg)
        remain = ind%arg
        ind = (ind-remain)/arg
        indices.insert(0, int(remain))
    return indices


def withLWnpDel(qSim):
    results = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        indices = indicesForSweep(ind, *qSim.inds)
        runSequence(qSim.Loop, ind)
        qSim.qRes.resetLast()
        withWDel(qSim)
        results.append(qSim.qRes.results)

def withLOnpDel(qSim):
    results = []
    for ind in range(len(qSim.Loop.sweeps[0].sweepList)):
        indices = indicesForSweep(ind, *qSim.inds)
        runSequence(qSim.Loop, ind)
        for qSys in qSim.subSys.values():
            qSys._genericQSys__prepareLastStateList()
        unitary = exponUni(qSim)
        qSim.qRes.resetLast()
        for ii in range(qSim.steps):
            __timeEvolDel(qSim, unitary)
        results.append(qSim.qRes.results)

def withLWpDel(qSim, p):
    results = p.map(partial(parallelSequenceWDel, qSim), range(len(qSim.Loop.sweeps[0].sweepList)))
    qSim.qRes._organiseRes(results, qSim.inds, qSim.indMultip)
            

def parallelSequenceWDel(qSim, ind):
    indices = indicesForSweep(ind, *qSim.inds)
    runSequence(qSim.Loop, indices)
    qSim.qRes.resetLast()
    withWDel(qSim)
    return qSim.qRes.results


def withLOpDel(qSim, p):
    nw = datetime.datetime.now()
    results = p.map(partial(parallelSequenceODel, qSim), range(qSim.indMultip))
    en = datetime.datetime.now()
    qSim.qRes._organiseRes(results, qSim.inds, qSim.indMultip)


def parallelSequenceODel(qSim, ind):
    indices = indicesForSweep(ind, *qSim.inds)
    runSequence(qSim.Loop, indices)
    for qSys in qSim.subSys.values():
        qSys._genericQSys__prepareLastStateList()
    unitary = exponUni(qSim)
    qSim.qRes.resetLast()
    for ii in range(qSim.steps):
        __timeEvolDel(qSim, unitary)
    return qSim.qRes.results

def withWDel(qSim):
    for qSys in qSim.subSys.values():
        qSys._genericQSys__prepareLastStateList()

    for ind in range(len(qSim.whileLoop.sweeps[0].sweepList)):
        runSequence(qSim.whileLoop, ind)
        unitary = exponUni(qSim)
        __timeEvolDel(qSim, unitary)

def __timeEvolDel(qSim, unitaryList):
    for ii in range(qSim.samples):
        for idx, qSys in enumerate(qSim.subSys.values()):
            for ind, unitary in enumerate(unitaryList[idx]):
                qSys._genericQSys__lastStateList[ind] = unitary @ qSys._genericQSys__lastStateList[ind]
        qSim._Simulation__compute()


def exponUni(qSim):
    unitary = []
    for qSys in qSim.subSys.values():
        subUni = qSys.unitary
        if not isinstance(subUni, list):
            unitary.append([subUni])
        else:
            unitary.append(subUni)
    return unitary

def runSequence(qSeq, ind):
    for i, sweep in enumerate(qSeq.sweeps):
        sweep.runSweep(ind[sweep.ind])