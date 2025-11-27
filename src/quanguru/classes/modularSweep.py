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

from numpy import array, reshape
from functools import partial
import time
import sys
from ..QuantumToolbox import densityMatrix, mat2Vec, vec2Mat

def runSimulation(qSim, p, showProgress=True):
    """
    Run quantum simulation with optional parallelisation and progress tracking.
    
    This function executes quantum parameter sweeps either in parallel or sequential mode.
    Progress tracking is controlled by the showProgress parameter.
    
    Parameters
    ----------
    qSim : Simulation
        The quantum simulation object containing the system and sweep parameters
    p : multiprocessing.Pool or None
        Pool object for parallel processing. If None, runs sequentially.
    showProgress : bool, optional
        Whether to display progress tracking. Default is True.
        Controls progress for both sequential and parallel runs.
        
    Notes
    -----
    For parallel processing, progress is displayed in real-time showing:
    - Progress bar with percentage completion
    - Current task count vs total tasks  
    - Elapsed time and estimated remaining time
    
    Examples
    --------
    >>> # Enable progress display (default)
    >>> sim.run(p=True, showProgress=True)
    
    >>> # Disable progress display
    >>> sim.run(p=True, showProgress=False)
    
    >>> # Progress also works for sequential runs
    >>> sim.run(p=False, showProgress=True)
    """
    # NOTE determine if more samples of a protocol step are requested.
    for protocol, _ in qSim.subSys.items():
        if hasattr(protocol, 'steps'):
            if any((step.simulation.samples > 1 for step in protocol.steps.values())):
                protocol.stepSample = True

    if p is None:
        nonParalEvol(qSim, showProgress)
    else:
        paralEvol(qSim, p, showProgress)


# This is the single process function
def nonParalEvol(qSim, showProgress=True):
    totalTasks = qSim.Sweep.indMultip
    updateInterval = int(totalTasks/501) + 1
    printBar = showProgress and totalTasks > 1
    if printBar:
        startTime = time.time()
        printPreamble(totalTasks, startTime, parallel=False)

    for ind in range(totalTasks):
        runSweepAndPrep(qSim, ind)
        qSim.qRes._organiseSingleProcRes() # pylint: disable=protected-access
        # Show progress for sequential runs
        if printBar:
            completed = ind + 1
            if completed % updateInterval == 0:
                printProgress(completed, totalTasks, startTime)

    # Final completion message for sequential runs
    if printBar:
        printProgress(1, 1, startTime)
        printEpilogue(startTime)

    qSim.qRes._finaliseAll(qSim.Sweep.inds) # pylint: disable=protected-access

# multi-processing functions
def paralEvol(qSim, p, showProgress=True):
    totalTasks = qSim.Sweep.indMultip
    if showProgress:
        startTime = time.time()
        completed = 0
        updateInterval = int(totalTasks/501) + 1
        printPreamble(totalTasks, startTime, parallel=True)

        # Use imap instead of map for iterative results that allow progress tracking
        results = []
        with p:
            for result in p.imap(partial(parallelTimeEvol, qSim), range(totalTasks), chunksize=1):
                results.append(result)
                completed += 1
                if completed % updateInterval == 0:
                    printProgress(completed, totalTasks, startTime)
        printProgress(1, 1, startTime)
        printEpilogue(startTime)
    else:
        # Original behavior without progress display
        results = p.map(partial(parallelTimeEvol, qSim), range(totalTasks), chunksize=1)
    qSim.qRes._organiseMultiProcRes(results, qSim.Sweep.inds) # pylint: disable=protected-access

def printPreamble(totalTasks, startTime, parallel=False):
    sweepType = 'parallel' if parallel else 'sequential'
    # Format start time as human-readable string
    startTimeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(startTime))
    sys.stdout.write(
        f"Starting {sweepType} sweep with {totalTasks} parameter combinations...\n"
        f"Simulation Start:\t{startTimeStr}\n"
        f'[{"-"*40}] {0.:.1f}% | Estimated Finish:'
    )
    sys.stdout.flush()


def printProgress(completed, totalTasks, startTime):
    progress = completed / totalTasks
    now = time.time()
    elapsedTime = now - startTime
    remainingTime = elapsedTime * (1/progress - 1)
    # Calculate estimated finish time as a timestamp
    estimatedFinishTime = now + remainingTime
    finishTimeStr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(estimatedFinishTime))
    # Progress bar display
    barLength = 40
    filledLength = int(barLength * progress)
    bar = '█' * filledLength + '-' * (barLength - filledLength)
    # Print all lines in one go
    sys.stdout.write(
        f'\r[{bar}] {progress*100:.1f}% | Est. Finish: {finishTimeStr}'
    )
    sys.stdout.flush()


