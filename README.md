# Read Me

## To contribute

Below is a list of key programming/Python concepts used in various parts of the library. I have divided them into two
parts for classes and QuantumToolbox, and into 3 parts for classes.

Also, I mostly use [camelCase](https://code.research.uts.edu.au/mKQuantum/QuantumSimulations/-/wikis/Variable%20Naming%20Conventions)

I created below list quickly glancing the classes and modules. Please let me know, if there is anything to be included
here. I mean, after seeing something that is not listed here, you might google learn it, but please also let
me know, so that this list is updated and becomes more complete for future.

### Classes

#### 1. Essentials

1. Define a class, inherit from it (with the use of `super().__init__()`), and use class magics such as `__slots__` and
`__new__`. 
1. Instance and class attributes. Attribute naming with `_` and `__` -> name mangling
1. Instance, class, and static methods and use of `super()` to extend these in sub-classes
1. Property decorator (`getter/setter`) and use of `fset` and `fget` to extend these in sub-classes
1. User defined decorators, argumented decorators, and recursion
1. `setattr`, `getattr`, and `hasattr` bult-in methods
1. `*args` and `**kwargs` use in methods/functions

#### 2. More details

1. extensions and monkey-patching, and duck-typing
1. Multi-processing basics with `Pool` and pickling
1. Mutable vs immutable types. Use of mutable types as default values for arguments in functions and methods (not a bug
a feature and we use it in some methods, mostly recursive methods). Also possibly, pass by reference and value.
1. `try-except-else-finally`

#### 3. Full extend

1. Inheritance vs composition
1. Module magics such as `__all__`
1. reStructured text and docstrings in numpy style, and **Sphinx** (`conf.py`, `Makefile`, etc.)
1. type hints and **mypy** (partially used)
1. linter settings and **pylint**
1. CI/CD tools (for gitlab)

### QuantumToolbox

1. Libraries for matrix creation and manipulation, such as `scipy.sparse`, `scipy.sparse.linalg`, `scipy.linalg` etc.
1. `@` matrix multiplication method. See [the PEP reference.](https://www.python.org/dev/peps/pep-0465/)
1. type hints and **mypy**

## Existing Documentation

A useful link for latex math symbols to use in docstrings: https://en.wikipedia.org/wiki/List_of_mathematical_symbols_by_subject
Not every latex command works, but almost all of them can be obtained by some combination of these.

To read the existing documentation: docs -> docsBuild -> index.html
Then, choose QuantumToolbox from the menu on the left.