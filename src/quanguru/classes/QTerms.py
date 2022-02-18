from .baseClasses import paramBoundBase
from .QSimBase import setAttr
from .exceptions import checkCorType, checkVal, checkNotVal

class QTerm(paramBoundBase):
    #: (**class attribute**) class label used in default naming
    label = 'QTerm'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['timeDependency', '_timeDepSys', '__frequency', '__order', '__operator', '__HamiltonianTerm', '__qSys']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: attribute to store the quantum systems of the term. This is either a single quantum system or a list/tuple of
        #: quantum systems, and these are needed for the dimension information of the matrix creations
        self.__qSys = None
        # operator and order are also need to be list/tuple of operators and orders values, so it is required to set the
        # qSystems of the term. Here, we set the qSystems before anything else.
        qSys = kwargs.pop('qSystems', None)
        if qSys is not None:
            self.qSystems = qSys
        #: frequency of the term which needs to be a numerical value (and None by default). A numerical default could
        #: lead to mistakes, therefore it is None by default.
        self.__frequency = None
        #: operator for the term needs to be a function (pointer) and it is used for the creation of the matrix
        #: representation of the operator. The library passes the dimension information into this function and converts
        #: the returned matrix into composite operator if needed. Therefore, this function only needs to return the
        #: simple matrix (not the composite) by using the dimension information.
        self.__operator = None
        #: the order/power for the operator of the term. The operator is raised to the power in this value
        self.__order = 1
        #: used for storing the matrix corresponding to this term
        self.__HamiltonianTerm = None #pylint:disable=invalid-name
        #: function that can be assigned by the user to update the parameters a function of time. The library passes the
        #: current time to this function, and any desired parameter can be updated as a function of time.
        self.timeDependency = None
        #: system to get the time information if time is None in _timeDependency.
        self._timeDepSys = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def _timeDependency(self, time=None):
        r"""
        Internal method that passes the current time to ``timeDependency`` method that needs to be defined by the user
        to update the desired parameters (such as frequency of the term) as a function of time.
        """
        if ((time is None) and (hasattr(self._timeDepSys, 'simulation'))):
            time = self._timeDepSys.simulation._currentTime

        if callable(self.timeDependency):
            self.timeDependency(self, time) # pylint: disable=assigning-non-slot,not-callable

    @property
    def qSystems(self):
        r"""
        Property to set and get the single quantum system or a list/tuple of quantum systems that are used by the term
        for the dimension information during the matrix creations.
        Setter replaces the existing system/s with the given and also resets the order and operator values to their
        defaults (with the subSys dict which holds other terms if self has more than 1 quantum system, i.e. coupling)
        """
        return self._QTerm__qSys

    @qSystems.setter
    def qSystems(self, qSys):
        self._QTerm__order = 1 # pylint: disable=assigning-non-slot
        self._QTerm__operator = None # pylint: disable=assigning-non-slot
        self.resetSubSys()
        if isinstance(qSys, (list, tuple)):
            qSys = [self.getByNameOrAlias(qsys) for qsys in qSys]
            for qsys in qSys:
                self.addSubSys(QTerm(qSystems=qsys, _internal=True))
        else:
            qSys = self.getByNameOrAlias(qSys)
        setAttr(self, '_QTerm__qSys', qSys)

    @staticmethod
    def _createTerm(qSystems, operators, orders=None, frequency=None):
        r"""
        Factory method to create new QTerm with the given qSystems, operators, and optional orders and frequency.

        Parameters
        ----------

        qSystems :
            Single or a list/tuple of quantum systems for qSystems of the newly created QTerm
        operators :
            Single or a list/tuple of operators (same number as qSystems) for the newly created QTerm
        orders :
            Single or a list/tuple of order values for each operator (same number as operators) for the newly created
            QTerm, default is 1 for each operator.
        frequency :
            Frequency of the newly created QTerm

        Returns
        -------
        QTerm
            Newly created QTerm object

        """
        newSys = QTerm()
        newSys.qSystems = qSystems
        newSys.operator = operators
        newSys.order = [1 for _ in qSystems] if (isinstance(qSystems, (list, tuple)) and (orders is None)) else orders
        newSys.frequency = frequency
        return newSys

    def _checkAndUpdateParamsWhenMultiple(self, vals, attrName, attrPrintName):
        r"""
        This is used internally when setting the operator and/or order of the term to ensure that the number of the
        operator and order are the same as qSystems.
        Before updating the value of operator and/or order, it makes couple of checks that raise errors,
        if there is no qSystem and/or the number of the qSystems and the vals does not match.

        Parameters
        ----------

        vals :
            New value of the attribute
        attrName : str
            Name of the attribute whose value is going to be changed.
        attrPrintName : str
            Simplified name of the attribute to use with the error messages of the checks to avoid printing the
            name-mangled attribute names

        """
        checkNotVal(self.qSystems, None, "qSystems of a term should be assigned before the operators and/or"+
                                         "order of the term")
        if (isinstance(vals, (list, tuple)) or isinstance(self.qSystems, (list, tuple))):
            checkCorType(self.qSystems, (list, tuple), f'{attrPrintName} is given a list of values, but the'+
                                                        ' qSystems is not a list of systems.')
            checkCorType(vals, (list, tuple), f'{attrPrintName} of a term with multiple system (i.e. a coupling term)')
            checkVal(len(vals), len(self.qSystems), f'Number of {attrPrintName} ({len(vals)}) should be the same as'+
                                                    f' number of qSystem ({len(self.subSys)})')
            for ind, qsys in enumerate(self.subSys.values()):
                setAttr(qsys, attrName, vals[ind])
        setAttr(self, attrName, vals)
        if self._paramUpdated:
            self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot

    @property
    def operator(self):
        r"""
        Sets and gets the operator/s of the term.
        """
        return self._QTerm__operator

    @operator.setter
    def operator(self, op):
        self._checkAndUpdateParamsWhenMultiple(op, '_QTerm__operator', 'operator')

    @property
    def order(self):
        r"""
        Sets and gets the order/s of the operator/s of the term.
        """
        return self._QTerm__order

    @order.setter
    def order(self, ordVal):
        self._checkAndUpdateParamsWhenMultiple(ordVal if ordVal is not None else 1, '_QTerm__order', 'order')

    @property
    def frequency(self):
        r"""
        Sets and gets the frequency of the term.
        """
        return self._QTerm__frequency

    @frequency.setter
    def frequency(self, freq):
        checkCorType(freq, (int, float, complex, type(None)), 'frequency of a term')
        setAttr(self, '_QTerm__frequency', 0 if freq == 0.0 else freq)

    def _constructMatrices(self):
        r"""
        The matrices for the operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        return self

    @property
    def totalHamiltonian(self):
        r"""
        Return the total Hamiltonian (ie frequency*operator) for this term.
        """
        if ((self._QTerm__HamiltonianTerm is None) or (self._paramUpdated)):
            self._QTerm__HamiltonianTerm = self.frequency*self._freeMatrix #pylint:disable=assigning-non-slot
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._QTerm__HamiltonianTerm

    @property
    def _freeMatrix(self):
        r"""
        Gets and sets the free matrix, ie without the frequency (or, equivalently frequency=1) of the term.
        """
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
            self._freeMatrix = None
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @_freeMatrix.setter
    def _freeMatrix(self, qMat):
        if qMat is not None:
            self._paramBoundBase__matrix = qMat # pylint: disable=no-member, assigning-non-slot
        else:
            self._constructMatrices()
