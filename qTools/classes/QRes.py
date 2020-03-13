from copy import deepcopy
from itertools import chain
from qTools.classes.QUni import qUniversal
from collections import defaultdict
from numpy import reshape, array

__all__ = [
    'qResults'
]

class qResBase(qUniversal):
    instances = 0
    label = 'qResBase'

    __slots__ = ['__results', '__states']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__results = defaultdict(list)
        self.__states = defaultdict(list)
        self._qUniversal__setKwargs(**kwargs)   

    @property
    def results(self):
        return self._qResBase__results

    @property
    def states(self):
        return self._qResBase__states

    def saveResults(self):
        pass

    def _saveResults(self):
        pass
    

class qResults(qResBase):
    instances = 0
    label = 'qResults'
    _allResults = {}

    __slots__ = ['allResults']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self._qUniversal__setKwargs(**kwargs)
        self.allResults = qResults._allResults
        self.allResults[self.superSys.name] = self

    def reset(self):
        for qRes in self.allResults.values():
            qRes._qResBase__results = defaultdict(list)
            qRes._qResBase__states = defaultdict(list)

    def _organiseMultiProcRes(self, results, inds, steps):
        for res in results:
            for keyUni, valUni in res.items():
                for key, val in valUni.results.items():
                    self.allResults[keyUni]._qResBase__results[key].extend(val)
                
                for key1, val1 in valUni.states.items():
                    self.allResults[keyUni]._qResBase__states[key1].extend(val1)
        self._organiseSingleProcRes(inds, steps)

    
    def _organiseSingleProcRes(self, inds, steps):
        for keyUni, valUni in self.allResults.items():
            for key, val in valUni.results.items():
                self.allResults[keyUni]._qResBase__results[key] = reshape(val, (*list(reversed(inds)), int(len(val)/steps),))
            
            for key1, val1, in valUni.states.items():
                self.allResults[keyUni]._qResBase__states[key1] = reshape(val1, (*list(reversed(inds)), int(len(val1)/steps),))
                #cls._qResultsContainer__results[key] = reshape(val, (*list(reversed(inds)), int(len(val)/steps),))
