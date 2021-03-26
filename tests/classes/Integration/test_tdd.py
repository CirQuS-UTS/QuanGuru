import pytest
import numpy as np
import qTools as qt
import tests.classes.Integration.tdd.tdd as td
#import tests.classes.Integration.tdd.tddData as tdData

vecStat05Dig =  qt.readCSV("tests/classes/Integration/tdd/tddData/vecStat05Dig.txt")
vecStat6Dig =  qt.readCSV("tests/classes/Integration/tdd/tddData/vecStat6Dig.txt")

vecStat05Ide =  qt.readCSV("tests/classes/Integration/tdd/tddData/vecStat05Ide.txt")
vecStat6Ide =  qt.readCSV("tests/classes/Integration/tdd/tddData/vecStat6Ide.txt")

nDig05 =  qt.readCSV("tests/classes/Integration/tdd/tddData/nDig05.txt")
nDig6 =  qt.readCSV("tests/classes/Integration/tdd/tddData/nDig6.txt")

nIde05 =  qt.readCSV("tests/classes/Integration/tdd/tddData/nIde05.txt")
nIde6 =  qt.readCSV("tests/classes/Integration/tdd/tddData/nIde6.txt")

sfid05 = qt.readCSV("tests/classes/Integration/tdd/tddData/sfid05.txt")
sfid6 = qt.readCSV("tests/classes/Integration/tdd/tddData/sfid6.txt")

@pytest.mark.parametrize("bo", [False, True])
def test_tddFromSaved(bo):
    td.simulation.run(p=bo)

    assert np.allclose(vecStat05Dig[0], td.dd.results["vecStat"][0][0])
    assert np.allclose(vecStat05Dig[1], td.dd.results["vecStat"][0][1])

    assert np.allclose(vecStat6Dig[0], td.dd.results["vecStat"][1][0])
    assert np.allclose(vecStat6Dig[1], td.dd.results["vecStat"][1][1])

    assert np.allclose(vecStat05Ide[0], td.ds.results["vecStat"][0][0])
    assert np.allclose(vecStat05Ide[1], td.ds.results["vecStat"][0][1])

    assert np.allclose(vecStat6Ide[0], td.ds.results["vecStat"][1][0])
    assert np.allclose(vecStat6Ide[1], td.ds.results["vecStat"][1][1])

    assert np.allclose(nDig05[0], td.simulation.results["nDig"][0][0])
    assert np.allclose(nDig05[1], td.simulation.results["nDig"][0][1])

    assert np.allclose(nDig6[0], td.simulation.results["nDig"][1][0])
    assert np.allclose(nDig6[1], td.simulation.results["nDig"][1][1])

    assert np.allclose(nIde05[0], td.simulation.results["nIde"][0][0])
    assert np.allclose(nIde05[1], td.simulation.results["nIde"][0][1])

    assert np.allclose(nIde6[0], td.simulation.results["nIde"][1][0])
    assert np.allclose(nIde6[1], td.simulation.results["nIde"][1][1])

    assert np.allclose(sfid05[0], td.simulation.results["sfid"][0][0])
    assert np.allclose(sfid05[1], td.simulation.results["sfid"][0][1])
    assert np.allclose(sfid6[0], td.simulation.results["sfid"][1][0])
    assert np.allclose(sfid6[1], td.simulation.results["sfid"][1][1])
