from collections import OrderedDict
import warnings
from typing import Any

from .base import addDecorator, _recurseIfList
from .QSimComp import QSimComp
from .QSimBase import setAttr
from .exceptions import checkNotVal

class QuSystem(QSimComp):
    #: (**class attribute**) class label used in default naming
    label = 'QuSystem'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__terms', '__dimension', '__firstTerm', '__compSys', '__dimsBefore', '__dimsAfter']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        #: First term is also stored in __firstTerm attribute
        self.__firstTerm = None
        #: dictionary of the terms
        self.__terms = OrderedDict()
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
        self._named__setKwargs(**kwargs) # pylint:disable=no-member

    # dimension methods and properties
    @property
    def _totalDim(self):
        r"""
        :attr:`QuSystem.dimension` returns the dimension of a quantum system itself, meaning it does not contain the
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
            self._QuSystem__dimension = 1 # pylint:disable=assigning-non-slot
            for su in self.subSys.values():
                self._QuSystem__dimension *= su.dimension # pylint:disable=assigning-non-slot,no-member
        return self._QuSystem__dimension # pylint:disable=no-member

    @dimension.setter
    def dimension(self, dim):
        if not self._isComposite: # pylint:disable=no-member
            oldVal = getattr(self, '_QuSystem__dimension')
            setAttr(self, '_QuSystem__dimension', dim)
            if self.superSys is not None: # to change dimsBefore/After of other systems if self is a subSys in superSys
                self.superSys._updateDimension(self, dim, oldVal) # pylint:disable=protected-access
        else:
            warnings.warn(self.name + ' is a composite system, cannot set dimension')

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
        for qsys in self.subSys.values():#update dimsBefore/After of other sub-system by comparing their ind with subSys
            if qsys.ind < subSys.ind:
                qsys._dimsAfter = int((qsys._dimsAfter*newDim)/oldDim)
            if qsys.ind > subSys.ind:
                qsys._dimsBefore = int((qsys._dimsBefore*newDim)/oldDim)
        if self.superSys is not None: # for nested structures, we still need to call _updateDimension on self.superSys
            self.superSys._updateDimension(self, newDim, oldDim) # pylint:disable=protected-access

    @property
    def _isComposite(self):
        r"""
        Used internally to set _QuSystem__compSys boolean, never query this before _QuSystem__compSys is set by
        some internal call. Otherwise, this will always return False (because subSys dict is always empty initially)
        """
        if self._QuSystem__compSys is None: # pylint:disable=no-member
            self._QuSystem__compSys = bool(len(self.subSys)) # pylint:disable=assigning-non-slot
        return self._QuSystem__compSys # pylint:disable=no-member

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
        setAttr(self, '_QuSystem_'+attrName, val)
        for qsys in self.subSys.values():
            setattr(qsys, attrName, int((getattr(qsys, attrName)*val)/oldVal))

    @property
    def _dimsBefore(self):
        r"""
        Property to set and get the :attr:`~genericQSys.__dimsBefore`. Getter can be used to get information, but the
        setter is intended purely for internal use.
        """
        return self._QuSystem__dimsBefore

    @_dimsBefore.setter
    def _dimsBefore(self, val):
        self._QuSystem__dimsABUpdate('_dimsBefore', val)

    @property
    def _dimsAfter(self):
        r"""
        Property to set and get the :attr:`~genericQSys.__dimsAfter`. Getter can be used to get information, but the
        setter is intended purely for internal use.
        """
        return self._QuSystem__dimsAfter

    @_dimsAfter.setter
    def _dimsAfter(self, val):
        self._QuSystem__dimsABUpdate('_dimsAfter', val)

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
        if self._QuSystem__compSys is None: # pylint:disable=no-member
            self._QuSystem__compSys = True # pylint:disable=assigning-non-slot
        elif self._QuSystem__compSys is False: # pylint:disable=no-member
            raise TypeError("Cannot add a sub-system to a single quantum system " + self.name)

        if subSys not in self.subSys.values():
            self._QuSystem__addSub(subSys)
        subSys.superSys = self
        self._paramUpdated = True
        subSys._paramBoundBase__paramBound[self.name] = self # pylint: disable=protected-access
        return super().addSubSys(subSys, **kwargs)

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
            (into _QuSystem__dimension) after its removed.
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
                setAttr(self, '_QuSystem__dimension', oldDim)
            subSys.superSys = None
            subSys._dimsAfter = 1
            subSys._dimsBefore = 1
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

        # TODO
        # need to remove any coupling/term that relies on the removed system
        # reset the initial state/s
        self.delMatrices(_exclude=[])

    # these will work after term object is implemented
    @property
    def terms(self):
        return self._QuSystem__terms # pylint:disable=no-member

    @addDecorator
    def addTerms(self, trm):
        self._QuSystem__terms[trm.name] = trm  # pylint:disable=no-member
        trm.superSys = self

    def resetTerms(self):
        self._QuSystem__terms = OrderedDict() # pylint:disable=assigning-non-slot

    @terms.setter
    def terms(self, trm):
        self.resetTerms()
        self.addTerms(trm)

    @property
    def _firstTerm(self):
        return self._QuSystem__firstTerm # pylint:disable=no-member

    @property
    def frequency(self):
        return self._firstTerm.frequency

    @frequency.setter
    def frequency(self, freq):
        self._firstTerm.frequency = freq

    @property
    def operator(self):
        return self._firstTerm.operator

    @operator.setter
    def operator(self, op):
        self._firstTerm.operator = op

    @property
    def order(self):
        return self._firstTerm.order

    @order.setter
    def order(self, odr):
        self._firstTerm.order = odr
