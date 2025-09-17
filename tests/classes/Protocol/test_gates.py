import quanguru as qg
import random
import numpy as np

def test_SpinRotation():
    """
    Test that the SpinRotation class correctly creates its superoperator
    """
    sysQub = qg.Qubit(frequency=round(random.random(), 2))
    angle = round(random.random()*2*np.pi, 2)

    c = np.cos(angle/2)
    s = np.sin(angle/2)

    spinX = np.array([[c, -1j*s],
                    [-1j*s, c]])


    spinY = np.array([[c, -s],
                      [s, c]])

    
    spinZ = np.array([[np.exp(-1j*angle/2), 0],
                    [0, np.exp(1j*angle/2)]])


    SOX = qg.SpinRotation(system = sysQub, angle=angle, rotationAxis='x')._rotMat(openSys=False).A
    SOY = qg.SpinRotation(system = sysQub, angle=angle, rotationAxis='y')._rotMat(openSys=False).A
    SOZ = qg.SpinRotation(system = sysQub, angle=angle, rotationAxis='z')._rotMat(openSys=False).A

    assert np.isclose(SOX,spinX).all()
    assert np.isclose(SOY,spinY).all()
    assert np.isclose(SOZ,spinZ).all()


def test_SpinRotationSO():
    """
    Test that the SpinRotation class correctly creates its superoperator
    """
    sysQub = qg.Qubit(frequency=round(random.random(), 2))
    angle = round(random.random()*2*np.pi, 2)

    c = np.cos(angle/2)
    s = np.sin(angle/2)

    spinX = np.array([[c*c, -1j*c*s, 1j*c*s, s*s],
                      [-1j*c*s, c*c, s*s, 1j*c*s],
                      [1j*c*s, s*s, c*c, -1j*c*s],
                      [s*s, 1j*c*s, -1j*c*s, c*c]])


    spinY = np.array([[c*c, -c*s, -c*s, s*s],
                      [c*s, c*c, -s*s, -c*s],
                      [c*s, -s*s, c*c, -c*s],
                      [s*s, c*s, c*s, c*c]])
    
    spinZ = np.array([[1, 0, 0, 0],
                      [0, np.exp(1j*angle), 0, 0],
                      [0, 0, np.exp(-1j*angle), 0],
                      [0, 0, 0, 1]])


    SOX = qg.SpinRotation(system = sysQub, angle=angle, rotationAxis='x')._rotMat(openSys=True).A
    SOY = qg.SpinRotation(system = sysQub, angle=angle, rotationAxis='y')._rotMat(openSys=True).A
    SOZ = qg.SpinRotation(system = sysQub, angle=angle, rotationAxis='z')._rotMat(openSys=True).A

    assert np.isclose(SOX,spinX).all()
    assert np.isclose(SOY,spinY).all()
    assert np.isclose(SOZ,spinZ).all()
