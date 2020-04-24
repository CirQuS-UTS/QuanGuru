from qTools.classes import QuantumSystem, Qubit, Cavity
from qTools.QuantumToolbox.operators import sigmaz, sigmam, sigmap, create, destroy, sigmax


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
    if qsystems[1].operator == sigmaz: # pylint: disable=comparison-with-callable
        #print('sigmaz')
        couplingObj = obj.createSysCoupling(qsystems, [destroy, sigmap], qsystems,
                                            [create, sigmam], superSys=obj, couplingStrength=cStrength)
        #couplingObj.addTerm()
    else:
        #print('number')
        couplingObj = obj.createSysCoupling(qsystems, [destroy, create], superSys=obj, couplingStrength=cStrength)
        couplingObj.addTerm(qsystems, [create, destroy])
    couplingObj.name = 'JCcoupling'
    return couplingObj

def Rabi(obj, subSys1, subSys2, cStrength):
    if isinstance(subSys1, Qubit):
        if not isinstance(subSys2, Cavity):
            raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
        qsystems = [subSys2, subSys1]
    elif isinstance(subSys2, Qubit):
        if not isinstance(subSys1, Cavity):
            raise ValueError('Jaynes-Cummings requires a qubit and a cavity')
        qsystems = [subSys1, subSys2]

    obj.couplingName = 'Rabi'
    if qsystems[1].operator == sigmaz: # pylint: disable=comparison-with-callable
        couplingObj = obj.createSysCoupling(qsystems, [destroy, sigmax], qsystems,
                                            [create, sigmax], superSys=obj, couplingStrength=cStrength)
        couplingObj.addTerm()
    # else:
    #     print('number')
    #     couplingObj = obj.createSysCoupling(qsystems, [destroy, create], superSys=obj, couplingStrength=cStrength)
    #     couplingObj.addTerm(qsystems,[create, destroy])
    # couplingObj.name = 'JCcoupling'
    return couplingObj

QuantumSystem.JC = JC
QuantumSystem.Rabi = Rabi
