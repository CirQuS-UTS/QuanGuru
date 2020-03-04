from copy import deepcopy
from itertools import chain
from qTools.classes.QUni import qUniversal
from collections import defaultdict

class qResults(qUniversal):
    instances = 0
    label = 'qUniversal'
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


