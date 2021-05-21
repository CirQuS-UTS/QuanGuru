# QuanGuru

[Cahit Kargi](https://github.com/cahitkargi),
[Fabio Henriques](https://github.com/Qfabiolous),
[Angsar Manatuly](https://github.com/AngsarM),
Adrien Di Lonardo,
Giorge Gemisis,
[Juan Pablo Dehollain](https://github.com/jpdehollain),
and [Nathan K. Langford](https://github.com/nklangford)

![Pipeline](https://code.research.uts.edu.au/mKQuantum/Libraries/QuanGuru/badges/master/pipeline.svg)
![Coverage](https://code.research.uts.edu.au/mKQuantum/Libraries/QuanGuru/badges/master/coverage.svg?job=integration_test)
![Pylint](https://code.research.uts.edu.au/mKQuantum/Libraries/QuanGuru/-/jobs/artifacts/master/raw/pylint/pylint.svg?job=pylint)


QuanGuru (pronounced Kangaroo) is a Python library for Quantum Sciences. This first module consists of tools for numerical simulations of Quantum systems.
It is still under-development, and the rough development plan is provided below.

We (mostly) use [camelCase](https://code.research.uts.edu.au/mKQuantum/QuantumSimulations/-/wikis/Variable%20Naming%20Conventions)

## (Rough) Development Plan

QuantumToolbox is already simple enough and stable. In parallel to future developments of classes, further additions and
improvements can be implemented in QuantumToolbox. I already have functions (for special state creations, operator norm
etc.) in my repo under possibleFutureQuantumToolbox. These functions and more can be implemented into QuantumToolbox
with proper tests, documentation etc.

### 1. Short term plan for the improvements on current code

1. Completing essential unit and integration tests
1. Restructuring and writing docstring for QSys, QPro, QGate, and QSim
1. Docstring for extensions
1. Writing tutorials and further improvements in docstring and tests

### 2. pip installable

At this point, we should have a stable version with enough documentation to make it pip available.

### 3. Future development 
Further additions will always have to be with proper tests, tutorials, docstring etc.

1. Implementation of SCQubits and QDrive using Adrien's work.
1. Open system simulation capability for the classes
1. Interfacing to other libraries such as QuTiP.

To read the existing documentation: docs -> docsBuild -> index.html
Then, choose QuantumToolbox from the menu on the left.