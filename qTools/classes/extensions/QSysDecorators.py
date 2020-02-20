import scipy.sparse as sp
from qTools.classes.QUni import qUniversal


def asignState(stateCreationFunc):
    def InitialStateDecorator(initialState):
        def wrapper(obj, inp):
            print(inp)
            if sp.issparse(inp):
                if inp.shape[0] == obj.dimension:
                    obj._genericQSys__initialState = inp
                    print('here3')
                else:
                    print('dude')
            elif isinstance(inp, int):
                obj._genericQSys__initialState = stateCreationFunc(obj.dimension, inp)
            elif len(inp) == len(obj.qSystems):
                print('creating state')
                dims = [val.dimension for val in obj.qSystems.values()]
                obj._genericQSys__initialState = stateCreationFunc(dims, inp)
            print('here2')
        return wrapper
    return InitialStateDecorator


def addCreateInstance(functionToCall):
    def systemAddCreateDecorator(addCreate):
        def wrapper(obj, clsInst, *args, **kwargs):
            newSub = None
            if isinstance(clsInst, qUniversal):
                if clsInst.superSys is None:
                    newSub = functionToCall(obj, clsInst)
                elif clsInst.superSys is obj:
                    clasOfNew = clsInst.__class__
                    newSub = clasOfNew.createCopy(clsInst, *args)
                    newSub = functionToCall(obj, newSub, *args)
                    print('Sub system is already in the composite, copy created and added')
            elif isinstance(clsInst, list):
                newSub = functionToCall(obj, 'qCoupling', clsInst, *args, **kwargs)
            else:
                newSub = clsInst(*args, **kwargs)
                newSub =functionToCall(obj, newSub, *args)
            newSub._qUniversal__setKwargs(**kwargs)
            newSub.superSys = obj
            obj.subSystems[newSub.name] = newSub
            return newSub
        return wrapper
    return systemAddCreateDecorator


def constructConditions(keyWords):
    def constructDecorator(construct):
        def wrapper(obj):
            for key, val in keyWords.items():
                if not isinstance(getattr(obj, key), val):
                    print(key + ' is not given for ' + obj.name)
                    return None
            else:
                contructedObj = construct(obj)
            return contructedObj
        return wrapper
    return constructDecorator
