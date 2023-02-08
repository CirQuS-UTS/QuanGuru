from quanguru.classes.extensions.pytketInterface import pytketCircuit
from quanguru.classes.QPro import genericProtocol

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
    prot = pytketCircuit(circuit=circ)
    assert isinstance(prot, genericProtocol)
    assert prot.circuit is circ
    assert prot._paramUpdated is False
    assert len(prot.system.subSys) == 2

def test_unitaryGenerationPytketCircuits():
    r"""
    Tests unitary generation abilities of wrapped circuits
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = pytketCircuit(circuit=circ)
    assert np.allclose(prot.unitary(), circ.get_unitary())

def test_reloadUnitaryGeneration():
    r"""
    Tests unitary generation abilities of wrapped circuits to adapt to modified original circuit
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = pytketCircuit(circuit=circ)
    unitary = circ.get_unitary()
    assert np.allclose(prot.unitary(), unitary)
    circ.Rz(0.5, 0)
    assert np.allclose(prot.unitary(), unitary)
    prot.loadCircuit()
    assert not np.allclose(prot.unitary(), unitary)
    assert np.allclose(prot.unitary(), circ.get_unitary())


def test_circuitIncludingMeasurement():
    r"""
    Tests unitary generation abilities of wrapped circuits to adapt to modified original circuit
    """
    circ = Circuit(3, 3)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.Measure(2, 2)
    circ.CX(1, 0)
    circ.measure_all()

    circMeasureless = Circuit(3, 3)
    circMeasureless.H(0)
    circMeasureless.Rz(0.25, 0)
    circMeasureless.CX(1, 0)

    prot = pytketCircuit(circuit=circ)
    assert np.allclose(prot.unitary(), circMeasureless.unitary())