##################  plotting libraries ################## 
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import MaxNLocator
from matplotlib.colors import BoundaryNorm

def __txtTocdict(file):
    list1 = []
    with open(file, "r") as inputfile:
        for line in inputfile:
            list2 = []
            for i in range(3):
                list2.append(float(line.strip().split(',')[i]))
            list1.append(list2)
    return list1

def createMAP(name):
    if name == 'GnYlPu':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict("/Users/cahitkargi/PycharmProjects/quantum-simulations/Plotting/colormaps/GnYlPu.txt"))
    elif name == 'PuYlGn':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict("/Users/cahitkargi/PycharmProjects/quantum-simulations/Plotting/colormaps/PuYlGn.txt"))
    elif name == 'YlPu':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict("/Users/cahitkargi/PycharmProjects/quantum-simulations/Plotting/colormaps/YlPu.txt"))
    elif name == 'PuYl':
        cmap = LinearSegmentedColormap.from_list('my_map', __txtTocdict("/Users/cahitkargi/PycharmProjects/quantum-simulations/Plotting/colormaps/PuYl.txt"))
    else:
        cmap = plt.get_cmap(name)
    return cmap

def normalizeCMAP(cmap, llim, ulim):
    levels = MaxNLocator(nbins=999).tick_values(llim, ulim)
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
    return norm