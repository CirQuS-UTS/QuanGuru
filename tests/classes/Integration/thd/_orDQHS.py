import numpy as np
import quanguru as qg

def _createNQubSys(numOfQubits, freeOperator=qg.Jz, freequency=0):
    compSys = numOfQubits * qg.Qubit()
    for qub in compSys.subSys.values():
        qub.frequency = freequency
        qub.operator = freeOperator
    return compSys

def _nnExchange(compSys, couplingStrength, op1=qg.sigmax, op2=qg.sigmay):
    couplingObjs = []
    numberOfSubSys = len(compSys.subSys)
    qubs = list(compSys.subSys.values())
    for ind in range(numberOfSubSys-1):
        s = [qubs[ind], qubs[ind+1]]
        couplingObjs.append(
            compSys.createTerm(operator=[op1, op1], frequency=couplingStrength, qSystem=s))
        couplingObjs.append(
            compSys.createTerm(operator=[op2, op2], frequency=couplingStrength, qSystem=s))
    return couplingObjs

def _xy(compSys, couplingStrength, qubits = None, exchangeCouplings = None):
    if qubits is None:
        qubits = list(compSys.subSys.values())

    # if exchangeCouplings is None:
    #     exchangeCouplings = compSys.qCouplings.values()

    interactionSteps = []
    ind = 0
    while ind in range(len(exchangeCouplings)):
        u1 = qg.freeEvolution(superSys=compSys)
        u1.createUpdate(system=[exchangeCouplings[ind], exchangeCouplings[ind+1]], key='frequency', value=couplingStrength/2)
        u1.createUpdate(system=qubits, key='frequency', value=0)
        interactionSteps.append(u1)
        ind += 2

    return interactionSteps

def _addInteractionStep(protocol, interactionSteps):
    for s in interactionSteps:
        protocol.addStep(s)
    return protocol

def _rots(qubits, rotDir='x'):
    xrots1 = qg.xGate(system=qubits, angle=np.pi/2, rotationAxis=rotDir)
    xrots2 = qg.xGate(system=qubits, angle=-np.pi/2, rotationAxis=rotDir)
    return [xrots1, xrots2]

def _xz(protocol, interactionSteps, rotList):
    protocol.addStep(rotList[0])
    _addInteractionStep(protocol, interactionSteps)
    protocol.addStep(rotList[1])
    return protocol

def _yz(protocol, interactionSteps, rotList):
    protocol.addStep(rotList[0])
    _addInteractionStep(protocol, interactionSteps)
    protocol.addStep(rotList[1])
    return protocol

def _digitalHeisenberg(numOfQubits, couplingStrength, freeOperator=qg.Jz, freequency=0,
                       sequence = ('f', 'xy', 'xz', 'yz')):
    compSys = _createNQubSys(numOfQubits, freeOperator=freeOperator, freequency=freequency)
    compSys.initialState = [0 if x < 1 else 1 for x in range(numOfQubits)]
    exchangeCouplings = _nnExchange(compSys, 0)
    protocol = qg.qProtocol(superSys=compSys)

    s1 = qg.freeEvolution(superSys=compSys)
    qubits = list(compSys.subSys.values())
    interactionSteps = _xy(compSys, couplingStrength, qubits, exchangeCouplings)
    xRots = _rots(qubits)
    yRots = _rots(qubits, 'y')

    for st in sequence:
        if st == 'f':
            protocol.addStep(s1)
        elif st == 'xy':
            _addInteractionStep(protocol, interactionSteps)
        elif st == 'xz':
            _xz(protocol, interactionSteps, xRots)
        elif st == 'yz':
            _yz(protocol, interactionSteps, yRots)

    return protocol

def _idealHeisenberg(numOfQubits, couplingStrength, freeOperator=qg.Jz, freequency=0):
    compSys = _createNQubSys(numOfQubits, freeOperator=freeOperator, freequency=freequency)
    compSys.initialState = [0 if x < 1 else 1 for x in range(numOfQubits)]
    _nnExchange(compSys, couplingStrength/2)
    _nnExchange(compSys, couplingStrength/2, qg.sigmax, qg.sigmaz)
    _nnExchange(compSys, couplingStrength/2, qg.sigmay, qg.sigmaz)
    return compSys._freeEvol


def digitalHeisenberg(numOfQubits, couplingStrength, freeOperator=qg.Jz, freequency=0, digital=True,
                      sequence = ('f', 'xy', 'xz', 'yz')):
    kwargs = {"numOfQubits":numOfQubits, "couplingStrength":couplingStrength,
              "freeOperator":freeOperator, "freequency":freequency}
    protocol = _digitalHeisenberg(**kwargs, sequence=sequence) if digital else _idealHeisenberg(**kwargs)

    if digital:
        protocol.alias = "qp"+str(numOfQubits)+ "Z" if freeOperator == qg.Jz else "qp"+str(numOfQubits)+ "Y"
    else:
        protocol.alias = "fp"+str(numOfQubits)+ "Z" if freeOperator == qg.Jz else "fp"+str(numOfQubits)+ "Y"
    return protocol
stepSizes = [0.01, 0.2]
totalSimTimeV = 5
nVals = [2, 3]

def compute(qsim, args):
    i = 0
    while i in range(len(args)):
        qsim.qRes.result = ['sfid'+str(i), qg.fidelityPure(args[i], args[i+1])]
        i += 2

    for key, val in qsim.subSys.items():
        sz = qsim.auxDict[str(len(val.subSys.values()))+'z']
        qsim.qRes.result = [key.name.alias[0]+'Exp', qg.expectation(sz, key.currentState)]

simulation = qg.Simulation()
simulation.delStates = True
for n in nVals:
    digitalHeis2 = digitalHeisenberg(numOfQubits=n, couplingStrength=1, freequency=1, freeOperator=qg.Jz)
    digitalHeis2.alias = 'DigitalX'+str(n)+'Qubits'
    digitalHeis2y = digitalHeisenberg(numOfQubits=n, couplingStrength=1, freequency=1, freeOperator=qg.Jy)
    digitalHeis2y.alias = 'DigitalY'+str(n)+'Qubits'
    idealHeis2 = digitalHeisenberg(numOfQubits=n, couplingStrength=1, freequency=1, freeOperator=qg.Jz, digital=False)
    idealHeis2.alias = 'IdealX'+str(n)+'Qubits'
    idealHeis2y = digitalHeisenberg(numOfQubits=n, couplingStrength=1, freequency=1, freeOperator=qg.Jy, digital=False)
    idealHeis2y.alias = 'IdealY'+str(n)+'Qubits'

    digitalHeis2.auxDict[str(n)+'x'] = qg.compositeOp(qg.sigmax(), dimA=2**(n-1))
    digitalHeis2.auxDict[str(n)+'y'] = qg.compositeOp(qg.sigmay(), dimA=2**(n-1))
    digitalHeis2.auxDict[str(n)+'z'] = qg.compositeOp(qg.sigmaz(), dimA=2**(n-1))

    simulation.addSubSys(digitalHeis2.superSys, digitalHeis2)
    simulation.addSubSys(idealHeis2.superSys, idealHeis2)
    simulation.addSubSys(digitalHeis2y.superSys, digitalHeis2y)
    simulation.addSubSys(idealHeis2y.superSys, idealHeis2y)

stepSizeSweep = simulation.Sweep.createSweep(system=simulation, sweepKey='stepSize', sweepList=stepSizes)

simulation.compute = compute
simulation.totalTime = totalSimTimeV
