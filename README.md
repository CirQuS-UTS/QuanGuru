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

## Minimal example
### 5 steps recipe with classes

#### 1. Define the system/Hamiltonian (and initial state) 
```python
import quanguru as qg
import numpy as np

spinSys = qg.QuantumSystem(frequency=1, operator=qg.sigmaz, dimension=2, alias='first')
spinSys.initialState = {0:0.2, 1:0.8}
```

#### 2. Define the protocol/s (optional)
```python
freeEvolution = qg.freeEvolution(system=spinSys)
ry = qg.SpinRotation(system='first', angle=np.pi/2, rotationAxis = 'y')
ProtocolY = qg.qProtocol(system=spinSys, steps=[ry.hc, freeEvolution, ry])
```

#### 3. Define "Simulation"
```python
spinSys.simulation.addSubSys(spinSys, ProtocolY)

spinSys.totalTime = 8*np.pi
spinSys.stepCount = 200
```

#### 4. Define parameter sweeps (optional)
```python
spinSys.simulation.Sweep.createSweep(system='first', sweepKey='frequency',
                                     sweepList=np.arange(-1, 1, 0.25))
```

#### 5. Define “compute function/s” (optional)
```python
sy = qg.sigmay()
def compute(sim, args):
    sim.qRes.singleResult = 'freeEvo', qg.expectation(sy, args[0])
    sim.qRes.singleResult = 'yRotPro', qg.expectation(sy, args[1])

spinSys.simCompute = compute
```

#### finally run the simulation and retrieve the results
```python
spinSys.runSimulation()
spinSys.resultsDict['freeEvo']
```

See [tutorials for more.](https://cirqus-uts.github.io/QuanGuru/classes/Tutorials/1_Qubit/Tutorials.html)


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
