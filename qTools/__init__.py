from .classes import *
from .QuantumToolbox import *
from .extensions import *
from .simUnits import *

__all__ = [
    'units',
    'settings'
]

class _settings(dict):
    def __init__(self, iterable):
        for k, v in iterable.items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        setattr(self, key, value)
        return super().__setitem__(key, value)

settings = _settings(
    {
        'trueVals': False
    }
)

class _units(dict):
    def __getitem__(self, key):
        if settings.trueVals:
            return trueValues[key]
        else:
            return defaultVals[key]

    def __getattr__(self, name):
        return self.__getitem__(name)

units = _units()