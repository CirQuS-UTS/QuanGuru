from qTools.classes.QUni import qUniversal

class updateBase(qUniversal):
    instances = 0
    label = 'updateBase'
    
    __slots__ = ['__key', '__function']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))

        self.__key = None
        self.__function = None
        
        self._qUniversal__setKwargs(**kwargs)

    @property
    def system(self):
        qSys = list(self.subSys.values())
        return (*qSys,) if len(qSys) > 1 else qSys[0]

    @system.setter
    def system(self, qSys):
        super().addSubSys(qSys)

    def _runUpdate(self, val):
        for subSys in self.subSys.values():
            setattr(subSys, self._updateBase__key, val)
