"""
    Contains classes for Quantum systems.

    .. currentmodule:: quanguru.classes.QSys

    .. autosummary::

        genericQSys
        QuantumSystem
        compQSystem
        termTimeDep
        term
        qSystem
        qCoupling
        Spin
        Qubit
        Cavity
        _initStDec
        _computeDef
        _calculateDef

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================    ================   ===============
       **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
    =======================    ==================    ================   ===============
      `genericQSys`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `QuantumSystem`            |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `compQSystem`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `termTimeDep`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `term`                     |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `qSystem`                  |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `qCoupling`                |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `Spin`                     |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `Qubit`                    |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `Cavity`                   |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_initStDec`               |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_computeDef`              |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
      `_calculateDef`            |w| |w| |w| |c|       |w| |w| |x|        |w| |w| |x|
    =======================    ==================    ================   ===============

""" #pylint: disable=too-many-lines

from collections import OrderedDict

from ..QuantumToolbox import operators as qOps #pylint: disable=relative-beyond-top-level

from .base import addDecorator, _recurseIfList
from .baseClasses import paramBoundBase
from .QSimComp import QSimComp
from .QSimBase import setAttr


def _computeDef(sys, state): # pylint: disable=unused-argument
    r"""
    Dummy compute method used when creating a copy of quantum systems.
    TODO I am not happy with this solution.
    """

def _calculateDef(sys): # pylint: disable=unused-argument
    r"""
    Dummy calculate method used when creating a copy of quantum systems.
    TODO I am not happy with this solution.
    """

class genericQSys(QSimComp):
    r"""
    Base class for both single (:class:`~qSystem`) and composite (:class:`~compQSystem`) quantum system classes, and I
    hope to combine those two classes in here. Currently, a proxy :class:`~QuantumSystem` is introduced as a
    temporary solution.
    """
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))

    def __rmul__(self, other):
        r"""
        With this method, ``*`` creates a composite quantum system that contains ``N=other`` many quantum systems with
        the same ``type`` as ``self``.
        """
        newComp = compQSystem()
        newComp.addSubSys(self)
        for _ in range(other - 1):
            newComp.addSubSys(self.copy())
        return newComp

    def copy(self, **kwargs): # pylint: disable=arguments-differ
        r"""
        Create a copy of ``self`` and also change the parameter of the newly created copy with ``kwargs``.
        """
        subSysList = []
        for sys in self.subSys.values():
            subSysList.append(sys.copy())

        if isinstance(self, qSystem):
            newSys = super().copy(dimension=self.dimension, terms=subSysList)
        elif isinstance(self, compQSystem):
            newSys = super().copy()
            for sys in subSysList:
                newSys.addSubSys(sys)

        if self.simulation._stateBase__initialStateInput._value is not None:
            newSys.initialState = self.simulation._stateBase__initialStateInput.value #pylint:disable=assigning-non-slot
        newSys._named__setKwargs(**kwargs) #pylint:disable=no-member
        return newSys

    def _timeDependency(self, time=None):
        r"""
        Passes down the current time in evolution to all the ``subSys``, which eventually are either ``term`` or
        ``qCoupling`` objects that are child classes of ``termTimeDep``, which updates the ``frequency`` of the
        corresponding coupling or term using the ``timeDependency`` method created and given by the user.
        TODO Create a demo and hyperlink here.
        """
        if time is None:
            time = self.simulation._currentTime
        for sys in self.subSys.values():
            sys._timeDependency(time)
        return time

