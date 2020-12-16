import scipy.constants as sciConst  # type: ignore

__all__ = [
    'settings',
    'constants'
]

defaultVals = {
    'hbar': 1
}

trueValues = {
    'hbar': sciConst.hbar
}


class _settings(dict):
    def __init__(self, iterable):
        super().__init__()
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


class _constants(dict):
    def __getitem__(self, key):
        if settings.trueVals:  # pylint: disable=E1101
            item = trueValues[key]
        else:
            item = defaultVals[key]
        return item

    def __getattr__(self, name):
        return self.__getitem__(name)


constants = _constants()
