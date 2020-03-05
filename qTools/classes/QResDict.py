from copy import deepcopy
from itertools import chain
from qTools.classes.QUni import qUniversal
from collections import defaultdict
from numpy import reshape, array

class qResultsContainer(qUniversal):
    instances = 0
    label = 'qUniversal'
    qResults = {}

    __slots__ = ['__results', '__lastSta', '__lastRes', '__states']
    def __init__(self, **kwargs):
        super().__init__()
        self.__results = defaultdict(list)
        self.__lastRes = defaultdict(list)
        self.__states = defaultdict(list)
        self.__lastSta = defaultdict(list)
        self._qUniversal__setKwargs(**kwargs)   

    @property
    def results(self):
        # TODO After eveything is done, make this the same as results
        return self._qResults__lastRes

    @property
    def resres(self):
        return self._qResults__results

    @property
    def states(self):
        return self._qResults__lastSta
        
    def reset(self):
        self._qResults__results = defaultdict(list)
        self._qResults__lastRes = defaultdict(list)
        self._qResults__states = defaultdict(list)
        self._qResults__lastSta = defaultdict(list)

    def resetLast(self):
        self._qResults__lastRes = defaultdict(list)
        self._qResults__lastSta = defaultdict(list)

    def _organiseRes(self, results, inds, steps):
        for res in results:
            for key, val in res.items():
                self._qResults__results[key].append(val)
        
        for key, val in self._qResults__results.items():
            lenOfVal = len(array(val).flatten())
            self._qResults__results[key] = reshape(val, (*list(reversed(inds)), int(lenOfVal/steps),))



class qResults(qResultsContainer):
    instances = 0
    label = 'qResultsContainer'

    __slots__ = []

    def __init__(self, **kwargs):
        super().__init__()
        qResultsContainer.qResults[self.superSys.name] = self
        self._qUniversal__setKwargs(**kwargs)  