class compQSystem(genericQSys):
    __slots__ = ['__qCouplings']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: an ordered dictionary for the coupling terms
        self.__qCouplings = OrderedDict()

    def _timeDependency(self, time=None):
        r"""
        Passes down the current time in evolution to all the ``subSys``, which eventually are either ``term`` or
        ``qCoupling`` objects that are child classes of ``termTimeDep``, which updates the ``frequency`` of the
        corresponding coupling or term using the ``timeDependency`` method created and given by the user.
        TODO Create a demo and hyperlink here.
        """
        time = super()._timeDependency(time=time)
        for coupling in self.qCouplings.values():
            coupling._timeDependency(time)

    @property
    def qCouplings(self):
        r"""
        returns the ordered dictionary of coupling terms.
        """
        return self._compQSystem__qCouplings

    def __addCoupling(self, couplingObj):
        r"""
        Internal method used when adding a coupling term.
        """
        self._compQSystem__qCouplings[couplingObj.name] = couplingObj
        couplingObj.superSys = self
        return couplingObj

    def createSysCoupling(self, *args, **kwargs):
        r"""
        Creates a coupling term, sets the ``kwargs`` for that coupling, and uses ``args`` for the coupling operators
        and the corresponding operators, see addTerm in qCoupling to understand how args works.
        TODO Create a tutorial and hyperlink here
        """
        newCoupling = self.addSubSys(qCoupling, **kwargs)
        newCoupling.addTerm(*args)
        return newCoupling

    def addSysCoupling(self, couplingObj):
        r"""
        Adds the given coupling term to ``self``.
        TODO Create a tutorial and hyperlink here
        """
        self.addSubSys(couplingObj)

