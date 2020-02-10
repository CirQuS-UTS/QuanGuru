class qUniversal:
    def __init__(self, **kwargs):
        super().__init__()
        self.__name = None
        self.__setKwargs(**kwargs)

    
    def __setKwargs(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name
        
