def plottingSet(ax):
    ax.minorticks_on()
    ax.tick_params('both', which='minor', width=1, length=2)
    ax.tick_params('both', which='major', width=1, length=4)
    #######
    for axis in ['bottom', 'left', 'top', 'right']:
        ax.spines[axis].set_linewidth(2.0)
    #######
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(20)
        tick.label.set_fontweight('bold')
    #######
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(20)
        tick.label.set_fontweight('bold')
    #######
    ax.ticklabel_format(axis='y', style='plain')
    ax.ticklabel_format(axis='x', style='plain')