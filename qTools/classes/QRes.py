from copy import deepcopy
from itertools import chain
from qTools.classes.QUni import qUniversal

class qResults(qUniversal):
    instances = 0
    label = 'qUniversal'
    __slots__ = ['__results', '__indB', '__indL', '__multiResults', '__resTotCount', '__prevRes', '__resCount', '__last', '__states', '__bLength', '__lLength']
    def __init__(self, **kwargs):
        super().__init__()
        self.__results = []
        self.__indB = 0
        self.__indL = 0
        self.__multiResults = []
        self.__resTotCount = 0
        self.__prevRes = False
        self.__resCount = 0
        self.__last = []
        self.__states = []
        self.__bLength = 0
        self.__lLength = 0
        self._qUniversal__setKwargs(**kwargs)

    @property
    def results(self):
        return self._qResults__multiResults

    @results.setter
    def result(self, val):
        if self._qResults__prevRes is True:
            self._qResults__multiResults[self._qResults__resCount][self.indB][self.indL].append(val)
            self._qResults__last[self._qResults__resCount].append(val)
            self._qResults__resCount += 1
        elif self._qResults__prevRes is False:
            self._qResults__last.append([])
            self._qResults__multiResults.append(deepcopy(self._qResults__results))
            self._qResults__multiResults[self._qResults__resTotCount][self.indB][self.indL].append(val)
            self._qResults__last[self._qResults__resTotCount].append(val)
            self._qResults__resTotCount += 1

    @property
    def states(self):
        return self._qResults__states

    @states.setter
    def state(self, st):
        self._qResults__states[self.indB][self.indL].append(st)

    def _createList(self):
        newList = []
        lList = []
        if self._qResults__lLength > 0:
            for indl in range(self._qResults__lLength):
                lList.append([])
        else:
            lList.append([])

        if self._qResults__bLength > 0:
            bList = []
            for indn in range(self._qResults__bLength):
                bList.append(deepcopy(lList))
            newList = bList
        else:
            newList = [deepcopy(lList)]

        self._qResults__results = newList
        self._qResults__states = deepcopy(newList)
        
    def reset(self):
        self._qResults__results = []
        self._qResults__indB = 0
        self._qResults__indL = 0
        self._qResults__multiResults = []
        self._qResults__resTotCount = 0
        self._qResults__prevRes = False
        self._qResults__resCount = 0
        self._qResults__last = []
        self._qResults__states = []


    @property
    def indB(self):
        return self._qResults__indB

    @indB.setter
    def indB(self, ii):
        self._qResults__indB = ii

    @property
    def indL(self):
        return self._qResults__indL

    @indL.setter
    def indL(self, ii):
        self._qResults__indL = ii

    def _unpack(self):
        unnested = []
        if ((self._qResults__bLength == 0) and (self._qResults__lLength != 0)):
            unnested = [list(chain(*sub)) for sub in self.results]
        elif ((self._qResults__bLength == 0) and (self._qResults__lLength == 0)):
            for result in self.results:
                nested = [list(chain(*sub)) for sub in result]
                unnested = [list(chain(*sub)) for sub in nested]
        elif ((self._qResults__bLength != 0) and (self._qResults__lLength == 0)):
            for result in self.results:
                unnested.append([list(chain(*sub)) for sub in result])
        elif ((self._qResults__bLength != 0) and (self._qResults__lLength != 0)):
            unnested = self.results

        self._qResults__multiResults = unnested
        return self.result

    def _prepare(self, qSim):
        if len(qSim.beforeLoop.sweeps) > 0:
            self._qResults__bLength = self._qResults__bLength = len(qSim.beforeLoop.sweeps[0].sweepList)

        if len(qSim.Loop.sweeps) > 0:
            self._qResults__lLength = len(qSim.Loop.sweeps[0].sweepList)


