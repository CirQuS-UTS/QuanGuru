from scqubits import Transmon, TunableTransmon
from scqubits.core.descriptors import WatchedProperty
from scqubits.core.central_dispatch import DispatchClient, CENTRAL_DISPATCH
from ..QSystem import QuantumSystem
from ..QSimBase import setAttr
import numpy as np
import scipy.optimize
import warnings


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

    __slots__ = ['_scqObj', '_watchedProperties']

    def __init__(self, **kwargs):

        if 'ncut' in kwargs and 'dimension' in kwargs:
            warnings.warn(
                "When initialising both ncut and dimension, the value for dimension takes precedence, "
                + "and ncut is set accordingly via ncut = (dim - 1)//2."
            )

        # instantiate the internal scqubits object with default parameters
        # (overridden by any kwargs that match the scqubits parameters)
        scqAttrs = self.scqType.default_params()
        keys = scqAttrs.keys()
        for key in keys:
            if key in kwargs.keys():
                scqAttrs[key] = kwargs.pop(key)
   
        self._scqObj = self.scqType(**scqAttrs)
        self._watchedProperties = [attr for attr in dir(self.scqType) if isinstance(getattr(self.scqType, attr), WatchedProperty)]

        super().__init__(**kwargs)

        self._QuantumSystem__compSys = False
        self.frequency = 1
        self.operator = self.scqHamiltonian
        QuantumSystem.dimension.fset(self, kwargs.pop('dimension', 2*self.ncut + 1))

    def scqHamiltonian(self, dim):
        r"""
        This method returns the qubit Hamiltonian
        """
        return self._scqObj.hamiltonian()

    @QuantumSystem.dimension.setter
    def dimension(self, dim):
        if dim % 2 == 0:
            raise ValueError('dimension must be odd for scqubits qubits')
        self.ncut = (dim - 1)//2

    def eigenstate(self, n):
        r"""
        This method returns the eigenvalues and eigenstates of the qubit Hamiltonian
        """
        return self._scqObj.numberbasis_wavefunction(esys=None, which=n).amplitudes.reshape(self.dimension, 1)

    def __getattribute__(self, __name: str):
        r"""
        Custom ``__getattribute__`` method to get the parameters related to the internal scqObj object through self
        """
        try:
            obj = super().__getattribute__(__name)
        except AttributeError as attErr1:
            try:
                obj = getattr(self._scqObj, __name)
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
                val = getattr(self._scqObj, __name)
                obj = setattr(self._scqObj, __name, __value)
                if val != __value and __name in self._watchedProperties:
                    self._paramUpdated = True
                    self._firstTerm._paramBoundBase__matrix = None
                    if __name == 'ncut':
                        QuantumSystem.dimension.fset(self, 2*self.ncut + 1)
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
    def find_EJ_EC(omega01, alpha):
        """
        Computes and returns approximated values of EJ and EC for a transmon given
        gap omega01 and anharmonicity
        """
        def budget(x):
            tmon = Transmon(EJ=x[0], EC=x[1], ng=0, ncut=30)
            return [tmon.E01() - omega01, alpha - tmon.anharmonicity()]
        
        if omega01 < 0 or alpha > 0 or abs(alpha) > abs(omega01):
            raise ValueError(f'Invalid transmon properties omega01={omega01}, anharmonicity={alpha}')

        EJ = (omega01 + (-alpha))**2 / (8*(-alpha))
        EC = np.abs(alpha)

        x = scipy.optimize.fsolve(budget, [EJ, EC])

        return x[0], x[1]
    
class scqTunableTransmon(scqTransmon):
    
    instances = 0
    label = 'scqTunableTransmon'
    scqType = TunableTransmon

    __slots__ = []
