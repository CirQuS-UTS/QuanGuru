import matplotlib.pyplot as plt
import Plotting.Functions as pltFncs
import numpy as np
import Plotting.plottingSettings as pltSet
import RMT_statistics.Modules.Distributions as RMTdist

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


def _pltEig(xax, Dims, Bins, x, Step=False, logScale=False):
    plt.hist(xax, bins=Bins, density=True)

    COE = [RMTdist.EigenVectorDist(X, int(Dims), 1) for X in x]
    CUE = [RMTdist.EigenVectorDist(X, int(Dims), 2) for X in x]
    CSE = [RMTdist.EigenVectorDist(X, int(Dims), 4) for X in x]

    if Step == False:
        plt.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
        plt.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
        plt.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
    elif Step == True:
        plt.step(x, COE, 'r-', label=r'COE ($\beta = 1$)')
        plt.step(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
        plt.step(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')

    ax = plt.gca()
    pltSet.plottingSet(ax)
    #ax.set_xticks([0.0, 0.075, 0.15])
    #ax.set_yticks([0, 100, 200])
    if logScale == True:
        ax.set_xscale('log')
        ax.set_yscale('log')
        plt.xlim([0.00001, 1])
        plt.ylim([0.1, 10*Dims])
    elif logScale == False:
        ax.set_ylim([0, 0.5 * Dims])
        ax.set_xlim([0, 0.04])

    plt.legend(loc='upper right', fontsize='x-large')


def pltEig(xax, Dims, Bins=None, Step=False, logScale=True, lvl=True):
    fig = plt.figure(figsize=(12, 9))
    if lvl == True:
        if isinstance(Bins, np.ndarray) == True:
            bin_means = (np.histogram(Bins, Bins, weights=Bins)[0] / np.histogram(Bins, Bins)[0])
            _pltEig(xax, Dims, Bins, bin_means, Step, logScale)
        else:
            x = np.arange(0.00001, 1, 0.00001)
            _pltEig(xax, Dims, 50, x, Step, logScale)
    else:
        plt.hist(xax, density=True)
    fig.text(0.5, 0.01, r'$|c_n|^2$', ha='center', fontsize=24)
    fig.text(0.005, 0.5, r'Prob($|c_n|^2$)', va='center', rotation='vertical', fontsize=24)
    plt.show()