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
    It is important to load the Circuit to ensure the representation that will be used is the same as the held circuit.
    This is done by default on instantiation and if changes are made to the Circuit these can be made to the QuanGuru
    wrapper by using :meth:`~loadCircuit`.
    """
    label = 'pytketCircuit'
    #: (**class attribute**) number of instances created internally by the library
    _internalInstances: int = 0
    #: (**class attribute**) number of instances created explicitly by the user
    _externalInstances: int = 0
    #: (**class attribute**) number of total instances = _internalInstances + _externalInstances
    _instances: int = 0

    __slots__ = ['_circuit']

    def __init__(self, **kwargs):
        super().__init__(_internal=kwargs.pop('_internal', False))
        self.circuit = None
        self.createUnitary = self.getPytketCircuitUnitary
        self._named__setKwargs(**kwargs)  # pylint: disable=no-member
        self.loadCircuit()


    @property
    def circuit(self) -> Circuit:
        r"""
        Gets and sets the circuit property. This is done by accessing the _circuit attribute.
        """
        return self._circuit

    @circuit.setter
    def circuit(self, circ: Circuit):
        self._circuit = circ
        self.loadCircuit()
    def getPytketCircuitUnitary(self, *args) -> Matrix:
        r"""
        Provides interface to using pytket circuits get_unitary method to get the circuits unitary
        Returns
        -------
        Matrix
            The circuit's unitary in matrix form
        """
        if self.circuit is None:
            raise ValueError("No Circuit has been added for this protocol.")
        return self.circuit.get_unitary()

    def loadCircuit(self):
        r"""
        Loads the circuit by ensuring there are the correct number of qubits in the system the protocol acts on
        and ensures that the unitary is updated and the protocol accurately represents the current state of the Circuit.
        """
        if self.circuit is None:
            self._paramBoundBase__matrix = None
            self.superSys = None
            return
        self._paramUpdated = True
        self.system = self.circuit.n_qubits * Qubit()
        self.unitary() #: This needs to be done now as otherwise changes after loading would also impact the protocol


