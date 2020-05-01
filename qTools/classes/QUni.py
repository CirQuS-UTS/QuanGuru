"""
    Module for the class qUniversal, which is inhereted by all other classes in this library.
"""

from collections import OrderedDict

__all__ = [
    'qUniversal'
]

def checkClass(classOf):
    """
        This is a decorator
    """
    def addDecorator(addRemoveFunction):
        def wrapper(obj, inp, **kwargs):
            clsDecoArg = globals()[classOf]
            if isinstance(inp, clsDecoArg):
                if getattr(inp, '_qUniversal__ind') is None:
                    if obj is not inp:
                        setattr(inp, '_qUniversal__ind', len(getattr(obj, '_qUniversal__subSys')))
                addRemoveFunction(obj, inp, **kwargs)
            elif isinstance(inp, str):
                if str in clsDecoArg.instNames.keys():
                    inp = wrapper(obj, clsDecoArg.instNames[inp], **kwargs)
                else:
                    clsInput = globals()[inp]
                    inp = wrapper(obj, clsInput, **kwargs)
            elif isinstance(inp, dict):
                for sys in inp.values():
                    # what to do with the keys?
                    inp = wrapper(obj, sys, **kwargs)
            elif inp is None:
                setattr(obj, '_qUniversal__subSys', OrderedDict())
                return getattr(obj, '_qUniversal__subSys', OrderedDict())
            elif inp.__class__ is type:
                newSys = inp()
                inp = wrapper(obj, newSys, **kwargs)
            else:
                for sys in inp:
                    inp = wrapper(obj, sys, **kwargs)
            return inp
        return wrapper
    return addDecorator


class extendedList(list):
    """
        this is a class
    """
    def extendedCopy(self, iterable):
        """
            This is a method
        """
        baseList = extendedList()
        for it in self:
            baseList.append(it)
        for exIt in iterable:
            baseList.append(exIt)
        return baseList


class qUniversal:
    """
        This is qUniversal
    """
    instances = 0
    label = 'qUniversal'
    instNames = {}

    toBeSaved = extendedList(['name'])

    __slots__ = ['__name', '__superSys', '__ind', '__subSys', '__allInstances', '__matrix']

    def __init__(self, **kwargs):
        super().__init__()
        self._incrementInstances()
        self.__name = self._qUniversal__namer()
        self.__superSys = None
        self.__subSys = OrderedDict()
        self.__ind = None
        self.__allInstances = qUniversal.instNames
        self.__matrix = None
        if kwargs['name'] is not None:
            self._qUniversal__setKwargs(name=kwargs.pop('name'), **kwargs)
        else:
            kwargs.pop('name')
            self._qUniversal__setKwargs(**kwargs)

    #def __del__(self):
    #    class_name = self.__class__.__name__

    def save(self):
        """
            This is save method
        """
        saveDict = {}
        for k in self.toBeSaved:
            val = getattr(self, k)
            if val is not None:
                saveDict[k] = val
        saveDict['class'] = self.__class__.__name__
        return saveDict

    def getObjByName(self, name):
        """
            A method
        """
        return self._qUniversal__allInstances[name]

    def __setKwargs(self, **kwargs):
        """
            A method
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

    def resetSubSys(self):
        """
            A method
        """
        setattr(self, '_qUniversal__subSys', OrderedDict())

    @property
    def subSys(self):
        """
            A method
        """
        return self._qUniversal__subSys

    @subSys.setter
    def subSys(self, subS):
        self.addSubSys(subS)

    @checkClass('qUniversal')
    def addSubSys(self, subS, **kwargs):
        """
            A method
        """
        subS._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        self._qUniversal__subSys[subS.name] = subS

    @checkClass('qUniversal')
    def removeSubSys(self, subS, **kwargs):
        """
            A method
        """
        subS._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        obj = self._qUniversal__subSys.pop(subS.name)
        self._updateInd()
        print(obj.name + ' is removed from subSys of ' + self.name)

    def _updateInd(self):
        """
            A method
        """
        for ind, obj in enumerate(self._qUniversal__subSys):
            obj.ind = ind

    @checkClass('qUniversal')
    def createSubSys(self, subSysClass, **kwargs):
        """
            A method
        """
        subSysClass._qUniversal__setKwargs(**kwargs) # pylint: disable=W0212
        self._qUniversal__subSys[subSysClass.name] = subSysClass

    @property
    def superSys(self):
        """
            A property
        """
        return self._qUniversal__superSys

    @superSys.setter
    def superSys(self, supSys):
        """
            A property setter
        """
        setattr(self, '_qUniversal__superSys', supSys)

    @property
    def ind(self):
        """
            A property
        """
        return self._qUniversal__ind

    @property
    def name(self):
        """
            A property
        """
        return self._qUniversal__name

    @name.setter
    def name(self, name):
        """
            A property setter
        """
        name = qUniversal.updateNames(self, name)
        setattr(self, '_qUniversal__name', name)

    @classmethod
    def updateNames(cls, obj, name, duplicate=False):
        """
            A class method
        """
        if name in cls.instNames.keys():
            duplicate = True
            if obj is cls.instNames[name]:
                cls.instNames[name] = cls.instNames.pop(obj.name)
            else:
                print(f'A duplicate name {name} is given,')
                name += str(obj.__class__.instances)
                print(f'it is changed to {name}')
                return cls.updateNames(obj, name, duplicate)
        else:
            if obj in cls.instNames.values():
                # can skip this and keep two keys for a system?
                cls.instNames[name] = cls.instNames.pop(obj.name)
            else:
                cls.instNames[name] = obj
        return name

    def copy(self, n=1, **kwargs):
        """
            A method
        """
        newSystems = []
        for ind in range(n): # pylint: disable=W0612
            sysClass = self.__class__
            newSystems.append(sysClass(**kwargs))

        if len(newSystems) == 1:
            newS = newSystems[0]
        else:
            newS = (*newSystems,)
        return newS

    def __namer(self):
        """
            A method
        """
        name = self.clsLabel() + str(self.clsInstances())
        qUniversal.instNames[name] = self
        return name

    @classmethod
    def _incrementInstances(cls):
        """
            A class method
        """
        cls.instances += 1

    @classmethod
    def clsInstances(cls):
        """
            A class method
        """
        return cls.instances

    @classmethod
    def clsLabel(cls):
        """
            A classs method
        """
        return cls.label
