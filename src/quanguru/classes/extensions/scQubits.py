from scqubits import Transmon, TunableTransmon
from scqubits.core.central_dispatch import DispatchClient, CENTRAL_DISPATCH
from ..QSystem import QuantumSystem
import numpy as np
import scipy.optimize


class scQubit(QuantumSystem):
#FIXME the dimension < _maxDim condition in the __init__ function

    label = 'scQubit'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

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

    def eigenstate(self, n):
        r"""
        This method returns the eigenvalues and eigenstates of the qubit Hamiltonian
        """
        return self.scqObj.numberbasis_wavefunction(esys=None, which=n).amplitudes.reshape(self.dimension, 1)

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


    @staticmethod
    def find_EJ_EC(ω01, α):
        """
        Computes and returns approximated values of EJ and EC for a transmon given
        gap ω01 and anharmonicity
        """
        def budget(x):
            tmon = Transmon(EJ=x[0], EC=x[1], ng=0, ncut=30)
            return [tmon.E01() - ω01, α - tmon.anharmonicity()]
        
        if ω01 < 0 or α > 0 or abs(α) > abs(ω01):
            raise ValueError(f'Invalid transmon properties ω01={ω01}, anharmonicity={α}')

        
        EJ = (ω01 + (-α))**2 / (8*(-α))
        EC = np.abs(α)
        # if not quiet:
        #     print('Estimates:')
        #     print(f'EJ    = {EJ}')
        #     print(f'EC    = {EC}')
        #     print(f'EJ/EC = {EJ/EC}')

        x = scipy.optimize.fsolve(budget, [EJ, EC])
        tmon = Transmon(EJ=x[0], EC=x[1], ng=0, ncut=30)

        # if not quiet:
            # print('Computation:')
            # print(f'EJ    = {x[0]}')
            # print(f'EC    = {x[1]}')
            # print(f'EJ/EC = {x[0]/x[1]}')
            # print(f'ω01   = {tmon.E01()}')
            # print(f'α     = {tmon.anharmonicity()}')
        return tmon.EJ, tmon.EC
    

class scqTunableTransmon(scqTransmon):
    
    instances = 0
    label = 'scqTunableTransmon'
    scqType = TunableTransmon

    __slots__ = []
