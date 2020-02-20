import scipy.sparse as sp


def asignState(stateCreationFunc):
    def InitialStateDecorator(initialState):
        def wrapper(obj, inp):
            if sp.issparse(inp):
                if inp.shape[0] == obj.dimension:
                    obj._genericQSys__initialState = inp
                else:
                    print('dude')
            elif isinstance(inp, int):
                obj._genericQSys__initialState = stateCreationFunc(obj.dimension, inp)
            elif len(inp) == len(obj.subSystems):
                dims = [val.dimension for val in obj.subSystems.values()]
                obj._genericQSys__initialState = stateCreationFunc(dims, inp)
        return wrapper
    return InitialStateDecorator