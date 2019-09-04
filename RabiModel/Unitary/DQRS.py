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
rabiParams.sweepMax = 2.4
rabiParams.sweepMin = -2.4
rabiParams.StepSize = 0.01
#rabiParams.bitflipTime = 2*rabiParams.StepSize
rabiParams.bitflipTime = 0.04
rabiParams.sweepPerturbation = 0.05
rabiParams.resonatorDimension = 200
rabiParams.sweepKey = 'resonator Frequency'
rabiParams.finalTime = 1.2

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

def fid(lis):
    fid = []
    for imn in range(len(lis[0])):
        fid.append(fidelitySparse(lis[0][imn], lis[1][imn]))
    return fid


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


p.close()
p.join()


end = datetime.datetime.now()
print(end - start)

################## Plotting Function ##################
def plot(Z,min, max):
    Y, X = np.meshgrid(rabiParams.times, rabiParams.sweepList)
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
plot(SimulationFidelity, 0,1)
plot(parityDigital, -1, 1)
plot(parityIdeal, -1, 1)
plot(photonDigital, 0, rabiParams.resonatorDimension)
plot(photonIdeal, 0, rabiParams.resonatorDimension)
plt.show()