import SaveRead.saveH5 as resa
import matplotlib.pyplot as plt
import numpy as np
import Plotting.plottingSettings as pltSet
import Plotting.Functions as pltFncs


"""
A terrible script that just works to test saved data
"""

timestamp10ns = 1572004073.247852
data10ns = resa.readData(timestamp10ns, '')
print(data10ns.keys())
print(data10ns.attrs.keys())

################## Plotting Function ##################
def plot(x, y, Z, min, max, ax, map = 'PuYlGn'):
    X, Y = np.meshgrid(x, y)
    pltSet.plottingSet(ax)
    cmap = pltFncs.createMAP(map)
    surf1 = ax.pcolormesh(X, Y, Z, cmap=cmap, norm=pltFncs.normalizeCMAP(cmap, min, max))
    return surf1


def plotR(x, y, Z, min, max, ax, map = 'PuYlGn'):
    Y, X = np.meshgrid(y, x)
    pltSet.plottingSet(ax)
    cmap = pltFncs.createMAP(map)
    surf1 = ax.pcolormesh(X, Y, Z, cmap=cmap)
    return surf1

def plotLine(x,y,ax,color,style,labbel):
    pltSet.plottingSet(ax)
    plt.plot(x,y,color=color,linestyle=style, label=labbel)
################## Plotting ##################

"""fig = plt.figure(figsize=(12,9))
ax = pltFncs.grid(2,1)
ax1 = pltFncs.grid(1,1)"""

fig, axs = plt.subplots(figsize=(12,9),ncols=2, nrows=3)
gs1 = axs[0, 0].get_gridspec()
gs2 = axs[0, 1].get_gridspec()
gs3 = axs[2, 0].get_gridspec()
# remove the underlying axes
for ax in [axs[0, 0],axs[1,0]]:
    ax.remove()

for ax in [axs[0, 1],axs[1,1]]:
    ax.remove()

for ax in [axs[2, 0],axs[2,1]]:
    ax.remove()

ax1 = fig.add_subplot(gs1[0:-1, 0])
ax2 = fig.add_subplot(gs1[0:-1, 1])
ax3 = fig.add_subplot(gs1[-1, 0])


"""print(list(data10ns['Photon Digital']))
plotR(data10ns['x'], data10ns['y'], data10ns['Loschmidt Echo Digital'], 0, 1, ax[0], map='PuYl')
plotR(data10ns['x'], data10ns['y'], data10ns['Loschmidt Echo Ideal'], 0, 1, ax[1], map='PuYl')
plotR(data10ns['x'], data10ns['y'], np.real(np.array(data10ns['Photon Digital'])), 0, 1, ax[2], map='PuYl')
surf = plotR(data10ns['x'], data10ns['y'], np.real(np.array(data10ns['Photon Ideal'])), 0, 1, ax[3], map='PuYl')
cbar2 = plt.colorbar(surf, ax=ax[3])
plotR(data10ns['x'], data10ns['y'], data10ns['Simulation Fidelity'], 0, 1, ax[4], map='PuYl')"""

