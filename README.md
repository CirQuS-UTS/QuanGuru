# QuanGuru - A Python package for numerical analyses of quantum systems

[![main](https://github.com/CirQuS-UTS/QuanGuru/actions/workflows/main.yml/badge.svg)](https://github.com/CirQuS-UTS/QuanGuru/actions/workflows/main.yml)
[![development](https://github.com/CirQuS-UTS/QuanGuru/actions/workflows/development.yml/badge.svg)](https://github.com/CirQuS-UTS/QuanGuru/actions/workflows/development.yml)


QuanGuru is a Python library for numerical analyses of Quantum systems.
It is still under-development, and the rough development plan is provided below.
The [github repo is in here](https://github.com/CirQuS-UTS/QuanGuru) and the [documentation are in here](https://cirqus-uts.github.io/QuanGuru/).
It can already be installed via pip
```bash
pip install quanguru
```

QuanGuru contains tools for numerical simulations of Quantum systems, and it is composed of two main sub-modules: (i) QuantumToolbox, and (ii) classes (for OOP, module to be renamed later).
QuantumToolbox consists **purely of Python functions** (no other objects) that create and/or use **matrices**.
The classes module (to be renamed later) contains classes to create flexible, simple, and object-oriented simulation scripts.
Classes uses QuantumToolbox for matrix operations, and QuantumToolbox can be used as a standalone library to carry the same simulations.


## (Rough) Development Plan

QuantumToolbox is already simple enough and stable.
In parallel to the developments of classes, further additions and improvements are going to be implemented in QuantumToolbox.
There are already other functions (for special state creations, eigen-value statistics etc.) in another private repo.

### 1. Short term plan for the improvements on current code

1. Complete the migration from gitlab (private server) to github, meaning re-establish CI/CD, pages, wiki, issues, etc.
1. Restructuring and writing docstring for QPro, QGate, QSim, and extensions
1. Improve the tutorials, further improvements in docstring, and more tests

### 2. Version 1

At this point, we should have a stable version with enough documentation and tests for the version 1.

### 3. Future development 
Further additions have to be with proper tests, tutorials, docstring etc.

1. Implementation of SCQubits and QDrive.
1. Interfacing to other libraries.
