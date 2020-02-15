# TODO turn prints into actual error raise, they are print for testing

def qSystemInitErrors(init):
    def new_function(obj, **kwargs):
        init(obj, **kwargs)
        if obj.dimension is None:
            className = obj.__class__.__name__
            print(className + ' requires a dimension')
        elif obj.frequency is None:
            className = obj.__class__.__name__
            print(className + ' requires a frequency')
    return new_function


def qCouplingInitErrors(init):
    def new_function(obj, *args):
        init(obj, *args)
        if obj._qCoupling__cFncs is None:
            className = obj.__class__.__name__
            print(className + ' requires a coupling functions')
        elif obj._qCoupling__qSys is None:
            className = obj.__class__.__name__
            print(className + ' requires a coupling systems')
        
        for ind in range(len(obj._qCoupling__qSys)):
            if len(obj._qCoupling__cFncs) != len(obj._qCoupling__qSys):
                className = obj.__class__.__name__
                print(className + ' requires same number of systems as coupling functions')

    return new_function