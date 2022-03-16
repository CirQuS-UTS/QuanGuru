import random as rn
import string
import multiprocessing
import platform
import sys
import os
from pathlib import Path
import numpy as np
import pytest

if platform.system() != 'Windows':
    if sys.version_info[1] >= 8:
        try:
            #multiprocessing.get_start_method() != 'fork'
            multiprocessing.set_start_method("fork")
        except: #pylint:disable=bare-except # noqa: E722
            pass

path = str(Path(os.getcwd()))
sys.path.insert(0, path)
sys.path.insert(0, path+'/src/')
from quanguru.QuantumToolbox import states#pylint: disable=import-error,wrong-import-position
from quanguru.QuantumToolbox import operators as ops #pylint: disable=import-error,wrong-import-position

class Helpers:
    # used for the helper function fixture, put any helper function for testing as a static method in here and use
    # helpers fixture (below) in the testing
    @staticmethod
    def generateRndDimAndExc(minval, dim=None):
        # generates a random integer btw 2 to 20 to be used as dimension, and another integer btw 0 to dim-1 to be used
        # either as the excitation or number of components in a super-position state
        if dim is None:
            dim = rn.randint(2, 20)
        return dim, rn.randint(minval, dim-1)
    @staticmethod
    def generateRndStateParams(dim=None):
        # using a randomly generated dimension and number of components, create a dictionary of random excitation
        # positions and correponding (random populations) as a key:value combination. it is already normalised
        dim, ncom = Helpers.generateRndDimAndExc(0, dim)
        comps = list(dict.fromkeys([rn.randint(0, dim-1) for k in range(ncom+1)]))
        pops = np.random.dirichlet(np.ones(len(comps)), size=1)[0]
        excs = dict(zip(comps, pops))
        return dim, excs
    @staticmethod
    def generateRndPureState(po=1, dim=None):
        # generate a random ket state.
        dim, excs = Helpers.generateRndStateParams(dim)
        state = sum([(np.sqrt(v)**po)*states.basis(dim, k) for k, v in excs.items()])
        return state, dim, excs
    @staticmethod
    def randString(N):
        return str(''.join(rn.choice(string.ascii_uppercase + string.digits) for _ in range(N)))
    @staticmethod
    def randStringList(n=4, N=10):
        return [Helpers.randString(rn.randint(3, 10)) for _ in range(rn.randint(n, N))]

@pytest.fixture
def helpers():
    # helpers fixture to access above helper functions in the testing
    return Helpers

@pytest.fixture
def referenceValues():
    # a fixture returning dictionary storing some reference values, such as some special operators, constants, etc
    return {
        'sigmaMinusReference': np.array([[0, 0], [1, 0]]), 'sigmaPlusReference': np.array([[0, 1], [0, 0]]),
        'sigmaXReference': np.array([[0, 1], [1, 0]]), 'sigmaYReference': np.array([[0, -1j], [1j, 0]]),
        'sigmaZReference': np.array([[1, 0], [0, -1]])
    }

qubitStates = {
        '0': np.array([[0], [1]]), '1': np.array([[1], [0]]),
        'x+': (1/np.sqrt(2))*np.array([[1], [1]]), 'x-': (1/np.sqrt(2))*np.array([[1], [-1]]),
        'y+': (1/np.sqrt(2))*np.array([[1], [1j]]), 'y-': (1/np.sqrt(2))*np.array([[1], [-1j]]),
        'BellPhi+': (1/np.sqrt(2))*np.array([[1], [0], [0], [1]]),
        'BellPhi-': (1/np.sqrt(2))*np.array([[1], [0], [0], [-1]]),
        'BellPsi+': (1/np.sqrt(2))*np.array([[0], [1], [1], [0]]),
        'BellPsi-': (1/np.sqrt(2))*np.array([[0], [1], [-1], [0]]),
        'product1': np.array([[1], [0], [0], [0]]),
        'product2': np.array([[0], [1], [0], [0]]),
        'product3': np.array([[0], [0], [1], [0]]),
        'product4': np.array([[0], [0], [0], [1]]),
    }

@pytest.fixture
def specialQubitStates():
    # a fixture returning a dictionary of some special qubit states
    return {**qubitStates, **{k+'dm':states.densityMatrix(v) for k, v in qubitStates.items()}}

@pytest.fixture
def singleQubitOperators():
    # a fixture returning qubit operators generated by our functions
    return {
        'sz':ops.sigmaz(), 'sy':ops.sigmay(), 'sx':ops.sigmax(), 'sp':ops.sigmap(), 'sm':ops.sigmam()
    }
