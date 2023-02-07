import quanguru as qg
import random
import numpy as np
from pytket import Circuit
def test_initialisePytketWrapper():
    r"""
    Tests initialisation of a pytket wrapper with a simple pytket circuit
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = qg.pytketInterface(circuit=circ)
    assert isinstance(prot, qg.genericProtocol)
    assert prot.circuit is circ
    assert prot._paramUpdated is False
    assert len(prot.system.subSystem) == 2

def test_unitaryGenerationPytketCircuits():
    r"""
    Tests unitaray generation abilities of wrapped circuits
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = qg.pytketInterface(circuit=circ)
    assert np.isclose(prot.unitary, circ.get_unitary())

def test_reloadUnitaryGeneration():
    r"""
    Tests unitaray generation abilities of wrapped circuits to adapt to modified origional circuit
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = qg.pytketInterface(circuit=circ)
    unitary = circ.get_unitary()
    assert np.isclose(prot.unitary, unitary)
    circ.Rz(0.5, 0)
    assert np.isclose(prot.unitary, unitary)
    prot.loadCircuit()
    assert np.isclose(prot.unitary, circ.get_unitary())


def test_circuitIncludingMeasurement:
    r"""
    Tests unitaray generation abilities of wrapped circuits to adapt to modified origional circuit
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    circ.measure_all()
    prot = qg.pytketInterface(circuit=circ)
    assert False