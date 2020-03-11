from functools import partial
import numpy as np
import datetime
from copy import deepcopy
#from qTools.classes.QResDict import qResultsContainer

def runSimulation(qSim, p):
    '''if qSim.delState is False:
        if len(qSim.Loop.sweeps) > 0:
            if len(qSim.timeDependency.sweeps) > 0:
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
            if len(qSim.timeDependency.sweeps) > 0:
                qSim.qRes.indB = 0
                qSim.qRes.indL = 0
                withW(qSim)
            else:
                for protoc, qSys in qSim.subSys.items():
                    protoc.lastState = qSys.initialState
                exponUni(qSim)
                qSim.qRes.indB = 0
                qSim.qRes.indL = 0
                __timeEvol(qSim)
    else:'''
    if len(qSim.Sweep.sweeps) > 0:
        if len(qSim.timeDependency.sweeps) > 0:
            if p is None:
                pass
                #withLWnpDel(qSim)
            else:
                pass
                withLOpDel(qSim, p)
        else:
            if p is None:
                pass
                #withLOnpDel(qSim)
            else:
                withLOpDel(qSim, p)
    else:
        if len(qSim.timeDependency.sweeps) > 0:
            pass
            #withWDel(qSim)
        else:
            pass
            '''for protoc, qSys in qSim.subSys.items():
                protoc.lastState = qSys.initialState
               #qSim._Simulation__compute()
            exponUni(qSim)
            __timeEvolDel(qSim)'''


def indicesForSweep(ind, *args):
    remain = 0
    indices = []
    for arg in args:
        #print(ind, arg)
        remain = ind%arg
        ind = (ind-remain)/arg
        indices.insert(0, int(remain))
    return indices


'''def withLWnpDel(qSim):
    results = []
    for ind in range(qSim.Sweep.indMultip):
        indices = indicesForSweep(ind, *qSim.Sweep.inds)
        qSim.Sweep.runSweep(indices)
        #qSim.qRes.resetLast()
        withWDel(qSim)
        results.append(qSim.qRes.results)
    qSim.qRes._organiseSingleProcRes(qSim.Sweep.inds, qSim.Sweep.indMultip)

def withLOnpDel(qSim):
    results = []
    for ind in range(qSim.Sweep.indMultip):
        indices = indicesForSweep(ind, *qSim.Sweep.inds)
        qSim.Sweep.runSweep(indices)
        for protoc, qSys in qSim.subSys.items():
            protoc.lastState = qSys.initialState
            #qSim._Simulation__compute()
        exponUni(qSim)
        #qSim.qRes.resetLast()
        for ii in range(qSim.steps):
            __timeEvolDel(qSim)
        results.append(qSim.qRes.results)
    qSim.qRes._organiseSingleProcRes(qSim.Sweep.inds, qSim.Sweep.indMultip)'''

def withLWpDel(qSim, p):
    results = p.map(partial(parallelSequenceWDel, qSim), range(qSim.Sweep.indMultip))
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds, qSim.Sweep.indMultip)


def withLOpDel(qSim, p):
    if len(qSim.timeDependency.sweeps) > 0:
        print('here')
        results = p.map(partial(parallelSequenceWDel, qSim), range(qSim.Sweep.indMultip))
    else:
        print('here2')
        results = p.map(partial(parallelSequenceODel, qSim), range(qSim.Sweep.indMultip))
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds, qSim.Sweep.indMultip)

def parallelSequenceWDel(qSim, ind):
    qSim.Sweep.runSweep(indicesForSweep(ind, *qSim.Sweep.inds))
    for protoc, qSys in qSim.subSys.items():
        protoc.lastState = qSys.initialState
    qSim.qRes.reset()
    qSim.timeDependency.prepare()
    withWDel(qSim)
    return deepcopy(qSim.qRes.allResults)

def parallelSequenceODel(qSim, ind):
    qSim.Sweep.runSweep(indicesForSweep(ind, *qSim.Sweep.inds))
    for protoc, qSys in qSim.subSys.items():
        protoc.lastState = qSys.initialState
    exponUni(qSim)
    qSim.qRes.reset()
    for ii in range(qSim.steps):
        __timeEvolDel(qSim)
    return deepcopy(qSim.qRes.allResults)

# Time evolution POSSIBILITIES
'''def withW(qSim):
    for protoc, qSys in qSim.subSys.items():
        protoc.lastState = qSys.initialState
        qSim._Simulation__compute()

    for ind in range(len(qSim.timeDependency.sweeps[0].sweepList)):
        qSim.timeDependency.runSweep(ind)
        exponUni(qSim)
        __timeEvol(qSim)'''

def withWDel(qSim):
    for ind in range(qSim.timeDependency.indMultip):
        qSim.timeDependency.runSweep(indicesForSweep(ind, *qSim.timeDependency.inds))
        exponUni(qSim)
        __timeEvolDel(qSim)

def __timeEvolDel(qSim):
    for protocol in qSim.subSys.keys():
        for ii in range(protocol.samples):
            qSim._Simulation__compute()
            protocol.lastState = protocol.unitary @ protocol.lastState
            #qSys.qRes.states[qSys.name + str(ind)] = qSys._genericQSys__lastStateList[ind]


'''def __timeEvol(qSim, unitaryList):
    for protocol in qSim.subSys.keys():
        for ii in range(protocol.samples):
            qSim._Simulation__compute()
            protocol.lastState = protocol.unitary @ protocol.lastState
            #qSys.qRes.states[qSys.name + str(ind)] = qSys._genericQSys__lastStateList[ind]'''

def exponUni(qSim):
    for protocol in qSim.subSys.keys():
        protocol.createUnitary()