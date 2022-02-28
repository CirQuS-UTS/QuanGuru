"""
    Contains methods that creates the objects for certain common couplings.

    .. currentmodule:: quanguru.classes.extensions.couplings

    .. autosummary::

        checkCavQub
        JC
        Rabi
        Dicke

    .. |c| unicode:: U+2705
    .. |x| unicode:: U+274C
    .. |w| unicode:: U+2000

    =======================    ==================   ==============   ================   ===============
       **Function Name**        **Docstrings**       **Examples**     **Unit Tests**     **Tutorials**
    =======================    ==================   ==============   ================   ===============
      `checkCavQub`             |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `JC`                      |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `Rabi`                    |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
      `Dicke`                   |w| |w| |w| |x|      |w| |w| |x|      |w| |w| |x|        |w| |w| |x|
    =======================    ==================   ==============   ================   ===============

"""

from ..QSys import compQSystem, QubitOld, CavityOld, SpinOld
from ..QSystem import QuantumSystem, Qubit, Cavity, Spin
from ..QTerms import QTerm
from ...QuantumToolbox.operators import sigmaz, Jz, create, destroy, Jp, Jm, sigmax, Jx


def checkCavQubOld(coupler):
    def couplerDecorator(obj, couplingStrength, subSys1=None, subSys2=None):
        if isinstance(subSys1, (QubitOld, SpinOld)):
            if not isinstance(subSys2, CavityOld):
                raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
            qsystems = [subSys2, subSys1]
        elif isinstance(subSys2, (QubitOld, SpinOld)):
            if not isinstance(subSys1, CavityOld):
                raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
            qsystems = [subSys1, subSys2]
        elif ((subSys1 is None) or (subSys2 is None)):
            qsystems = []
            for sys in obj.subSys.values():
                if isinstance(sys, (CavityOld, QubitOld, SpinOld)):
                    if len(qsystems) == 0:
                        qsystems.append(sys)
                    elif not isinstance(sys, qsystems[0].__class__):
                        qsystems.append(sys)

                    if len(qsystems) == 2:
                        break
            return couplerDecorator(obj, couplingStrength, *qsystems)
        return coupler(obj, couplingStrength, *qsystems)
    return couplerDecorator


@checkCavQubOld
def JCold(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj = obj.createSysCoupling(qsystems, [destroy, Jp], qsystems,
                                            [create, Jm], superSys=obj, couplingStrength=couplingStrength)
    else:
        couplingObj = obj.createSysCoupling(qsystems, [destroy, create], superSys=obj,
                                            couplingStrength=couplingStrength)
        couplingObj.addTerm(qsystems, [create, destroy])
    return couplingObj


@checkCavQubOld
def RabiOld(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj = obj.createSysCoupling(qsystems, [destroy, sigmax], qsystems,
                                            [create, sigmax], superSys=obj, couplingStrength=couplingStrength)
    return couplingObj


@checkCavQubOld
def DickeOld(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj = obj.createSysCoupling(qsystems, [destroy, Jx], qsystems,
                                            [create, Jx], superSys=obj, couplingStrength=couplingStrength)
    return couplingObj

compQSystem.JC = JCold
compQSystem.Rabi = RabiOld
compQSystem.Dicke = DickeOld


def checkCavQub(coupler):
    def couplerDecorator(obj, couplingStrength, subSys1=None, subSys2=None):
        if isinstance(subSys1, (Qubit, Spin)):
            if not isinstance(subSys2, Cavity):
                raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
            qsystems = [subSys2, subSys1]
        elif isinstance(subSys2, (Qubit, Spin)):
            if not isinstance(subSys1, Cavity):
                raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
            qsystems = [subSys1, subSys2]
        elif ((subSys1 is None) or (subSys2 is None)):
            qsystems = []
            for sys in obj.subSys.values():
                if isinstance(sys, (Cavity, Qubit, Spin)):
                    if len(qsystems) == 0:
                        qsystems.append(sys)
                    elif not isinstance(sys, qsystems[0].__class__):
                        qsystems.append(sys)

                    if len(qsystems) == 2:
                        break
            return couplerDecorator(obj, couplingStrength, *qsystems)
        return coupler(obj, couplingStrength, *qsystems)
    return couplerDecorator

@checkCavQub
def JC(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj1 = obj.createTerm(qSystem=qsystems, operator=[destroy, Jp])
        couplingObj2 = obj.createTerm(qSystem=qsystems, operator=[create, Jm])
        couplingObj = QTerm(subSys=[couplingObj1, couplingObj2], qSystem=obj, superSys=obj, frequency=couplingStrength)
    else:
        couplingObj1 = obj.createTerm(qSystem=qsystems, operator=[destroy, create])
        couplingObj2 = obj.createTerm(qSystem=qsystems, operator=[create, destroy])
        couplingObj = QTerm(subSys=[couplingObj1, couplingObj2], qSystem=obj, superSys=obj, frequency=couplingStrength)
    return couplingObj


@checkCavQub
def Rabi(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj1 = obj.createTerm(qSystem=qsystems, operator=[destroy, sigmax])
        couplingObj2 = obj.createTerm(qSystem=qsystems, operator=[create, sigmax])
        couplingObj = QTerm(subSys=[couplingObj1, couplingObj2], qSystem=obj, superSys=obj, frequency=couplingStrength)
    return couplingObj


@checkCavQub
def Dicke(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj1 = obj.createTerm(qSystem=qsystems, operator=[destroy, Jx])
        couplingObj2 = obj.createTerm(qSystem=qsystems, operator=[create, Jx])
        couplingObj = QTerm(subSys=[couplingObj1, couplingObj2], qSystem=obj, superSys=obj, frequency=couplingStrength)
    return couplingObj

QuantumSystem.JC = JC
QuantumSystem.Rabi = Rabi
QuantumSystem.Dicke = Dicke
