from qTools.classes.computeBase import computeBase
import qTools.QuantumToolbox.states as qSta


class qBase(computeBase):
    instances = 0
    label = 'qBase'

    __slots__ = ['__initialState', '__paramUpdated', '__initialStateInput']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None))
        self.__initialState = None
        self.__initialStateInput = None
        self.__paramUpdated = False
        self._qUniversal__setKwargs(**kwargs)  # pylint: disable=no-member

    @property
    def _paramUpdated(self):
        return self._qBase__paramUpdated

    @property
    def initialState(self):
        """
            This works by assuming that its setter/s makes sure that _qBase__initialState is not None for single systems,
            if its state is set.
            If single system initial state is not set, it will try creating here, but single system does not have qSystem,
            so will raise the below error.
        """
        if self._qBase__initialState is None:
            try:
                self._qBase__initialState = qSta.tensorProd(*[val.initialState for val in self.qSystems.values()]) # pylint: disable=assigning-non-slot
            except AttributeError:
                try:
                    self._qBase__initialState = qSta.tensorProd(*[val.initialState for val in self.superSys.qSystems.values()]) # pylint: disable=assigning-non-slot
                except AttributeError:
                    raise ValueError(self.name + ' is not given an initial state')
        return self._qBase__initialState
