import numpy as np
import pytest
import random as rn
import quanguru as qt

sz = qt.sigmaz()
sy = qt.sigmay()
sx = qt.sigmax()
def comp(simOB, states):
    st = states[0]
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
    assert np.allclose([qt.expectation(sx, sim.states[i]) for i in range(sim.stepCount+1)], sim.qRes.results['x'])
    assert np.allclose([singleQubit.sxExpectation(sim.stepSize*i, p0, p0, freq) for i in range(sim.stepCount+1)], sim.qRes.results['x'])
    assert np.allclose([singleQubit.syExpectation(sim.stepSize*i, p0, p0, freq) for i in range(sim.stepCount+1)], sim.qRes.results['y'])
    assert np.allclose([singleQubit.szExpectation(p0, p0) for i in range(sim.stepCount+1)], sim.qRes.results['z'])
    assert np.allclose([singleQubit.analyticalC0(sim.stepSize*i, p0, freq).real for i in range(sim.stepCount+1)], [s.A[0][0].real for s in sim.states])
    assert np.allclose([singleQubit.analyticalC0(sim.stepSize*i, p0, freq).imag for i in range(sim.stepCount+1)], [s.A[0][0].imag for s in sim.states])
    assert np.allclose([singleQubit.analyticalC1(sim.stepSize*i, p0, freq).real for i in range(sim.stepCount+1)], [s.A[1][0].real for s in sim.states])
    assert np.allclose([singleQubit.analyticalC1(sim.stepSize*i, p0, freq).imag for i in range(sim.stepCount+1)], [s.A[1][0].imag for s in sim.states])

def randSingQubStateCoefs():
    c0 = rn.random() + 1j*rn.random()
    c1 = rn.random() + 1j*rn.random()
    totalNorm = np.sqrt(c0.real**2 + c0.imag**2 + c1.real**2 + c1.imag**2)
    c0 = c0/totalNorm
    c1 = c1/totalNorm
    return (c0, c1)

@pytest.mark.parametrize("bo, multiSweep, multiParam", [(False, False, False), (True, False, False),
                                                        (False, True, False), (True, True, False),
                                                        (False, True, True), (True, True, True)])
def test_singleQubitSweepEvolution(bo, multiSweep, multiParam, singleQubit):
    qt.freeEvolution._freqCoef = 2*np.pi
    # evolve a single qubits
    freqs = [10*rn.random(),10*rn.random(),10*rn.random()]
    cList = [randSingQubStateCoefs(), randSingQubStateCoefs(), randSingQubStateCoefs()]
    stCoefList = [{0:cList[i][0],1:cList[i][1]} for i in range(len(cList))]
    qub = qt.Qubit(frequency=freqs[0],initialState=stCoefList[0],simTotalTime=4,simStepSize=0.01,simCompute=comp, _inpCoef=True)
    sim = qub.simulation
    sim.Sweep.createSweep(system=qub.name, sweepKey="frequency", sweepList=freqs)
    if multiSweep:
        sim.Sweep.createSweep(system=qub.name, sweepKey="initialState", sweepList=stCoefList, multiParam=multiParam)
    sim.run(p=bo)
    for j, f in enumerate(freqs):
        combWhile = multiParam and len(cList)-1
        for ind in range(int(combWhile)+1):
            c00 = cList[(j*int(not multiParam) + ind*int(multiParam))*int(multiSweep)][0]
            c01 = cList[(j*int(not multiParam) + ind*int(multiParam))*int(multiSweep)][1]
            xExpects = sim.qRes.results['x'][j][ind] if multiParam else sim.qRes.results['x'][j]
            yExpects = sim.qRes.results['y'][j][ind] if multiParam else sim.qRes.results['y'][j]
            zExpects = sim.qRes.results['z'][j][ind] if multiParam else sim.qRes.results['z'][j]
            assert np.allclose([singleQubit.sxExpectation(sim.stepSize*i, c01, c00, f) for i in range(sim.stepCount+1)], xExpects)
            assert np.allclose([singleQubit.syExpectation(sim.stepSize*i, c01, c00, f) for i in range(sim.stepCount+1)], yExpects)
            assert np.allclose([singleQubit.szExpectation(c01, c00) for i in range(sim.stepCount+1)], zExpects)

            states = sim.states[j][ind] if multiParam else sim.states[j]
            assert np.allclose([qt.expectation(sx, states[i]) for i in range(sim.stepCount+1)], xExpects)
            assert np.allclose([singleQubit.analyticalC0(sim.stepSize*i, c00, f).real for i in range(sim.stepCount+1)], [s.A[0][0].real for s in states])
            assert np.allclose([singleQubit.analyticalC0(sim.stepSize*i, c00, f).imag for i in range(sim.stepCount+1)], [s.A[0][0].imag for s in states])
            assert np.allclose([singleQubit.analyticalC1(sim.stepSize*i, c01, f).real for i in range(sim.stepCount+1)], [s.A[1][0].real for s in states])
            assert np.allclose([singleQubit.analyticalC1(sim.stepSize*i, c01, f).imag for i in range(sim.stepCount+1)], [s.A[1][0].imag for s in states])
