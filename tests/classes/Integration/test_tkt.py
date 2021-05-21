import pytest
import numpy as np
import QuanGuru as qt
import tests.classes.Integration.tkt.tkt as tk

ex = qt.readCSV("tests/classes/Integration/tkt/tktData/ex.txt")
fd = qt.readCSV("tests/classes/Integration/tkt/tktData/fd.txt")
dl = qt.readCSV("tests/classes/Integration/tkt/tktData/dl.txt")

@pytest.mark.parametrize("bo", [False, True])
def test_tddFromSaved(bo):
    tk.kt.runSimulation(p=bo)
    for i in range(len(ex)):
        assert np.allclose(tk.kt.simulation.results["ex"][i], ex[i])
        assert np.allclose(tk.kt.simulation.results["fd"][i], fd[i])
        assert np.allclose(tk.kt.simulation.results["dl"][i], dl[i])