class termTimeDep(paramBoundBase):
    r"""
    Parent class for :class:`~term` and :class:`~qCoupling` and I hope to combine those two in here.
    """

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: function that can be assigned by the user to update the parameters a function of time. The library passes the
        #: current time to this function
        self.timeDependency = None
       

    def copy(self, **kwargs):  # pylint: disable=arguments-differ
        r"""
        Create a copy ``self`` and change the values of the attributes given in ``kwargs``.
        """
        newSys = super().copy(frequency=self.frequency, operator=self.operator, order=self.order, **kwargs)
        return newSys

    def order(self, ordVal):
        if self._paramBoundBase__matrix is not None: # pylint: disable=no-member
            self.freeMat = None

    def _constructMatrices(self):
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        Currently, this is just pass and extended in the child classes, and the goal is to combine those methods in here
        """
        ...

    @property
    def totalHam(self):
        r"""
        Return the total Hamiltonian for this term.
        """
        return self.frequency*self.freeMat

    @property
    def freeMat(self):
        r"""
        Gets and sets the free matrix, ie without the frequency (or, equivalently frequency=1) of the term.
        """
        #if ((self._paramBoundBase__matrix is None) or (self._paramUpdated)): # pylint: disable=no-member
        if self._paramBoundBase__matrix is None: # pylint: disable=no-member
            self.freeMat = None
            self._paramBoundBase__paramUpdated = False # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qMat):
        if qMat is not None:
            self._paramBoundBase__matrix = qMat # pylint: disable=no-member, assigning-non-slot
        else:
            #if len(self._qBase__subSys) == 0: # pylint: disable=no-member
            #    raise ValueError('No operator is given for coupling Hamiltonian')
            #if self.operator is None:
            #    raise ValueError('No operator is given for free Hamiltonian')
            self._constructMatrices()

    def _timeDependency(self, time=None):
        r"""
        Internal method that passes the current time to ``timeDependency`` method that needs to be defined by the user
        to update the relevant parameters (such as frequency of the term) as a function of time.
        """
        if time is None:
            time = self.superSys.simulation._currentTime

        if callable(self.timeDependency):
            if hasattr(self, 'frequency'):
                self.frequency = self.timeDependency(self, time) # pylint: disable=assigning-non-slot,not-callable
            elif hasattr(self, 'couplingStrength'):
                self.couplingStrength = self.timeDependency(self, time) #pylint:disable=assigning-non-slot,not-callable

class term(termTimeDep):
    r"""
    Term object for simple (i.e. non-coupling) terms in the Hamiltonian.
    """
    #: (**class attribute**) class label used in default naming
    label = 'term'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []

    @paramBoundBase.superSys.setter
    def superSys(self, supSys):
        r"""
        Extends superSys setter to also add aliases to self.
        New aliases are (any name/alias of superSys) + Term + (number of terms)
        TODO What if there is already a superSys, and also alias list contains user given aliases as well.
        """
        paramBoundBase.superSys.fset(self, supSys) # pylint: disable=no-member
        termCount = len(self.superSys.subSys) if self in self.superSys.subSys.values() else len(self.superSys.subSys)+1 # pylint: disable=no-member,line-too-long # noqa: E501
        self.alias = [na+"Term"+str(termCount) for na in self.superSys.name._aliasClass__members()] # pylint: disable=no-member, protected-access,line-too-long # noqa: E501

    @property
    def _freeMatSimple(self):
        r"""
        Return the matrix corresponding to the operator of the term, but this method does not make it into a composite
        operator even if the term belongs to a system in a composite quantum system.
        """
        h = self._constructMatrices(dimsBefore=1, dimsAfter=1, setMat=False)
        return h

    def _constructMatrices(self, dimsBefore=None, dimsAfter=None, setMat=True): #pylint:disable=arguments-differ
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        if dimsBefore is None:
            dimsBefore = self.superSys._dimsBefore # pylint: disable=no-member

        if dimsAfter is None:
            dimsAfter = self.superSys._dimsAfter # pylint: disable=no-member

        if not (isinstance(self.superSys.dimension, (int, int64, int32, int16)) and callable(self.operator)): # pylint: disable=no-member
            raise TypeError('?')

        dimension = self.superSys._genericQSys__dimension # pylint: disable=no-member
        if self.operator in [qOps.Jz, qOps.Jy, qOps.Jx, qOps.Jm, qOps.Jp, qOps.Js]:
            dimension = 0.5*(dimension-1)

        if self.operator not in [qOps.sigmam, qOps.sigmap, qOps.sigmax, qOps.sigmay, qOps.sigmaz]:
            mat = qOps.compositeOp(self.operator(dimension), #pylint:disable=assigning-non-slot
                                   dimsBefore, dimsAfter)**self.order
        else: # pylint: disable=bare-except
            mat = qOps.compositeOp( # pylint: disable=no-member, assigning-non-slot
                self.operator(), dimsBefore, dimsAfter)**self.order

        if setMat:
            self._paramBoundBase__matrix = mat #pylint:disable=assigning-non-slot
        return mat

class qSystem(genericQSys):
    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        # TODO
        qSysKwargs = ['terms', 'subSys', 'name', 'superSys', 'dimension', 'alias']
        for key in qSysKwargs:
            val = kwargs.pop(key, None)
            if val is not None:
                setattr(self, key, val)

        if len(self.subSys) == 0:
            self.addSubSys(term(superSys=self, **kwargs))

    @property
    def _totalHamSimple(self):
        r"""
        returns the total Hamiltonian of the single quantum system, but this method does not take the dimension
        before/after into account even if ``self`` is a sub-system of a composite system.
        """
        return sum([(obj.frequency * obj._freeMatSimple) for obj in self.subSys.values()])#pylint:disable=protected-access

    @property
    def freeMat(self):
        r"""
        returns the free (i.e. no frequency or, equivalently frequency=1) matrix for the operator of the first term in
        its Hamiltonian.
        """
        return self.firstTerm.freeMat # pylint: disable=no-member

    @freeMat.setter
    def freeMat(self, qOpsFunc):
        r"""
        Setter for the freeMat. This is used internally in construct matrices methods.
        """
        if callable(qOpsFunc):
            self.firstTerm.operator = qOpsFunc
            self.firstTerm._constructMatrices() # pylint: disable=protected-access
        elif qOpsFunc is not None:
            self.firstTerm._paramBoundBase__matrix = qOpsFunc  # pylint: disable=assigning-non-slot
        else:
            if self.firstTerm.operator is None:
                raise ValueError('No operator is given for free Hamiltonian')
            self.firstTerm._constructMatrices() # pylint: disable=protected-access

    @property
    def operator(self):
        r"""
        Gets a list of the operators for the terms in its Hamiltonian, and sets the operator only for the first term.
        """
        operators = [obj._termTimeDep__operator for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return operators if len(operators) > 1 else operators[0]

    @operator.setter
    def operator(self, op):
        self.firstTerm.operator = op

    @property
    def frequency(self):
        r"""
        Setter and getter of the frequency of the first term in its Hamiltonian.
        """
        #frequencies = [obj._termTimeDep__frequency for obj in list(self.subSys.values())] # pylint: disable=protected-access
        #return frequencies if len(frequencies) > 1 else frequencies[0]
        return self.firstTerm.frequency

    @frequency.setter
    def frequency(self, freq):
        self.firstTerm.frequency = freq

    @property
    def order(self):
        r"""
        Sets and gets the order/power of the operator of the first term in its Hamiltonian.
        """
        orders = [obj._termTimeDep__order for obj in list(self.subSys.values())] # pylint: disable=protected-access
        return orders if len(orders) > 1 else orders[0]

    @order.setter
    def order(self, ordVal):
        self.firstTerm.order = ordVal

    @property
    def firstTerm(self):
        r"""
        Returns the first term in its Hamiltonian
        """
        return list(self.subSys.values())[0]

    @property
    def terms(self):
        r"""
        returns a list of the term objects used for its Hamiltonian.
        """
        qSys = list(self.subSys.values())
        return qSys if len(qSys) > 1 else qSys[0]

    @addDecorator
    def addSubSys(self, subSys, **kwargs):
        r"""
        extends the addSubSys method from the parent classes and uses it add terms to its Hamiltonian.
        """
        if not isinstance(subSys, term):
            raise TypeError('?')
        kwargs['superSys'] = self
        newS = super().addSubSys(subSys, **kwargs)
        # FIXME use setAttr, check also for operator
        self._paramUpdated = True
        newS._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return subSys

    @_recurseIfList
    def _removeSubSysExc(self, subSys, _exclude=[]): # pylint: disable=arguments-differ, dangerous-default-value
        r"""
        Method to remove a term from its Hamiltonian.
        """
        if self not in _exclude:
            _exclude.append(self)
            subSys = self.getByNameOrAlias(subSys)
            if self.superSys is not None:
                self.superSys._removeSubSysExc(subSys, _exclude=_exclude) # pylint: disable=protected-access

            if subSys in self.subSys.values():
                super()._removeSubSysExc(subSys, _exclude=_exclude)

    @terms.setter
    def terms(self, subSys):
        r"""
        add terms to its Hamiltonian with this setter.
        """
        genericQSys.subSys.fset(self, subSys) # pylint: disable=no-member
        for sys in self.subSys.values():
            sys.superSys = self

    def addTerm(self, operator, frequency=0, order=1):
        r"""
        Calls the addSubSys to add terms, this method is created to provide a more intuitive name than addSubSys
        """
        newTerm = self.addSubSys(term(operator=operator, frequency=frequency, order=order, superSys=self))
        return newTerm

    @_recurseIfList
    def removeTerm(self, termObj):
        r"""
        Calls the removeSubSys to remove terms, this method is created to provide a more intuitive name than
        removeSubSys
        """
        self._removeSubSysExc(termObj, _exclude=[])

class qCoupling(termTimeDep):
    r"""
    Class to create coupling terms between quantum systems.
    """
    #: (**class attribute**) class label used in default naming
    label = 'qCoupling'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = []

    #@qCouplingInitErrors
    def __init__(self, *args, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._named__setKwargs(**kwargs) # pylint: disable=no-member
        self.addTerm(*args)

    # TODO might define setters
    @property
    def couplingOperators(self):
        r"""
        returns a list of coupling operators stored in this coupling term
        """
        ops = []
        for co in self._qBase__subSys.values(): # pylint: disable=no-member
            ops.append(co[1])
        return ops

    @property
    def coupledSystems(self):
        r"""
        returns the list of coupled systems by this coupling term
        """
        ops = []
        for co in self._qBase__subSys.values(): # pylint: disable=no-member
            ops.append(co[0])
        return ops

    @property
    def couplingStrength(self):
        r"""
        Gets and sets the coupling strength for this coupling. This is simply an alternative terminology for frequency.
        """
        return self.frequency

    @couplingStrength.setter
    def couplingStrength(self, strength):
        self.frequency = strength

    def __coupOrdering(self, qts): # pylint: disable=no-self-use
        r"""
        method used internally to make some sorting of the operators. This is implemented so that there are some
        flexibilities for user when creating coupling.
        """
        qts = sorted(qts, key=lambda x: x[0], reverse=False)
        oper = qts[0][1]
        for ops in range(len(qts)-1):
            oper = oper @ qts[ops+1][1]
        return oper

    def _constructMatrices(self):
        r"""
        The matrices for operators constructed and de-constructed whenever they should be, and this method is used
        internally in various places when the matrices are needed to be constructed.
        """
        cMats = []
        for ind in range(len(self._qBase__subSys)): # pylint: disable=no-member
            qts = []
            for indx in range(len(list(self._qBase__subSys.values())[ind])): # pylint: disable=no-member
                sys = list(self._qBase__subSys.values())[ind][0][indx] # pylint: disable=no-member
                order = sys.ind
                oper = list(self._qBase__subSys.values())[ind][1][indx] # pylint: disable=no-member
                if oper in [qOps.sigmam, qOps.sigmap, qOps.sigmax, qOps.sigmay, qOps.sigmaz]:
                    cHam = qOps.compositeOp(oper(), sys._dimsBefore, sys._dimsAfter)
                else:
                    dimension = sys._genericQSys__dimension
                    if oper in [qOps.Jz, qOps.Jy, qOps.Jx, qOps.Jm, qOps.Jp, qOps.Js]:
                        dimension = 0.5*(dimension-1)
                    cHam = qOps.compositeOp(oper(dimension), sys._dimsBefore, sys._dimsAfter)
                ts = [order, cHam]
                qts.append(ts)
            cMats.append(self._qCoupling__coupOrdering(qts))
        #h = []
        #if ((self.couplingStrength != 0) or (self.couplingStrength is not None)):
        #    h = [self.couplingStrength * sum(cMats)]
        self._paramBoundBase__matrix = sum(cMats) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix # pylint: disable=no-member

    def __addTerm(self, count, ind, sys, *args):
        r"""
        used internally when adding terms to the coupling.
        """
        if callable(args[count][ind]):
            lo = len(self.subSys)
            self._qBase__subSys[str(lo)] = (sys, tuple(args[count])) # pylint: disable=no-member
            count += 1
            if count < len(args):
                count = self.__addTerm(count, ind, sys, *args)
        return count

    def addTerm(self, *args):
        r"""
        method to add terms to the coupling.
        """
        counter = 0
        while counter in range(len(args)):
            # TODO write a generalisation for this one
            if isinstance(self.getByNameOrAlias(args[counter][0]), qSystem):
                qSystems = [self.getByNameOrAlias(obj) for obj in args[counter]]
                for qsys in qSystems:
                    qsys._paramBoundBase__paramBound[self.name] = self
                if callable(args[counter+1][1]):
                    #if tuple(args[counter + 1]) in self._qBase__subSys.keys(): # pylint: disable=no-member
                    #    print(tuple(args[counter + 1]), 'already exists')
                    lo = len(self.subSys)
                    self._qBase__subSys[str(lo)] = (qSystems, tuple(args[counter + 1])) # pylint: disable=no-member
                    counter += 2
                # TODO does not have to pass qSystem around
                if counter < len(args):
                    counter = self._qCoupling__addTerm(counter, 1, qSystems, *args)
            else:
                # TODO raise a meaningful error
                break
        self._paramBoundBase__matrix = None # pylint: disable=assigning-non-slot
        return self

    @_recurseIfList
    def removeSysCoupling(self, sys):
        r"""
        method to remove terms from the coupling, simply calls removeSubSys, this method is to create terminology
        """
        self._removeSubSysExc(sys, _exclude=[])

    @_recurseIfList
    def _removeSubSysExc(self, subSys, _exclude=[]): # pylint: disable=dangerous-default-value
        r"""
        method to remove terms from the coupling
        """
        vals = self._qBase__subSys.values() # pylint: disable=no-member
        for ind, val in enumerate(vals):
            systs = val[0]
            if subSys in systs:
                self._qBase__subSys.pop(str(ind)) # pylint: disable=no-member
