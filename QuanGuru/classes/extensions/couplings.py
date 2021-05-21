from QuanGuru.classes.QSys import compQSystem, Qubit, Cavity, Spin
from QuanGuru.QuantumToolbox.operators import sigmaz, Jz, create, destroy, Jp, Jm, sigmax, Jx


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
    obj.couplingName = 'JC'
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj = obj.createSysCoupling(qsystems, [destroy, Jp], qsystems,
                                            [create, Jm], superSys=obj, couplingStrength=couplingStrength)
    else:
        couplingObj = obj.createSysCoupling(qsystems, [destroy, create], superSys=obj,
                                            couplingStrength=couplingStrength)
        couplingObj.addTerm(qsystems, [create, destroy])
    #couplingObj.alias = 'JCcoupling'
    return couplingObj


@checkCavQub
def Rabi(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    obj.couplingName = 'Rabi'
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj = obj.createSysCoupling(qsystems, [destroy, sigmax], qsystems,
                                            [create, sigmax], superSys=obj, couplingStrength=couplingStrength)
        #couplingObj.addTerm()
    # else:
    #     print('number')
    #  couplingObj = obj.createSysCoupling(qsystems, [destroy, create], superSys=obj, couplingStrength=couplingStrength)
    #     couplingObj.addTerm(qsystems,[create, destroy])
    # couplingObj.name = 'JCcoupling'
    return couplingObj


@checkCavQub
def Dicke(obj, couplingStrength, subSys1=None, subSys2=None):
    qsystems = [subSys1, subSys2]
    obj.couplingName = 'Dicke'
    if qsystems[1].operator in [sigmaz, Jz]: # pylint: disable=comparison-with-callable
        couplingObj = obj.createSysCoupling(qsystems, [destroy, Jx], qsystems,
                                            [create, Jx], superSys=obj, couplingStrength=couplingStrength)
        #couplingObj.addTerm()
    # else:
    #     print('number')
    #  couplingObj = obj.createSysCoupling(qsystems, [destroy, create], superSys=obj, couplingStrength=couplingStrength)
    #     couplingObj.addTerm(qsystems,[create, destroy])
    # couplingObj.name = 'JCcoupling'
    return couplingObj

compQSystem.JC = JC
compQSystem.Rabi = Rabi
compQSystem.Dicke = Dicke
