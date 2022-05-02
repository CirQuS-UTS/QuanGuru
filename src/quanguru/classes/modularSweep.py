"""
    Contain an implementation of the sweep that uses modular arithmetic.

    .. currentmodule:: quanguru.classes.modularSweep

    .. autosummary::

        runSimulation
        nonParalEvol
        paralEvol
        parallelTimeEvol
        _runSweepAndPrep
        timeDependent
        timeEvolDefault
        timeEvolBase

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
      `runSimulation`            |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `nonParalEvol`             |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `paralEvol`                |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `parallelTimeEvol`         |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `_runSweepAndPrep`         |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `timeDependent`            |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `timeEvolDefault`          |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `timeEvolBase`             |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from functools import partial
from ..QuantumToolbox import densityMatrix, mat2Vec, vec2Mat

def runSimulation(qSim, p):
    # NOTE determine if more samples of a protocol step are requested.
    for protocol, _ in qSim.subSys.items():
        if hasattr(protocol, 'steps'):
            if any((step.simulation.samples > 1 for step in protocol.steps.values())):
                protocol.stepSample = True

    if p is None:
        nonParalEvol(qSim)
    else:
        paralEvol(qSim, p)

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
        if callable(qSim.evolFunc):
            protocol.currentState = protocol.initialState if not protocol._isOpen else densityMatrix(protocol.initialState)# pylint: disable=protected-access,line-too-long

    qSim.qRes._resetLast() # pylint: disable=protected-access
    qSim._computeBase__calculate("start")
    for protocol in qSim.subSys.keys():
        qSim.subSys[protocol]._computeBase__calculate("start") # pylint: disable=protected-access
        protocol._computeBase__calculate("start") # pylint: disable=protected-access
    timeDependent(qSim)
    qSim._computeBase__calculate("end")
    for protocol in qSim.subSys.keys():
        qSim.subSys[protocol]._computeBase__calculate("end") # pylint: disable=protected-access
        protocol._computeBase__calculate("end") # pylint: disable=protected-access

def timeDependent(qSim):
    td = False
    if len(qSim.timeDependency.sweeps) > 0:
        td = True
        if list(qSim.timeDependency.sweeps.values())[0]._sweepList is not None: #pylint: disable=protected-access
            qSim.timeDependency.prepare()
        else:
            qSim.timeDependency._Sweep__inds = [qSim.stepCount] #pylint: disable=protected-access
        # TODO timeDependency sweep with multi-parameter is an undefined behaviour
        #  if there are multiple sweeps when using sweeps for time-dependency, all of them has to run simultaneously.
        #  if they are combinatorial multi-parameter sweep, the behavior is undefined.
        #  labels: undefined behaviour
        qSim._timeBase__stepCount._value = qSim.timeDependency.indMultip # pylint: disable=protected-access
        for pro, sim in qSim.subSys.items(): # pylint: disable=protected-access
            sim.simulation._timeBase__stepCount._value = sim.simulation.timeDependency.indMultip # pylint: disable=protected-access
            pro.simulation._timeBase__stepCount._value = pro.simulation.timeDependency.indMultip # pylint: disable=protected-access
    timeEvolDefault(qSim, td)


# These are the specific solution method, user should define their own timeEvol function to use other solution methods
# This flexibility should be reflected into protocol object
def timeEvolDefault(qSim, td):
    for protocol in qSim.subSys.keys():
        protocol.sampleStates = []
    if callable(qSim.evolFunc):
        qSim._Simulation__compute() # pylint: disable=protected-access
    for protocol in qSim.subSys.keys():
        qSim.subSys[protocol]._computeBase__compute(protocol.currentState) # pylint: disable=protected-access
        protocol._computeBase__compute(protocol.currentState) # pylint: disable=protected-access

    if callable(qSim.evolFunc):
        for ind in range(qSim.stepCount):
            qSim._Simulation__index = ind # pylint: disable=protected-access
            if td:
                qSim.timeDependency.runSweep(qSim.timeDependency._indicesForSweep(ind, *qSim.timeDependency.inds))

            qSim.evolFunc(qSim)
            qSim._Simulation__compute() # pylint: disable=protected-access
            for protocol in qSim.subSys.keys():
                qSim.subSys[protocol]._computeBase__compute(protocol.currentState) # pylint: disable=protected-access
                protocol._computeBase__compute(protocol.currentState) # pylint: disable=protected-access

def timeEvolBase(qSim):
    for protocol in qSim.subSys.keys(): #pylint:disable=too-many-nested-blocks
        if protocol._isOpen: # pylint: disable=protected-access
            state = mat2Vec(protocol.currentState)
            state = protocol.unitary() @ state
            protocol.currentState = vec2Mat(state)
        else:
            protocol.sampleStates = []
            if protocol.stepSample:
                for step in protocol.steps.values():
                    for _ in range(step.simulation.samples):
                        protocol.currentState = step.unitary() @ protocol.currentState
                        protocol.sampleStates.append(protocol.currentState)
            else:
                protocol.currentState = protocol.unitary() @ protocol.currentState
        #protocol.sampleStates = []
        #qSim.subSys[protocol]._computeBase__compute([protocol.currentState]) # pylint: disable=protected-access
        #sampleCompute = qSim is protocol.simulation

        # NOTE for time-dependent Hamiltonians in a digital quantum simulation, we may change the hamiltonian parameter
        # at evert dt, which might be divided into N steps. Below line was introduced for such cases.
        #for __ in range(int(protocol.simulation._timeBase__stepCount.value/qSim._timeBase__stepCount.value)): # pylint: disable=protected-access, line-too-long # noqa: E501

        # NOTE in a protocol we may want to have more than 1 sample. Below line was introduced for such cases.
        #for ___ in range(protocol.simulation.samples):

        # NOTE this was using protocol.simulation compute function in above cases, if running simulation is not
        # protocol.simulation. protocol.compute is called by the running simulation.
        #if not sampleCompute:
        #    protocol.simulation._Simulation__compute() # pylint: disable=protected-access

        # NOTE we may even want to have more samples during a specific step of a protocol. below lines cover that. this
        # was used quantum kicked top. it was appending the states into a list, which is passed to compute outside.
        #if protocol.stepSample:
        #    for step in protocol.steps.values():
        #        for _ in range(step.simulation.samples):
        #            protocol.currentState = step.unitary @ protocol.currentState
        #            protocol.sampleStates.append(protocol.currentState)
        # NOTE below elif is when we just want samples from the protocol not steps, but we did not give compute. stores
        # the states to reach and use in some other compute
        #elif protocol.compute is None:
        #    protocol.currentState = protocol.unitary @ protocol.currentState
        #    protocol.sampleStates.append(protocol.currentState)
        # NOTE when only sample the protocol and compute is given, the states are passed 1 by 1.
        #else:
        #for step in protocol.subSys.values():
        #    protocol.currentState = step.unitary @ protocol.currentState
        #    protocol._computeBase__compute([protocol.currentState]) # pylint: disable=protected-access
