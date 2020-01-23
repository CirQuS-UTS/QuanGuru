import matplotlib.pyplot as plt
import Plotting.Functions as pltFncs
import numpy as np


def colorPlot(x, y, z, irregular=False):
    if irregular is False:
        cm = plt.get_cmap('inferno')
        fig2, ax2 = plt.subplots()
        Y, X = np.meshgrid(y, x)
        surf2 = ax2.pcolormesh(X, Y, z, cmap=cm, norm=pltFncs.normalizeCMAP(cm, -1, 1))
        cbar = plt.colorbar(surf2)
        cbar.set_ticks([-1, 0, 1])
        plt.show()
        print('s')
        return surf2
    else:
        surf2 = colorPlotIreg(x, y[-1], z)
        cbar = plt.colorbar(surf2)
        cbar.set_ticks([-1, 0, 1])
        return surf2


def colorPlotIreg(x, y, z):
    fig2, ax2 = plt.subplots()
    for hdgf in range(len(x) - 1):
        StepSize = x[hdgf]
        Y0 = np.arange(0, y + StepSize, StepSize)
        X0 = [StepSize, StepSize + x[hdgf + 1] - x[hdgf]]
        Z0 = []
        for bkg in range(len(Y0)):
            z0 = []
            z0.append(z[hdgf][bkg])
            Z0.append(z0)

        X, Y = np.meshgrid(X0, Y0)
        cm = plt.get_cmap('inferno')
        surf2 = ax2.pcolormesh(X, Y, Z0, cmap=cm, norm=pltFncs.normalizeCMAP(cm, -1, 1))
    return surf2
