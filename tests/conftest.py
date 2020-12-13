import random as rn
import sys
import os
from pathlib import Path
import numpy as np
import pytest
path = str(Path(os.getcwd()))
sys.path.insert(0, path)
from qTools.QuantumToolbox import states#pylint: disable=import-error,wrong-import-position

class Helpers:
    @staticmethod
    def generateRndDimAndExc(minval):
        dim = rn.randint(2, 20)
        return dim, rn.randint(minval, dim-1)
    @staticmethod
    def generateRndStateParams():
        dim, ncom = Helpers.generateRndDimAndExc(1)
        comps = list(dict.fromkeys([rn.randint(1, dim-1) for k in range(ncom)]))
        pops = np.random.dirichlet(np.ones(len(comps)), size=1)[0]
        excs = dict(zip(comps, pops))
        return dim, excs
    @staticmethod
    def generateRndPureState(po=1):
        dim, excs = Helpers.generateRndStateParams()
        state = sum([(np.sqrt(v)**po)*states.basis(dim, k) for k, v in excs.items()])
        return state, dim, excs

@pytest.fixture
def helpers():
    return Helpers

@pytest.fixture
def constants():
    return {
        'sigmaMinusReference': np.array([[0, 0], [1, 0]]), 'sigmaPlusReference': np.array([[0, 1], [0, 0]]),
        'sigmaXReference': np.array([[0, 1], [1, 0]]), 'sigmaYReference': np.array([[0, -1j], [1j, 0]]),
        'sigmaZReference': np.array([[1, 0], [0, -1]])
    }
