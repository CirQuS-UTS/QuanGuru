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

timestamp = 1567583365.299213
data = readData(timestamp, '')
print(data.keys())

"""parityOp = parityEXP(sp.kron(number(20), identity(2), format='csc')).toarray()

def ex(states):
    par = []
    for j in range(len(states)):
        par.append(expectationSparse(parityOp, sp.csc_matrix(states[j])))
    return par

p = Pool(processes=cpu_count())

parity = p.map(ex, data)
p.close()
p.join()"""
##### parallel comp #####


end = datetime.datetime.now()

Y, X = np.meshgrid(data['y'], data['x'])
Z = data['Pertubation Fidelity Digital']

fig = plt.figure()
ax = fig.add_subplot(111)
surf1 = ax.pcolormesh(X, Y, Z, cmap="inferno")
cbar = plt.colorbar(surf1)
plt.show()