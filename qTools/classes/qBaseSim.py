from qTools.classes.computeBase import computeBase
from qTools.classes.Simulation import Simulation

class qBaseSim(computeBase):
    isinstances = 0
    label = 'qBase'

    __slots__ = ['__simulation']

    def __init__(self, **kwargs):
        super().__init__(name=kwargs.pop('name', None), _internal=kwargs.pop('_internal', False))
        self.__simulation = Simulation(_internal=True, superSys=self)
        self._qBaseSim__simulation._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        self._qUniversal__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def simulation(self):
        return self._qBaseSim__simulation

    @simulation.setter
    def simulation(self, sim):
        if sim is None:
            self._qBaseSim__simulation = Simulation() # pylint: disable=assigning-non-slot
        elif sim == 'new':
            self._qBaseSim__simulation = Simulation() # pylint: disable=assigning-non-slot
        else:
            self._qBaseSim__simulation = sim # pylint: disable=assigning-non-slot
            sim._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
            for sys in self.subSys.values():
                if sys is not self:
                    if hasattr(sys, 'simulation'):
                        sys.simulation = sim

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        if self not in _exclude:
            _exclude = super().delMatrices(_exclude)
            _exclude = self.simulation.delMatrices(_exclude)
        return _exclude