def printEpilogue(startTime):
    seconds = time.time() - startTime

    sys.stdout.write(
        f'\nSimulation completed in ' + time.strftime('%Hh %Mm %Ss', time.gmtime(seconds))
    )


# need this to avoid return part, which is only needed in multi-processing
def parallelTimeEvol(qSim, ind):
    runSweepAndPrep(qSim, ind)
    return qSim.qRes._copyAllResBlank() # pylint: disable=protected-access

# These two functions, respectively, run Sweep and timeDependent (sweep) parameter updates
# In the timeDependet case, evolFunc of first function is the second function
def runSweepAndPrep(qSim, ind):
    qSim._Simulation__index = -1 # pylint: disable=protected-access

    if len(qSim.Sweep.inds) > 0:
        qSim.Sweep.runSweep(qSim.Sweep._indicesForSweep(ind, *qSim.Sweep.inds))

    for protocol in qSim.subSys.keys():
        if callable(qSim.evolFunc):
            # if isinstance(protocol.initialState, list): 
            #     protocol.initialState = array(protocol.initialState)
            shape = protocol.initialState.shape
            if len(shape) == 1:
                protocol.initialState = reshape(protocol.initialState, (shape[0], 1))
                shape = protocol.initialState.shape
            isKet = (shape[1] == 1)
            isDensityMatrix = (shape[0] == shape[1])
            if not protocol._isOpen:
                protocol.currentState = protocol.initialState
            else:
                if isDensityMatrix:
                    protocol.currentState = protocol.initialState
                elif isKet:
                    print("Initial state is assumed to be a ket: automatically converting to a density matrix")
                    protocol.currentState = densityMatrix(protocol.initialState)
                else:
                    raise ValueError("Initial state should be a ket (shape = (n, 1)) or density matrix (shape = (shape = (n, n))) for an open system simulation")

    qSim.qRes._resetLast() # pylint: disable=protected-access
    qSim._computeBase__calculate("pre")
    for protocol in qSim.subSys.keys():
        protocol._computeBase__calculate("pre") # pylint: disable=protected-access
    calledFor = []
    for protocol, qsystem in qSim.subSys.items():
        if qsystem not in calledFor:
            qsystem._computeBase__calculate("pre") # pylint: disable=protected-access
            calledFor.append(qsystem)
    timeDependent(qSim)
    qSim._computeBase__calculate("post")
    for protocol in qSim.subSys.keys():
        protocol._computeBase__calculate("post") # pylint: disable=protected-access
    calledFor = []
    for protocol, qsystem in qSim.subSys.items():
        if qsystem not in calledFor:
            qsystem._computeBase__calculate("post") # pylint: disable=protected-access
            calledFor.append(qsystem)

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
        # qSim._timeBase__stepCount._value = qSim.timeDependency.indMultip # pylint: disable=protected-access
        # for pro, sim in qSim.subSys.items(): # pylint: disable=protected-access
        #     sim.simulation._timeBase__stepCount._value = sim.simulation.timeDependency.indMultip_intervals # pylint: disable=protected-access
        #     pro.simulation._timeBase__stepCount._value = pro.simulation.timeDependency.indMultip_intervals # pylint: disable=protected-access
    timeEvolDefault(qSim, td)


# These are the specific solution method, user should define their own timeEvol function to use other solution methods
# This flexibility should be reflected into protocol object
def timeEvolDefault(qSim, td):
    for protocol in qSim.subSys.keys():
        protocol.sampleStates = []
    if callable(qSim.evolFunc):
        qSim._Simulation__compute() # pylint: disable=protected-access
    for protocol in qSim.subSys.keys():
        protocol._computeBase__compute(protocol.currentState) # pylint: disable=protected-access
    calledFor = []
    for protocol, qsystem in qSim.subSys.items():
        if qsystem not in calledFor:
            qsystem._computeBase__compute(protocol.currentState) # pylint: disable=protected-access
            calledFor.append(qsystem)

    if callable(qSim.evolFunc):
        for ind in range(qSim.stepCount):
            for system in qSim.subSys.values():
                system._timeDependency()
            qSim._Simulation__index = ind # pylint: disable=protected-access
            if td:
                qSim.timeDependency.runSweep(qSim.timeDependency._indicesForSweep(ind, *qSim.timeDependency.inds))

            qSim.evolFunc(qSim)
            qSim._Simulation__compute() # pylint: disable=protected-access
            for protocol in qSim.subSys.keys():
                protocol._computeBase__compute(protocol.currentState) # pylint: disable=protected-access
            calledFor = []
            for protocol, qsystem in qSim.subSys.items():
                if qsystem not in calledFor:
                    qsystem._computeBase__compute(protocol.currentState) # pylint: disable=protected-access
                    calledFor.append(qsystem)

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
