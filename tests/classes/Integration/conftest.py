import numpy as np
import pytest
import qTools as qt #pylint: disable=import-error


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

    sz = qt.sigmaz()
    sy = qt.sigmay()
    sx = qt.sigmax()

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

@pytest.fixture
def singleQubit():
    # singleQubit fixture used to access above class and its method from the tests
    return _singleQubit()

@pytest.fixture
def twoQubitsExchange():
    # singleQubit fixture used to access above class and its method from the tests
    return _twoQubitsExchange()
