# r"""
#     Contains the new classes for protocols.

#     .. currentmodule:: quanguru.classes.QProtocol

#     .. autosummary::

#         QProtocol

#     .. |c| unicode:: U+2705
#     .. |x| unicode:: U+274C
#     .. |w| unicode:: U+2000

#     =======================    ==================    ================   ===============
#        **Function Name**        **Docstrings**        **Unit Tests**     **Tutorials**
#     =======================    ==================    ================   ===============
#       `QProtocol`                |w| |w| |w| |x|       |w| |w| |x|        |w| |w| |x|
#     =======================    ==================    ================   ===============

# """

# from ..QuantumToolbox import evolution as lio #pylint: disable=relative-beyond-top-level
# from ..QuantumToolbox.operators import identity #pylint: disable=relative-beyond-top-level

# from .base import qBase, addDecorator
# from .baseClasses import updateBase
# from .QSimBase import _parameter
# from .QSimComp import QSimComp
# from .QSweep import Sweep


# class QProtocol(QSimComp): # pylint: disable = too-many-instance-attributes
#     label = 'QProtocol'
#     #: (**class attribute**) number of instances created internally by the library
#     _internalInstances: int = 0
#     #: (**class attribute**) number of instances created explicitly by the user
#     _externalInstances: int = 0
#     #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
#     _instances: int = 0

#     #: (**class attribute**) to store number of exponentiations, incremented by _increaseExponentiationCount method
#     numberOfExponentiations = 0

#     @classmethod
#     def _increaseExponentiationCount(cls):
#         r"""
#         This is a classmethod (used internally) to increment the `numberOfExponentiations` count.
#         """
#         cls.numberOfExponentiations += 1
#         return cls.numberOfExponentiations

#     __slots__ = ['__currentState', '__inProtocol', '__fixed', '__ratio', '__updates', '__dissipator', '_openSys',
#                  '_getUnitary', 'timeDependency', '__identity', 'sampleStates', 'stepSample']

#     def __init__(self, **kwargs):
#         super().__init__(_internal=kwargs.pop('_internal', False))
#         #: during time evolution, the current state of the protocol at the current time is stored in this attribute
#         #: it is an instance of `_parameter` so that the nested-protocols can refer to the same state that is store
#         #: by the outer-most protocol.
#         self.__currentState = _parameter()
#         #: stores an identity matrix with the total dimension of the system of the protocol.
#         #: this is used internally and introduces slight performance enhancement.
#         self.__identity = None
#         #: some steps might be used more than once in the same protocol or in different protocol/s. with this boolean,
#      #: it is determined if self is already a step in a protocol, so that a `copyStep` (of self) is used when self is
#         #: used again as a step in the same protocol or in different protocol/s.
#         self.__inProtocol = False
#         #: when parameters of a step are going to be fixed during the whole simulation (including parameter sweeps),
#         #: we can label it as fixed to optimize number of exponentiations.
#         self.__fixed = False
#         #: ratio of the stepSize of self to the stepSize of simulation. Used for higher order Trotterisations, so that
#         #: there is only one step size to be swept and the relative step sizes are determined by this ratio, which
#         #: might also be negative as required by higher (than 2) Trotterisation orders.
#         self.__ratio = 1
#         #: stores a list of updates for this protocol/step.
#         self.__updates = []
#         #: when constructing the unitary evolution of a protocol, certain parts of this creation might be replaced by
#         #: other methods depending on the solution method we used. this attribute stores the `_getUnitary`, which is
#         #: part of getUnitary method that (uses createUnitary and) returns the unitary matrix.
#         # TODO I will create a tutorial explaning this.
#         self._getUnitary = self._defGetUnitary
#      #: when we use compute function with delStates, we might want to sample several number of time-steps first, then
#         #: call the compute, which might provide performance benefits when using other solution methods than matrix
#         #: exponentiation. This list is used for this purpose (and also relies on samples number of self.simulation).
#         # TODO requires a tutorial and NOTE not completely decided on every detail of how to use this.
#         self.sampleStates = []
#         #: boolean to determine if a single state or a list of states is samples (related to sampleStates)
#         self.stepSample = False
#         #: This is an instance of sweep class, but it is called at every time-step, so that we can change a parameter
#         #: as a function of time.
#         # TODO new approach of _timeDependency method in QSystem is much more flexible and
#         # intuitive than this, and I will more that approach to QSimComp class to make it also available here.
#         self.timeDependency = Sweep(superSys=self)
#         #: a dictionary to store the dissipator objects used in open-system simulations
#         self.__dissipator = {}
#         #: boolean to determine if it is an open-system simulation.
#         self._openSys = False
#         self._named__setKwargs(**kwargs) # pylint: disable=no-member

#     @property
#     def fixed(self):
#         r"""
#      Setter & getter for the boolean determining if self is a fixed protocol, ie calculates the unitary once and does
#         not change it even when the parameters of the system or simulation are changed/updated.
#         """
#         return self._QProtocol__fixed

#     @fixed.setter
#     def fixed(self, boolean):
#         self._QProtocol__fixed = boolean # pylint: disable=assigning-non-slot

#     def _defGetUnitary(self, collapseOps = None, decayRates = None):
#         r"""
#         Default method for `_getUnitary`. TODO I will re-visit this implementation, which is meant to be replaceable.
#         """
#         runCreate = False
#         if self._paramUpdated:
#             if not self.fixed:
#                 runCreate = True
#         elif self._paramBoundBase__matrix is None: # pylint: disable=no-member
#             runCreate = True

#         if runCreate:
#             lc = 1
#             td = False
#             if len(self.timeDependency.sweeps) > 0:
#                 lc = self.timeDependency.indMultip
#                 td = True

#             unitary = self._identity(openSys=self._isOpen)
#             for ind in range(lc):
#                 if td:
#                     self.timeDependency.runSweep(self.timeDependency._indicesForSweep(ind, *self.timeDependency.inds))
#                 unitary = self._createUnitary(collapseOps, decayRates) @ unitary # pylint: disable=no-member
#             self._paramBoundBase__matrix = unitary # pylint: disable=assigning-non-slot
#         return self._paramBoundBase__matrix # pylint: disable=no-member
