import HeisenbergModel.Modules.Evolutions_Unitary as uniEvo
import HeisenbergModel.Modules.Hamiltonians as hams
import classes.parameterObj as pObj
import QuantumToolbox.TimeEvolution as tEvo
import QuantumToolbox.functions as qFncs
import scipy.sparse as sp
import QuantumToolbox.operators as qOps
import QuantumToolbox.states as states
import datetime
from multiprocessing import Pool, cpu_count
from functools import partial
import Plotting.plottingSettings as pltSet
import Plotting.Functions as pltFncs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

start = datetime.datetime.now()

heisenbergParams = pObj.Model()
heisenbergParams.simulationParameters.sweepKey = 'StepSize'
heisenbergParams.systemParameters.g = 2
heisenbergParams.simulationParameters.finalTime = 5
heisenbergParams.simulationParameters.sweepMax = 2
heisenbergParams.simulationParameters.sweepMin = 0.01
heisenbergParams.simulationParameters.sweepPerturbation = 0.01

heisenbergParams.simulationParameters.results['x'] = []
heisenbergParams.simulationParameters.results['y'] = []

hams.twoQubitHeisenberg(heisenbergParams)
hams.threeQubitHeisenberg(heisenbergParams)

population1 = sp.kron(qOps.sigmaz(), qOps.identity(2), format='csc')

heisenbergParams.initialState = sp.kron(states.basis(2,1), states.basis(2,0), format='csc')


p = Pool(processes=cpu_count())
heisenbergParams.unitary = uniEvo.DigitalTwo
statesDigital = p.map(partial(tEvo.evolveTimeIndep, heisenbergParams), heisenbergParams.sweepList)
for i in range(len(statesDigital)):
    heisenbergParams.StepSize = heisenbergParams.sweepList[i]
    heisenbergParams.simulationParameters.results['x'].append([heisenbergParams.sweepList[i],
                                                           heisenbergParams.sweepList[i] +
                                                           heisenbergParams.simulationParameters.sweepPerturbation])
    heisenbergParams.simulationParameters.results['y'].append(heisenbergParams.times)

populationTwo = p.map(partial(qFncs.expectationList, population1),statesDigital)
p.close()
p.join()

end = datetime.datetime.now()
print(end - start)
def plot(x, y, Z, min, max, ax):
    X, Y = np.meshgrid(x, y)
    pltSet.plottingSet(ax)
    if min == 0:
        cmap = pltFncs.createMAP('PuYlGn')
    else:
        cmap = pltFncs.createMAP('PuYlGn')
    surf1 = ax.pcolormesh(X, Y, Z, cmap=cmap, norm=pltFncs.normalizeCMAP(cmap, min, max))
    return surf1

fig = plt.figure()
ax = fig.add_subplot(111)
for hdgf in range(len(heisenbergParams.simulationParameters.results['x'])):
    Z = []
    for bkg in range(len(heisenbergParams.simulationParameters.results['y'][hdgf])):
        z = []
        z.append(populationTwo[hdgf][bkg])
        Z.append(z)
    surf1 = plot(heisenbergParams.simulationParameters.results['x'][hdgf], heisenbergParams.simulationParameters.results['y'][hdgf], Z, 0, 1, ax)
cbar = plt.colorbar(surf1)
ax.set_xscale("log", nonposx='clip')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(x), 0)))).format(x)))
plt.show()

