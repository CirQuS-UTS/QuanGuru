import datetime
import classes.parameterObj as pObj
import RabiModel.Modules.Hamiltonians as hams
import RabiModel.Modules.Evolutions_Unitary as uniEvo
import QuantumToolbox.TimeEvolution as tEvo
import scipy.sparse as sp
import QuantumToolbox.states as states
import QuantumToolbox.operators as qOps
from multiprocessing import Pool, cpu_count
from functools import partial
import QuantumToolbox.functions as qFncs
import QuantumToolbox.quasiProbabilities as qProb

start = datetime.datetime.now()
################## Simulation Parameters ##################
rabiParams = pObj.Rabi('rabiParams')
rabiParams.sweepKey = 'StepSize'
rabiParams.sweepMin = 0.005
rabiParams.sweepMax = 0.1
rabiParams.sweepPerturbation = 0.005
rabiParams.resonatorFrequency = 0.1
rabiParams.qubitFreqJC = 2
rabiParams.qubitFreq = 2
rabiParams.finalTime = 2
rabiParams.resonatorDimension = 10
rabiParams.Note = ' Threshold in tau for non-degenerate qubit case'
rabiParams.saveParameters()

rabiParams.initialState = sp.kron(states.basis(rabiParams.resonatorDimension, 0), states.basis(2, 1), format='csc')
hams.Hamiltonians(rabiParams)
cavParity = qOps.parityEXP(rabiParams.HamiltonianCavity)
photonN = rabiParams.HamiltonianCavity


bas = states.genericBasisBra(2*rabiParams.resonatorDimension)

if rabiParams.sweepKey == 'StepSize':
    for step in rabiParams.sweepList:
        rabiParams.StepSize = step
        rabiParams.results['y'].append(rabiParams.times)
        rabiParams.results['x'].append([step, step+rabiParams.sweepPerturbation])
elif rabiParams.sweepKey == 'resonatorFrequency':
    rabiParams.results['y'] = rabiParams.times
    rabiParams.results['x'] = rabiParams.sweepList

################## Simulation ##################
p = Pool(processes=cpu_count())
print('simulating Digital')
rabiParams.unitary = uniEvo.digitalRabi
statesDigital = p.map(partial(tEvo.evolveTimeIndep, rabiParams), rabiParams.sweepList)
print('simulating Ideal')
rabiParams.unitary = uniEvo.idealRabi
statesIdeal = p.map(partial(tEvo.evolveTimeIndep, rabiParams), rabiParams.sweepList)

################## Computation ##################
print('Calculating Parity')
parityDigital = p.map(partial(qFncs.expectationList, cavParity),statesDigital)
parityIdeal = p.map(partial(qFncs.expectationList, cavParity),statesIdeal)
print('Calculating Photon Number')
photonNumberDigital = p.map(partial(qFncs.expectationList, photonN),statesDigital)
photonNumberIdeal = p.map(partial(qFncs.expectationList, photonN),statesIdeal)

rabiParams.results['Parity Digital'] = parityDigital
rabiParams.results['Parity Ideal'] = parityIdeal
rabiParams.results['Photon Ideal'] = photonNumberIdeal
rabiParams.results['Photon Digital'] = photonNumberDigital

print('Simulation fidelity')
simFid = []
for brbw in range(len(statesDigital)):
    fid = []
    for aewr in range(len(statesDigital[brbw])):
        fid.append(qFncs.fidelityKet(statesDigital[brbw][aewr], statesIdeal[brbw][aewr]))
    simFid.append(fid)

print('Chaos measures')
losEchoDig = []
losEchoIde = []
IPRdig = []
IPRide = []
for qraa in range(len(statesDigital)):
    echod = p.map(partial(qFncs.fidelityKet, statesDigital[qraa][0]), statesDigital[qraa])
    losEchoDig.append(echod)
    echoi = p.map(partial(qFncs.fidelityKet, statesDigital[qraa][0]), statesIdeal[qraa])
    losEchoIde.append(echoi)
    iprd = p.map(partial(qFncs.IPRket,bas),statesDigital[qraa])
    IPRdig.append(iprd)
    ipri = p.map(partial(qFncs.IPRket,bas),statesIdeal[qraa])
    IPRide.append(ipri)

rabiParams.results['Simulation Fidelity'] = simFid
rabiParams.results['Loschmidt Echo Digital'] = losEchoDig
rabiParams.results['Loschmidt Echo Ideal'] = losEchoIde
rabiParams.results['IPR Digital'] = IPRdig
rabiParams.results['IPR Ideal'] = IPRide
print(len(statesDigital))
#rabiParams.statesToSave(statesDigital, 'Digital States')
#rabiParams.statesToSave(statesIdeal, 'Ideal States')

print('Reducing the states')
"""reducedCavDig = []
reducedCavIde = []"""
reducedQubDig = []
reducedQubIde = []
leng = len(statesDigital)
for aste in range(leng):
    """redcd = p.map(partial(partial(qFncs.partial_trace, [0]), [rabiParams.resonatorDimension, 2]), statesDigital[0])
    redci = p.map(partial(partial(qFncs.partial_trace, [0]), [rabiParams.resonatorDimension, 2]), statesIdeal[0])"""
    redqd = p.map(partial(partial(qFncs.partial_trace, [1]), [rabiParams.resonatorDimension, 2]), statesDigital[0])
    redqi = p.map(partial(partial(qFncs.partial_trace, [1]), [rabiParams.resonatorDimension, 2]), statesIdeal[0])
    """reducedCavDig.append(redcd)
    reducedCavIde.append(redci)"""
    reducedQubDig.append(redqd)
    reducedQubIde.append(redqi)
    del statesDigital[0]
    del statesIdeal[0]

print('Wigner and entropy')
"""WigIde = []
WigDig = []"""
entIde = []
entDig = []
for rtav in range(len(reducedQubDig)):
    """wigi = p.map(partial(qProb.Wigner, rabiParams.xvec), reducedCavIde[rtav])
    wigd = p.map(partial(qProb.Wigner, rabiParams.xvec), reducedCavDig[rtav])"""
    enti = p.map(qFncs.entropy, reducedQubIde[rtav])
    entd = p.map(qFncs.entropy, reducedQubDig[rtav])
    """WigIde.append(wigi)
    WigDig.append(wigd)"""
    entIde.append(enti)
    entDig.append(entd)

#rabiParams.results['Wigner Ideal'] = WigIde
rabiParams.results['Entropy Ideal'] = entIde
#rabiParams.results['Wigner Digital'] = WigDig
rabiParams.results['Entropy Digital'] = entDig
rabiParams.irregular = True
rabiParams. saveResults()

p.close()
p.join()

end = datetime.datetime.now()
print(end - start)