for hdgf in range(len(data10ns['x'])-1):
    Z0 = []
    Z1 = []
    Z2 = []
    Z3 = []
    Z4 = []
    Z5 = []
    Z6 = []
    Z7 = []
    Z8 = []
    Z9 = []
    Z10 = []
    for bkg in range(len(data10ns['y'][str(hdgf)])):
        z0 = []
        z1 = []
        z2 = []
        z3 = []
        z4 = []
        z5 = []
        z6 = []
        z7 = []
        z8 = []
        z9 = []
        z10 = []
        z0.append(data10ns['Photon Digital'][str(hdgf)][bkg])
        z1.append(data10ns['Photon Ideal'][str(hdgf)][bkg])
        z2.append(data10ns['Simulation Fidelity'][str(hdgf)][bkg])
        """z3.append(data10ns['Photon Ideal'][str(hdgf)][bkg])
        z4.append(data10ns['Photon Digital'][str(hdgf)][bkg])
        z5.append(data10ns['Photon Ideal'][str(hdgf)][bkg])
        z6.append(data10ns['Photon Digital'][str(hdgf)][bkg])
        z7.append(data10ns['Photon Ideal'][str(hdgf)][bkg])
        z8.append(data10ns['Loschmidt Echo Digital'][str(hdgf)][bkg])
        z9.append(data10ns['Loschmidt Echo Ideal'][str(hdgf)][bkg])
        z10.append(data10ns['Simulation Fidelity'][str(hdgf)][bkg])"""
        Z0.append(z0)
        Z1.append(z1)
        Z2.append(z2)
        Z3.append(z3)
        Z4.append(z4)
        Z5.append(z5)
        Z6.append(z6)
        Z7.append(z7)
        Z8.append(z8)
        Z9.append(z9)
        Z10.append(z10)
    surf1 = plot(1000*np.array(data10ns['x'][str(hdgf)]), data10ns['y'][str(hdgf)], Z0, 0, 500, ax1, map='PuYl')
    surf2 = plot(1000*np.array(data10ns['x'][str(hdgf)]), data10ns['y'][str(hdgf)], Z1, 0, 500, ax2, map='PuYl')
    surf3 = plot(1000*np.array(data10ns['x'][str(hdgf)]), data10ns['y'][str(hdgf)], Z2, 0, 1, ax3, map='GrYl')
    """surf4 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z3, 0, 100, ax[3])
    surf5 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z4, 0, 1, ax[4])
    surf6 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z5, 0, 1, ax[5])
    surf7 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z6, 1, 50, ax[6])
    surf8 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z7, 1, 50, ax[7])
    surf9 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z8, 0, 1, ax[8])
    surf10 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z9, 0, 1, ax[9])
    surf11 = plot(data10ns['x'][str(hdgf)], data10ns['y'][str(hdgf)], Z10, 0, 1, ax[10])"""


def cb(cbar, ticks):
    cbar.ax.tick_params(labelsize=20)

    for l in cbar.ax.yaxis.get_ticklabels():
        l.set_weight("bold")
    cbar.set_ticks(ticks)

cbar1 = plt.colorbar(surf1, ax=ax1)
cb(cbar1,[0,200,400])
cbar2 = plt.colorbar(surf2, ax=ax2)
cb(cbar2,[-1,200,400])
cbar3 = plt.colorbar(surf3, ax=ax3)
cb(cbar3,[0,0.5,1])
"""cbar4 = plt.colorbar(surf4, ax=ax[3])
cb(cbar4,[0,50,100])
cbar5 = plt.colorbar(surf5, ax=ax[4])
cb(cbar5,[0,0.5,1])
cbar6 = plt.colorbar(surf6, ax=ax[5])
cb(cbar6,[0,0.5,1])
cbar7 = plt.colorbar(surf7, ax=ax[6])
cb(cbar7,[0,25,50])
cbar8 = plt.colorbar(surf8, ax=ax[7])
cb(cbar8,[0,25,50])
cbar9 = plt.colorbar(surf9, ax=ax[8])
cb(cbar9,[0,0.5,1])
cbar10 = plt.colorbar(surf10, ax=ax[9])
cb(cbar10,[0,0.5,1])
cbar11 = plt.colorbar(surf11, ax=ax[10])
cb(cbar11,[0,0.5,1])"""


def axL(ax, y=False,x=False):
    ax.set_ylim([0, 2])
    #ax.set_xlim([1, 100])
    if y == True:
        ax.set_yticks([0.0,1, 2])
    else:
        ax.set_yticklabels([''] * 10)

    if x == True:
        ax.set_xticks([0, 0.02, 0.04, 0.06, 0.08, 0.1])
    else:
        ax.set_xticklabels([''] * 10)

axL(ax=ax1, y=True, x=True)
axL(ax=ax2, x=True)
axL(ax=ax3, y=True, x=True)

ax1.set_xscale('log')
ax2.set_xscale('log')
ax3.set_xscale('log')

"""ax1.set_xlim([0.001, 0.1])
ax2.set_xlim([0.001, 0.1])
ax3.set_xlim([0.001, 0.1])"""


"""axL(ax=ax[3])
axL(ax=ax[4], y=True)
axL(ax=ax[5])
axL(ax=ax[6], y=True)
axL(ax=ax[7])
axL(ax=ax[8], y=True)
axL(ax=ax[9], x=True)
axL(ax=ax[10], y=True, x=True)
ax[11].set_axis_off()"""

plt.show()