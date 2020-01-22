import matplotlib.pyplot as plt
import Plotting.Functions as pltFncs
import numpy as np
import Plotting.plottingSettings as pltSet

def cb(cbar, ticks):
    cbar.ax.tick_params(labelsize=20)

    for l in cbar.ax.yaxis.get_ticklabels():
        l.set_weight("bold")
    cbar.set_ticks(ticks)


def colorPlot(x,y, z, maxC=1, minC=-1, mapC = 'PuYlGn', irregular=False):
    if (mapC == 'PuYlGn') and (minC == 0):
        mapC == 'PuYl'

    if irregular == False:
        cm = pltFncs.createMAP(mapC)
        fig2, ax2 = plt.subplots()
        pltSet.plottingSet(ax2)
        Y, X = np.meshgrid(y, x)
        surf2 = ax2.pcolormesh(X, Y, z, cmap=cm, norm=pltFncs.normalizeCMAP(cm, minC, maxC))
        cbar = plt.colorbar(surf2)
        cb(cbar,[minC,(minC+maxC)/2,maxC])
        plt.show()
        return surf2
    else:
        surf2 = colorPlotIreg(x, y[-1], z, maxC, minC, mapC)
        cbar = plt.colorbar(surf2)
        cb(cbar,[minC,(minC+maxC)/2,maxC])
        return surf2


def colorPlotIreg(x, y, z, maxC=1, minC=-1, mapC = 'PuYlGn'):
    fig2, ax2 = plt.subplots()
    pltSet.plottingSet(ax2)
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
        cm = pltFncs.createMAP(mapC)
        surf2 = ax2.pcolormesh(X, Y, Z0, cmap=cm, norm=pltFncs.normalizeCMAP(cm, minC, maxC))
    return surf2