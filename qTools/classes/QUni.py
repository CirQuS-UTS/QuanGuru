class qUniversal:
    instances = 0
    label = 'universal'
    instNames = {}
    __slots__ = ['__name','__superSys', '__ind','__subSys']
    def __init__(self, **kwargs):
        super().__init__()
        self._incrementInstances()
        self.__name = self.__namer()
        self.__superSys = None
        self.__subSys = {}
        self.__ind = None
        self.__setKwargs(**kwargs)

    def __del__(self):
        class_name = self.__class__.__name__
    
    def __setKwargs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def superSys(self):
        return self.__superSys

    @superSys.setter
    def superSys(self, supSys):
        supSys.subSys[self.name] = self
        self.__superSys = supSys

    @property
    def ind(self):
        return self.__ind

    @ind.setter
    def ind(self, numb):
        self.__ind = numb

    @property
    def name(self):
        return self.__name
        
    @name.setter
    def name(self, name):
        self.__name = qUniversal.updateNames(self, name)

    @classmethod
    def updateNames(cls, obj, name):
        if name in cls.instNames.keys():
            name += str(obj.__class__.instances)
            print('You have created a duplicate name ' + name)
        cls.instNames[name] = obj
        return name

    @staticmethod
    def createCopy(qUninstance, **kwargs):
        sysClass = qUninstance.__class__
        newSub = sysClass(**kwargs)
        return newSub
        
    def __namer(self):
        name = self.clsLabel() + str(self.clsInstances())
        return name

    @classmethod
    def _incrementInstances(cls):
        cls.instances += 1

    @classmethod
    def clsInstances(cls):
        """Return the current number of instances of this class, useful for auto naming."""
        return cls.instances

    @classmethod
    def clsLabel(cls):
        """Return the prefix to use for auto naming."""
        return cls.label