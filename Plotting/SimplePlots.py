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


def __pltEig(xax, Dims, Bins=None, x=None, Step=False, logScale=False, ax=None, Legend=True, xlim=0.04):
    if ax == None:
        ax = plt.gca()

    if (isinstance(Bins, np.ndarray) == True) or (isinstance(Bins, int)):
        ax.hist(xax, bins=Bins, density=True)
    else:
        ax.hist(xax, density=True)
    
    COE = [RMTdist.EigenVectorDist(X, int(Dims), 1) for X in x]
    CUE = [RMTdist.EigenVectorDist(X, int(Dims), 2) for X in x]
    CSE = [RMTdist.EigenVectorDist(X, int(Dims), 4) for X in x]

    if Step == False:
        ax.plot(x, COE, 'r-', label=r'COE ($\beta = 1$)')
        ax.plot(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
        ax.plot(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')
    elif Step == True:
        ax.step(x, COE, 'r-', label=r'COE ($\beta = 1$)')
        ax.step(x, CUE, 'g-', label=r'CUE ($\beta = 2$)')
        ax.step(x, CSE, 'b-', label=r'CSE ($\beta = 4$)')

    ax = pltSet.plottingSet(ax)
    
    if logScale == True:
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlim([0.00001, 1])
        ax.set_ylim([0.1, 10*Dims])
    elif logScale == False:
        ax.set_ylim([0, Dims])
        ax.set_xlim([0, xlim])
        ax.set_yticks([0.0, Dims/2, Dims])
        ax.set_xticks([0.0, xlim/2, xlim])

    if Legend == True:
        ax.legend(loc='upper right', fontsize='x-large')

    return 'nothing'

def _pltEig(xax, Dims, ax, Bins=None, Step=False, logScale=True, lvl=True, Legend=True, xLim=0.04):
    if lvl == True:
        if isinstance(Bins, np.ndarray) == True:
            bin_means = (np.histogram(Bins, Bins, weights=Bins)[0] / np.histogram(Bins, Bins)[0])
            __pltEig(xax, Dims, Bins, bin_means, Step, logScale, ax, Legend, xLim)
        else:
            x = np.arange(0.00001, 1, 0.00001)
            __pltEig(xax, Dims, Bins, x, Step, logScale, ax, Legend, xLim)
        return 'nothing'
    else:
        ax.hist(xax, density=True)
        return 'nothing'

def pltEig(xax, Dims, Bins=None, Step=False, logScale=True, lvl=True, ax=None, Legend=True, xlim=0.04):
    if ax == None:
        fig = plt.figure(figsize=(12, 9))
        _pltEig(xax, Dims, ax, Bins, Step, logScale, lvl, Legend, xlim)
        fig.text(0.5, 0.01, r'$|c_n|^2$', ha='center', fontsize=24)
        fig.text(0.005, 0.5, r'# of $|c_n|^2$', va='center', rotation='vertical', fontsize=24)
        plt.show()
        return 'nothing'
    else:
        _pltEig(xax, Dims, ax, Bins, Step, logScale, lvl, Legend, xlim)
        return 'nothing'