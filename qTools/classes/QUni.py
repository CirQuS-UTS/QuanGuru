def checkClass(classOf):
    def addDecorator(addRemoveFunction):
        def wrapper(obj, inp):
            cls1 = globals()[classOf]

            if isinstance(inp, cls1):
                addRemoveFunction(obj, inp)
            elif isinstance(inp, str):
                addRemoveFunction(obj, cls1.instNames[inp])
            elif isinstance(inp, dict):
                for sys in inp.values():
                    # TODO what to do with the keys?
                    wrapper(obj, sys)
            elif inp is None:
                addRemoveFunction(obj, inp)
            else:
                for sys in inp:
                    wrapper(obj, sys)
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
    def addSubSys(self, subS):
        if subS is not None:
            self._qUniversal__subSys[subS.name] = subS
        elif subS is None:
            self._qUniversal__subSys = {}
    
    @checkClass('qUniversal')
    def removeSubSys(self, subS):
        obj = self._qUniversal__subSys.pop(subS.name)
        print(obj.name + ' is removed from subSys of ' + self.name)

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