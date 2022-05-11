"""
    Contains the QuantumSystem class used for quantum systems

    .. currentmodule:: quanguru.classes.QSystem

    .. autosummary::

        QuantumSystem

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `QuantumSystem`            |w| |w| |w| |c|       |w| |w| |c|        |w| |w| |c|
    =======================    ==================    ================   ===============

"""

import warnings
from typing import Any
from numpy import ndarray
from scipy.sparse import spmatrix

from .base import addDecorator, _recurseIfList, aliasDict
from .QSimComp import QSimComp
from .QPro import freeEvolution
from .QSimBase import setAttr
from .QTerms import QTerm
from .exceptions import checkVal, checkNotVal, checkCorType

from ..QuantumToolbox.linearAlgebra import tensorProd #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox.states import superPos #pylint: disable=relative-beyond-top-level
from ..QuantumToolbox.operators import number, Jz, sigmam, sigmap, sigmax, sigmay, sigmaz

def _initStDec(_createInitialState):
    r"""
    Decorater to handle different inputs for initial state creation.
    """
    def wrapper(obj, inp=None):
        # if the given input is a state with consistent shape, simply returns it back
        # if the shape is inconsistent raises an error
        if isinstance(inp, (ndarray, spmatrix)):
            checkVal(inp.shape[0], obj.dimension, 'Dimension mismatch with the initial state input and the dimesion of'+
                                                   ' the system')
            state = inp
        else:
            # if the input is None, tries using the initialStateInput of the simulation object
            # this is introduced as convenience so that we can call the _createInitialState without any argument
            # and it will use the input set through the initial state setter
            if inp is None:
                inp = obj.simulation._stateBase__initialStateInput.value
            state = _createInitialState(obj, inp)
        return state
    return wrapper

