import random as rn
import numpy as np
import pytest
from qTools.QuantumToolbox import states #pylint: disable=import-error
from qTools.QuantumToolbox import operators as ops #pylint: disable=import-error
from qTools.QuantumToolbox import evolution as evo #pylint: disable=import-error


class _singleQubit: #pylint:disable=too-many-instance-attributes
    sz = ops.sigmaz()
    sy = ops.sigmay()
    sx = ops.sigmax()
    sp = ops.sigmap()
    sm = ops.sigmam()

    ket1 = states.basis(2, 0)
    ket0 = states.basis(2, 1)

    def __init__(self) -> None:
        super().__init__()
        self.stepSize = 0.01
        self.finalTime = 2 + self.stepSize
        self.create()
        self.calculate = self.defaultCalculate
        self.evolutionMethod = self.unitary
        self.collapseOpsAndRates = {}

    def defaultCalculate(self, *args):
        pass

    @property
    def stepCount(self):
        return int(self.finalTime / self.stepSize)

    def create(self) -> None:
        self.frequency = rn.random()
        initialC0real = rn.random() #pylint:disable=invalid-name
        initialC0imag = rn.random() #pylint:disable=invalid-name
        initialC1real = rn.random() #pylint:disable=invalid-name
        initialC1imag = rn.random() #pylint:disable=invalid-name

        initialC0 = (initialC0real + 1j*initialC0imag)/(initialC0real**2 + initialC0imag**2)
        initialC1 = (initialC1real + 1j*initialC1imag)/(initialC1real**2 + initialC1imag**2)

        self.Hamiltonian = 0.5*self.frequency*self.sz

        self.initialState = states.superPos(2, {0: initialC1, 1: initialC0}, populations=False)
        self.initialC0 = self.initialState.A[1][0] #pylint:disable=invalid-name
        self.initialC1 = self.initialState.A[0][0] #pylint:disable=invalid-name

    def unitary(self):
        return evo.Unitary(2*np.pi*self.Hamiltonian, self.stepSize)

    def Liouvillian(self):
        return evo.Liouvillian(2*np.pi*self.Hamiltonian,
                               self.collapseOpsAndRates.keys(), self.collapseOpsAndRates.values())

    def openEvolution(self):
        return evo.LiouvillianExp(2*np.pi*self.Hamiltonian, self.stepSize,
                                  self.collapseOpsAndRates.keys(), self.collapseOpsAndRates.values())

    def evolve(self, *args):
        evolution = self.evolutionMethod()
        state = self.initialState
        if evolution.shape[0] != state.shape[0]:
            state = states.mat2Vec(states.densityMatrix(state))
            for i in range(self.stepCount):
                self.calculate(self, states.vec2Mat(state), i, *args)
                state = evolution @ state
        else:
            for i in range(self.stepCount):
                self.calculate(self, state, i, *args)
                state = evolution @ state

@pytest.fixture
def singleQubit():
    return _singleQubit()
