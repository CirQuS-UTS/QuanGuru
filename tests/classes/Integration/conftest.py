import numpy as np
import pytest
import random
import quanguru as qg #pylint: disable=import-error


class _singleQubit:
    @staticmethod
    def analyticalC0(t, c0, freq): return c0*(np.e**(0.5*2*np.pi*1j*freq*t))
    @staticmethod
    def analyticalC1(t, c1, freq): return c1*(np.e**(-0.5*2*np.pi*1j*freq*t))
    @staticmethod
    def sxExpectation(t, c0, c1, freq): return 2*(np.conj(c0)*c1*np.e**(-1j*2*np.pi*freq*t)).real
    @staticmethod
    def syExpectation(t, c0, c1, freq): return 2*(1j*np.conj(c0)*c1*np.e**(-1j*2*np.pi*freq*t)).real
    @staticmethod
    def szExpectation(c0, c1): return (abs(c1)**2) - (abs(c0)**2)
    @staticmethod
    def analyticalC0(t, c0, freq): return c0*(np.e**(-0.5*2*np.pi*1j*freq*t))
    @staticmethod
    def analyticalC1(t, c1, freq): return c1*(np.e**(0.5*2*np.pi*1j*freq*t))

    sz = qg.sigmaz()
    sy = qg.sigmay()
    sx = qg.sigmax()

class _twoQubitsExchange:
    # implement the analytical solutions
    @staticmethod
    def rbFreq(f1, f2, g): return np.sqrt(((f1-f2)**2) + ((2*g)**2))
    @staticmethod
    def c00(f1, f2, a00, t=0): return a00*np.exp(-1j*(f1+f2)*t/2)
    @staticmethod
    def c11(f1, f2, a11, t=0): return a11*np.exp(1j*(f1+f2)*t/2)
    @staticmethod
    def c_1(rbf, c10inp, c01inp, detun, cStg): return (c10inp + (c01inp*((rbf+detun)/(2*cStg))))/(rbf/cStg)
    @staticmethod
    def c_2(rbf, c10inp, c01inp, detun, cStg): return (-c10inp + (c01inp*((rbf-detun)/(2*cStg))))/(rbf/cStg)
    @staticmethod
    def c10(rbf, c10inp, c01inp, detun, cStg, t=0): return (_twoQubitsExchange.c_1(rbf, c10inp, c01inp, detun, cStg)*((rbf-detun)/(2*cStg)))*np.exp(-1j*rbf*t/2) - (_twoQubitsExchange.c_2(rbf, c10inp, c01inp, detun, cStg)*((rbf+detun)/(2*cStg)))*np.exp(1j*rbf*t/2)
    @staticmethod
    def c01(rbf, c10inp, c01inp, detun, cStg, t=0): return (_twoQubitsExchange.c_1(rbf, c10inp, c01inp, detun, cStg)*np.exp(-1j*rbf*t/2) + _twoQubitsExchange.c_2(rbf, c10inp, c01inp, detun, cStg)*np.exp(1j*rbf*t/2))
    @staticmethod
    def sz1Exp(a11, a00, c1, c2, rbf, detun, cStg, t): return np.abs(a11)**2 - np.abs(a00)**2 + ((((rbf-detun)/(2*cStg))**2)-1)*(np.abs(c1)**2) + ((((rbf+detun)/(2*cStg))**2)-1)*(np.abs(c2)**2) - 4*((c1*np.conjugate(c2)*np.exp(-1j*rbf*t)).real)

class _JC:
    def __init__(self) -> None:
        # define the qubit frequencies and the coupling strength randomly
        self.qubFreq = 2*random.random()
        self.resFreq = 2*random.random()
        self.gStg = 2*random.random()
        self.detuning = self.resFreq-self.qubFreq

        self.cavDim = random.randint(5, 15)

        # define the initial coefficients randomly
        self.stateCoefs = [random.random() + 1j*random.random() for i in range((2*self.cavDim)-2)]

        # normalise the initial coefficients
        self.cTotNorm = np.sqrt(sum([a.real**2 + a.imag**2 for a in self.stateCoefs]))
        self.stateCoefs = [self.stateCoefs[i]/self.cTotNorm for i in range((2*self.cavDim)-2)]
        # make sure it is normalised
        np.sqrt(sum([a.real**2 + a.imag**2 for a in self.stateCoefs]))

        self.cav = qg.Cavity(dimension=self.cavDim, frequency=self.resFreq)
        self.qub = qg.Qubit(frequency=self.qubFreq)

        self.jc = self.cav + self.qub
        self.couplingObj = self.jc.JC(self.gStg)

        self.jc.simStepSize = 0.01
        self.jc.simTotalTime = 8
        self.jc.simCompute = self.comp
        self.jc.simDelStates = True
    @staticmethod
    def comp(sim, states):
        st = states[0]
        #sim.qRes.result = ("sz1", expectation(photonNum, st))
        #sim.qRes.result = ("sz2", expectation(qubSz, st))
        dim = sim.auxObj.dim
        #dim = st.shape[0] # FIXME This causes bug in _reShape
        for i in range(dim-2):
            sim.qRes.result = (str(i) + "real", st.A[i][0].real)
            sim.qRes.result = (str(i) + "imag", st.A[i][0].imag)
    # implement the analytical solutions
    @staticmethod
    def quanGenRabiFreq(g, detun=0, n=0):
        return np.sqrt((detun**2) + (4*(g**2)*(n+1)))
    @staticmethod
    def c1(qRf, qgRf, detun, cn, cn1):
        d = (-qRf*cn) + (cn1*(qgRf - detun))
        return d/(2*qgRf)
    @staticmethod
    def c2(qRf, qgRf, detun, cn, cn1):
        d = (qRf*cn) + (cn1*(qgRf + detun))
        return d/(2*qgRf)
    @staticmethod
    def c_n_1(n, wr, detun, qRf, qgRf, c_1, c_2, t):
        fp = c_1*np.exp(-1j*(((n+0.5)*wr) - (0.5*qgRf))*t*2*np.pi)*(-(qgRf + detun))
        sp = c_2*np.exp(-1j*(((n+0.5)*wr) + (0.5*qgRf))*t*2*np.pi)*((qgRf - detun))
        return (fp+sp)/qRf
    @staticmethod
    def c_np1_0(n, wr, detun, qRf, qgRf, c_1, c_2, t):
        fp = c_1*np.exp(-1j*(((n+0.5)*wr) - (0.5*qgRf))*t*2*np.pi)
        sp = c_2*np.exp(-1j*(((n+0.5)*wr) + (0.5*qgRf))*t*2*np.pi)
        return fp+sp
    @staticmethod
    def cavQubStateToInds(n, qubEx):
        return 2*n + (not qubEx)
    @staticmethod
    def cavQubIndsToState(ind):
        n = ind//2
        qub = int(not ind % 2)
        return (n, qub)
    @staticmethod
    def c00(c0in, wq, t):
        return c0in*np.exp(1j*wq*t*np.pi)

@pytest.fixture
def singleQubit():
    # singleQubit fixture used to access above class and its method from the tests
    return _singleQubit()

@pytest.fixture
def twoQubitsExchange():
    # singleQubit fixture used to access above class and its method from the tests
    return _twoQubitsExchange()

@pytest.fixture
def JC():
    return _JC()
