import datetime
from classes.parameterObj import ParamObj
from RabiModel.Modules.Hamiltonians import Hamiltonians
from RabiModel.Modules.Evolutions_Unitary import digitalRabi, idealRabi
from QuantumToolbox.TimeEvolution import timeEvolve
from QuantumToolbox.operators import parityEXP
from QuantumToolbox.functions import expectationSparse
import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sp
from QuantumToolbox.states import basis
from multiprocessing import Pool, cpu_count
from functools import partial
from Plotting.Functions import createMAP, normalizeCMAP


start = datetime.datetime.now()

rabiParams = ParamObj('rabiParams')
rabiParams.initialState = sp.kron(basis(rabiParams.resonatorDimension, 0), basis(2, 1), format='csc')
Hamiltonians(rabiParams, resonatorDimension=rabiParams.resonatorDimension)
rabiParams.unitary = digitalRabi
parityOp = parityEXP(rabiParams.HamiltonianCavity)
states = []


##### loop comp #####
"""def ex(states):
    par = []
    for j in range(len(states)):
        par.append(expectationSparse(parityOp, states[j]))
    return par

for i in range(len(rabiParams.sweepList)):
    rabiParams.resonatorFrequency = rabiParams.sweepList[i]
    state = timeEvolve(rabiParams)
    states.append(state)
    
parity = []
for k in range(len(states)):
    parity.append(ex(states[k]))"""
##### loop comp #####

##### parallel comp #####
def ev(sweep):
    rabiParams.resonatorFrequency = sweep
    stat = timeEvolve(rabiParams)
    return stat

def ex(states):
    par = []
    for j in range(len(states)):
        par.append(expectationSparse(parityOp, states[j]))
    return par

p = Pool(processes=cpu_count())

states = p.map(ev, rabiParams.sweepList)
rabiParams.statesToSave(states)
parity = p.map(ex, states)
p.close()
p.join()
rabiParams.save()
##### parallel comp #####


end = datetime.datetime.now()
print(end - start)

Y, X = np.meshgrid(rabiParams.times, rabiParams.sweepList)
Z = parity

fig = plt.figure()
ax = fig.add_subplot(111)
cmap =createMAP('PuYlGn')
surf1 = ax.pcolormesh(X, Y, Z, cmap=cmap, norm=normalizeCMAP(cmap, -1, 1))
cbar = plt.colorbar(surf1)
plt.show()