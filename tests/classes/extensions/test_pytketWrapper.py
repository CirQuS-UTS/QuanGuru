from quanguru.classes.extensions.CircuitAdapters import pytketCircuit
from quanguru.classes.QPro import genericProtocol, qProtocol
from quanguru.classes.QSystem import Qubit

import random
import numpy as np

try:
    from pytket import Circuit
    import pytket as pt
    pytketInstalled = True
except (ImportError, ModuleNotFoundError):
    pytketInstalled = False

from functools import wraps
import pytest

def checkPytketInstalled(func):
    r"""
    Function wrapper that ensures pytket is installed before using its api
    """
    @wraps(func)
    def checkInstallation(*args, **kwargs):
        if pytketInstalled:
            func(*args, **kwargs)
    return checkInstallation

def test_pytketInstalled():
    r"""
    Tests pytket is installed.
    If it is not all other tests/classes/extensions/test_pytketWrapper.py tests are unchecked
    """
    assert pytketInstalled

@checkPytketInstalled
def test_defineEmptyPytketWrapper():
    r"""
    Tests that pytket wrappers do not need a circuit to be defined
    """
    prot = pytketCircuit()
    assert prot.system is None
    assert prot.circuit is None
    with pytest.raises(ValueError, match='No Circuit has been added for this protocol.'):
        prot.unitary()


@checkPytketInstalled
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
    assert prot._paramUpdated is True
    assert len(prot.system.subSys) == 2


@checkPytketInstalled
def test_initialisePytketWrapperWithSystem():
    r"""
    Tests initialisation of a pytket wrapper with a simple pytket circuit from a given system
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    system = 2 * Qubit()
    prot = pytketCircuit(circuit=circ, system=system)
    assert isinstance(prot, genericProtocol)
    assert prot.circuit is circ
    assert prot._paramUpdated is True
    assert prot.system is system


@checkPytketInstalled
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


@checkPytketInstalled
def test_unitaryGenerationWithSystem():
    r"""
    Tests unitary generation abilities of wrapped circuits from given system
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    system = 2 * Qubit()
    prot = pytketCircuit(circuit=circ, system=system)
    assert np.allclose(prot.unitary(), circ.get_unitary())


@checkPytketInstalled
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
    prot.update()
    assert not np.allclose(prot.unitary(), unitary)
    assert np.allclose(prot.unitary(), circ.get_unitary())


@checkPytketInstalled
def test_usingPytketWrapperAsStep():
    r"""
    Tests using a pytket wrapper as a step within another protocol
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = pytketCircuit(circuit=circ)

    circ2 = Circuit(2, 2)
    circ2.Rz(0.5, 0)
    circ2.CX(1, 0)
    circ2.H(0)
    prot2 = pytketCircuit(circuit=circ2)

    mainProtocol = qProtocol(system=2 * Qubit(), steps=[prot, prot2])
    unitary = prot2.unitary() @ prot.unitary()
    assert np.allclose(mainProtocol.unitary(), unitary)

@checkPytketInstalled
def test_usingPytketWrapperCopyStep():
    r"""
    Tests using a pytket wrapper as a step within another protocol
    """
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = pytketCircuit(circuit=circ)

    protHC = prot.hc

    mainProtocol = qProtocol(system=2 * Qubit(), steps=[prot, protHC])
    unitary = protHC.unitary() @ prot.unitary()
    assert np.allclose(mainProtocol.unitary(), unitary)


@checkPytketInstalled
def test_changeSystemSizePytketWrapper():
    circ = Circuit(2, 2)
    circ.H(0)
    circ.Rz(0.25, 0)
    circ.CX(1, 0)
    prot = pytketCircuit(circuit=circ)
    circ.add_qubit(pt.Qubit(2))
    prot.update()
    assert np.allclose(circ.get_unitary(), prot.unitary())

