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

    __slots__ = ['timeDependency', '__frequency', '__order', '__operator']

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
        self._named__setKwargs(**kwargs) # pylint: disable=no-member

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
        checkCorType(frequency, (int, float, complex), 'frequency of a term')
        self.superSys = qSystems
        # if isinstance(qSystems, (list, tuple)):
        #     checkCorType(operators, (list, tuple), 'operator/s of a term with multiple system (i.e. a coupling term)')
        #     orders = [1 for _ in operators] if orders is None else orders
        #     checkCorType(orders, (list, tuple), 'operator/s of a term with multiple system (i.e. a coupling term)')
        #     checkVal(len(operators), len(qSystems), f'Number of operators ({len(operators)}) should be the same as'+
        #                                             f' number of qSystem ({len(qSystems)})')
        #     checkVal(len(orders), len(operators), f'Number of orders ({len(orders)}) should be the same as'+
        #                                           f' number of qSystem ({len(operators)})')
        #     for ind, qsys in enumerate(qSystems):
        #         self.addSubSys(QTerm(superSys=self.getByNameOrAlias(qsys), operator=operators[ind], order=[ind],
        #                              _internal='True'))
        self.operator = operators
        self.order = orders
        self.frequency = frequency

    def _checkAndUpdateParamsWhenMultiple(self, vals, attrName, attrPrintName):
        checkNotVal(self.superSys, None, "qSystems/superSys of a term should be assigned before the operators and/or"+
                                         "order of the term")
        if isinstance(vals, (list, tuple)):
            checkCorType(self.superSys, (list, tuple), f'{attrPrintName} is given a list of values, but the'+
                                                        ' qSystems/superSys is not a list of systems.')
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
        self._checkAndUpdateParamsWhenMultiple(ordVal, '_QTerm__order', 'order')

    @property
    def frequency(self):
        r"""
        Sets and gets the frequency of the term.
        """
        return self._QTerm__frequency

    @frequency.setter
    def frequency(self, freq):
        checkCorType(freq, (int, float, complex), 'frequency of a term')
        setAttr(self, '_QTerm__frequency', 0 if freq == 0.0 else freq)
