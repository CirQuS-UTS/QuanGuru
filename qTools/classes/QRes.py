from collections import defaultdict
from qTools.classes.QUni import qUniversal

__all__ = [
    'qResults'
]


class qResBlank:
    __slots__ = ['__results', '__states', '__resultsLast', '__statesLast', '__average', '__calculated']
    def __init__(self):
        super().__init__()
        self.__results = defaultdict(list)
        self.__average = defaultdict(list)
        self.__resultsLast = defaultdict(list)
        self.__states = defaultdict(list)
        self.__statesLast = defaultdict(list)
        self.__calculated = defaultdict(list)

    @property
    def results(self):
        return self._qResBlank__resultsLast

    @property
    def states(self):
        return self._qResBlank__statesLast

class qResBase(qUniversal):
    instances = 0
    label = 'qResBase'

    __slots__ = ['__results', '__states', '__resultsLast', '__statesLast', '__average', '__calculated']
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.__results = defaultdict(list)
        self.__average = defaultdict(list)
        self.__resultsLast = defaultdict(list)
        self.__states = defaultdict(list)
        self.__statesLast = defaultdict(list)
        self.__calculated = defaultdict(list)
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def calculated(self):
        return self._qResBase__calculated

    @calculated.setter
    def calculated(self, keyValList):
        self._qResBase__calculated[keyValList[0]].append(keyValList[1])

    @property
    def results(self):
        return self._qResBase__resultsLast

    @results.setter
    def result(self, keyValList):
        self._qResBase__resultsLast[keyValList[0]].append(keyValList[1])

    @results.setter
    def resAverage(self, keyValList):
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
        #else:
        #    valCountPair = self._qResBase__average.pop(key, None)
        #    if valCountPair is not None:
        #        val = valCountPair[0]
        #        counter = valCountPair[1]
        #        # FIXME does not work if storing say ndarray
        #        avg = ((counter*val) + value)/(counter + 1)
        #        self._qResBase__average


    @property
    def states(self):
        return self._qResBase__statesLast

    def saveResults(self):
        pass

    def _saveResults(self):
        pass

class qResults(qResBase):
    instances = 0
    _externalInstances = 0
    _internalInstances = 0
    label = 'qResults'
    _allResults = {}

    __slots__ = ['allResults']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        kwargs.pop('allResults', None)
        self.allResults = qResults._allResults
        self.allResults[self.name] = self # pylint: disable=no-member
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    def _copyAllResBlank(self):
        allResCopy = {}
        for sys in self.allResults.values():
            newQRes = qResBlank()
            newQRes._qResBlank__results = sys._qResBase__results # pylint: disable=assigning-non-slot
            newQRes._qResBlank__average = sys._qResBase__average # pylint: disable=assigning-non-slot
            newQRes._qResBlank__states = sys._qResBase__states # pylint: disable=assigning-non-slot
            newQRes._qResBlank__resultsLast = sys._qResBase__resultsLast # pylint: disable=assigning-non-slot
            newQRes._qResBlank__statesLast = sys._qResBase__statesLast # pylint: disable=assigning-non-slot
            newQRes._qResBlank__calculated = sys._qResBase__calculated # pylint: disable=assigning-non-slot
            allResCopy[sys.name] = newQRes
        return allResCopy

    @qResBase.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        qResBase.superSys.fset(self, supSys) # pylint: disable=no-member
        self.allResults.pop(self.name) # pylint: disable=no-member
        self.name = self.superSys.name + 'Results' # pylint: disable=no-member
        self.allResults[self.name] = self # pylint: disable=no-member

    def _reset(self):
        for qRes in self.allResults.values():
            qRes._qResBase__results = defaultdict(list)
            qRes._qResBase__average = defaultdict(list)
            qRes._qResBase__states = defaultdict(list)
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)
            qRes._qResBase__calculated = defaultdict(list)

    def _resetLast(self, calculateException):
        for qRes in self.allResults.values():
            qRes._qResBase__resultsLast = defaultdict(list)
            qRes._qResBase__statesLast = defaultdict(list)
            qRes._qResBase__average = defaultdict(list)
            if qRes is not calculateException:
                qRes._qResBase__calculated = defaultdict(list)

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
            qResults._allResults[keyUni]._qResBase__results[key].append(val) # pylint: disable=no-member

        for key1, val1, in valUni.states.items():
            qResults._allResults[keyUni]._qResBase__states[key1].append(val1) # pylint: disable=no-member

    def _organiseSingleProcRes(self):
        for keyUni, valUni in self.allResults.items():
            self._organise(keyUni, valUni)

    def _finalise(self, inds):
        for key, val in self._qResBase__results.items(): # pylint: disable=no-member
            if inds != []:
                self._qResBase__results[key], _ = self._reShape(val, list(reversed(inds))) # pylint: disable=no-member
            else:
                self._qResBase__results[key] = val[0]  # pylint: disable=no-member

        for key1, val1 in self._qResBase__states.items(): # pylint: disable=no-member
            if inds != []:
                self._qResBase__states[key1], _ = self._reShape(val1, list(reversed(inds))) # pylint: disable=no-member
            else:
                self._qResBase__states[key1] = val1[0] # pylint: disable=no-member
        self._qResBase__resultsLast = self._qResBase__results # pylint: disable=assigning-non-slot, no-member
        self._qResBase__statesLast = self._qResBase__states # pylint: disable=assigning-non-slot, no-member

    @staticmethod
    def _reShape(lis, inds, counter=0, totalCount=0):
        newList = []
        if counter < (len(inds)-1):
            counter += 1
            for _ in range(inds[counter-1]):
                nList, totalCount = qResults._reShape(lis, inds, counter, totalCount)
                newList.append(nList)
        else:
            for _ in range(inds[counter]):
                lisToAppend = lis[totalCount]
                if isinstance(lisToAppend, list):
                    if len(lisToAppend) == 1:
                        lisToAppend = lisToAppend[0]
                newList.append(lisToAppend)
                totalCount += 1
            return (newList, totalCount)
        return (newList, totalCount)
