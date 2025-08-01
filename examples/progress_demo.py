#!/usr/bin/env python3
"""
Example demonstrating the new progress tracking feature for parallel processing in QuanGuru.

This script shows how to:
1. Create a quantum simulation with parameter sweeps
2. Run simulations with progress tracking enabled (default)
3. Control progress display settings
4. Compare parallel vs sequential execution with progress bars

Author: GitHub Copilot Assistant
Date: 2025
"""

import numpy as np
import sys
import os

# Add the QuanGuru package to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import quanguru as qg
except ImportError as e:
    print(f"Error importing QuanGuru: {e}")
    print("Make sure you're running this from the QuanGuru root directory")
    sys.exit(1)

def compute_expectation(qsys, state):
    """
    Compute sigma_x expectation value.
    
    This function is defined at module level so it can be pickled
    for multiprocessing. Local functions inside other functions
    cannot be pickled.
    """
    if not hasattr(qsys, 'resultsDict'):
        qsys.resultsDict = {}
    if 'sigma_x' not in qsys.resultsDict:
        qsys.resultsDict['sigma_x'] = []
    
    # Calculate expectation value
    sigma_x_exp = qg.expectation(qg.sigmax(), state)
    qsys.resultsDict['sigma_x'].append(sigma_x_exp.real)

def create_demo_simulation():
    """Create a simple qubit simulation with parameter sweeps."""
    print("Setting up quantum simulation...")
    
    # Create a simple qubit system
    qubit = qg.Qubit(
        frequency=1.0,
        initialState=[1, 0],  # |0⟩ state
        alias="DemoQubit"
    )
    
    # Set simulation parameters
    simulation = qubit.simulation
    simulation.totalTime = 2 * np.pi  # One period
    simulation.stepSize = 0.1
    
    # Create parameter sweeps
    frequency_list = np.linspace(0.5, 2.0, 20)  # 20 frequency values
    amplitude_list = np.linspace(0.1, 1.0, 15)  # 15 amplitude values
    
    # Add sweeps (combinatorial gives us 20 × 15 = 300 parameter combinations)
    freq_sweep = simulation.Sweep.createSweep(
        system=qubit, 
        sweepKey="frequency", 
        sweepList=frequency_list
    )
    
    # Add a second sweep for the Rabi amplitude
    # First add a driving term
    drive_term = qubit.createTerm(operator=qg.sigmax, frequency=0.5)
    
    amp_sweep = simulation.Sweep.createSweep(
        system=drive_term,
        sweepKey="frequency", 
        sweepList=amplitude_list,
        combinatorial=True  # This creates a combinatorial sweep
    )
    
    # Assign the compute function (defined at module level for multiprocessing compatibility)
    qubit.compute = compute_expectation
    
    # Don't store states to save memory
    simulation.delStates = True
    
    print(f"Created simulation with {simulation.Sweep.indMultip} parameter combinations")
    return simulation

def demonstrate_progress_features():
    """Demonstrate the progress tracking features."""
    
    print("=" * 60)
    print("QuanGuru Progress Tracking Feature Demonstration")
    print("=" * 60)
    
    # Create the simulation
    sim = create_demo_simulation()
    
    print("\n1. Running with PARALLEL processing and progress tracking (default):")
    print("-" * 50)
    
    if __name__ == "__main__":  # Required for multiprocessing on Windows
        try:
            # Run with parallel processing and progress tracking
            sim.run(p=True)
            print("✓ Parallel execution with progress completed successfully!")
            
        except Exception as e:
            print(f"Parallel execution failed (this is normal on some systems): {e}")
            print("Falling back to sequential execution...")
    
    print("\n2. Running with SEQUENTIAL processing and progress tracking:")
    print("-" * 50)
    
    # Reset results for fair comparison
    sim.qRes._reset()
    
    # Run sequential with progress
    sim.run(p=False)
    print("✓ Sequential execution with progress completed successfully!")
    
    print("\n3. Running with progress tracking DISABLED:")
    print("-" * 50)
    
    # Reset results
    sim.qRes._reset()
    
    # Disable progress tracking
    sim._show_progress = False
    sim._show_parallel_progress = False
    
    print("Running without progress display...")
    sim.run(p=False)
    print("✓ Execution without progress completed successfully!")
    
    # Re-enable for next demo
    sim._show_progress = True
    sim._show_parallel_progress = True
    
    print("\n4. Customizing progress display:")
    print("-" * 50)
    print("You can control progress display by setting simulation attributes:")
    print("  sim._show_progress = False          # Disable sequential progress")
    print("  sim._show_parallel_progress = False # Disable parallel progress")
    
    print("\n" + "=" * 60)
    print("Demonstration completed!")
    print("=" * 60)
    
    # Show some results
    if hasattr(sim.qRes, 'resultsDict') and 'sigma_x' in sim.qRes.resultsDict:
        print(f"\nCalculated {len(sim.qRes.resultsDict['sigma_x'])} expectation values")
        print(f"Example sigma_x values: {sim.qRes.resultsDict['sigma_x'][:5]}...")

def main():
    """Main function to run the demonstration."""
    try:
        demonstrate_progress_features()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
