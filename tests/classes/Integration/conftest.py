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

    sz = qt.sigmaz()
    sy = qt.sigmay()
    sx = qt.sigmax()

@pytest.fixture
def singleQubit():
    # singleQubit fixture used to access above class and its method from the tests
    return _singleQubit()
