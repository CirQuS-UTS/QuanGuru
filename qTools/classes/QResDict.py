from copy import deepcopy
from itertools import chain
from qTools.classes.QUni import qUniversal
from collections import defaultdict
from numpy import reshape, array

class qResultsContainer(qUniversal):
    instances = 0
    label = 'qResultsContainer'
    qResults = {}
    lastResults = {}

    __slots__ = ['__results', '__lastSta', '__lastRes', '__states']
    def __init__(self, **kwargs):
        super().__init__()
        self.__results = defaultdict(list)
        self.__states = defaultdict(list)
        self._qUniversal__setKwargs(**kwargs)   

    @property
    def results(self):
        # TODO After eveything is done, make this the same as results
        return self._qResultsContainer__results

    @property
    def resres(self):
        return self._qResultsContainer__results

    @property
    def states(self):
        return self._qResultsContainer__states
        
    def reset(self):
        self._qResultsContainer__results = defaultdict(list)
        self._qResultsContainer__states = defaultdict(list)

    def _organiseMultiProcRes(self, results, inds, steps):
        for res in results:
            for key, val in res.items():
                self._qResultsContainer__results[key].extend(val)
        
        self._organiseSingleProcRes(inds, steps)

    def _organiseSingleProcRes(self, inds, steps):
        for key, val in self._qResultsContainer__results.items():
            self._qResultsContainer__results[key] = reshape(val, (*list(reversed(inds)), int(len(val)/steps),))

    def saveResults(self):
        pass

    def _saveResults(self):
        pass

    @classmethod
    def allResults(cls):
        return cls.qResults


class qResults(qResultsContainer):
    instances = 0
    label = 'qResults'

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs)
        qResultsContainer.qResults[self.superSys] = self
