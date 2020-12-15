from typing import Callable, Iterable, List

def loopIt(func: Callable, *inps: Iterable) -> List:
    """
    Trivial method for looping over a function for several inputs (in any iterable form).

    Parameters
    ----------
    func : [type]
        [description]
    inps : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    return [func(*inp) for inp in zip(*inps)]
