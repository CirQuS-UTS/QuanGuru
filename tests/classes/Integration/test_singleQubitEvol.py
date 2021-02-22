import numpy as np
import pytest
import random as rn
import qTools as qt

sz = qt.sigmaz()
sy = qt.sigmay()
sx = qt.sigmax()
def comp(simOB, st):
    simOB.qRes.result = ["x", qt.expectation(sx, st)]
    simOB.qRes.result = ["y", qt.expectation(sy, st)]
    simOB.qRes.result = ["z", qt.expectation(sz, st)]

@pytest.mark.parametrize("bo", [False, True])
def test_singleQubitSimpleEvolution(bo, singleQubit):
    # evolve a single qubit
    freq = 10*rn.random()
    p0 = np.sqrt(0.5)
    sim = qt.Qubit(frequency=freq,initialState=[0,1],simTotalTime=4,simStepSize=0.01,simCompute=comp).runSimulation(p=bo)
    assert np.allclose([singleQubit.sxExpectation(sim.stepSize*i, p0, p0, freq) for i in range(sim.stepCount+1)], sim.qRes.results['x'])
    assert np.allclose([singleQubit.syExpectation(sim.stepSize*i, p0, p0, freq) for i in range(sim.stepCount+1)], sim.qRes.results['y'])
    assert np.allclose([singleQubit.szExpectation(p0, p0) for i in range(sim.stepCount+1)], sim.qRes.results['z'])

@pytest.mark.parametrize("bo", [False, True])
def test_singleQubitSweepEvolution(bo, singleQubit):
    # evolve a single qubits
    freqs = [10*rn.random(),10*rn.random(),10*rn.random()]
    p0 = np.sqrt(0.5)
    qub = qt.Qubit(frequency=freqs[0],initialState=[0,1],simTotalTime=4,simStepSize=0.01,simCompute=comp)
    sim = qub.simulation
    sim.Sweep.createSweep(system=qub, sweepKey="frequency", sweepList=freqs)
    sim.run(p=bo)
    for j, f in enumerate(freqs):
        assert np.allclose([singleQubit.sxExpectation(sim.stepSize*i, p0, p0, f) for i in range(sim.stepCount+1)], sim.qRes.results['x'][j])
        assert np.allclose([singleQubit.syExpectation(sim.stepSize*i, p0, p0, f) for i in range(sim.stepCount+1)], sim.qRes.results['y'][j])
        assert np.allclose([singleQubit.szExpectation(p0, p0) for i in range(sim.stepCount+1)], sim.qRes.results['z'][j])
