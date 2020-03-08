from qTools.classes.QUni import qUniversal


class updateBase(qUniversal):
    instances = 0
    label = 'updateBase'
    
    __slots__ = ['__key', '__function']

    def __init__(self, **kwargs):
        super().__init__()
        self._qUniversal__setKwargs(**kwargs)
        self.__key = None
        self.__function = None
        self._updateBase__function = None

    @property
    def system(self):
        qSys = list(self.subSys.values())
        return (*qSys,) if len(qSys) > 1 else qSys[0]

    @system.setter
    def system(self, qSys):
        super().addSubSys(qSys)

    def _runUpdate(self, val):
        if self._updateBase__function is None:
            for subSys in self.subSys.values():
                setattr(subSys, self._updateBase__key, val)
        else:
            # TODO track this part
            self._updateBase__function(self, self.superSys.superSys)
