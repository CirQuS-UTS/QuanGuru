import pytest
import platform
import numpy as np
import quanguru as qg

ex = qg.readCSV("tests/classes/Integration/tkt/tktData/ex.txt")
fd = qg.readCSV("tests/classes/Integration/tkt/tktData/fd.txt")
dl = qg.readCSV("tests/classes/Integration/tkt/tktData/dl.txt")

@pytest.mark.parametrize("bo", [False, True])
def test_tktFromSaved(bo):
    if not (bo and (platform.system() == 'Windows')):
        qg.freeEvolution._freqCoef = 2*np.pi
        import tests.classes.Integration.tkt._orKT as tk
        tk.kt.runSimulation(p=bo)
        for i in range(len(ex)):
            assert np.allclose(tk.kt.simulation.results["ex"][i], ex[i])
            assert np.allclose(tk.kt.simulation.results["fd"][i], fd[i])
            assert np.allclose(tk.kt.simulation.results["dl"][i], dl[i])
        qg.freeEvolution._freqCoef = 1