import numpy as np

def drawSchematic(protocol, system, key, res=100):
    T = sum([step.time for step in protocol.steps])
    time = np.linspace(0, T, res)
    t = 0
    schematic = np.ones(res)
    
    for step in protocol.steps:
        if system in step._FreeEvolution__system:
            arg = step._FreeEvolution__system.index(system)
            value = step._FreeEvolution__value[arg]
        else:
            value = getattr(system, key)
        
        schematic[np.logical_and(time>=t , time<=t+step.time)] = value
        t += step.time 
    
    return time, schematic