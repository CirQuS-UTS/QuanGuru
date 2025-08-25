import scqubits as scq
from ..QSys import qSystem
from numpy import abs, diag, ones
from scipy.sparse import csc_matrix


class scQubit(qSystem):
#FIXME the dimension < _maxDim condition in the __init__ function

    instances = 0
    label = 'scQubit'
    scqType = None

    __slots__ = ['scqObj']

    def __init__(self, **kwargs):
        super().__init__(terms=kwargs.pop('terms', None), subSys=kwargs.pop('subSys', None))

        # instantiating the scqObj
        scqAttrs = self.scqType.default_params()
        scqAttrs.update({key: kwargs[key] for key in kwargs if key in scqAttrs})

        self.scqObj = self.scqType(**scqAttrs)

        # @property
        # def groundedHamiltonian(self):
        #     """Get the groundedHamiltonian flag"""
        #     return getattr(self.scqObj, 'groundedHamiltonian', False)

        # @groundedHamiltonian.setter
        # def groundedHamiltonian(self, value):
        #     """Set the groundedHamiltonian flag"""
        #     self.scqObj.groundedHamiltonian = value
        #     self._udpateScqHam()

        # handle the dimension
        # kwargs['dimension'] = kwargs.get('dimension', self._max_dim)
        # if kwargs['dimension'] > (self._max_dim):
        #     raise ValueError('\'dimension\' must be less than or equal to than (' + self._max_dim_label + ')')

        #setting the frequency (can be overwritten by the user)
        self.frequency = 1

        #setting the truncated dimension
        self.dimension = self.scqObj.truncated_dim

        #defining the attributes inherited from parent classes
        remaining_kwargs = {key: kwargs[key] for key in kwargs if key not in scqAttrs}
        for key, value in remaining_kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value) # pylint: disable=no-member
        # self._qUniversal__setKwargs(**{key: kwargs[key] for key in kwargs if key not in scqAttrs}) # pylint: disable=no-member
        self.operator = self.scqHamiltonian



    def scqHamiltonian(self, energy_esys=True):
        # #retrieving the hamiltonian in eigenstate basis
        # ham = self.scqObj.matrixelement_table('hamiltonian', evals_count=dimension)

        # # setting small elements to zero such that using a sparse matrix is justifiable
        # ham[abs(ham) < 10e-15] = 0

        # return csc_matrix(ham)

        r"""This method returns the qubit Hamiltonian
        
        Parameters:
        -----------
        energy_esys : bool, optional
            If False: return in charge basis 
            Else: return in energy eigenbasis 
        """
        if energy_esys is False:
            return self.scqObj.hamiltonian(energy_esys=False)
        else: 
            return self.scqObj.hamiltonian(energy_esys=True)  # charge basis
        

    def _udpateScqHam(self):
        self._paramUpdated = True
        self.firstTerm._paramBoundBase__matrix = None

    #abstract method
    @property
    def _max_dim(self):
        pass  
    
class scqTransmon(scQubit):
#FIXME ncut and dimension error checking

    instances = 0
    label = 'scqTransmon'
    _max_dim_label = '2*ncut + 1'
    scqType = scq.Transmon

    __slots__ = []
      
    @property
    def _max_dim(self):
        return self.scqObj.ncut*2+1
    
    @property
    def EJ(self):
        return self.scqObj.EJ

    @EJ.setter
    def EJ(self, EJ):
        self.scqObj.EJ = EJ
        self._udpateScqHam()

    @property
    def EC(self):
        return self.scqObj.EC

    @EC.setter
    def EC(self, EC):
        self.scqObj.EC = EC
        self._udpateScqHam()

    @property
    def ng(self):
        return self.scqObj.ng

    @ng.setter
    def ng(self, ng):
        self.scqObj.ng = ng
        self._udpateScqHam()

    @property
    def ncut(self):
        return self.scqObj.ncut

    # add a setter for self.dimension to ensure that (2*ncut + 1) > dimension
    @ncut.setter
    def ncut(self, ncut):
        # if (2*ncut + 1) < self.dimension:
        #     raise ValueError('(2*ncut + 1) must be greater than or equal to than \'dimension\'. Try changing dimension first')
        self.scqObj.ncut = ncut
        self._udpateScqHam()

    @scQubit.dimension.setter
    def dimension(self, dim):
        # if (2*self.ncut + 1) < dim:
        #     raise ValueError('(2*ncut + 1) must be greater than or equal to than \'dimension\'. Try changing dimension first')
        scQubit.dimension.fset(self, dim)
        
    def scqNOperator(self, energy_esys=None):
        r"""This method returns the charge operator matrix
        
        Parameters:
        -----------
        energy_esys : bool, optional
            If False: return in chrage basis 
            Else: return in energy eigenbasis 
        """
        if energy_esys is False:
            return self.scqObj.n_operator(energy_esys=False)
        else: 
            return self.scqObj.n_operator(energy_esys=True)  # charge basis




class scqTunableTransmon(scqTransmon):
    
    instances = 0
    label = 'scqTunableTransmon'
    scqType = scq.TunableTransmon

    __slots__ = []

    @property
    def EJmax(self):
        return self.scqObj.EJmax

    @EJmax.setter
    def EJmax(self, EJmax):
        self.scqObj.EJmax = EJmax
        self._udpateScqHam()

    @property
    def d(self):
        return self.scqObj.d

    @d.setter
    def d(self, d):
        self.scqObj.d = d
        self._udpateScqHam()

    @property
    def flux(self):
        return self.scqObj.flux

    @flux.setter
    def flux(self, flux):
        self.scqObj.flux = flux
        self._udpateScqHam()

    # Override EJ property since it's calculated differently for tunable transmon
    @property
    def EJ(self):
        return self.scqObj.EJ

    # Remove the inherited EJ setter since EJ is calculated from EJmax, d, and flux
    @scqTransmon.EJ.deleter
    def EJ(self):
        pass  # EJ is read-only for tunable transmon
