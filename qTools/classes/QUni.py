__all__ = [
    'qUniversal'
]

def checkClass(classOf):
    def addDecorator(addRemoveFunction):
        def wrapper(obj, inp, **kwargs):
            cls1 = globals()[classOf]
            if isinstance(inp, cls1):
                inp._qUniversal__setKwargs(**kwargs)
                addRemoveFunction(obj, inp, **kwargs)
                return inp
            elif isinstance(inp, str):
                if str in cls1.instNames.keys():
                    inp = wrapper(obj, cls1.instNames[inp], **kwargs)
                else:
                    cls2 = globals()[inp]
                    inp = wrapper(obj, cls2, **kwargs)
            elif isinstance(inp, dict):
                for sys in inp.values():
                    # TODO what to do with the keys?
                    inp = wrapper(obj, sys, **kwargs)
            elif inp is None:
                obj._qUniversal__subSys = {}
                return obj._qUniversal__subSys
            elif inp.__class__ is type:
                newSys = inp()
                inp = wrapper(obj, newSys, **kwargs)
            else:
                for sys in inp:
                    inp = wrapper(obj, sys, **kwargs)
            return inp
        return wrapper
    return addDecorator

class qUniversal:
    instances = 0
    label = 'qUniversal'
    instNames = {}
    
    __slots__ = ['__name', '__superSys', '__ind', '__subSys']

    def __init__(self, **kwargs):
        super().__init__()
        self._incrementInstances()
        self.__name = self._qUniversal__namer()
        self.__superSys = None
        self.__subSys = {}
        self.__ind = None
        self._qUniversal__setKwargs(**kwargs)

    def __del__(self):
        class_name = self.__class__.__name__
    
    def __setKwargs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def subSys(self):
        return self._qUniversal__subSys

    @subSys.setter
    def subSys(self, subS):
        self.addSubSys(subS)
             
    @checkClass('qUniversal')         
    def addSubSys(self, subS, **kwargs):
        self._qUniversal__subSys[subS.name] = subS
    
    @checkClass('qUniversal')
    def removeSubSys(self, subS, **kwargs):
        obj = self._qUniversal__subSys.pop(subS.name)
        print(obj.name + ' is removed from subSys of ' + self.name)
        
    @checkClass('qUniversal')
    def createSubSys(self, subSysClass, **kwargs):
        self._qUniversal__subSys[subSysClass.name] = subSysClass
        

    @property
    def superSys(self):
        return self._qUniversal__superSys

    @superSys.setter
    def superSys(self, supSys):
        self._qUniversal__superSys = supSys

    @property
    def ind(self):
        return self._qUniversal__ind

    @ind.setter
    def ind(self, numb):
        self._qUniversal__ind = numb

    @property
    def name(self):
        return self._qUniversal__name
        
    @name.setter
    def name(self, name):
        self._qUniversal__name = qUniversal.updateNames(self, name)

    @classmethod
    def updateNames(cls, obj, name, duplicate=False):
        if name in cls.instNames.keys():
            duplicate = True
            if obj is cls.instNames[name]:
                cls.instNames[name] = cls.instNames.pop(obj.name)
                return name
            else:
                name += str(obj.__class__.instances)
                return cls.updateNames(obj, name, duplicate)
        else:
            if duplicate is True:
                print('A duplicate name is given,' + '\n' + 'it is changed to ' + name)

            if obj in cls.instNames.values():
                # TODO can skip this and keep two keys for a system
                cls.instNames[name] = cls.instNames.pop(obj.name)
            else:
                cls.instNames[name] = obj
            return name

    def copy(self, n=1, **kwargs):
        newSystems = [] 
        for ind in range(n):
            sysClass = self.__class__
            newSystems.append(sysClass(**kwargs))

        if len(newSystems) == 1:
            return newSystems[0]
        else:
            return (*newSystems,)
        
    def __namer(self):
        name = self.clsLabel() + str(self.clsInstances())
        qUniversal.instNames[name] = self
        return name

    @classmethod
    def _incrementInstances(cls):
        cls.instances += 1

    @classmethod
    def clsInstances(cls):
        return cls.instances

    @classmethod
    def clsLabel(cls):
        return cls.label