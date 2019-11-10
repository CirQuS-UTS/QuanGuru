def evolveTimeIndep(obj, sweep):
    setattr(obj.systemParameters, obj.simulationParameters.sweepKey, sweep)
    unitary = obj.unitary
    state = obj.initialState
    stepSize = obj.systemParameters.StepSize
    Unitary = unitary(obj, stepSize)
    if obj.simulationParameters.allStates:
        states = [state]
        for ijkn in range(len(obj.times) - 1):
            state = Unitary @ state
            states.append(state)
        return states
    else:
        for ijkn in range(len(obj.times) - 1):
            state = Unitary @ state
        return state


def evolveTimeDep(obj, allStates = True):
    unitary = obj.unitary
    state = obj.initialState
    stepSize = obj.systemParameters.StepSize
    timeKey = obj.simulationParameters.timeKey
    if allStates:
        states = [state]
        for ijkn in range(len(obj.times) - 1):
            state = __timeDepEvol(obj,timeKey,obj.timeDepParam[ijkn],unitary,stepSize,state)
            states.append(state)
        return states
    else:
        for ijkn in range(len(obj.times) - 1):
            state = __timeDepEvol(obj,timeKey,obj.timeDepParam[ijkn],unitary,stepSize,state)
        return state


def evolveVaryingStep(obj, allStates = True):
    unitary = obj.unitary
    state = obj.initialState
    timeKey = obj.simulationParameters.timeKey
    if allStates:
        states = [state]
        for ijkn in range(len(obj.times) - 1):
            stepSize = obj.StepSizeList[ijkn]
            state = __timeDepEvol(obj,timeKey,obj.timeDepParam[ijkn],unitary,stepSize,state)
            states.append(state)
        return states
    else:
        for ijkn in range(len(obj.times) - 1):
            stepSize = obj.StepSizeList[ijkn]
            state = __timeDepEvol(obj,timeKey,obj.timeDepParam[ijkn],unitary,stepSize,state)
        return state


def __timeDepEvol(obj, timeKey, timeDepParam, unitary, stepSize, state):
    setattr(obj.systemParameters, timeKey, timeDepParam)
    Unitary = unitary(obj, stepSize)
    stateF = Unitary @ state
    return stateF
