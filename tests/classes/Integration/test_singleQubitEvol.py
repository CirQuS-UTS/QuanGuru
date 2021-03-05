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
    qt.freeEvolution._freqCoef = 2*np.pi
    # evolve a single qubit
    freq = 10*rn.random()
    p0 = np.sqrt(0.5)
    sim = qt.Qubit(frequency=freq,initialState=[0,1],simTotalTime=4,simStepSize=0.01,simCompute=comp).runSimulation(p=bo)
    assert np.allclose([singleQubit.sxExpectation(sim.stepSize*i, p0, p0, freq) for i in range(sim.stepCount+1)], sim.qRes.results['x'])
    assert np.allclose([singleQubit.syExpectation(sim.stepSize*i, p0, p0, freq) for i in range(sim.stepCount+1)], sim.qRes.results['y'])
    assert np.allclose([singleQubit.szExpectation(p0, p0) for i in range(sim.stepCount+1)], sim.qRes.results['z'])

@pytest.mark.parametrize("bo", [False, True])
def test_singleQubitSweepEvolution(bo, singleQubit):
    qt.freeEvolution._freqCoef = 2*np.pi
    # evolve a single qubits
    freqs = [10*rn.random(),10*rn.random(),10*rn.random()]
    c0 = rn.random() + 1j*rn.random()
    c1 = rn.random() + 1j*rn.random()
    totalNorm = np.sqrt(c0.real**2 + c0.imag**2 + c1.real**2 + c1.imag**2)
    c0 = c0/totalNorm
    c1 = c1/totalNorm
    qub = qt.Qubit(frequency=freqs[0],initialState={0:c1,1:c0},simTotalTime=4,simStepSize=0.01,simCompute=comp, _inpCoef=True)
    sim = qub.simulation
    sim.Sweep.createSweep(system=qub.name, sweepKey="frequency", sweepList=freqs)
    sim.run(p=bo)
    for j, f in enumerate(freqs):
        assert np.allclose([singleQubit.sxExpectation(sim.stepSize*i, c0, c1, f) for i in range(sim.stepCount+1)], sim.qRes.results['x'][j])
        assert np.allclose([singleQubit.syExpectation(sim.stepSize*i, c0, c1, f) for i in range(sim.stepCount+1)], sim.qRes.results['y'][j])
        assert np.allclose([singleQubit.szExpectation(c0, c1) for i in range(sim.stepCount+1)], sim.qRes.results['z'][j])
