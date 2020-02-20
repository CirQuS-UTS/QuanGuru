
def Compute(compute):
    def wrapper(obj, qSys, state):
        if obj.compute is not None:
            if callable(obj.compute):
                results = obj.compute(qSys, state)
                return results
            else:
                pass
    return wrapper