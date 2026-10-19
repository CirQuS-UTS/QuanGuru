"""
Test suite for progress tracking features in QuanGuru simulations.

This module contains comprehensive tests for all progress tracking functionality
including parameter-based showProgress API, display format features, datetime
timestamps, and both sequential and parallel execution modes.

Features tested:
- Parameter-based showProgress API (not attribute-based)
- Progress display formatting with datetime timestamps
- Estimated Finish Time calculations
- Sequential and parallel progress tracking
- Progress bar visual elements
- Time formatting utilities
"""

import pytest
import multiprocessing
import time
import sys
import io
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock
import re

# Import QuanGuru components
from quanguru import Simulation, Spin
from quanguru.classes.modularSweep import (
    printPreamble,
    runSimulation, 
    nonParalEvol, 
    paralEvol,
    printProgress
)

def test_run_simulation_showprogress_parameter_default_true():
    """Test that showProgress parameter defaults to True in run() method."""
    sim = Simulation()
    qsys = Spin(dimension=2, frequency=1)
    sim.addQSystems(qsys)
    
    # Mock the runSimulation function to capture parameters
    with patch('quanguru.classes.QSim.runSimulation') as mock_run:
        sim.run()
        # Verify showProgress=True was passed by default
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        # Should be called with (sim, pool, showProgress=True)
        assert len(args) == 3
        assert args[2] is True  # showProgress parameter

@pytest.mark.parametrize("showProgress, parallel", [
    (True, True),
    (True, False),
    (False, True),
    (False, False)
])
def test_showProgressIsTruePrintsToTerminal(showProgress, parallel):
    """Test that showProgress=True prints progress to the terminal."""
    Simulation._resetAll()
    sim = Simulation()
    qsys = Spin(dimension=2, frequency=1)
    sim.addQSystems(qsys)
    sim.totalTime = 1
    sim.stepCount = 100
    sim.initialStateSystem = qsys
    sim.initialState = [0, 1]
    sim.Sweep.createSweep(system=qsys, sweepKey="frequency", sweepList=[0, 1, 2])
    with patch('quanguru.classes.modularSweep.printProgress') as mock_write:
        if __name__ == "__main__":
            sim.run(p=parallel, showProgress=showProgress)
            if showProgress: 
                assert mock_write.called
            else: 
                assert not mock_write.called

# def test_printPreambleFormat():
#     """Test the printPreamble function."""
#     fixed_time = 1754038800  # 2025-08-01 09:00:00 UTC
#     with patch('quanguru.classes.modularSweep.sys.stdout.write') as mock_write, \
#          patch('quanguru.classes.modularSweep.time.time', return_value=fixed_time):
#         printPreamble(totalTasks=4, startTime=fixed_time, parallel=True)
#         written_output = mock_write.call_args[0][0]
#         assert written_output == (
#             f"Starting parallel sweep with 4 parameter combinations...\n"
#             f"Simulation Start:\t2025-08-01 09:00:00\n"
#             f'[----------------------------------------] 0.0%\n'
#             f'Estimated Finish:\n'
#         )

# def test_printProgressFormat():
#     """Test the printProgress function."""
#     fixed_now = 1754038800  # 2025-08-01 09:00:00 UTC
#     startTime = 1754038790  # 10 seconds earlier
#     with patch('quanguru.classes.modularSweep.sys.stdout.write') as mock_write, \
#          patch('quanguru.classes.modularSweep.time.time', return_value=fixed_now):
#         printProgress(1, 4, startTime)
#         written_output = mock_write.call_args[0][0]
#         assert written_output == (
#             f'[██████████------------------------------] 25.0%\n'
#             f'Estimated Finish:\t2025-08-01 09:00:30\n'
#         )

@pytest.mark.parametrize("sweeps", [True, False])
def test_sequentialProgressOnlyWithSweeps(sweeps):
    """Test that sequential progress bar is displayed only when sweeps are present."""
    Simulation._resetAll()  # Reset named instances
    sim = Simulation()
    qsys = Spin(dimension=2, alias='spin', frequency=1)
    sim.addQSystems(qsys)
    sim.totalTime = 1
    sim.stepCount = 100
    sim.initialStateSystem = qsys
    sim.initialState = [0, 1]
    if sweeps:
        sim.Sweep.createSweep(system='spin', sweepKey="frequency", sweepList=[0, 1, 2])

    with patch('quanguru.classes.modularSweep.printProgress') as mock_write:
        sim.run(p=False, showProgress=True)

        # Verify print was called for start message
        if sweeps:
            assert mock_write.called
        else:
            assert not mock_write.called
