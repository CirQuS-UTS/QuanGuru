from quanguru.QuantumToolbox import _helpers #pylint: disable=import-error

def test_loopIt():
    # testing the (multivariate) function looping helper with a simple multiplication function
    def mulT(a, b, c):
        return a*b*c
    al = range(10)
    bl = [2*i for i in range(10)]
    cl = [3*i for i in range(10)]
    assert _helpers.loopIt(mulT, al, al, al) == [0, 1, 8, 27, 64, 125, 216, 343, 512, 729]
    assert _helpers.loopIt(mulT, al, bl, cl) == [0, 6, 48, 162, 384, 750, 1296, 2058, 3072, 4374]
