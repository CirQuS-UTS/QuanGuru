import numpy as np
import platform
import pytest
import random
import quanguru as qg

def comp(sim, st):
    #sim.qRes.result = ("sz1", expectation(photonNum, st))
    #sim.qRes.result = ("sz2", expectation(qubSz, st))
    dim = sim.auxObj.dim
    for i in range(dim-2):
        sim.qRes.result = (str(i) + "real", st.A[i][0].real)
        sim.qRes.result = (str(i) + "imag", st.A[i][0].imag)

@pytest.mark.parametrize("bo, multiSweep, multiParam", [(False, False, False), (True, False, False),
                                                        (False, True, False), (True, True, False),
                                                        (False, True, True), (True, True, True)])
def test_JCEvolution(bo, multiSweep, multiParam, JC):
    if not (bo and (platform.system() == 'Windows')):
        qg.freeEvolution._freqCoef = 2 * np.pi
        cavDimList = sorted([random.randint(5, 15) for i in range(4)])
        initCavList = [{i:(random.random() + 1j*random.random()) for i in range(cdim-2)} for cdim in cavDimList]
        initQubList = [{i:(random.random() + 1j*random.random()) for i in range(2)} for _ in cavDimList]
        JC.cav.dimension = cavDimList[0]
        JC.qub.initialState = initQubList[0]
        JC.cav.initialState = initCavList[0]
        #JC.jc.initialState = qg.normalise(sum([JC.stateCoefs[i]*qg.basis(2*JC.cavDim, i) for i in range((2*JC.cavDim)-2)]))
        assert JC.jc.initialState is not None
        assert np.round(qg.norm(JC.jc.initialState), 12) == 1
        JC.jc.auxObj.dim = 2*cavDimList[0]
        stepSizeList = [0.05*random.random() for k in range(4)]
        sweep = JC.jc.simulation.Sweep.createSweep(system=JC.jc.simulation, sweepKey="stepSize", sweepList=stepSizeList)
        if multiSweep:
            dimSweep = JC.jc.simulation.Sweep.createSweep(system=JC.cav, sweepKey="dimension", sweepList=cavDimList, multiParam=multiParam)
            initCavSweep = JC.jc.simulation.Sweep.createSweep(system=JC.cav, sweepKey="initialState", sweepList=initCavList)
            initQubSweep = JC.jc.simulation.Sweep.createSweep(system=JC.qub, sweepKey="initialState", sweepList=initQubList)
        JC.jc.runSimulation(p=bo)
        JC.jc.simulation.Sweep.removeSweep(sweep)
        if multiSweep:
            #JC.jc.simulation.Sweep.removeSweep(dimSweep)
            JC.jc.simulation.Sweep.removeSweep([dimSweep, initCavSweep, initQubSweep])
        assert len(JC.jc.simulation.Sweep.subSys) == 0

        for cind, stepSize in enumerate(stepSizeList):
            combWhile = multiParam and len(cavDimList)-1
            JC.jc.simStepSize = stepSize
            tlist = JC.jc.simulation.timeList
            for ind in range(int(combWhile)+1):
                JC.cav.dimension = cavDimList[ind+((not multiParam)*cind*multiSweep)]
                JC.qub.initialState = initQubList[ind+((not multiParam)*cind*multiSweep)]
                JC.cav.initialState = initCavList[ind+((not multiParam)*cind*multiSweep)]
                inSt = JC.jc.initialState.A
                for i in range((2*cavDimList[0])-2):
                    n, q = JC.cavQubIndsToState(i)
                    ind2 = JC.cavQubStateToInds(n + (- 1)**(not q), not q) if ((n + (- 1)**(not q)) >= 0) else 1
                    quantRabiFreq = JC.quanGenRabiFreq(JC.gStg, 0, n) if q == 1 else JC.quanGenRabiFreq(JC.gStg, 0, n-1)
                    quantGRF = JC.quanGenRabiFreq(JC.gStg, JC.detuning, n) if q == 1 else JC.quanGenRabiFreq(JC.gStg, JC.detuning, n-1)
                    indSmall = (i > ind2)*ind2 + (i < ind2)*i if ind2 != 1 else 1
                    indBig = (i < ind2)*ind2 + (i > ind2)*i if ind2 != 1 else 1
                    c1Init = JC.c1(quantRabiFreq, quantGRF, JC.detuning, inSt[indSmall][0], inSt[indBig][0])
                    c2Init = JC.c2(quantRabiFreq, quantGRF, JC.detuning, inSt[indSmall][0], inSt[indBig][0])
                    resRe = []
                    resIm = []
                    if i != 1:
                        for t in tlist:
                            coef = JC.c_n_1(n=n, wr=JC.resFreq, detun=JC.detuning, qRf=quantRabiFreq, qgRf=quantGRF, c_1=c1Init, c_2=c2Init, t=t) if q == 1 else JC.c_np1_0(n=n-1, wr=JC.resFreq, detun=JC.detuning, qRf=quantRabiFreq, qgRf=quantGRF, c_1=c1Init, c_2=c2Init, t=t)
                            resRe.append(coef.real)
                            resIm.append(coef.imag)
                    else:
                        for t in tlist:
                            coef = JC.c00(inSt[1][0], JC.qubFreq, t)
                            resRe.append(coef.real)
                            resIm.append(coef.imag)

                    realRes = JC.jc.simulation.results[str(i)+'real'][cind][ind] if multiParam else JC.jc.simulation.results[str(i)+'real'][cind]
                    imagRes = JC.jc.simulation.results[str(i)+'imag'][cind][ind] if multiParam else JC.jc.simulation.results[str(i)+'imag'][cind]
                    assert np.allclose(resRe, realRes)
                    assert np.allclose(resIm, imagRes)
        qg.freeEvolution._freqCoef = 1
