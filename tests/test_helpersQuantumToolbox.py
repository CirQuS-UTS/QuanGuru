from qTools.QuantumToolbox import _helpers #pylint: disable=import-error

def test_loopIt():
    def mulT(a, b, c):
        return a*b*c
    al = range(10)
    assert _helpers.loopIt(mulT, al, al, al) == [0, 1, 8, 27, 64, 125, 216, 343, 512, 729]
