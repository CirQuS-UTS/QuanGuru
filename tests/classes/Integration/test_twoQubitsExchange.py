import numpy as np
import random
import quanguru as qg

qub1Sz = qg.tensorProd(qg.sigmaz(), qg.identity(2))
qub2Sz = qg.tensorProd(qg.identity(2), qg.sigmaz())
# store the real and imaginary parts for each coeffiecient at each step
def comp(sim, states):
    st = states[0]
    sim.qRes.result = ("sz1", qg.expectation(qub1Sz, st))
    sim.qRes.result = ("sz2", qg.expectation(qub2Sz, st))
    sim.qRes.result = ("c00real", st.A[0][0].real)
    sim.qRes.result = ("c00imag", st.A[0][0].imag)
    sim.qRes.result = ("c10real", st.A[1][0].real)
    sim.qRes.result = ("c10imag", st.A[1][0].imag)
    sim.qRes.result = ("c01real", st.A[2][0].real)
    sim.qRes.result = ("c01imag", st.A[2][0].imag)
    sim.qRes.result = ("c11real", st.A[3][0].real)
    sim.qRes.result = ("c11imag", st.A[3][0].imag)

def test_twoQubitExchange(twoQubitsExchange):
    qg.freeEvolution._freqCoef = 1
    # define the qubit frequencies and the coupling strength randomly
    freq1 = 2*random.random()
    freq2 = 2*random.random()
    gList =  [2*random.random() for _ in range(4)]
    cStg = gList[0]

    # define the initial coefficients randomly
    c00inp = random.random() + 1j*random.random()
    c10inp = random.random() + 1j*random.random()
    c01inp = random.random() + 1j*random.random()
    c11inp = random.random() + 1j*random.random()

    # normalise the initial coefficients
    cTotNorm = np.sqrt(sum([a.real**2 + a.imag**2 for a in [c00inp, c10inp, c01inp, c11inp]]))
    c00inp = c00inp/cTotNorm
    c10inp = c10inp/cTotNorm
    c01inp = c01inp/cTotNorm
    c11inp = c11inp/cTotNorm
    # make sure it is normalised
    assert np.round(np.sqrt(sum([a.real**2 + a.imag**2 for a in [c00inp, c10inp, c01inp, c11inp]])),  12) == 1


    # create two qubits with the random frequencies
    qb1 = qg.Qubit(frequency=freq1)
    qb2 = qg.Qubit(frequency=freq2)
    qbIn = qb1 + qb2

    # couple the qubits with the random coupling strength
    coupling1 = qbIn.createTerm(qSystem=[qb1, qb2], operator=[qg.sigmam, qg.sigmap], frequency=cStg)
    coupling2 = qbIn.createTerm(qSystem=[qb1, qb2], operator=[qg.sigmap, qg.sigmam], frequency=cStg)

    # create the initial state with the random coefficients
    qbIn.initialState = c00inp*qg.basis(4, 0) + c10inp*qg.basis(4, 1) + c01inp*qg.basis(4, 2) + c11inp*qg.basis(4, 3)
    # make sure it is normalised
    assert np.round(qg.norm(qbIn.initialState), 12) == 1

    # define simulation step size and total time
    qbIn.simStepSize = 0.01
    qbIn.simTotalTime = 8

    qbIn.simCompute = comp
    qbIn.simDelStates = True
    cSweep1 = qbIn.simulation.Sweep.createSweep(system=coupling1, sweepKey="frequency", sweepList=gList)
    cSweep2 = qbIn.simulation.Sweep.createSweep(system=coupling2, sweepKey="frequency", sweepList=gList)
    qbIn.runSimulation()

    for ind, cStg in enumerate(gList):
        rabifreq = twoQubitsExchange.rbFreq(freq2, freq1, cStg)
        detun = freq2 - freq1
        c1 = twoQubitsExchange.c_1(rabifreq, c10inp, c01inp, detun, cStg)
        c2 = twoQubitsExchange.c_2(rabifreq, c10inp, c01inp, detun, cStg)

        assert np.allclose([twoQubitsExchange.sz1Exp(c00inp, c11inp, c1, c2, rabifreq, detun, cStg, t) for t in qbIn.simulation.timeList], qbIn.simulation.results["sz1"][ind])

        assert np.allclose([twoQubitsExchange.c01(rabifreq, c10inp, c01inp, detun, cStg, t).real for t in qbIn.simulation.timeList], qbIn.simulation.results["c01real"][ind])
        assert np.allclose([twoQubitsExchange.c01(rabifreq, c10inp, c01inp, detun, cStg, t).imag for t in qbIn.simulation.timeList], qbIn.simulation.results["c01imag"][ind])

        assert np.allclose([twoQubitsExchange.c10(rabifreq, c10inp, c01inp, detun, cStg, t).real for t in qbIn.simulation.timeList], qbIn.simulation.results["c10real"][ind])
        assert np.allclose([twoQubitsExchange.c10(rabifreq, c10inp, c01inp, detun, cStg, t).imag for t in qbIn.simulation.timeList], qbIn.simulation.results["c10imag"][ind])

        assert np.allclose([twoQubitsExchange.c00(freq1, freq2, c00inp, t).real for t in qbIn.simulation.timeList], qbIn.simulation.results["c00real"][ind])
        assert np.allclose([twoQubitsExchange.c00(freq1, freq2, c00inp, t).imag for t in qbIn.simulation.timeList], qbIn.simulation.results["c00imag"][ind])

        assert np.allclose([twoQubitsExchange.c11(freq1, freq2, c11inp, t).real for t in qbIn.simulation.timeList], qbIn.simulation.results["c11real"][ind])
        assert np.allclose([twoQubitsExchange.c11(freq1, freq2, c11inp, t).imag for t in qbIn.simulation.timeList], qbIn.simulation.results["c11imag"][ind])
