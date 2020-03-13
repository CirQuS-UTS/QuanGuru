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

    __slots__ = ['__results', '__states', '__resultsLast', '__statesLast']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__results = defaultdict(list)
        self.__resultsLast = defaultdict(list)
        self.__states = defaultdict(list)
        self.__statesLast = defaultdict(list)
        self._qUniversal__setKwargs(**kwargs)   

    @property
    def results(self):
        return self._qResBase__resultsLast

    @property
    def states(self):
        return self._qResBase__statesLast

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
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)

    def resetLast(self):
        for qRes in self.allResults.values():
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)

    def _organiseMultiProcRes(self, results, inds):
        for res in results:
            for keyUni, valUni in res.items():
                self._organise(keyUni, valUni, inds)
        
        for qres in qResults._allResults.values():
            qres._finalise(inds)

    @staticmethod
    def _organise(keyUni, valUni, inds):
        for key, val in valUni.results.items():
            qResults._allResults[keyUni]._qResBase__results[key].append(val)
        
        for key1, val1, in valUni.states.items():
            qResults._allResults[keyUni]._qResBase__states[key1].append(val1)
        
    def _organiseSingleProcRes(self, inds):
        for keyUni, valUni in self.allResults.items():
            self._organise(keyUni, valUni, inds)

    def _finalise(self, inds):
        for key, val in self._qResBase__results.items():
            self._qResBase__results[key] = self._reShape(val, list(reversed(inds)))

        for key1, val1 in self._qResBase__states.items():
            self._qResBase__states[key1] = self._reShape(val1, list(reversed(inds)))
        self._qResBase__resultsLast = self._qResBase__results
        self._qResBase__statesLast = self._qResBase__states

    @staticmethod
    def _reShape(lis, inds, counter=0, totalCount=0):
        newList = []
        if counter < (len(inds)-1):
            counter += 1
            for indx in range(inds[counter-1]):
                nList, totalCount = qResults._reShape(lis, inds, counter, totalCount)
                newList.append(nList)
        else:
            for indx in range(inds[counter]):
                newList.append(lis[totalCount])
                totalCount += 1
            return (newList, totalCount)
        return newList


