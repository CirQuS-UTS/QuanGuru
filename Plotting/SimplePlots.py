import matplotlib.pyplot as plt
import Plotting.Functions as pltFncs
import numpy as np

def colorPlot(x,y, z):
    cm = plt.get_cmap('inferno')
    fig2, ax2 = plt.subplots()
    Y, X = np.meshgrid(y, x)
    surf2 = ax2.pcolormesh(X, Y, z, cmap=cm, norm=pltFncs.normalizeCMAP(cm, -1, 1))
    cbar = plt.colorbar(surf2)
    plt.show()
    return surf2