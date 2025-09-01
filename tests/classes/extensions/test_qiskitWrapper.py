from quanguru.classes.extensions.CircuitAdapters import qiskitCircuit
from quanguru.classes.QPro import genericProtocol, qProtocol
from quanguru.classes.QSystem import Qubit

import random
import numpy as np

try:
    from qiskit import QuantumCircuit, QuantumRegister
    from qiskit.quantum_info import Operator
    qiskitInstalled = True
except (ImportError, ModuleNotFoundError):
    qiskitInstalled = False

from functools import wraps
import pytest

def checkQiskitIntsalled(func):
    r"""
    Function wrapper that ensures qiskit is installed before using its api
    """
    @wraps(func)
    def checkInstallation(*args, **kwargs):
        if qiskitInstalled:
            func(*args, **kwargs)
    return checkInstallation

def test_qiskitInstalled():
    r"""
    Tests qiskit is installed.
    If it is not all other tests/classes/extensions/test_qiskitWrapper.py tests are unchecked
    """
    assert qiskitInstalled

@checkQiskitIntsalled
def test_defineEmptyQiskitWrapper():
    r"""
    Tests that pytket wrappers do not need a circuit to be defined
    """
    prot = qiskitCircuit()
    assert prot.system is None
    assert prot.circuit is None
    with pytest.raises(ValueError, match='No Circuit has been added for this protocol.'):
        prot.unitary()


@checkQiskitIntsalled
def test_initialiseQiskitWrapper():
    r"""
    Tests initialisation of a pytket wrapper with a simple pytket circuit
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)


    prot = qiskitCircuit(circuit=circ)
    assert isinstance(prot, genericProtocol)
    assert prot.circuit is circ
    assert prot._paramUpdated is True
    assert len(prot.system.subSys) == 2


@checkQiskitIntsalled
def test_initialiseQiskitWrapperWithSystem():
    r"""
    Tests initialisation of a pytket wrapper with a simple pytket circuit from a given system
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)
    system = 2 * Qubit()
    prot = qiskitCircuit(circuit=circ, system=system)
    assert isinstance(prot, genericProtocol)
    assert prot.circuit is circ
    assert prot._paramUpdated is True
    assert prot.system is system


@checkQiskitIntsalled
def test_unitaryGenerationQiskitCircuits():
    r"""
    Tests unitary generation abilities of wrapped circuits
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)
    prot = qiskitCircuit(circuit=circ)
    print(Operator(circ).data)
    assert np.allclose(prot.unitary(), Operator(circ).data)


@checkQiskitIntsalled
def test_unitaryGenerationWithSystem():
    r"""
    Tests unitary generation abilities of wrapped circuits from given system
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)
    system = 2 * Qubit()
    prot = qiskitCircuit(circuit=circ, system=system)
    assert np.allclose(prot.unitary(), Operator(circ).data)


@checkQiskitIntsalled
def test_reloadUnitaryGeneration():
    r"""
    Tests unitary generation abilities of wrapped circuits to adapt to modified original circuit
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)
    prot = qiskitCircuit(circuit=circ)
    unitary = Operator(circ).data
    assert np.allclose(prot.unitary(), unitary)
    circ.rz(0.5, 0)
    assert np.allclose(prot.unitary(), unitary)
    prot.update()
    assert not np.allclose(prot.unitary(), unitary)
    assert np.allclose(prot.unitary(), Operator(circ).data)


@checkQiskitIntsalled
def test_usingQiskitWrapperAsStep():
    r"""
    Tests using a qiskit wrapper as a step within another protocol
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)
    prot = qiskitCircuit(circuit=circ)

    circ2 = QuantumCircuit(2)
    circ2.h(0)
    circ2.rz(0.5, 0)
    circ2.rx(0.5, 0)
    circ2.cx(0, 1)
    prot2 = qiskitCircuit(circuit=circ2)

    mainProtocol = qProtocol(system=2 * Qubit(), steps=[prot, prot2])
    unitary = prot2.unitary() @ prot.unitary()
    assert np.allclose(mainProtocol.unitary(), unitary)

@checkQiskitIntsalled
def test_usingQiskitWrapperCopyStep():
    r"""
    Tests using a qiskit wrapper as a step within another protocol
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)
    prot = qiskitCircuit(circuit=circ)

    protHC = prot.hc

    mainProtocol = qProtocol(system=2 * Qubit(), steps=[prot, protHC])
    unitary = protHC.unitary() @ prot.unitary()
    assert np.allclose(mainProtocol.unitary(), unitary)


@checkQiskitIntsalled
def test_changeSystemSizeQiskitWrapper():
    r"""
    Tests changing the size of the system automatically through the qiskit circuit
    """
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.rx(0.5, 0)
    circ.cx(0, 1)
    prot = qiskitCircuit(circuit=circ)
    reg = QuantumRegister(1)
    circ.add_register(reg)
    prot.update()
    assert np.allclose(Operator(circ).data, prot.unitary())
