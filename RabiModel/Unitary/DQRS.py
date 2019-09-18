import datetime
from classes.parameterObj import ParamObj
from RabiModel.Modules.Hamiltonians import Hamiltonians
from RabiModel.Modules.Evolutions_Unitary import digitalRabi, idealRabi
from QuantumToolbox.TimeEvolution import timeEvolve
from QuantumToolbox.operators import parityEXP
from QuantumToolbox.functions import expectationSparse, fidelitySparse
import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sp
from QuantumToolbox.states import basis
from multiprocessing import Pool, cpu_count
from functools import partial
from Plotting.plottingSettings import plottingSet
from Plotting.Functions import createMAP, normalizeCMAP

start = datetime.datetime.now()
################## Simulation Parameters ##################
rabiParams = ParamObj('rabiParams')
rabiParams.offset = 1000
rabiParams.sweepMax = 1
rabiParams.g = 1
rabiParams.sweepMin = -51
rabiParams.StepSize = 0.02
rabiParams.sweepPerturbation = 0.01
rabiParams.resonatorDimension = 20
rabiParams.sweepKey = 'resonator Frequency'
rabiParams.finalTime = 5

rabiParams.initialState = sp.kron(basis(rabiParams.resonatorDimension, 0), basis(2, 1), format='csc')
Hamiltonians(rabiParams, resonatorDimension=rabiParams.resonatorDimension)

parityOp = parityEXP(rabiParams.HamiltonianCavity)
photonN = rabiParams.HamiltonianCavity


################## Parallel Simulation/Computation Functions ##################
def ev(obj, sweep):
    obj.resonatorFrequency = sweep
    stat = timeEvolve(obj)
    return stat


def ex(operator,states):
    par = []
    for j in range(len(states)):
        par.append(expectationSparse(operator, states[j]))
    return par


################## Simulation ##################
p = Pool(processes=cpu_count())

rabiParams.unitary = digitalRabi
statesDigital = p.map(partial(ev, rabiParams), rabiParams.sweepList)
rabiParams.unitary = idealRabi
statesIdeal = p.map(partial(ev, rabiParams), rabiParams.sweepList)

################## Computation ##################
parityDigital = p.map(partial(ex, parityOp),statesDigital)
parityIdeal = p.map(partial(ex, parityOp),statesIdeal)
photonDigital = p.map(partial(ex, photonN),statesDigital)
photonIdeal = p.map(partial(ex, photonN),statesIdeal)
p.close()
p.join()

rabiParams.results['Parity Digital'] = parityDigital
rabiParams.results['Parity Ideal'] = parityIdeal
rabiParams.results['Photon Digital'] = photonDigital
rabiParams.results['Photon Ideal'] = photonIdeal

SimulationFidelity = []
for i in range(len(statesDigital)):
    fid = []
    for k in range(len(statesDigital[0])):
        fid.append(fidelitySparse(statesDigital[i][k], statesIdeal[i][k]))
    SimulationFidelity.append(fid)

rabiParams.results['Simulation Fidelity'] = SimulationFidelity

pertFidelityDigital = []
pertFidelityIdeal = []
for h in range(len(statesDigital)):
    fidD = []
    fidI = []
    for bb in range(len(statesDigital[0])):
        fidD.append(fidelitySparse(statesDigital[h][bb], statesDigital[h-1][bb]))
        fidI.append(fidelitySparse(statesIdeal[h][bb], statesIdeal[h-1][bb]))
    pertFidelityDigital.append(fidD)
    pertFidelityIdeal.append(fidI)

rabiParams.results['Pertubation Fidelity Digital'] = pertFidelityDigital
rabiParams.results['Pertubation Fidelity Ideal'] = pertFidelityIdeal
rabiParams.results['x'] = rabiParams.sweepList
rabiParams.results['y'] = rabiParams.times
rabiParams.save()


end = datetime.datetime.now()
print(end - start)

################## Plotting Function ##################
def plot(Z,min, max, x = None):
    if not isinstance(x, list):
        Y, X = np.meshgrid(rabiParams.times, rabiParams.sweepList)
    else:
        Y, X = np.meshgrid(rabiParams.times, x)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plottingSet(ax)
    if min == 0:
        cmap = createMAP('PuYl')
    else:
        cmap = createMAP('PuYlGn')
    surf1 = ax.pcolormesh(X, Y, Z, cmap=cmap, norm=normalizeCMAP(cmap, min, max))
    cbar = plt.colorbar(surf1)


################## Plotting ##################
plot(pertFidelityIdeal, 0, 1)
plot(pertFidelityDigital, 0, 1)
plot(SimulationFidelity, 0,1)
plot(parityDigital, -1, 1)
plot(parityIdeal, -1, 1)
plot(photonDigital, 0, rabiParams.resonatorDimension)
plot(photonIdeal, 0, rabiParams.resonatorDimension)
plt.show()