from HeisenbergModel.Modules.Evolutions_Unitary import DigitalTwo, DigitalThree, IdealTwo, IdealThree
from HeisenbergModel.Modules.Hamiltonians import twoQubitHeisenberg, threeQubitHeisenberg
from classes.parameterObj import ParamObj
from QuantumToolbox.TimeEvolution import timeEvolve
from QuantumToolbox.functions import expectationSparse, fidelitySparse
import scipy.sparse as sp
from QuantumToolbox.operators import sigmaz, identity
from QuantumToolbox.states import basis
import datetime
from multiprocessing import Pool, cpu_count
from functools import partial
from Plotting.plottingSettings import plottingSet
from Plotting.Functions import createMAP, normalizeCMAP
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

start = datetime.datetime.now()

heisenbergParams = ParamObj('heisenbergParams')
heisenbergParams.g = 2
heisenbergParams.finalTime = 5
heisenbergParams.sweepMax = 2
heisenbergParams.sweepMin = 0.001
heisenbergParams.sweepPerturbation = 0.001

heisenbergParams.results['x'] = []
heisenbergParams.results['y'] = []

twoQubitHeisenberg(heisenbergParams)
threeQubitHeisenberg(heisenbergParams)

population1 = sp.kron(sigmaz(), identity(2), format='csc')

heisenbergParams.initialState = sp.kron(basis(2,1), basis(2,0), format='csc')

def evolution(obj, sweep):
    obj.StepSize = sweep
    stat = timeEvolve(obj)
    return stat


def expectation(operator,states):
    par = []
    for j in range(len(states)):
        print(states[j])
        par.append(expectationSparse(operator, states[j]))
    return par

p = Pool(processes=cpu_count())
heisenbergParams.unitary = DigitalTwo
statesDigital = p.map(partial(evolution, heisenbergParams), heisenbergParams.sweepList)
for i in range(len(statesDigital)):
    heisenbergParams.StepSize = heisenbergParams.sweepList[i]
    heisenbergParams.results['x'].append([heisenbergParams.sweepList[i], heisenbergParams.sweepList[i] + heisenbergParams.sweepPerturbation])
    heisenbergParams.results['y'].append(heisenbergParams.times)

populationTwo = p.map(partial(expectation, population1),statesDigital)
p.close()
p.join()

end = datetime.datetime.now()
print(end - start)
def plot(x, y, Z, min, max, ax):
    X, Y = np.meshgrid(x, y)
    plottingSet(ax)
    if min == 0:
        cmap = createMAP('PuYlGn')
    else:
        cmap = createMAP('PuYlGn')
    surf1 = ax.pcolormesh(X, Y, Z, cmap=cmap, norm=normalizeCMAP(cmap, min, max))
    return surf1

fig = plt.figure()
ax = fig.add_subplot(111)
for hdgf in range(len(heisenbergParams.results['x'])):
    Z = []
    for bkg in range(len(heisenbergParams.results['y'][hdgf])):
        z = []
        z.append(populationTwo[hdgf][bkg])
        Z.append(z)
    surf1 = plot(heisenbergParams.results['x'][hdgf], heisenbergParams.results['y'][hdgf], Z, 0, 1, ax)
cbar = plt.colorbar(surf1)
ax.set_xscale("log", nonposx='clip')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(x), 0)))).format(x)))
plt.show()

