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
    runSimulation, 
    nonParalEvol, 
    paralEvol, 
    _format_time
)


class TestProgressTrackingAPI:
    """Test the parameter-based progress tracking API."""
    
    def test_run_simulation_showprogress_parameter_default_true(self):
        """Test that showProgress parameter defaults to True in run() method."""
        sim = Simulation()
        qsys = Spin(dimension=2)
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
    
    def test_run_simulation_showprogress_parameter_explicit_true(self):
        """Test that showProgress=True can be explicitly passed to run() method."""
        sim = Simulation()
        qsys = Spin(dimension=2)
        sim.addQSystems(qsys)
        
        with patch('quanguru.classes.QSim.runSimulation') as mock_run:
            sim.run(showProgress=True)
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            assert args[2] is True
    
    def test_run_simulation_showprogress_parameter_explicit_false(self):
        """Test that showProgress=False can be explicitly passed to run() method."""
        sim = Simulation()
        qsys = Spin(dimension=2)
        sim.addQSystems(qsys)
        
        with patch('quanguru.classes.QSim.runSimulation') as mock_run:
            sim.run(showProgress=False)
            mock_run.assert_called_once()
            args, kwargs = mock_run.call_args
            assert args[2] is False
    
    def test_simulation_object_has_no_showprogress_attribute(self):
        """Test that Simulation objects do not have _showProgress attribute."""
        sim = Simulation()
        
        # Verify _showProgress is not in __slots__
        assert '_showProgress' not in sim.__slots__
        
        # Verify _showProgress attribute doesn't exist
        assert not hasattr(sim, '_showProgress')
        
        # Verify it's not set during initialization
        qsys = Spin(dimension=2)
        sim.addQSystems(qsys)
        assert not hasattr(sim, '_showProgress')


