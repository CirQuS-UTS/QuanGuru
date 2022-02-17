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

    __slots__ = ['timeDependency', '_timeDepSys', '__frequency', '__order', '__operator', '__HamiltonianTerm']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        checkNotVal((("qSystems" in kwargs) and ("superSys" in kwargs)), True,
                    "qSystems is another name for superSys, and both of them are given. Use only one of them")
        supSys = kwargs.pop('qSystems', None)
        supSys = kwargs.pop('superSys', None) if supSys is None else supSys
        if supSys is not None:
            self.superSys = supSys
        #: frequency of the term, it is is the coupling strength in the case of coupling term
        self.__frequency = None
        #: operator for the term
        self.__operator = None
        #: the order/power for the operator of the term. The operator is raised to the power in this value
        self.__order = 1
        #: used for storing the matrix corresponding to this term
        self.__HamiltonianTerm = None
        #: function that can be assigned by the user to update the parameters a function of time. The library passes the
        #: current time to this function
        self.timeDependency = None
        #: system to get the time information if time is None in _timeDependency
        self._timeDepSys = None
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

    def _timeDependency(self, time=None):
        r"""
        Internal method that passes the current time to ``timeDependency`` method that needs to be defined by the user
        to update the relevant parameters (such as frequency of the term) as a function of time.
        """
        if ((time is None) and (hasattr(self._timeDepSys, 'simulation'))):
            time = self._timeDepSys.simulation._currentTime

        if callable(self.timeDependency):
            self.timeDependency(self, time) # pylint: disable=assigning-non-slot,not-callable

    @property
    def qSystems(self):
        return self.superSys

    @qSystems.setter
    def qSystems(self, supSys):
        self.superSys = supSys

    @paramBoundBase.superSys.setter
    def superSys(self, supSys):
        self._QTerm__order = 1 # pylint: disable=assigning-non-slot
        self._QTerm__operator = None # pylint: disable=assigning-non-slot
        self.resetSubSys()
        if isinstance(supSys, (list, tuple)):
            supSys = [self.getByNameOrAlias(qsys) for qsys in supSys]
            for qsys in supSys:
                self.addSubSys(QTerm(superSys=qsys, _internal=True))
        else:
            supSys = self.getByNameOrAlias(supSys)
        setAttr(self, '_qBase__superSys', supSys)

    def _createTerm(self, qSystems, operators, orders=None, frequency=None):
        self.superSys = qSystems
        self.operator = operators
        self.order = [1 for _ in qSystems] if (isinstance(qSystems, (list, tuple)) and (orders is None)) else orders
        self.frequency = frequency

    def _checkAndUpdateParamsWhenMultiple(self, vals, attrName, attrPrintName):
        checkNotVal(self.superSys, None, "qSystems/superSys of a term should be assigned before the operators and/or"+
                                         "order of the term")
        if (isinstance(vals, (list, tuple)) or isinstance(self.superSys, (list, tuple))):
            checkCorType(self.superSys, (list, tuple), f'{attrPrintName} is given a list of values, but the'+
                                                        ' qSystems/superSys is not a list of systems.')
            checkCorType(vals, (list, tuple), f'{attrPrintName} of a term with multiple system (i.e. a coupling term)')
            checkVal(len(vals), len(self.superSys), f'Number of {attrPrintName} ({len(vals)}) should be the same as'+
                                                    f' number of qSystem ({len(self.subSys)})')
            for ind, qsys in enumerate(self.subSys.values()):
                setAttr(qsys, attrName, vals[ind])
        setAttr(self, attrName, vals)
        if self._paramUpdated:
            self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot

    @property
    def operator(self):
        r"""
        Sets and gets the operator for term.
        """
        return self._QTerm__operator

    @operator.setter
    def operator(self, op):
        self._checkAndUpdateParamsWhenMultiple(op, '_QTerm__operator', 'operator')

    @property
    def order(self):
        r"""
        Sets and gets the order of the operator of the term.
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
        Return the total Hamiltonian for this term.
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
