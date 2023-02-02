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
from quanguru import genericProtocol, Matrix
from pytket import Circuit

class pytketCircuit(genericProtocol):
    r"""
    Wraps Pytket Circuits in a way such that they can be used in QuanGuru as protocols. Can be interfaced with as
    any other protocol would be. This implementation stores a reference to a Pytket Circuit in :attr:`~circuit`
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
        self._named__setKwargs(**kwargs)  # pylint: disable=no-member
        self.createUnitary = self.getPytketCircuitUnitary
        # Ensure super system and paramBound are set up correctly original protocol is provided

    @property
    def circuit(self) -> Circuit:
        r"""
        Gets and sets the circuit property. This is done by accessing the _circuit attribute.
        """
        return self._circuit

    @circuit.setter
    def circuit(self, circ: Circuit):
        self._circuit = circ

    def getPytketCircuitUnitary(self) -> Matrix:
        r"""
        Provides interface to using pytket circuits get_unitary method to get the circuits unitary
        Returns
        -------
        Matrix
            The circuit's unitary in matrix form
        """
        return self.circuit.get_unitary()