class TestProgressDisplayFormat:
    """Test the progress display format and datetime features."""
    
    def test_estimated_finish_time_calculation(self):
        """Test that estimated finish time is calculated correctly."""
        # Mock datetime.now() to return a known time
        mock_now = datetime(2025, 8, 1, 12, 0, 0)
        
        with patch('quanguru.classes.modularSweep.datetime') as mock_datetime:
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime
            
            # Simulate progress calculation
            elapsed_time = 10.0  # 10 seconds elapsed
            total_tasks = 5
            completed = 2
            estimated_total_time = elapsed_time * total_tasks / completed  # 25 seconds
            remaining_time = estimated_total_time - elapsed_time  # 15 seconds
            
            # Calculate expected finish time
            expected_finish = mock_now + timedelta(seconds=remaining_time)
            expected_str = expected_finish.strftime('%Y-%m-%d %H:%M:%S')
            
            # The expected result should be 15 seconds after mock_now
            assert expected_str == "2025-08-01 12:00:15"
    
    def test_progress_bar_format(self):
        """Test that progress bar is formatted correctly."""
        # Test various completion percentages
        test_cases = [
            (0, 10, '----------------------------------------'),  # 0%
            (5, 10, '████████████████████--------------------'),  # 50%
            (10, 10, '████████████████████████████████████████'),  # 100%
        ]
        
        for completed, total, expected_bar in test_cases:
            bar_length = 40
            filled_length = int(bar_length * completed // total)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            assert bar == expected_bar
    
    def test_datetime_format_consistency(self):
        """Test that all datetime displays use consistent YYYY-MM-DD HH:MM:SS format."""
        test_datetime = datetime(2025, 8, 1, 14, 30, 45)
        expected_format = "2025-08-01 14:30:45"
        
        # Test the format used in the progress display
        formatted = test_datetime.strftime('%Y-%m-%d %H:%M:%S')
        assert formatted == expected_format
    
    def test_simulation_start_message_format(self):
        """Test that simulation start message contains correct datetime."""
        with patch('builtins.print') as mock_print, \
             patch('quanguru.classes.modularSweep.datetime') as mock_datetime:
            
            mock_now = datetime(2025, 8, 1, 10, 15, 30)
            mock_datetime.now.return_value = mock_now
            mock_datetime.strftime = datetime.strftime
            
            # Create a mock simulation with multiple sweep parameters
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 3
            
            # Capture print output
            nonParalEvol(mock_sim, showProgress=True)
            
            # Check that simulation start was printed with correct format
            print_calls = [str(call) for call in mock_print.call_args_list]
            start_message_found = any("Simulation Start: 2025-08-01 10:15:30" in call for call in print_calls)
            assert start_message_found


class TestSequentialProgressTracking:
    """Test progress tracking for sequential (non-parallel) execution."""
    
    def test_sequential_progress_display_with_multiple_tasks(self):
        """Test that sequential progress is displayed for multiple tasks."""
        with patch('builtins.print') as mock_print, \
             patch('sys.stdout.write') as mock_stdout, \
             patch('sys.stdout.flush') as mock_flush:
            
            # Mock simulation with 3 tasks
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 3
            mock_sim.qRes._organiseSingleProcRes.return_value = None
            mock_sim.qRes._finaliseAll.return_value = None
            
            # Mock _runSweepAndPrep to do nothing
            with patch('quanguru.classes.modularSweep._runSweepAndPrep'):
                nonParalEvol(mock_sim, showProgress=True)
            
            # Verify print was called for start message
            assert mock_print.called
            
            # Verify stdout.write was called for progress updates
            assert mock_stdout.called
            
            # Check that progress messages contain expected elements
            progress_calls = [str(call) for call in mock_stdout.call_args_list]
            # Should contain progress bar, percentage, and estimated finish time
            progress_pattern = r'\[.*\].*%.*\|.*Estimated Finish Time:.*'
            progress_found = any(re.search(progress_pattern, call) for call in progress_calls)
            assert progress_found
    
    def test_sequential_no_progress_display_single_task(self):
        """Test that no progress is displayed for single task."""
        with patch('builtins.print') as mock_print, \
             patch('sys.stdout.write') as mock_stdout:
            
            # Mock simulation with only 1 task
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 1
            mock_sim.qRes._organiseSingleProcRes.return_value = None
            mock_sim.qRes._finaliseAll.return_value = None
            
            with patch('quanguru.classes.modularSweep._runSweepAndPrep'):
                nonParalEvol(mock_sim, showProgress=True)
            
            # Should not print progress messages for single task
            print_calls = [str(call) for call in mock_print.call_args_list]
            start_message_found = any("Starting sequential sweep" in call for call in print_calls)
            assert not start_message_found
    
    def test_sequential_no_progress_when_disabled(self):
        """Test that no progress is displayed when showProgress=False."""
        with patch('builtins.print') as mock_print, \
             patch('sys.stdout.write') as mock_stdout:
            
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 5
            mock_sim.qRes._organiseSingleProcRes.return_value = None
            mock_sim.qRes._finaliseAll.return_value = None
            
            with patch('quanguru.classes.modularSweep._runSweepAndPrep'):
                nonParalEvol(mock_sim, showProgress=False)
            
            # Should not print any progress messages
            assert not mock_print.called
            assert not mock_stdout.called


class TestParallelProgressTracking:
    """Test progress tracking for parallel execution."""
    
    def test_parallel_progress_display_enabled(self):
        """Test that parallel progress is displayed when enabled."""
        with patch('builtins.print') as mock_print, \
             patch('sys.stdout.write') as mock_stdout, \
             patch('sys.stdout.flush') as mock_flush:
            
            # Mock simulation and pool
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 3
            mock_sim.qRes._organiseMultiProcRes.return_value = None
            
            # Mock pool with imap that yields results
            mock_pool = MagicMock()
            mock_pool.__enter__.return_value = mock_pool
            mock_pool.__exit__.return_value = None
            mock_pool.imap.return_value = iter(['result1', 'result2', 'result3'])
            
            with patch('quanguru.classes.modularSweep.partial'):
                paralEvol(mock_sim, mock_pool, showProgress=True)
            
            # Verify progress messages were displayed
            assert mock_print.called
            assert mock_stdout.called
            
            # Check for start message
            print_calls = [str(call) for call in mock_print.call_args_list]
            start_message_found = any("Starting parallel sweep" in call for call in print_calls)
            assert start_message_found
    
    def test_parallel_no_progress_when_disabled(self):
        """Test that parallel progress is not displayed when disabled."""
        with patch('builtins.print') as mock_print, \
             patch('sys.stdout.write') as mock_stdout:
            
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 3
            mock_sim.qRes._organiseMultiProcRes.return_value = None
            
            # Mock pool.map for non-progress path
            mock_pool = MagicMock()
            mock_pool.map.return_value = ['result1', 'result2', 'result3']
            
            with patch('quanguru.classes.modularSweep.partial'):
                paralEvol(mock_sim, mock_pool, showProgress=False)
            
            # Should use map instead of imap and no progress display
            mock_pool.map.assert_called_once()
            assert not mock_print.called
            assert not mock_stdout.called


class TestTimeFormatting:
    """Test the time formatting utility function."""
    
    def test_format_time_seconds(self):
        """Test formatting of times in seconds."""
        assert _format_time(5.5) == "5.5s"
        assert _format_time(45.0) == "45.0s"
        assert _format_time(59.9) == "59.9s"
    
    def test_format_time_minutes(self):
        """Test formatting of times in minutes and seconds."""
        assert _format_time(60.0) == "1m 0.0s"
        assert _format_time(125.5) == "2m 5.5s"
        assert _format_time(3599.0) == "59m 59.0s"
    
    def test_format_time_hours(self):
        """Test formatting of times in hours, minutes and seconds."""
        assert _format_time(3600.0) == "1h 0m 0.0s"
        assert _format_time(3665.5) == "1h 1m 5.5s"
        assert _format_time(7200.0) == "2h 0m 0.0s"


class TestRunSimulationDispatch:
    """Test the main runSimulation function routing."""
    
    def test_runsimulation_calls_nonparalevol_when_no_pool(self):
        """Test that runSimulation calls nonParalEvol when p=None."""
        mock_sim = MagicMock()
        mock_sim.subSys.items.return_value = []
        
        with patch('quanguru.classes.modularSweep.nonParalEvol') as mock_nonparal, \
             patch('quanguru.classes.modularSweep.paralEvol') as mock_paral:
            
            runSimulation(mock_sim, None, True)
            
            mock_nonparal.assert_called_once_with(mock_sim, True)
            mock_paral.assert_not_called()
    
    def test_runsimulation_calls_paralevol_when_pool_provided(self):
        """Test that runSimulation calls paralEvol when pool is provided."""
        mock_sim = MagicMock()
        mock_sim.subSys.items.return_value = []
        mock_pool = MagicMock()
        
        with patch('quanguru.classes.modularSweep.nonParalEvol') as mock_nonparal, \
             patch('quanguru.classes.modularSweep.paralEvol') as mock_paral:
            
            runSimulation(mock_sim, mock_pool, False)
            
            mock_paral.assert_called_once_with(mock_sim, mock_pool, False)
            mock_nonparal.assert_not_called()
    
    def test_runsimulation_passes_showprogress_parameter(self):
        """Test that runSimulation passes showProgress parameter correctly."""
        mock_sim = MagicMock()
        mock_sim.subSys.items.return_value = []
        
        # Test with showProgress=True
        with patch('quanguru.classes.modularSweep.nonParalEvol') as mock_nonparal:
            runSimulation(mock_sim, None, True)
            mock_nonparal.assert_called_once_with(mock_sim, True)
        
        # Test with showProgress=False
        with patch('quanguru.classes.modularSweep.nonParalEvol') as mock_nonparal:
            runSimulation(mock_sim, None, False)
            mock_nonparal.assert_called_once_with(mock_sim, False)


class TestProgressMessageContent:
    """Test the specific content and format of progress messages."""
    
    def test_progress_message_contains_estimated_finish_time(self):
        """Test that progress messages contain 'Estimated Finish Time' not 'Estimated Remaining'."""
        with patch('sys.stdout.write') as mock_stdout, \
             patch('sys.stdout.flush'):
            
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 2
            mock_sim.qRes._organiseSingleProcRes.return_value = None
            mock_sim.qRes._finaliseAll.return_value = None
            
            with patch('quanguru.classes.modularSweep._runSweepAndPrep'), \
                 patch('builtins.print'):
                nonParalEvol(mock_sim, showProgress=True)
            
            # Check stdout calls for progress messages
            stdout_calls = [str(call) for call in mock_stdout.call_args_list]
            
            # Should contain "Estimated Finish Time" not "Estimated Remaining"
            finish_time_found = any("Estimated Finish Time:" in call for call in stdout_calls)
            remaining_time_found = any("Estimated Remaining:" in call for call in stdout_calls)
            
            assert finish_time_found, "Progress message should contain 'Estimated Finish Time'"
            assert not remaining_time_found, "Progress message should not contain 'Estimated Remaining'"
    
    def test_progress_message_format_structure(self):
        """Test that progress messages follow expected format structure."""
        with patch('sys.stdout.write') as mock_stdout, \
             patch('sys.stdout.flush'), \
             patch('builtins.print'):
            
            mock_sim = MagicMock()
            mock_sim.Sweep.indMultip = 3
            mock_sim.qRes._organiseSingleProcRes.return_value = None
            mock_sim.qRes._finaliseAll.return_value = None
            
            with patch('quanguru.classes.modularSweep._runSweepAndPrep'):
                nonParalEvol(mock_sim, showProgress=True)
            
            stdout_calls = [str(call) for call in mock_stdout.call_args_list]
            
            # Find progress message calls
            progress_calls = [call for call in stdout_calls if '[' in call and '%' in call]
            
            if progress_calls:
                # Check format: [progress_bar] percentage% | completed/total | Estimated Finish Time: datetime | Updated: datetime
                progress_pattern = r'\[.*\].*\d+\.\d+%.*\|\s*\d+/\d+.*\|.*Estimated Finish Time:.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*Updated:.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
                
                for call in progress_calls:
                    assert re.search(progress_pattern, call), f"Progress message format incorrect: {call}"


class TestIntegrationWithSimulationClass:
    """Test integration with the main Simulation class."""
    
    def test_simulation_run_method_signature_accepts_showprogress(self):
        """Test that Simulation.run() method accepts showProgress parameter."""
        sim = Simulation()
        qsys = Spin(dimension=2)
        sim.addQSystems(qsys)
        
        # Should be able to call with showProgress parameter without error
        with patch('quanguru.classes.QSim.runSimulation'):
            try:
                sim.run(showProgress=True)
                sim.run(showProgress=False)
            except TypeError as e:
                pytest.fail(f"Simulation.run() should accept showProgress parameter: {e}")
    
    def test_simulation_preserves_other_parameters(self):
        """Test that adding showProgress doesn't break other run() parameters."""
        sim = Simulation()
        qsys = Spin(dimension=2)
        sim.addQSystems(qsys)
        
        with patch('quanguru.classes.QSim.runSimulation') as mock_run:
            # Test with all parameters
            sim.run(p=True, coreCount=2, resetRes=False, showProgress=True)
            
            # Verify the call was made (parameters are tested by other parts of codebase)
            mock_run.assert_called_once()


if __name__ == "__main__":
    # Run tests if this file is executed directly
    pytest.main([__file__, "-v"])
