import scipy.sparse as sp
from qTools.classes.QUni import qUniversal


# def asignState(stateCreationFunc):
#    def InitialStateDecorator(initialState):
#        def wrapper(obj, inp):
#            obj._qBase__initialStateInput = inp
#            if sp.issparse(inp):
#                if inp.shape[0] == obj.dimension:
#                    obj._qBase__initialState = inp
#                else:
#                    print('Dimension mismatch')
#            else:
#                initialState(obj, inp)
#        return wrapper
#    return InitialStateDecorator


def InitialStateDecorator(initialState):
    def wrapper(obj, inp):
        obj._qBase__initialStateInput = inp # pylint: disable=protected-access
        if sp.issparse(inp):
            if inp.shape[0] == obj.dimension:
                obj._qBase__initialState = inp # pylint: disable=protected-access
            else:
                raise ValueError('Dimension mismatch')
        else:
            initialState(obj, inp)
    return wrapper

def addCreateInstance(functionToCall):
    def systemAddCreateDecorator():
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
                newSub = functionToCall(obj, 'qCoupling', clsInst, *args)
            else:
                newSub = clsInst(*args)
                newSub = functionToCall(obj, newSub, *args)
            newSub._qUniversal__setKwargs(**kwargs)
            newSub.superSys = obj
            #obj.subSys[newSub.name] = newSub
            return newSub
        return wrapper
    return systemAddCreateDecorator


def constructConditions(keyWords):
    def constructDecorator(construct):
        def wrapper(obj):
            for key, val in keyWords.items():
                if not isinstance(getattr(obj, key), val):
                    print(key + ' is not given for ' + obj.name)
                    contructedObj = None
                    break
            else:
                contructedObj = construct(obj)
            return contructedObj
        return wrapper
    return constructDecorator
