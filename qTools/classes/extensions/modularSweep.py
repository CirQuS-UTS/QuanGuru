import qTools.QuantumToolbox.liouvillian as lio
from qTools.classes.QUni import qUniversal
from functools import partial
import numpy as np
from copy import deepcopy
import datetime
import matplotlib.pyplot as plt


def modularSweep(ind, *args):
    remain = 0
    indices = []
    for arg in args:
        #print(ind, arg)
        remain = ind%arg
        ind = (ind-remain)/arg
        indices.insert(0, int(remain))
    return indices


def withLOpDel(qSim, p):
    nw = datetime.datetime.now()
    results = p.map(partial(parallelSequenceODel, qSim), range(qSim.indMultip))
    en = datetime.datetime.now()

    for res in results:
        for key, val in res.items():
            qSim.qRes._qResults__results[key].append(val)
    
    for key, val in qSim.qRes._qResults__results.items():
        qSim.qRes._qResults__results[key] = np.reshape(val, (*list(reversed(qSim.inds)),qSim.steps,))


def parallelSequenceODel(qSim, ind):
    indices = modularSweep(ind, *qSim.inds)
    runSequence(qSim.Loop, indices)
    for qSys in qSim.subSys.values():
        qSys._genericQSys__prepareLastStateList()
    unitary = exponUni(qSim)
    qSim.qRes.resetLast()
    for ii in range(qSim.steps):
        __timeEvolDel(qSim, unitary)
    return qSim.qRes.results

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