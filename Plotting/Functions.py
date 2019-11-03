##################  plotting libraries ################## 
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import BoundaryNorm

def __txtTocdict(file, half=False):
    list1 = []
    with open(file, "r") as inputfile:
        ina = 0
        for line in inputfile:
            if ina < 128:
                list2 = []
                for i in range(3):
                    list2.append(float(line.strip().split(',')[i]))
                list1.append(list2)
                if half == True:
                    ina += 1
            else:
                break
    return list1

def createMAP(name, half=False):
    root = '/Users/cahitkargi/PycharmProjects/quantum-simulations'
    if name == 'GnYlPu':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict(root+ "/Plotting/colormaps/GnYlPu.txt", half))
    elif name == 'PuYlGn':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict(root+"/Plotting/colormaps/PuYlGn.txt", half))
    elif name == 'YlPu':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict(root+"/Plotting/colormaps/YlPu.txt", half))
    elif name == 'PuYl':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict(root+"/Plotting/colormaps/PuYl.txt", half))
    else:
        cmap = plt.get_cmap(name)
    return cmap

def normalizeCMAP(cmap, llim, ulim):
    levels = MaxNLocator(nbins=999).tick_values(llim, ulim)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
    return norm

def grid(n,m):
    axList = []
    for i in range(n):
        for j in range(m):
            ax = plt.subplot2grid((n, m), (i, j), colspan=1)
            axList.append(ax)
    return axList