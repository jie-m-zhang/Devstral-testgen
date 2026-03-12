import matplotlib.pyplot as plt
import numpy as np
import warnings

def test_constrained_layout_false_no_warning():
    """
    Test that no warning is raised when using constrained_layout=False
    with plt.subplots_adjust.

    This reproduces the bug where a UserWarning is incorrectly raised
    even when constrained_layout=False is explicitly set.
    """
    # Create test data
    a = np.linspace(0, 2*np.pi, 100)
    b = np.sin(a)
    c = np.cos(a)

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Create figure with constrained_layout=False
        fig, ax = plt.subplots(1, 2, figsize=(8, 2), constrained_layout=False)
        ax[0].plot(a, b)
        ax[1].plot(a, c)

        # This should NOT raise a warning when constrained_layout=False
        plt.subplots_adjust(wspace=0)

        # Check if any warnings were raised
        if len(w) > 0:
            for warning in w:
                print(f"Warning raised: {warning.category.__name__}: {warning.message}")
                # Check if it's the specific warning we're looking for
                if "incompatible with subplots_adjust" in str(warning.message):
                    print("FAIL: The bug is present - warning raised despite constrained_layout=False")
                    plt.close(fig)
                    assert False, f"Unexpected warning: {warning.message}"

        print("PASS: No warning raised - bug is fixed")
        plt.close(fig)

if __name__ == "__main__":
    test_constrained_layout_false_no_warning()