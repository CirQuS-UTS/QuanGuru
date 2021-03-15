import numpy as np
import pytest
import random
import qTools as qt

def comp(sim, st):
    #sim.qRes.result = ("sz1", expectation(photonNum, st))
    #sim.qRes.result = ("sz2", expectation(qubSz, st))
    dim = sim.auxObj.dim
    for i in range(dim-2):
        sim.qRes.result = (str(i) + "real", st.A[i][0].real)
        sim.qRes.result = (str(i) + "imag", st.A[i][0].imag)

@pytest.mark.parametrize("bo", [False, True])
def test_singleQubitSimpleEvolution(bo, JC):
    # define the qubit frequencies and the coupling strength randomly
    qubFreq = 2*random.random()
    resFreq = 2*random.random()
    gStg = 2*random.random()
    detuning = resFreq-qubFreq

    cavDim = random.randint(3, 12)

    # define the initial coefficients randomly
    stateCoefs = [random.random() + 1j*random.random() for i in range((2*cavDim)-2)]

    # normalise the initial coefficients
    cTotNorm = np.sqrt(sum([a.real**2 + a.imag**2 for a in stateCoefs]))
    stateCoefs = [stateCoefs[i]/cTotNorm for i in range((2*cavDim)-2)]
    # make sure it is normalised
    np.sqrt(sum([a.real**2 + a.imag**2 for a in stateCoefs]))

    cav = qt.Cavity(dimension=cavDim, frequency=resFreq)
    qub = qt.Qubit(frequency=qubFreq)

    jc = cav + qub
    jc.JC(gStg)

    jc.initialState = qt.normalise(sum([stateCoefs[i]*qt.basis(2*cavDim, i) for i in range((2*cavDim)-2)]))
    assert np.round(qt.norm(jc.initialState), 12) == 1

    # define simulation step size and total time
    jc.simStepSize = 0.01
    jc.simTotalTime = 8
    jc.simCompute = comp
    jc.simDelStates = True
    jc.auxObj.dim = 2*cavDim
    jc.runSimulation(p=bo)

    detuning = resFreq-qubFreq
    inSt = jc.initialState.A

    for i in range((2*cavDim)-2):
        n, q = JC.cavQubIndsToState(i)
        ind2 = JC.cavQubStateToInds(n + (- 1)**(not q), not q) if ((n + (- 1)**(not q)) >= 0) else 1
        quantRabiFreq = JC.quanGenRabiFreq(gStg, 0, n) if q == 1 else JC.quanGenRabiFreq(gStg, 0, n-1)
        quantGRF = JC.quanGenRabiFreq(gStg, detuning, n) if q == 1 else JC.quanGenRabiFreq(gStg, detuning, n-1)
        indSmall = (i > ind2)*ind2 + (i < ind2)*i if ind2 != 1 else 1
        indBig = (i < ind2)*ind2 + (i > ind2)*i if ind2 != 1 else 1
        c1Init = JC.c1(quantRabiFreq, quantGRF, detuning, inSt[indSmall][0], inSt[indBig][0])
        c2Init = JC.c2(quantRabiFreq, quantGRF, detuning, inSt[indSmall][0], inSt[indBig][0])
        resRe = []
        resIm = []
        if i != 1:
            for t in jc.simulation.timeList:
                coef = JC.c_n_1(n=n, wr=resFreq, detun=detuning, qRf=quantRabiFreq, qgRf=quantGRF, c_1=c1Init, c_2=c2Init, t=t) if q == 1 else JC.c_np1_0(n=n-1, wr=resFreq, detun=detuning, qRf=quantRabiFreq, qgRf=quantGRF, c_1=c1Init, c_2=c2Init, t=t)
                resRe.append(coef.real)
                resIm.append(coef.imag)
        else:
            for t in jc.simulation.timeList:
                coef = JC.c00(inSt[1][0], qubFreq, t)
                resRe.append(coef.real)
                resIm.append(coef.imag)

        assert np.allclose(resRe, jc.simulation.results[str(i)+'real'])
        assert np.allclose(resIm, jc.simulation.results[str(i)+'imag'])