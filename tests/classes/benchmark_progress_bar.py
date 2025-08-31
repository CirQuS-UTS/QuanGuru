import time
from quanguru import Simulation, Qubit, QuantumSystem, Jx, Jz, expectation, tensorProd, identity, basis
import quanguru as qg
from numpy import linspace

def compute(sim, state):
    sim.qRes.singleResult = 'z', expectation(tensorProd(identity(2), Jz((5-1)/2)), state[0])

def sequentialDuration(showProgress):
    qg.named._resetAll()
    sim = Simulation()
    qsys = Qubit(frequency=1, alias='qubit') + QuantumSystem(dimension=5, frequency=1, operator=Jx, alias='cavity')
    sim.addQSystems(qsys)
    sim.totalTime = 1
    sim.stepCount = 500
    sim.initialStateSystem = qsys
    sim.initialState = basis(10, 0)
    sim.Sweep.createSweep(system='qubit', sweepKey="frequency", sweepList=linspace(0, 1, 200))
    sim.Sweep.createSweep(system='cavity', sweepKey="frequency", sweepList=linspace(0, 1, 200), combinatorial=True)
    sim.compute = compute
    
    start = time.perf_counter()
    sim.run(p=False, showProgress=showProgress)
    elapsed = time.perf_counter() - start
    # print(f"Sequential | showProgress={showProgress} | Time: {elapsed:.4f}s")
    return elapsed

def parallelDuration(showProgress):
    qg.named._resetAll()
    sim = Simulation()
    qsys = Qubit(frequency=1, alias='qubit') + QuantumSystem(dimension=5, frequency=1, operator=Jx, alias='cavity')
    sim.addQSystems(qsys)
    sim.totalTime = 1
    sim.stepCount = 500
    sim.initialStateSystem = qsys
    sim.initialState = basis(10, 0)
    sim.Sweep.createSweep(system='qubit', sweepKey="frequency", sweepList=linspace(0, 1, 200))
    sim.Sweep.createSweep(system='cavity', sweepKey="frequency", sweepList=linspace(0, 1, 200), combinatorial=True)
    sim.compute = compute

    start = time.perf_counter()
    sim.run(p=True, showProgress=showProgress)
    elapsed = time.perf_counter() - start
    # print(f"Parallel   | showProgress={showProgress} | Time: {elapsed:.4f}s")
    return elapsed

def relativeOverhead():
    # Run both sequential and parallel, with and without progress bar
    seq_no_bar = sequentialDuration(False)
    seq_with_bar = sequentialDuration(True)
    par_no_bar = parallelDuration(False)
    par_with_bar = parallelDuration(True)
    
    print("\nSummary of progress bar overhead (seconds):")
    print(f"Sequential: With bar = {seq_with_bar:.0f}, Without bar = {seq_no_bar:.0f}, Overhead = {seq_with_bar - seq_no_bar:.0f}")
    print(f"Parallel:   With bar = {par_with_bar:.0f}, Without bar = {par_no_bar:.0f}, Overhead = {par_with_bar - par_no_bar:.0f}")

if __name__ == '__main__':
    relativeOverhead()