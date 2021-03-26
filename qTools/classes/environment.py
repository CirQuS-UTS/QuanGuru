from ..QuantumToolbox import evolution as qEvo #pylint: disable=relative-beyond-top-level

from .QSys import qCoupling, termTimeDep


class environment(termTimeDep): # pylint:disable=too-few-public-methods
    label = 'environment'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    @property
    def envCouplings(self):
        return self.subSys.values()

class envCoupling(qCoupling):
    label = 'envCoupling'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['type', '__envMatrix']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "dissipator"
        self.__envMatrix = None

    @property
    def dissipator(self):
        if ((self._paramUpdated) or (self._envCoupling__envMatrix is None)): # pylint: disable=no-member
            if self.type.lower() == "dissipator":
                self._envCoupling__envMatrix = qEvo.dissipator(self.freeMat) # pylint: disable=assigning-non-slot
        return self._envCoupling__envMatrix # pylint: disable=no-member
