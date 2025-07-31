# QuanGuru Progress Tracking Feature

This document describes the new progress tracking feature for parallel and sequential parameter sweeps in QuanGuru.

## Overview

The QuanGuru library now includes real-time progress tracking for quantum simulations involving parameter sweeps. This feature provides visual feedback about:

- Current progress percentage
- Number of completed vs total parameter combinations
- Elapsed time since start
- Estimated remaining time
- Visual progress bar

## Features

### Automatic Progress Display
- **Enabled by default** for both parallel and sequential processing
- **Real-time updates** during simulation execution
- **Time estimation** based on current progress
- **Visual progress bar** with percentage completion

### Parallel Processing Progress
When using `simulation.run(p=True)`:
```
Starting parallel sweep with 300 parameter combinations...
[████████████████████████████████████████] 100.0% | 300/300 | Elapsed: 2m 15.3s | Remaining: 0.0s
Parallel sweep completed in 2m 15.3s
```

### Sequential Processing Progress  
When using `simulation.run(p=False)`:
```
Starting sequential sweep with 300 parameter combinations...
[████████████████████████████████████████] 100.0% | 300/300 | Elapsed: 5m 42.1s | Remaining: 0.0s
Sequential sweep completed in 5m 42.1s
```

## Usage

### Basic Usage (Default Behavior)
```python
import quanguru as qg
import numpy as np

# Create your quantum simulation
qubit = qg.Qubit(frequency=1.0, initialState=[1, 0])
simulation = qubit.simulation

# Add parameter sweeps
freq_sweep = simulation.Sweep.createSweep(
    system=qubit, 
    sweepKey="frequency", 
    sweepList=np.linspace(0.5, 2.0, 100)
)

# Run with progress tracking (enabled by default)
simulation.run(p=True)  # Parallel with progress
# OR
simulation.run(p=False) # Sequential with progress
```

### Controlling Progress Display

You can disable progress tracking by setting simulation attributes:

```python
# Disable progress for sequential runs
simulation._show_progress = False

# Disable progress for parallel runs  
simulation._show_parallel_progress = False

# Run without progress display
simulation.run(p=True)   # No progress shown
simulation.run(p=False)  # No progress shown

# Re-enable progress
simulation._show_progress = True
simulation._show_parallel_progress = True
```

### Custom Progress Control

```python
# Only show progress for large sweeps
if simulation.Sweep.indMultip > 50:
    simulation._show_progress = True
    simulation._show_parallel_progress = True
else:
    simulation._show_progress = False
    simulation._show_parallel_progress = False

simulation.run(p=True)
```

## Progress Display Format

The progress display shows:

```
[████████████████████████████████████████] 75.5% | 151/200 | Elapsed: 1m 30.2s | Remaining: 29.8s
```

Where:
- `[████████...]` - Visual progress bar (40 characters wide)
- `75.5%` - Percentage completion
- `151/200` - Current task / Total tasks
- `Elapsed: 1m 30.2s` - Time since simulation started
- `Remaining: 29.8s` - Estimated time until completion

## Time Formatting

Times are automatically formatted for readability:
- Under 60 seconds: `45.2s`
- 1-60 minutes: `5m 23.1s`  
- Over 1 hour: `2h 15m 30.5s`

## Technical Details

### Implementation
- Uses `multiprocessing.Pool.imap()` instead of `map()` for parallel processing to enable iterative result processing
- Progress tracking adds minimal overhead (~1% performance impact)
- Progress updates are printed to `sys.stdout` with carriage returns for real-time updating

### Compatibility
- Works with all existing QuanGuru simulations
- Backward compatible - existing code will automatically get progress tracking
- Safe to disable if not desired

### Thread Safety
- Progress tracking is designed to work safely with multiprocessing
- No shared state between parallel workers

## Example Scripts

See `examples/progress_demo.py` for a complete demonstration of the progress tracking features.

## Troubleshooting

### Progress Not Showing
- Ensure `total_tasks > 1` (single-task sweeps don't show progress)
- Check that progress attributes are set to `True`
- Verify your terminal supports carriage return updates

### Performance Impact
- Progress tracking adds minimal overhead
- For maximum performance, disable with `_show_progress = False`

### Windows Multiprocessing
- Multiprocessing on Windows requires the main execution to be wrapped in `if __name__ == "__main__":`
- Progress tracking works correctly with this requirement

## Future Enhancements

Potential future improvements could include:
- Customizable progress bar styles
- Log file output for progress
- Webhook notifications for long-running simulations
- Integration with Jupyter notebook widgets

## Contributing

If you have suggestions for improving the progress tracking feature, please open an issue or submit a pull request on the QuanGuru GitHub repository.
