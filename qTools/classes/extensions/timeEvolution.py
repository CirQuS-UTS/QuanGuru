





































# time evolve
def __timeEvolDel(qSys, unitary):
    qSys._genericQSys__lastStateList = unitary @ qSys._genericQSys__lastStateList
        
def __timeEvol(qSys, unitary):
    qSys.qRes.state = qSys._genericQSys__lastStateList
    qSys._genericQSys__lastStateList = unitary @ qSys._genericQSys__lastStateList

def __timeEvolDelComp(qSys, unitary, compute):
    qSys._genericQSys__lastStateList = unitary @ qSys._genericQSys__lastStateList
    qRes._qResults__resCount = 0
    compute()
    qRes._qResults__prevRes = True
        
def __timeEvolComp(qSys, unitary, compute):
    qSys.qRes.state = qSys._genericQSys__lastStateList
    qSys._genericQSys__lastStateList = unitary @ qSys._genericQSys__lastStateList
    qRes._qResults__resCount = 0
    compute()
    qRes._qResults__prevRes = True

# Exponentiate
def exponUni(qSys):
    unitary = qSys.unitary
    return unitary

def exponUniMultiProtoc(qSys):
    unitary = []
    for qSys in qSim.subSystems.values():
        subUni = qSys.unitary
        if not isinstance(subUni, list):
            unitary.append([subUni])
        else:
            unitary.append(subUni)
    return unitary

def exponUniMultiSys(qSys):
    unitary = []
    for qSys in qSim.subSystems.values():
        subUni = qSys.unitary
        if not isinstance(subUni, list):
            unitary.append([subUni])
        else:
            unitary.append(subUni)
    return unitary

def exponUniMultiBoth(qSys):
    unitary = []
    for qSys in qSim.subSystems.values():
        subUni = qSys.unitary
        if not isinstance(subUni, list):
            unitary.append([subUni])
        else:
            unitary.append(subUni)
    return unitary

# run sequence
def runSequence(qSeq, ind):
    for sweep in qSeq.sweeps:
        sweep.runSweep(ind)