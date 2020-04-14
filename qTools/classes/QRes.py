from qTools.classes.QUni import qUniversal
from collections import defaultdict

__all__ = [
    'qResults'
]

class qResBase(qUniversal):
    instances = 0
    label = 'qResBase'

    __slots__ = ['__results', '__states', '__resultsLast', '__statesLast', '__average']
    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__results = defaultdict(list)
        self.__average = defaultdict(list)
        self.__resultsLast = defaultdict(list)
        self.__states = defaultdict(list)
        self.__statesLast = defaultdict(list)
        self._qUniversal__setKwargs(**kwargs)   

    @property
    def results(self):
        return self._qResBase__resultsLast

    @property
    def resultsKeyValList(self):
        return self._qResBase__resultsLast

    @resultsKeyValList.setter
    def resultsKeyValList(self, keyValList):
        self._qResBase__resultsLast[keyValList[0]].append(keyValList[1])

    @resultsKeyValList.setter
    def averageKeyVal(self, keyValList):
        valCountPair = self._qResBase__average.pop(keyValList[0], None)
        if valCountPair is not None:
            val = valCountPair[0]
            counter = valCountPair[1]
            # FIXME does not work if storing say ndarray
            avg = ((counter*val) + keyValList[1])/(counter + 1)
            self._qResBase__average[keyValList[0]] = [avg, counter+1]
            self._qResBase__resultsLast[keyValList[0]] = avg
        else:
            val = keyValList[1]
            # FIXME does not work if storing say ndarray
            self._qResBase__average[keyValList[0]] = [val, 1]
            self._qResBase__resultsLast[keyValList[0]] = val


    def resultsMethod(self, key, value, average=False):
        if not average:
            if isinstance(key, str):
                self._qResBase__resultsLast[key].append(value)
            elif isinstance(value, str):
                self._qResBase__resultsLast[value].append(key)
        '''else:
            valCountPair = self._qResBase__average.pop(key, None)
            if valCountPair is not None:
                val = valCountPair[0]
                counter = valCountPair[1]
                # FIXME does not work if storing say ndarray
                avg = ((counter*val) + value)/(counter + 1)
                self._qResBase__average'''


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
        kwargs.pop('allResults', None)
        self.allResults = qResults._allResults
        self._qUniversal__setKwargs(**kwargs)
        self.allResults = qResults._allResults
        if self.superSys is not None:
            self.allResults[self.superSys.name] = self

    @qResBase.superSys.setter
    def superSys(self, supSys):
        removedFromAllRes = False
        oldSupSys = self.superSys
        qResBase.superSys.fset(self, supSys)
        if oldSupSys is not None:
            removedFromAllRes = True
            removedSys = self.allResults.pop(oldSupSys.name)
            assert removedSys is self

        if supSys is not None:
            removedFromAllRes = False
            self.allResults[self.superSys.name] = self

        if removedFromAllRes is True:
            print('?')

    def _reset(self):
        for qRes in self.allResults.values():
            qRes._qResBase__results = defaultdict(list)
            qRes._qResBase__average = defaultdict(list)
            qRes._qResBase__states = defaultdict(list)
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)

    def _resetLast(self):
        for qRes in self.allResults.values():
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)
            qRes._qResBase__average = defaultdict(list)

    def _organiseMultiProcRes(self, results, inds):
        for res in results:
            for keyUni, valUni in res.items():
                self._organise(keyUni, valUni)

        self._finaliseAll(inds)

    @classmethod
    def _finaliseAll(cls, inds):
        for qres in cls._allResults.values():
            qres._finalise(inds)

    @staticmethod
    def _organise(keyUni, valUni):
        for key, val in valUni.results.items():
            qResults._allResults[keyUni]._qResBase__results[key].append(val)
        
        for key1, val1, in valUni.states.items():
            qResults._allResults[keyUni]._qResBase__states[key1].append(val1)
        
    def _organiseSingleProcRes(self):
        for keyUni, valUni in self.allResults.items():
            self._organise(keyUni, valUni)

    def _finalise(self, inds):
        for key, val in self._qResBase__results.items():
            self._qResBase__results[key], _ = self._reShape(val, list(reversed(inds)))

        for key1, val1 in self._qResBase__states.items():
            self._qResBase__states[key1], _ = self._reShape(val1, list(reversed(inds)))
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
        return (newList, totalCount)
