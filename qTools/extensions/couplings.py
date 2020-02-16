from qTools.classes import QuantumSystem, Qubit, Cavity
from qTools.QuantumToolbox.operators import sigmaz, number, sigmam, sigmap, create, destroy


def JC(obj, subSys1, subSys2, cStrength):
    if isinstance(subSys1, Qubit):
        if not isinstance(subSys2, Cavity):
            raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
        qsystems = [subSys2, subSys1]
    elif isinstance(subSys2, Qubit):
        if not isinstance(subSys1, Cavity):
            raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
        qsystems = [subSys1, subSys2]

    obj.couplingName = 'JC'
    if qsystems[1].operator == sigmaz:
        print('sigmaz')
        couplingObj = obj.createSysCoupling(qsystems, [destroy, sigmap], cStrength, superSys=obj)
        couplingObj.addTerm(qsystems,[create, sigmam])
    else:
        print('number')
        couplingObj = obj.createSysCoupling(qsystems, [destroy, create], cStrength, superSys=obj)
        couplingObj.addTerm(qsystems,[create, destroy])
    couplingObj.name = 'JCcoupling'
    return couplingObj


QuantumSystem.JC = JC