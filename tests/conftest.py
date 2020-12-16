import random as rn
import sys
import os
from pathlib import Path
import numpy as np
import pytest
path = str(Path(os.getcwd()))
sys.path.insert(0, path)
from qTools.QuantumToolbox import states#pylint: disable=import-error,wrong-import-position
from qTools.QuantumToolbox import operators as ops #pylint: disable=import-error

class Helpers:
    @staticmethod
    def generateRndDimAndExc(minval, dim=None):
        if dim is None:
            dim = rn.randint(2, 20)
        return dim, rn.randint(minval, dim-1)
    @staticmethod
    def generateRndStateParams(dim=None):
        dim, ncom = Helpers.generateRndDimAndExc(0, dim)
        comps = list(dict.fromkeys([rn.randint(0, dim-1) for k in range(ncom+1)]))
        pops = np.random.dirichlet(np.ones(len(comps)), size=1)[0]
        excs = dict(zip(comps, pops))
        return dim, excs
    @staticmethod
    def generateRndPureState(po=1, dim=None):
        dim, excs = Helpers.generateRndStateParams(dim)
        state = sum([(np.sqrt(v)**po)*states.basis(dim, k) for k, v in excs.items()])
        return state, dim, excs

@pytest.fixture
def helpers():
    return Helpers

@pytest.fixture
def referenceValues():
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
    return {**qubitStates, **{k+'dm':states.densityMatrix(v) for k, v in qubitStates.items()}}

@pytest.fixture
def singleQubitOperators():
    return {
        'sz':ops.sigmaz(), 'sy':ops.sigmay(), 'sx':ops.sigmax(), 'sp':ops.sigmap(), 'sm':ops.sigmam()
    }
