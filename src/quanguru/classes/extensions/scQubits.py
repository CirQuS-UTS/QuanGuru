from scqubits import Transmon, TunableTransmon
from scqubits.core.central_dispatch import DispatchClient, CENTRAL_DISPATCH
from ..QSystem import QuantumSystem
import numpy as np

class scQubit(QuantumSystem):
#FIXME the dimension < _maxDim condition in the __init__ function

    instances = 0
    label = 'scQubit'
    scqType = None

    __slots__ = ['scqObj', '__ncut', '__listener']

    def __init__(self, **kwargs):
        # instantiating the scqObj
        scqAttrs = self.scqType.default_params()
        keys = scqAttrs.keys()
        for key in keys:
            if key in kwargs.keys():
                scqAttrs[key] = kwargs.pop(key)
   
        self.scqObj = self.scqType(**scqAttrs)

        super().__init__(**kwargs)

        self.__listener = DispatchClient()
        self.__listener.receive = self._paramUpdatedHandler
        CENTRAL_DISPATCH.register("QUANTUMSYSTEM_UPDATE", self.__listener)

        self._QuantumSystem__compSys = False
        self.frequency = 1
        self.__ncut = 0
        self.dimension = 2*self.scqObj.ncut + 1
        self.operator = self.scqHamiltonian

    def _paramUpdatedHandler(self, event, sender):
        """
        Callback function to handle parameter updates from scqubits objects pertaining to the Hamiltonian
        """
        if sender is self.scqObj:
            self._paramUpdated = True
            if self._scQubit__ncut != self.scqObj.ncut:
                self._scQubit__ncut = self.scqObj.ncut
                QuantumSystem.dimension.fset(self, 2*self._scQubit__ncut + 1)

    def scqHamiltonian(self, dim):
        r"""
        This method returns the qubit Hamiltonian
        """
        return self.scqObj.hamiltonian()

    @QuantumSystem.dimension.setter
    def dimension(self, dim):
        if dim % 2 == 0:
            raise ValueError('dimension must be odd for scqubits qubits')
        self.scqObj.ncut = (dim - 1)//2

    def eigenstate(self, n=0):
        r"""
        This method returns the eigenvalues and eigenstates of the qubit Hamiltonian
        """
        return self.scqObj.numberbasis_wavefunction(esys=None, which=n)

    def __getattribute__(self, __name: str):
        r"""
        Custom ``__getattribute__`` method to get the parameters related to the internal scqObj object through self
        """
        try:
            obj = super().__getattribute__(__name)
        except AttributeError as attErr1:
            try:
                obj = getattr(self.scqObj, __name)
            except AttributeError as exc:
                raise attErr1 from exc
        return obj

    def __setattr__(self, __name: str, __value) -> None:
        r"""
        Custom ``__setattr__`` method to set the parameters related to the internal scqObj object through self
        """
        try:
            obj = super().__setattr__(__name, __value)
        except AttributeError as attErr1:
            try:
                obj = setattr(self.scqObj, __name, __value)
            except AttributeError as exc:
                raise attErr1 from exc
        return obj

class scqTransmon(scQubit):

    instances = 0
    label = 'scqTransmon'
    _max_dim_label = '2*ncut + 1'
    scqType = Transmon

    __slots__ = []

    #TODO add static method for finding EJ and EC...
    # (override the find_EJ_EC static method in scqubits.Transmon class) using numerical optimisation

class scqTunableTransmon(scqTransmon):
    
    instances = 0
    label = 'scqTunableTransmon'
    scqType = TunableTransmon

    __slots__ = []
