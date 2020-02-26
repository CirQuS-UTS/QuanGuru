

class qResults:
    def __init__(self):
        super().__init__()
        self.__results = []
        self.__indB = 0
        self.__indL = 0
        #self.__indW = 0
        self.__multiResults = []
        self.__resTotCount = 0
        self.__prevRes = False
        self.__resCount = 0

    @property
    def results(self):
        return self._qResults__results

    @results.setter
    def results(self, val):
        if self._qResults__prevRes is True:
            self._qResults__multiResults[self._qResults__resCount][self.indB][self.indL].append(val)
            self._qResult__resCount += 1
        elif self._qResults__prevRes is False:
            self._qResults__multiResults.append(self._qResults__results)
            self._qResults__multiResults[self._qResults__resTotCount][self.indB][self.indL].append(val)
            self._qResults__resTotCount += 1

    def createList(self, bLength, lLength):
        newList = []
        lList = []
        for indl in range(lLength):
            lList.append([])

        if bLength > 0:
            bList = []
            for indn in range(bLength):
                bList.append(lList)
            newList = bList
        else:
            newList = [lList]

        self._qResults__results = newList

        

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

    '''@property
    def indW(self):
        return self._qResults__indW'''

    '''@ind.setter
    def indW(self, ii):
        self._qResults__indW = ii'''

