from qTools.classes.computeBase import computeBase
from qTools.classes.QUni import checkClass


class qBase(computeBase):
    instances = 0
    label = 'qBase'

    __slots__ = ['__initialState', '__paramUpdated', '__initialStateInput', '__paramBound']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__initialState = None
        self.__initialStateInput = None
        self.__paramUpdated = False
        self.__paramBound = {}
        self._qUniversal__setKwargs(**kwargs)  # pylint: disable=no-member

    @checkClass('qUniversal')
    def _addParamBound(self, bound, **kwargs):
        bound._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member
        self._qBase__paramBound[bound.name] = bound

    @property
    def _paramUpdated(self):
        return self._qBase__paramUpdated

    @property
    def initialState(self):
        return self._qBase__initialState

    @property
    def _initialStateInput(self):
        return self._qBase__initialStateInput