class QuantumSystem(QSimComp): # pylint:disable=too-many-instance-attributes
    r"""
    Class for quantum systems, both for single and composite systems, which can also be nested.
    """
    #: (**class attribute**) class label used in default naming
    label = 'QuantumSystem'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__terms', '__dimension', '__firstTerm', '__compSys', '__dimsBefore', '__dimsAfter', '_inpCoef',
                 '__unitary']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: First term is also stored in __firstTerm attribute
        self.__firstTerm = None
        #: dictionary of the terms
        self.__terms = aliasDict()
        #: dimension of Hilbert space of the quantum system
        self.__dimension = 1
        #: boolean flag for composite/single systems
        self.__compSys = None
        #: Total dimension of the other quantum systems **before** ``self`` in a composite system.
        #: It is 1, when ``self``` is the first system in the composite system or ``self`` is not in a composite system.
        self.__dimsBefore = 1
        #: Total dimension of the other quantum systems **after** ``self`` in a composite system.
        #: It is 1, when ``self`` is the last system in the composite system.
        self.__dimsAfter = 1
        #: boolean to determine whether initialState inputs contains complex coefficients (the probability amplitudes)
        #: or the populations
        self._inpCoef = kwargs.pop("_inpCoef", False)
        #: an internal :class:`~freeEvolution` protocol, this is the default evolution when a simulation is run.
        self.__unitary = freeEvolution(_internal=True)
        self._QuantumSystem__unitary.superSys = self # pylint: disable=no-member
        self._QSimComp__simulation.addQSystems(subS=self, Protocol=self._freeEvol) # pylint: disable=no-member
        self._named__setKwargs(**kwargs) # pylint:disable=no-member

    # matrices
    def _constructMatrices(self):
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        noSubSys = (len(self.subSys) == 0)
        noTerms = (len(self.terms) == 0)
        selfComp = self._isComposite
        if (noSubSys and noTerms):
            if selfComp is False:
                warnings.warn(f'{self.name} is given a dimension ({self.dimension}), but it is not given any term/s.'+\
                               'If it is intentional, please ignore this')
            else:
                warnings.warn(f'{self.name} is not given any sub-system/s or any term/s.' + \
                               'If it is intentional, please ignore this')

        for sys in self.subSys.values():
            sys._constructMatrices() # pylint: disable=protected-access
        for ter in self.terms.values():
            ter._constructMatrices() # pylint: disable=protected-access

    def _timeDependency(self, time=None):
        r"""
        An internal method used to pass down the current time in evolution to all the ``subSys`` and ``terms``. The term
        objects timeDependency functions are used for updating relevant parameters as a function of time.
        """
        if time is None:
            time = self.simulation._currentTime
        for sys in self.subSys.values():
            sys._timeDependency(time)
        for ter in self.terms.values():
            ter._timeDependency(time)
        return time

    @_initStDec
    def _createInitialState(self, inp=None):
        r"""
        Method that creates a state from the given input, which is handeled by the _initStDec decorator for different
        input cases.
        """
        if self._isComposite:
            inp = [qsys._initialStateInput for qsys in self.subSys.values()] if inp is None else inp
            subSysStates = [qsys._createInitialState(inp[ind]) for ind, qsys in enumerate(self.subSys.values())]  # pylint: disable=protected-access
            initialState = tensorProd(*subSysStates)
        else:
            checkNotVal(inp, None, self.name + ' is not given an initial state')
            initialState = superPos(self.dimension, inp, not self._inpCoef)
        return initialState

    @QSimComp.initialState.setter # pylint: disable=no-member
    def initialState(self, inp):
        r"""
        Sets the initial state from a given input ``inp``.
        """
        checkNotVal(self._QuantumSystem__compSys,None,f'Type of {self.name} is ambiguous. Single and composite systems'+
                                                   ' handle initial state inputs differently, so you need to set other'+
                                                   f' relevant parameters to determine the type of {self.name}')
        if self.superSys is not None:
            self.superSys.simulation._stateBase__initialState.value = None # breaks the bound to the other _parameter

        if self._isComposite:
            if not isinstance(inp, (ndarray, spmatrix)):
                checkCorType(inp, (list, tuple), 'Composite state initial state input')
                checkVal(len(inp), len(self.subSys),f'Number of inputs ({len(inp)}) to initial state should be the'+
                                                   f' same as number of sub-system ({len(self.subSys)}) of {self.name}')
                for ind, qsys in enumerate(self.subSys.values()):
                    qsys.initialState = inp[ind]
        self.simulation.initialState = inp # pylint: disable=no-member, protected-access

    @property
    def _subSysHamiltonian(self):
        r"""
        returns the sum of sub-system Hamiltonian
        """
        return sum([val.totalHamiltonian for val in self.subSys.values()])

    @property
    def totalHamiltonian(self): # pylint: disable=invalid-overridden-method
        r"""
        returns the total Hamiltonian of ``self`` including the coupling terms.
        """
        if ((self._paramUpdated) or (self._paramBoundBase__matrix is None)): # pylint: disable=no-member
            self._paramBoundBase__matrix = self._subSysHamiltonian + self._termHamiltonian # pylint: disable=assigning-non-slot
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member, assigning-non-slot

    @property
    def _termHamiltonian(self):
        r"""
        returns the sum of term Hamiltonian
        """
        return sum([val.totalHamiltonian for val in self.terms.values() if val.operator is not None])

    # dimension methods and properties
    @property
    def _totalDim(self):
        r"""
        :attr:`QuantumSystem.dimension` returns the dimension of a quantum system itself, meaning it does not contain
        dimensions of the other systems if ``self`` is in a composite system, ``_totalDim`` returns the total dimension
        by also taking the dimensions before and after ``self`` in a composte system.
        """
        return self.dimension * self._dimsBefore * self._dimsAfter#pylint:disable=E1101

    @property
    def dimension(self):
        r"""
        Property to get the dimension of any quantum system and also to set the dimension of single quantum systems.
        It calculates the dimension of a composite system on every call.
        For composite systems, setter raises a warning. For single system, setter also calls _updateDimension on its
        `superSys` (if there is one).
        """
        if self._isComposite: # pylint:disable=no-member
            self._QuantumSystem__dimension = 1 # pylint:disable=assigning-non-slot
            for su in self.subSys.values():
                self._QuantumSystem__dimension *= su.dimension # pylint:disable=assigning-non-slot,no-member
        return self._QuantumSystem__dimension # pylint:disable=no-member

    @dimension.setter
    def dimension(self, dim):
        if self._QuantumSystem__compSys is None: # pylint:disable=no-member
            self._QuantumSystem__compSys = bool(len(self.subSys)) # pylint:disable=assigning-non-slot

        if not self._isComposite: # pylint:disable=no-member
            checkCorType(dim, int, "dimension of a QuantumSystem has to be an integer")
            checkVal(dim>0, True, "dimension of a QuantumSystem has to be larger than 0")
            isPauli = any(term.operator in [sigmam, sigmap, sigmax, sigmay, sigmaz] for term in self.terms.values())
            checkVal(not (isPauli and (dim!=2)), True,
                     f'given dimension for quantum system ({self.name}) is {dim} but it has Pauli as term')
            oldVal = getattr(self, '_QuantumSystem__dimension')
            setAttr(self, '_QuantumSystem__dimension', dim)
            if self._paramUpdated:
                self.delMatrices(_exclude=[])
                if self.superSys is not None:# to change dimsBefore/After of other systems if self in subSys of superSys
                    self.superSys._updateDimension(self, dim, oldVal) # pylint:disable=protected-access
        else:
            warnings.warn(self.name + ' is a composite system, cannot set dimension')

    @property
    def subSysDimensions(self):
        r"""
        Returns a (nested) list of dimensions of the quantum systems contained in ``self``, if self is composite, else
        returns self.dimension.
        """
        return [sys.subSysDimensions for sys in self.subSys.values()] if self._isComposite else self.dimension

    def _updateDimension(self, subSys, newDim, oldDim):
        r"""
        Internal method to update dimension before/after information of the sub-systems when the dimension of a
        sub-system is updated. It is called in the dimension setter.

        Parameters
        ----------

        subSys :
            The sub-system whose dimension is being updated.
        newDim : int
            The new dimension of the subSys
        oldDim : int
            The old dimension of the subSys

        """
        self.delMatrices(_exclude=[])
        for qsys in self.subSys.values():#update dimsBefore/After of other sub-system by comparing their ind with subSys
            if qsys.ind < subSys.ind:
                qsys._dimsAfter = int((qsys._dimsAfter*newDim)/oldDim)
            if qsys.ind > subSys.ind:
                qsys._dimsBefore = int((qsys._dimsBefore*newDim)/oldDim)
        if self.superSys is not None: # for nested structures, we still need to call _updateDimension on self.superSys
            self.superSys._updateDimension(self, newDim, oldDim) # pylint:disable=protected-access

    def __dimsABUpdate(self, attrName, val):
        r"""
        Common parts of the dimsBefore/After setters are combined in this method.

        Parameters
        ----------

        attrName : str
            _dimsBefore/After as a string to be used with setAttr&setattr
        val : int
            new value of _dimsBefore/After

        """
        oldVal = getattr(self, attrName)
        setAttr(self, '_QuantumSystem_'+attrName, val)
        for qsys in self.subSys.values():
            setattr(qsys, attrName, int((getattr(qsys, attrName)*val)/oldVal))

    @property
    def _dimsBefore(self):
        r"""
        Property to set and get the :attr:`~QuantumSystem.__dimsBefore`. Getter can be used to get information, but the
        setter is intended purely for internal use.
        """
        return self._QuantumSystem__dimsBefore

    @_dimsBefore.setter
    def _dimsBefore(self, val):
        self._QuantumSystem__dimsABUpdate('_dimsBefore', val)

    @property
    def _dimsAfter(self):
        r"""
        Property to set and get the :attr:`~QuantumSystem.__dimsAfter`. Getter can be used to get information, but the
        setter is intended purely for internal use.
        """
        return self._QuantumSystem__dimsAfter

    @_dimsAfter.setter
    def _dimsAfter(self, val):
        self._QuantumSystem__dimsABUpdate('_dimsAfter', val)

    @property
    def _isComposite(self):
        r"""
        Used internally to set _QuantumSystem__compSys boolean, never query this before _QuantumSystem__compSys is set
        by some internal call. Otherwise, this will always return False (because subSys dict is always empty initially)
        """
        if self._QuantumSystem__compSys is None:
            warnings.warn(f'{self.name} type (whether it is a single or composite system) is ambiguous'+\
                           'If it is intentional, please ignore this')
        return self._QuantumSystem__compSys # pylint:disable=no-member

    def _hasInSubs(self, other):
        r"""
        Returns True if the given system is in self.subSys or in any other subSys nested inside the self.subSys
        """
        return (other in self.subSys.values() or any(qs._hasInSubs(other) for qs in self.subSys.values())) # pylint:disable=protected-access

    # sub-system methods and properties
    @property
    def ind(self):
        r"""
        If ``self`` is in a composite quantum system, this return an index representing the position of ``self`` in the
        composite system, else it returns 0.
        Also, the first system in a composite quantum system is at index 0.
        This is mainly used for _updateDimension where we compare the position of a sub-system against the others to
        determine whether _dimsBefore/After needs to be updated.
        """
        ind = 0
        if self.superSys is not None:
            ind += list(self.superSys.subSys.values()).index(self)
        return ind

    def __addSub(self, subSys):
        r"""
        internal method used to update relevant information (such as dimension before/after) for the existing and newly
        added sub-systems. This is purely for internal use.
        """
        for subS in self.subSys.values():
            subS._dimsAfter *= subSys.dimension
            subSys._dimsBefore *= subS.dimension
        return subSys

    @addDecorator
    def addSubSys(self, subSys, **kwargs):
        r"""
        Extends the addSubSys method for composite quantum systems to set the __compSys boolean (to True, if None),
        update the dimsBefore/After of the sub-systems, set self as superSys of the sub-system, and set _paramUpdated to
        True, or it raises a TypeError if __compSys is already set to False.
        Also, it places self into the _paramBoundBase__paramBound dictionary of the sub-system, so that parameter
        updates of the sub-system also sets the _paramUpdated of self to True.
        Note that composite systems can contain other composite systems as sub-systems.
        """
        if self._QuantumSystem__compSys is None: # pylint:disable=no-member
            self._QuantumSystem__compSys = True # pylint:disable=assigning-non-slot
        elif self._QuantumSystem__compSys is False: # pylint:disable=no-member
            raise TypeError("Cannot add a sub-system to a single quantum system " + self.name)

        if subSys not in self.subSys.values():
            self._QuantumSystem__addSub(subSys)
        subSys.superSys = self
        self._paramUpdated = True
        subSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        super().addSubSys(subSys, **kwargs)
        self.delMatrices(_exclude=[])
        return subSys

    def delMatrices(self, _exclude=[]): # pylint: disable=dangerous-default-value
        r"""
        This method extends :meth:`delMatrices <QSimComp.delMatrices>` of :class:`QSimComp` to also call
        :meth:`delMatrices <paramBoundBase.delMatrices>` on terms.
        """
        super().delMatrices(_exclude=_exclude)
        for ter in self.terms.values():
            _exclude = ter.delMatrices(_exclude=_exclude)
        return _exclude

    def __add__(self, other):
        r"""
        overload the + operator to create a composite quantum system between ``self`` and the ``other`` quantum system.
        """
        other = self.getByNameOrAlias(other)
        checkCorType(other, QuantumSystem, "{other} is not an instance of QuantumSystem")
        if ((self._QuantumSystem__compSys in (True, None)) and (not other._isComposite)):
            self.addSubSys(other.copy() if (other is self) else other)
            newComp = self
        elif ((self._QuantumSystem__compSys is None) and other._QuantumSystem__compSys):
            newComp = other
        elif self._QuantumSystem__compSys is other._QuantumSystem__compSys:
            newComp = QuantumSystem(subSys=[self, other.copy() if (other is self) else other])
            # TODO copy the simulation parameters, and what to do with compute and calculate?
        elif ((not self._isComposite) and (other._isComposite)):
            other.addSubSys(self)
            newComp = other
        return newComp

    def __sub__(self, other):
        r"""
        overload the ``-`` operator to remove the ``other`` from ``self``, which should be the composite quantum system
        containing/connected-to the other.
        """
        self._removeSubSysExc(other, _exclude=[])
        return self

    @_recurseIfList
    def _removeSubSysExc(self, subSys: Any, _exclude=[]) -> None: # pylint:disable=dangerous-default-value
        r"""
            Method to remove a given subSys (which might be a single or composite system) from a composite system, which
            might be self or any other composite system in the nested-system structure.
            This method traverses through the nested-structure to find the subSys (that will be removed) and uses
            _exclude to avoid infinite loops, that, for example, might be created when a system calls _removeSubSysExc
            on its superSys which calls _removeSubSysExc on its subSys, by calling _removeSubSysExc on self if self is
            not in _exclude.
            Since _exclude needs to be empty in each call, this method should not be called directly, removeSubSys is a
            wrapper around this and always calls this with an empty _exclude.
            Raises an error if removeSubSys is called on a single system.
            This method also updates the dimsBefore/After of the remaining sub-systems (and the removed system), deletes
            the existing matrices so that they are re-created with the proper dimensions.
            When removing a single system, it sets the dimension of the single system to 1, so that all the
            dimsBefore/After information are updated by the dimensionUpdate method.
            However, we might still need the removed system, so its dimension is stored (in oldDim) and set back again
            (into _QuantumSystem__dimension) after its removed.
            When removing a composite system, it makes _removeSubSysExc to each sub-system of the removed composite
            system, and these nested calls sets the dimensions of all the single systems below the removed composite to
            1 so that the dimsBefore/After information are again updated by the dimensionUpdate method.
            However, the removed composite system might still be needed, and we might not want these dimensions to be 1
            or these single systems to be removed from the removed composite system.
            These are avoided by storing&setting the dimensions back to their original values for single systems and
            adding the removed sub-systems of removed composite systems back in.
        """
        checkNotVal(self._isComposite, False,
                    f"{self.name} is not a composite. removeSubSys cannot be called on single systems")
        subSys = self.getByNameOrAlias(subSys)
        if subSys in self.subSys.values():
            _exclude.append(self)
            if subSys._isComposite: # pylint:disable=protected-access
                # need to create this for two reasons
                # 1. because subSys.subSys changes its size due to _removeSubSysExc calls
                # 2. we add these systems back again after removal
                qsysList = list(subSys.subSys.values())
                for qsys in qsysList:
                    subSys._removeSubSysExc(qsys, _exclude=_exclude)#pylint:disable=protected-access
                super()._removeSubSysExc(subSys, _exclude=_exclude)
                # add the sub-systems of subSys back again
                subSys.addSubSys(qsysList)
            else:
                oldDim = subSys.dimension
                subSys.dimension = 1
                super()._removeSubSysExc(subSys, _exclude=_exclude)
                setAttr(self, '_QuantumSystem__dimension', oldDim)
            subSys.superSys = None
            subSys._dimsAfter = 1
            subSys._dimsBefore = 1
            subSys.delMatrices(_exclude=[])
            _exclude.append(subSys)
        else:
            if self not in _exclude:
                _exclude.append(self)
                for qsys in self.subSys.values():
                    if qsys._isComposite: #pylint:disable=protected-access
                        qsys._removeSubSysExc(subSys, _exclude=_exclude) #pylint:disable=protected-access
                        if subSys in _exclude:
                            break
                else:
                    if self.superSys is not None:
                        self.superSys._removeSubSysExc(subSys, _exclude=_exclude) #pylint:disable=protected-access

        if subSys is not self:
            termObjs = list(self.terms.values())
            for ter in termObjs:
                ter._removeTermIfQSysInList(self, subSys)#pylint:disable=protected-access
        self.delMatrices(_exclude=[])
        self._paramUpdated = True

    #free evolution composition and protocols
    # TODO test these with the protocol tests
    @property
    def _freeEvol(self):
        r"""
        Property to get the ``default`` internal ``freeEvolution`` proptocol.
        """
        return self._QuantumSystem__unitary

    def unitary(self):
        r"""
        Returns the unitary evolution operator for ``self``.
        """
        unitary = self._QuantumSystem__unitary.unitary()
        self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return unitary

    def addProtocol(self, protocol=None, system=None, protocolRemove=None):
        r"""
        adds the given ``protocol`` into ``self.simulation`` and uses ``self`` as ``system`` if it is not given.
        It also can removed a protocol (``protocolRemove``) at the same time.
        """
        if system is None:
            system = self
        self.simulation.addProtocol(protocol=protocol, system=system, protocolRemove=protocolRemove)

    # TODO THESE NEEDS TESTS

    def createTerm(self, operator, frequency=None, qSystem=None, order=None, superSys=None): #pylint:disable=too-many-arguments
        r"""
        Method to create a new term with the given parameters and also set the given kwargs to the new term.

        Parameters
        ----------

        operator : Callable or List[Callable]
            operator/s of the term
        frequency :
            frequency of the term, by default None
        qSystem : QuantumSystem
            quantum system/s for the given operator/s, and it is self if no system is given
        order :
            order/s of the operator/s, it is set to 1 by default if no order value is given

        Returns
        -------
        QTerm
            Newly created QTerm object

        """
        if qSystem is None:
            qSystem = self

        if isinstance(qSystem, (list, tuple)):
            checkVal(self._isComposite, True, "Cannot add a multi-operator term (ie a coupling) to a single system")
            qSystem = [self.getByNameOrAlias(qsys) for qsys in qSystem]
            for qsys in qSystem:
                checkVal(self._hasInSubs(qsys), True,
                         f"Cannot add a multi-operator term (ie a coupling) to {self.name}, because {qsys.name} is not"+
                         f"contained in the {self.name}")
        else:
            qSystem = self.getByNameOrAlias(qSystem)
        superSys = self if superSys is None else superSys
        newTerm = QTerm._createTerm(superSys=superSys, qSystem=qSystem, operator=operator, order=order,#pylint:disable=protected-access
                                    frequency=frequency)
        qObj = self if isinstance(qSystem, (list, tuple)) else qSystem
        qObj.addTerms(newTerm)
        return newTerm

    @property
    def terms(self):
        r"""
        Property to get & set the terms of the quantum system. Note that the setter is not intended for adding a new
        term, but replace the all the existing terms with the given term/s (which can be a single term or a list of
        terms, and it also works with names and/or aliases). In order to add an additional term to existing ones, use
        ``addTerm`` method.
        """
        return self._QuantumSystem__terms # pylint:disable=no-member

    @addDecorator
    def addTerms(self, trm, **kwargs):
        r"""
        Method to add an existing term to self and also optionally set some of the term parameters through the kwargs.
        """
        checkCorType(trm, QTerm, f"addTerms argument/s ({trm.name})")
        supSys = kwargs.pop('superSys', self)
        trm._named__setKwargs(**kwargs) # pylint: disable=W0212
        if len(self.terms) == 0:
            self._QuantumSystem__firstTerm = trm #pylint:disable=assigning-non-slot
        self._QuantumSystem__terms[trm.name] = trm  # pylint:disable=no-member
        self._paramUpdated = True
        trm.superSys = supSys
        trm._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access, no-member

    def _removeTermExc(self, termObj, _exclude=[]): #pylint:disable=dangerous-default-value
        r"""
        The method to find and remove the term from a quantum system.
        """
        termObj = self.getByNameOrAlias(termObj)
        checkCorType(termObj, QTerm, f"Given object {termObj.name} is not a term")
        if termObj in self.terms.values():
            _exclude.append(self)
            self.terms.pop(termObj.name)
            _exclude.append(termObj)
        else:
            if self not in _exclude:
                _exclude.append(self)
                for qsys in self.subSys.values():
                    qsys._removeTermExc(termObj, _exclude) #pylint:disable=protected-access
                    if termObj in _exclude:
                        break
                else:
                    if self.superSys is not None:
                        self.superSys._removeTermExc(termObj, _exclude) #pylint:disable=protected-access
        self.delMatrices(_exclude=[])
        self._paramUpdated = True

    @_recurseIfList
    def removeTerm(self, termObj):
        r"""
        Method to remove the given term from the quantum system. This can be called on any system in a composite system
        to remove any term, even if it belongs to another sub-system. This is intended so that the term of a subsystem
        can be removed through the composite system, especially for nested-composite systems.
        You can also give a list of terms (or their named/aliases) to be removed.
        This method is a wrapper around the actual remove method the ``_removeTermExc`` so that it is called with an
        empty _exclude list, which is used to avoid infinite recursions when finding the term inside a nested system.
        Note that it will raise an error, if the given term is the first-term if the system.
        """
        termObj = self.getByNameOrAlias(termObj)
        self._removeTermExc(termObj=termObj, _exclude=[])

    def resetTerms(self):
        r"""
        Method to delete all the existing terms by assigning a new empty dictionary.
        """
        self._QuantumSystem__terms = aliasDict() # pylint:disable=assigning-non-slot

    @terms.setter
    def terms(self, trm):
        self.resetTerms()
        self.addTerms(trm)

    @property
    def _firstTerm(self):
        r"""
        Property to get the first term of the quantum system.
        """
        if self._QuantumSystem__firstTerm is None:
            self.addTerms(QTerm(qSystem=self))
        return self._QuantumSystem__firstTerm # pylint:disable=no-member

    @property
    def frequency(self):
        r"""
        Property to get & set the frequency of the first term of the quantum system.
        """
        return self._firstTerm.frequency

    @frequency.setter
    def frequency(self, freq):
        self._firstTerm.frequency = freq

    @property
    def operator(self):
        r"""
        Property to get & set the operator of the first term of the quantum system.
        """
        return self._firstTerm.operator

    @operator.setter
    def operator(self, op):
        self._firstTerm.operator = op

    @property
    def order(self):
        r"""
        Property to get & set the order of the first term of the quantum system.
        """
        return self._firstTerm.order

    @order.setter
    def order(self, odr):
        self._firstTerm.order = odr

    @property
    def _freeMatrix(self):
        r"""
        Property to get & set the free (i.e. no frequency or, equivalently frequency=1) matrix for the first term.
        """
        return self._firstTerm._freeMatrix # pylint: disable=protected-access

    @_freeMatrix.setter
    def _freeMatrix(self, qMat):
        self._firstTerm._freeMatrix = qMat # pylint: disable=protected-access

    def copy(self, **kwargs):
        newSys = super().copy()
        for qsys in self.subSys.values():
            cqsys = qsys.copy()
            cqsys.alias = qsys.name + "_" + cqsys.name
            newSys.addSubSys(cqsys)
        subSysList = list(newSys.subSys.values())
        termsList = list(newSys.terms.values())#pylint:disable=no-member
        for ind, ter in enumerate(self.terms.values()):
            if isinstance(ter.qSystem, QuantumSystem):
                qSystemNames = newSys
            else:
                qSystemNames = []
                for qsys in ter.qSystem:
                    qSystemNames.append(qsys.name + "_" + subSysList[qsys.ind-1].name)
            if ind > len(termsList):
                newSys.createTerm(qSystem=qSystemNames, #pylint:disable=no-member
                                 operator=ter.operator,
                                 frequency=ter.frequency,
                                 order=ter.order)
            else:
                termsList[ind]._named__setKwargs(qSystem=qSystemNames, #pylint:disable=no-member
                                                 operator=ter.operator,
                                                 frequency=ter.frequency,
                                                 order=ter.order)
        if self.simulation._stateBase__initialStateInput._value is not None:
            newSys.initialState = self.simulation._stateBase__initialStateInput.value #pylint:disable=assigning-non-slot
        if not self._isComposite:
            newSys.dimension = self.dimension#pylint:disable=assigning-non-slot
            newSys._inpCoef = self._inpCoef # pylint: disable=protected-access,assigning-non-slot
        newSys._named__setKwargs(**kwargs) #pylint:disable=no-member
        return newSys

    def __rmul__(self, other):
        r"""
        With this method, ``*`` creates a composite quantum system that contains ``N=other`` many quantum systems with
        the same ``type`` as ``self``.
        """
        newComp = QuantumSystem()
        newComp.addSubSys(self)
        for _ in range(other - 1):
            newComp.addSubSys(self.copy())
        return newComp

