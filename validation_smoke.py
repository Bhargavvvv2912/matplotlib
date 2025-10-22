# validation_smoke.py

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# IMPORTANT: Matplotlib on a headless server requires a non-GUI backend.
# We must set this BEFORE importing pyplot.
matplotlib.use("Agg")

def run_matplotlib_smoke_test():
    """
    Performs a simple but representative workflow with Matplotlib to validate
    its core functionality. This acts as a fast "smoke test".
    """
    print("--- Starting Matplotlib Smoke Test ---")
    
    try:
        # --- Test 1: The "Basic" Test ---
        # Goal: Can we create a figure, an axes, and plot a simple line?
        # This tests the core object creation, basic plotting commands, and NumPy integration.
        print("Running Basic Test: Create a simple line plot...")
        
        fig, ax = plt.subplots()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y)
        
        # Verify a basic property of the plot
        assert len(ax.lines) == 1, f"Basic Test Failed: Expected 1 line on the axes, found {len(ax.lines)}"
        
        # Save the figure to a temporary file
        fig.savefig("smoke_test_basic.png")
        plt.close(fig) # Close the figure to free up memory
        
        print("Basic Test PASSED.")

        # --- Test 2: The "Complex" Test ---
        # Goal: Can we create a more complex plot with multiple elements, styles,
        # and text, including using a compiled C++ component (contour plotting)?
        # This tests the rendering engine, font handling, and compiled extensions.
        print("\nRunning Complex Test: Create a styled contour plot...")

        # Create data for a contour plot
        delta = 0.025
        x = y = np.arange(-3.0, 3.0, delta)
        X, Y = np.meshgrid(x, y)
        Z1 = np.exp(-(X**2) - Y**2)
        Z2 = np.exp(-((X - 1) ** 2) - (Y - 1) ** 2)
        Z = (Z1 - Z2) * 2

        fig, ax = plt.subplots()
        CS = ax.contour(X, Y, Z, levels=5, colors='k') # 'k' for black
        
        # Add labels and a title (tests font handling via FreeType)
        ax.clabel(CS, inline=True, fontsize=10)
        ax.set_title('Simple Contour Plot')

        # Verify a property of the complex plot
        assert len(CS.collections) == 5, f"Complex Test Failed: Expected 5 contour levels, found {len(CS.collections)}"
        
        fig.savefig("smoke_test_complex.png")
        plt.close(fig)

        print("Complex Test PASSED.")
        
        # --- If all tests pass ---
        print("\n--- Matplotlib Smoke Test: ALL TESTS PASSED ---")
        sys.exit(0) # Exit with a success code

    except Exception as e:
        # If any part of the workflow fails, print the error and exit with a failure code.
        print(f"\n--- Matplotlib Smoke Test: FAILED ---", file=sys.stderr)
        print(f"Error during smoke test: {type(e).__name__} - {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_matplotlib_smoke_test()