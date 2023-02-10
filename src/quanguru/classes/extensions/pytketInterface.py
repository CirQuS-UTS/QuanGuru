"""
    Contains interface through which pytket circuitry can be interacted with.

    .. currentmodule:: quanguru.classes.extensions.pytketInterface

    .. autosummary::



    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
      `pytketCircuit`            |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""
from ..QPro import genericProtocol
from ..QSystem import Qubit
from ...QuantumToolbox.customTypes import Matrix
from pytket import Circuit


class pytketCircuit(genericProtocol):
    r"""
    Wraps Pytket Circuits in a way such that they can be used in QuanGuru as protocols. Can be interfaced with as
    any other protocol would be. This implementation stores a reference to a Pytket Circuit in :attr:`~circuit.`
    It is important to update to ensure the representation that will be used is the same as the held circuit.
    This is done by default on instantiation and if changes are made to the Circuit these can be made to the QuanGuru
    wrapper by using :meth:`~update()`.
    """
    label = 'pytketCircuit'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['_circuit', '__defaultSystem']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self._circuit = None
        self.createUnitary = self._getPytketCircuitUnitary
        # Ensure that system is set before circuit by moving it to the front
        # If not done circuit is loaded without system and extra system is created
        if 'system' in kwargs.keys():
            kwargs = {'system': kwargs.pop('system'), **kwargs}
            self.__defaultSystem = False

        self._named__setKwargs(**kwargs)  # pylint: disable=no-member
        if self.system is None:
            self.superSys = self.circuit.n_qubits * Qubit()  # superSys used to not change __default system to false
            self.__defaultSystem = True
    @property
    def circuit(self) -> Circuit:
        r"""
        Gets and sets the circuit property. This is done by accessing the _circuit attribute.
        When set it will also update the circuit.
        """
        return self._circuit

    @circuit.setter
    def circuit(self, circ: Circuit):
        self._circuit = circ
        self.update()

    def unitary(self) -> Matrix:
        r"""
        Override unitary() method of genericProtocol to ensure that the system is prepared before running the unitary
        genereation functionality. Gets the unitary of the protocol/Circuit.

        Returns
        -------
        Matrix:
            the unitary of the protocol
        """
        self._preparePytketWrapper()
        self.system._timeDependency()  # pylint: disable=no-member
        if self._paramUpdated and not self.fixed or self._paramBoundBase__matrix is None:
                self._paramBoundBase__matrix = self.getUnitary(None, None) # pylint: disable=assigning-non-slot
        return self._paramBoundBase__matrix

    @genericProtocol.system.setter
    def system(self, supSys):
        self.superSys = supSys # pylint: disable=no-member
        # Overriden so that we know if the system was assigned by user
        self._pytketCircuit__defaultSystem = False

    def _getPytketCircuitUnitary(self, *args) -> Matrix:
        r"""
        Provides interface to using pytket circuits get_unitary method to get the circuits unitary and ensures the
        circuit is prepared for unitary genereation.
        Returns
        -------
        Matrix
            The circuit's unitary in matrix form
        """
        return self.circuit.get_unitary()

    def _preparePytketWrapper(self):
        r"""
        Ensures a circuit, and it's wrapper are prepared for unitary generation by ensuring dimension will match for an
        automatically defined system.
        """
        if self.circuit is None:
            raise ValueError("No Circuit has been added for this protocol.")
        # Ensure that the system has correct dimension if it is automatically made
        while self.__defaultSystem and self.circuit.n_qubits > len(self.system.subSys):
            self.superSys += Qubit()
        while self.__defaultSystem and self.circuit.n_qubits < len(self.system.subSys):
            self.superSys -= Qubit()
