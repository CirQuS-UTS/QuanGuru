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

from ..QSystem import QuantumSystem, Qubit, Cavity, Spin
from ..QTerms import QTerm
from ...QuantumToolbox.operators import sigmaz, Jz, create, destroy, Jp, Jm, sigmax, Jx


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
        couplingObj1 = QTerm(qSystem=qsystems, operator=[destroy, Jp], superSys=obj)
        couplingObj2 = QTerm(qSystem=qsystems, operator=[create, Jm], superSys=obj)
    else:
        couplingObj1 = QTerm(qSystem=qsystems, operator=[destroy, create], superSys=obj)
        couplingObj2 = QTerm(qSystem=qsystems, operator=[create, destroy], superSys=obj)
    couplingObj = QTerm(subSys=[couplingObj1, couplingObj2], qSystem=obj, superSys=obj, frequency=couplingStrength)
    obj.addTerms(couplingObj)
    return couplingObj


@checkCavQub
def Rabi(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj1 = QTerm(qSystem=qsystems, operator=[destroy, sigmax], superSys=obj)
        couplingObj2 = QTerm(qSystem=qsystems, operator=[create, sigmax], superSys=obj)
    couplingObj = QTerm(subSys=[couplingObj1, couplingObj2], qSystem=obj, superSys=obj, frequency=couplingStrength)
    obj.addTerms(couplingObj)
    return couplingObj


@checkCavQub
def Dicke(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj1 = QTerm(qSystem=qsystems, operator=[destroy, Jx], superSys=obj)
        couplingObj2 = QTerm(qSystem=qsystems, operator=[create, Jx], superSys=obj)
    couplingObj = QTerm(subSys=[couplingObj1, couplingObj2], qSystem=obj, superSys=obj, frequency=couplingStrength)
    obj.addTerms(couplingObj)
    return couplingObj

QuantumSystem.JC = JC
QuantumSystem.Rabi = Rabi
QuantumSystem.Dicke = Dicke
