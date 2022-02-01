from audioop import add
from collections import OrderedDict
import warnings

from .base import addDecorator
from .QSimComp import QSimComp

class QuSystem(QSimComp):
    #: (**class attribute**) class label used in default naming
    label = 'QuSystem'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['__terms', '__dimension', '__firstTerm']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._QuSystem__firstTerm = None # pylint:disable=assigning-non-slot
        self._QuSystem__terms = OrderedDict() # pylint:disable=assigning-non-slot
        self._QuSystem__dimension = None # pylint:disable=assigning-non-slot

    @property
    def dimension(self):
        if len(self.subSys) > 0:
            dim = 1
            for su in self.subSys.values():
                dim *= su.dimension
            self._QuSystem__dimension = dim # pylint:disable=assigning-non-slot
        return self._QuSystem__dimension # pylint:disable=no-member

    @dimension.setter
    def dimension(self, dim):
        if len(self.subSys) == 0:
            self._QuSystem__dimension = dim # pylint:disable=assigning-non-slot
        else:
            warnings.warn(self.name + ' is a composite system, so dimension is not set')

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

    @addDecorator
    def addSubSys(self, subSys, **kwargs):
        subSys.superSys = self
        return super().addSubSys(subSys, **kwargs)

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
