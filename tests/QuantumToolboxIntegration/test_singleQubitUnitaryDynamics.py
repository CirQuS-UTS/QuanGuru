import numpy as np
import pytest
from qTools.QuantumToolbox import linearAlgebra as la  #pylint: disable=import-error
from qTools.QuantumToolbox import functions as fns #pylint: disable=import-error

analyticalC0 = lambda t, c0, freq: c0*(np.e**(0.5*2*np.pi*1j*freq*t))
analyticalC1 = lambda t, c1, freq: c1*(np.e**(-0.5*2*np.pi*1j*freq*t))

sxExpectation = lambda t, c0, c1, freq: 2*(np.conj(c0)*c1*np.e**(-1j*2*np.pi*freq*t)).real
syExpectation = lambda t, c0, c1, freq: 2*(1j*np.conj(c0)*c1*np.e**(-1j*2*np.pi*freq*t)).real
szExpectation = lambda c0, c1: (abs(c1)**2) - (abs(c0)**2)

numericalCoef = {'C0real':[], 'C0imag':[], 'C1real':[], 'C1imag':[]}
analyticCoef = {'C0real':[], 'C0imag':[], 'C1real':[], 'C1imag':[]}
expectationsNumeric = {'sz':[], 'sx':[], 'sy':[]}
expectationsAnalytic = {'sz':[], 'sx':[], 'sy':[]}

def singleQubitFreeCalculate(qub, state, i):
    ct1 = la.innerProd(state, qub.ket1) # <ket1|state> ordering is important
    ct0 = la.innerProd(state, qub.ket0)

    numericalCoef['C0real'].append(ct0.real)
    numericalCoef['C0imag'].append(ct0.imag)
    numericalCoef['C1real'].append(ct1.real)
    numericalCoef['C1imag'].append(ct1.imag)

    ca0 = analyticalC0(i*qub.stepSize, qub.initialC0, qub.frequency)
    ca1 = analyticalC1(i*qub.stepSize, qub.initialC1, qub.frequency)

    analyticCoef['C0real'].append(ca0.real)
    analyticCoef['C0imag'].append(ca0.imag)
    analyticCoef['C1real'].append(ca1.real)
    analyticCoef['C1imag'].append(ca1.imag)

    expectationsNumeric['sz'].append(fns.expectation(qub.sz, state))
    expectationsNumeric['sy'].append(fns.expectation(qub.sy, state))
    expectationsNumeric['sx'].append(fns.expectation(qub.sx, state))

    expectationsAnalytic['sx'].append(sxExpectation(i*qub.stepSize, qub.initialC0, qub.initialC1, qub.frequency))
    expectationsAnalytic['sy'].append(syExpectation(i*qub.stepSize, qub.initialC0, qub.initialC1, qub.frequency))
    expectationsAnalytic['sz'].append(szExpectation(qub.initialC0, qub.initialC1))

def test_singleQubitEvolve(singleQubit):
    singleQubit.calculate = singleQubitFreeCalculate
    singleQubit.evolve()
    for k, v in numericalCoef.items():
        assert singleQubit.stepCount == len(v)
        assert singleQubit.stepCount == len(analyticCoef[k])
    for k, v in expectationsNumeric.items():
        assert singleQubit.stepCount == len(v)
        assert singleQubit.stepCount == len(expectationsAnalytic[k])

@pytest.mark.depends(on=['test_singleQubitEvolve'])
@pytest.mark.parametrize("num, ana", [[numericalCoef[k], analyticCoef[k]] for k in numericalCoef])
def test_complexAmplitudesDynamicsInSingleQubitEvolution(num, ana):
    assert np.allclose(num, ana)

@pytest.mark.depends(on=['test_singleQubitEvolve'])
@pytest.mark.parametrize("num, ana", [[expectationsNumeric[k], expectationsAnalytic[k]] for k in expectationsNumeric])
def test_expectationValuesInSingleQubitEvolution(num, ana):
    assert np.allclose(num, ana)
