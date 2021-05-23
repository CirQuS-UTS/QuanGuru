import random as rn
import numpy as np
import pytest
from quanguru.QuantumToolbox import states #pylint: disable=import-error
from quanguru.QuantumToolbox import operators as ops #pylint: disable=import-error
from quanguru.QuantumToolbox import evolution as evo #pylint: disable=import-error


class _singleQubit: #pylint:disable=too-many-instance-attributes
    # used in the singleQubit fixture below
    # contain methods, class attributes, etc. to be used integration tests using a single qubit
    # this is introduced to both avoid code duplication in various tests and optimise by not creating certain things
    # repeatedly, such as operators, time evolution operators, etc.

    # Pauli matrices created ones, and accessed from instances of this class
    sz = ops.sigmaz()
    sy = ops.sigmay()
    sx = ops.sigmax()
    sp = ops.sigmap()
    sm = ops.sigmam()

    # spin up and down states for reference and created ones, and accessed from instances of this class
    ket1 = states.basis(2, 0)
    ket0 = states.basis(2, 1)

    # some qubit attributes used to optimise testing
    def __init__(self) -> None:
        super().__init__()
        self.stepSize = 0.01
        self.finalTime = 2 + self.stepSize
        self.create()
        self.calculate = self.defaultCalculate
        self.evolutionMethod = self.unitary
        self.collapseOpsAndRates = {}

    # a dummy method that is replaced by re-assigning calculate attribute, which is used to write flexible tests while
    # keeping optimisations provided by this class. this flexible function calculates both numeric and analytic
    # expectations. they are not hard-coded, since the qubit parameters are randomly assigned in each test run to
    # provide more robust tests, see below.
    def defaultCalculate(self, *args):
        pass

    # number of steps from initial time to final time (used in time evolutions)
    @property
    def stepCount(self):
        return int(self.finalTime / self.stepSize)

    # create qubit attributes (parameters, initial state, etc.) randomly in different test runs
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

    # creates the unitary time evolution operator
    def unitary(self):
        return evo.Unitary(2*np.pi*self.Hamiltonian, self.stepSize)

    # creates the Liouvillian super-operator
    def Liouvillian(self):
        return evo.Liouvillian(2*np.pi*self.Hamiltonian,
                               self.collapseOpsAndRates.keys(), self.collapseOpsAndRates.values())

    # exponentiates the Liouvillian super-operator
    def openEvolution(self):
        return evo.LiouvillianExp(2*np.pi*self.Hamiltonian, self.stepSize,
                                  self.collapseOpsAndRates.keys(), self.collapseOpsAndRates.values())

    # time evolves the qubit, and calls calculate function at each step
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
    # singleQubit fixture used to access above class and its method from the tests
    return _singleQubit()
