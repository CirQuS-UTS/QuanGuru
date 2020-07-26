from ..QuantumToolbox import evolution as qEvo #pylint: disable=relative-beyond-top-level

from .QSys import couplingBase, _timeDep


class environment(_timeDep):
    instances = 0
    label = 'environment'

    @property
    def envCouplings(self):
        return self.subSys.values()

class envCoupling(couplingBase):
    instances = 0
    label = 'envCoupling'

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
