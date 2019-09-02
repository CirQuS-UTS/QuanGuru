def __Unitary(states, Unitary, loop, times):
    if loop:
        for ijkn in range(len(times) - 1):
            state = Unitary @ states[-1]
            states.append(state)
    else:
        state = Unitary @ states[-1]
        states.append(state)
    return states


def __evolTime(obj, states, unitary, loop, times):
    if not obj.subTrotter:
        stepSize = obj.StepSize
        Unitary = unitary(obj, stepSize)
        states = __Unitary(states, Unitary, loop, times)
    else:
        if obj.constantTrotterStep:
            stepSize = obj.TrotterStep
            Unitary = unitary(obj, stepSize)
            for kngd in range(len(times)):
                states = __Unitary(states, Unitary, loop, times)
        else:
            for kngd in range(len(times)):
                stepSize = obj.TrotterStep
                Unitary = unitary(obj, stepSize)
                states = __Unitary(states, Unitary, loop, times)
    return states


def timeEvolve(obj):
    unitary = obj.unitary
    states = [obj.initialState]
    timeDepHam = obj.timeDepHam
    if not timeDepHam:
        states = __evolTime(obj, states, unitary, True, obj.times)
    else:
        timeKey = obj.timeKey
        constStep = obj.constantStepSize
        if constStep:
            for ifrt in range(len(obj.timeDepParam)):
                setattr(obj, timeKey, obj.timeDepParam[ifrt])
                states = __evolTime(obj, states, unitary, False, obj.TrotterTimes)
        else:
            for ifrt in range(len(obj.timeDepParam)):
                setattr(obj, timeKey, obj.timeDepParam[ifrt])
                setattr(obj, 'StepSize', obj.StepSizeList[ifrt])
                states = __evolTime(obj, states, unitary, False, obj.TrotterTimes)
    return states
