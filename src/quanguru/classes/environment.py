"""
    THESE ARE JUST SOME INITIAL IDEAS. NOT COMPLETED OR USED YET.

    .. currentmodule:: quanguru.classes.environment

    .. autosummary::

        _genericOpen
        dissipatorObj
        thermalBath

"""

from ..QuantumToolbox.thermodynamics import nBarThermal
from ..QuantumToolbox.operators import compositeOp
from .baseClasses import paramBoundBase
from .QSimBase import setAttr

class _genericOpen(paramBoundBase):
    r"""
    Parent class for ``thermalBath`` and ``dissipator``.
    """
    #: (**class attribute**) class label used in default naming
    label: str = '_genericOpen'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []

    @property
    def system(self):
        r"""
        Get and set the system to which the bath is attached.
        """
        return self.superSys

    @system.setter
    def system(self, supSys):
        self.superSys = supSys # pylint: disable=no-member

    @paramBoundBase.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        paramBoundBase.superSys.fset(self, supSys) # pylint: disable=no-member
        supSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access

class dissipatorObj(_genericOpen):
    label = 'dissipator'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['type', '__operator', '__rate', '__bath']

    def __init__(self, **kwargs):
        self.type = 1
        self.__operator = None
        self.__rate = 0
        self.__bath = thermalBath()
        super().__init__(**kwargs)

    @property
    def temperature(self):
        r"""
        Gets and sets the temperature of the bath.
        """
        return self._dissipatorObj__bath.temperature

    @temperature.setter
    def temperature(self, temp):
        self._dissipatorObj__bath.temperature = temp

    @_genericOpen.superSys.setter # pylint: disable=no-member
    def superSys(self, supSys):
        _genericOpen.superSys.fset(self, supSys) # pylint: disable=no-member
        self.addToProtocol(supSys._freeEvol)

    def addToProtocol(self, protocol):
        protocol._genericProtocol__dissipator[self] = self.jRate #pylint:disable=protected-access
        self._paramBoundBase__paramBound[protocol.name] = protocol # pylint: disable=no-member

    @property
    def jRate(self):
        return self._dissipatorObj__rate*(self._dissipatorObj__bath.nBar + self.type)

    @jRate.setter
    def jRate(self, rate):
        setAttr(self, '_dissipatorObj__rate', rate)

    @property
    def jOper(self):
        return self._dissipatorObj__operator

    @property
    def jOperMatrix(self):
        return self._paramBoundBase__matrix # pylint:disable=no-member

    @jOperMatrix.setter
    def jOperMatrix(self, jOpMat):
        if ((jOpMat is None) or self._paramUpdated):
            setAttr(self, '_paramBoundBase__matrix',
                    compositeOp(self.jOper, dimA=self.superSys._dimsAfter, dimB=self.superSys._dimsBefore)) # pylint:disable=no-member
            self._paramBoundBase__paramUpdated = False # pylint:disable=assigning-non-slot

    @jOper.setter
    def jOper(self, jop):
        setAttr(self, '_dissipatorObj__operator', jop)
        if self._paramUpdated:
            self.jOperMatrix = None

class thermalBath(_genericOpen): # pylint:disable=too-few-public-methods
    r"""
    Object for a thermal bath that contains several ``dissipator``, which is a child class of this.
    """
    #: (**class attribute**) class label used in default naming
    label: str = 'environment'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__temperature', '__charFreq', '__nbar']

    def __init__(self, **kwargs) -> None:
        #: temperature of the bath
        self.__temperature = 0
        #: characteristics frequency of the bath
        self.__charFreq = 1
        #: nbar corresponding to the above temperature and frequency
        self.__nbar = 0
        super().__init__(**kwargs)

    @property
    def jOpers(self):
        return [ds.jOper for ds in self.subSys.values()] # pylint: disable=no-member

    @jOpers.setter
    def jOpers(self, ops, rates, systems):
        if isinstance(rates, list):
            for ind, op in enumerate(ops):
                self.dissipator = dissipatorObj(system=systems[ind], jOper=op, jRate=rates[ind])

    @property
    def dissipator(self):
        r"""
        Get and set the dissipator objects that contain the jump operator from which the dissipator term is going to be
        created.
        """
        return self.subSys

    @_genericOpen.subSys.setter
    def subSys(self, subS):
        _genericOpen.subSys.fset(self, subS)
        subS._dissipatorObj__bath = self #pylint:disable=protected-access
        self._paramBoundBase__paramBound[subS.name] = subS # pylint: disable=no-member

    @dissipator.setter
    def dissipator(self, subS):
        assert isinstance(subS, dissipatorObj)
        self.subSys = subS

    @property
    def temperature(self):
        r"""
        Gets and sets the temperature of the bath.
        """
        return self._thermalBath__temperature

    @temperature.setter
    def temperature(self, temp):
        setAttr(self, '_thermalBath__temperature', temp)

    @property
    def charFreq(self):
        r"""
        Gets and sets the characteristics frequency of the bath.
        """
        return self._thermalBath__charFreq

    @charFreq.setter
    def charFreq(self, freq):
        setAttr(self, '_thermalBath__charFreq', freq)

    @property
    def nBar(self):
        r"""
        Returns the nBar of the thermal bath, and re-calculates the ``nBar`` if the ``temperature`` or ``charFreq`` are
        changed.
        """
        if self._paramUpdated:
            setAttr(self, '_thermalBath__nbar', nBarThermal(self.charFreq, self.temperature))
            self._paramBoundBase__paramUpdated = False # pylint:disable=assigning-non-slot
        return self._thermalBath__nbar
