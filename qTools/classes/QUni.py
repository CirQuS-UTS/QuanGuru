class qUniversal:
    instances = 0
    label = 'universal'
    instNames = {}

    def __init__(self, **kwargs):
        super().__init__()
        self._incrementInstances()
        self.__name = self.__namer()
        self.superSys = None
        self.__setKwargs(**kwargs)

    def __del__(self):
        class_name = self.__class__.__name__
    
    def __setKwargs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

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
        self.__name = name
        qUniversal.updateNames(self)

    @classmethod
    def updateNames(cls, obj):
        if obj.name in cls.instNames.values():
            print('You have created a duplicate name')
        cls.instNames[obj] = obj.name

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
        """Return the current number of instances of this class,
        useful for auto naming."""
        return cls.instances

    @classmethod
    def clsLabel(cls):
        """Return the prefix to use for auto naming."""
        return cls.label