QuantumSystem._createAstate = QuantumSystem._createInitialState # pylint:disable=protected-access

class Cavity(QuantumSystem): # pylint: disable=too-many-ancestors
    r"""
    Cavity class, the only difference from a generic quantum object is that, by default, its operator is the number
    operator.
    """
    #: (**class attribute**) class label used in default naming
    label = 'Cavity'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False), _inpCoef=kwargs.pop("_inpCoef", False))
        self._QuantumSystem__compSys = False #pylint:disable=assigning-non-slot
        self.operator = number
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

class Spin(QuantumSystem): # pylint: disable=too-many-ancestors
    r"""
    Object for a single Spin system with spin j (jValue).
    """
    #: (**class attribute**) class label used in default naming
    label = 'Spin'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__jValue']
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False), _inpCoef=kwargs.pop("_inpCoef", False))
        self._QuantumSystem__compSys = False #pylint:disable=assigning-non-slot
        #: operator for (the first term in) its Hamiltonian
        self.operator = Jz
        #: spin quantum number
        self.__jValue = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    @property
    def jValue(self):
        r"""
        Gets and sets the spin quantum number
        """
        return (self._QuantumSystem__dimension-1)/2 # pylint: disable=no-member

    @jValue.setter
    def jValue(self, value):
        self._Spin__jValue = value # pylint: disable=assigning-non-slot
        self.dimension = int((2*value) + 1)

class Qubit(Spin): # pylint: disable=too-many-ancestors
    r"""
    Spin 1/2 special case of Spin class, i.e. a Qubit.
    """
    #: (**class attribute**) class label used in default naming
    label = 'Qubit'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False), _inpCoef=kwargs.pop("_inpCoef", False))
        self._QuantumSystem__compSys = False #pylint:disable=assigning-non-slot
        kwargs['dimension'] = 2
        self.dimension  = 2
        self.operator = Jz
        self._named__setKwargs(**kwargs) # pylint: disable=no-member
