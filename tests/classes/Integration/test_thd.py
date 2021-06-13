import pytest
import numpy as np
import quanguru as qt
import tests.classes.Integration.thd.thd as th

fp2ZExp = qt.readCSV("tests/classes/Integration/thd/thdData/fp2ZExp.txt")
fp2YExp = qt.readCSV("tests/classes/Integration/thd/thdData/fp2YExp.txt")

fp3ZExp = qt.readCSV("tests/classes/Integration/thd/thdData/fp3ZExp.txt")
fp3YExp = qt.readCSV("tests/classes/Integration/thd/thdData/fp3YExp.txt")

qp2ZExp = qt.readCSV("tests/classes/Integration/thd/thdData/qp2ZExp.txt")
qp2YExp = qt.readCSV("tests/classes/Integration/thd/thdData/qp2YExp.txt")

qp3ZExp = qt.readCSV("tests/classes/Integration/thd/thdData/qp3ZExp.txt")
qp3YExp = qt.readCSV("tests/classes/Integration/thd/thdData/qp3YExp.txt")

sfid2Y = qt.readCSV("tests/classes/Integration/thd/thdData/sfid2Y.txt")
sfid2Z = qt.readCSV("tests/classes/Integration/thd/thdData/sfid2Z.txt")

sfid3Y = qt.readCSV("tests/classes/Integration/thd/thdData/sfid3Y.txt")
sfid3Z = qt.readCSV("tests/classes/Integration/thd/thdData/sfid3Z.txt")

@pytest.mark.parametrize("bo", [False, True])
def test_tddFromSaved(bo):
    th.simulation.run(p=bo)

    assert np.allclose(fp2ZExp[0], th.simulation.results["fp2ZExp"][0])
    assert np.allclose(fp2ZExp[1], th.simulation.results["fp2ZExp"][1])

    assert np.allclose(fp2YExp[0], th.simulation.results["fp2YExp"][0])
    assert np.allclose(fp2YExp[1], th.simulation.results["fp2YExp"][1])

    assert np.allclose(fp3ZExp[0], th.simulation.results["fp3ZExp"][0])
    assert np.allclose(fp3ZExp[1], th.simulation.results["fp3ZExp"][1])

    assert np.allclose(fp3YExp[0], th.simulation.results["fp3YExp"][0])
    assert np.allclose(fp3YExp[1], th.simulation.results["fp3YExp"][1])

    assert np.allclose(qp2ZExp[0], th.simulation.results["qp2ZExp"][0])
    assert np.allclose(qp2ZExp[1], th.simulation.results["qp2ZExp"][1])

    assert np.allclose(qp2YExp[0], th.simulation.results["qp2YExp"][0])
    assert np.allclose(qp2YExp[1], th.simulation.results["qp2YExp"][1])

    assert np.allclose(qp3ZExp[0], th.simulation.results["qp3ZExp"][0])
    assert np.allclose(qp3ZExp[1], th.simulation.results["qp3ZExp"][1])

    assert np.allclose(qp3YExp[0], th.simulation.results["qp3YExp"][0])
    assert np.allclose(qp3YExp[1], th.simulation.results["qp3YExp"][1])

    assert np.allclose(sfid2Y[0], th.simulation.results["sfid2"][0])
    assert np.allclose(sfid2Y[1], th.simulation.results["sfid2"][1])

    assert np.allclose(sfid2Z[0], th.simulation.results["sfid0"][0])
    assert np.allclose(sfid2Z[1], th.simulation.results["sfid0"][1])

    assert np.allclose(sfid3Y[0], th.simulation.results["sfid6"][0])
    assert np.allclose(sfid3Y[1], th.simulation.results["sfid6"][1])

    assert np.allclose(sfid3Z[0], th.simulation.results["sfid4"][0])
    assert np.allclose(sfid3Z[1], th.simulation.results["sfid4"][1])