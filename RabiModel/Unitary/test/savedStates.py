from SaveRead.saveH5 import readData
import datetime
from QuantumToolbox.functions import expectationSparse
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool, cpu_count
from QuantumToolbox.operators import number, identity
from QuantumToolbox.operators import parityEXP
from classes.parameterObj import ParamObj
import scipy.sparse as sp

data = readData(1567416516.606023, 'states')

parityOp = parityEXP(sp.kron(number(200), identity(2), format='csc')).toarray()

def ex(states):
    par = []
    for j in range(len(states)):
        par.append(expectationSparse(parityOp, sp.csc_matrix(states[j])))
    return par

p = Pool(processes=cpu_count())

parity = p.map(ex, data)
p.close()
p.join()
##### parallel comp #####


end = datetime.datetime.now()

rabiParams = ParamObj('rabiParams')
Y, X = np.meshgrid(rabiParams.times, rabiParams.sweepList)
Z = parity

fig = plt.figure()
ax = fig.add_subplot(111)
surf1 = ax.pcolormesh(X, Y, Z, cmap="inferno")
cbar = plt.colorbar(surf1)
plt.show()