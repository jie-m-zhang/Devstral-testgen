"""
Test to reproduce the issue: legend draggable as keyword

This test should FAIL on the base commit (5c4595267ccd3daf78f5fd05693b7ecbcd575c1e)
and PASS on the head commit (73909bcb408886a22e2b84581d6b9e6d9907c813)
"""

import matplotlib.pyplot as plt
import matplotlib.legend as legend_module

def test_legend_draggable_keyword():
    """
    Test that the Legend class accepts a 'draggable' keyword argument.

    This reproduces the issue where users cannot pass draggable=True
    directly to the Legend __init__ method.
    """
    # Create a simple figure and axes
    fig, ax = plt.subplots()

    # Create some data to plot
    line, = ax.plot([1, 2, 3], [1, 2, 3], label='Test Line')

    # Try to create a legend with draggable=True keyword
    # This should work on the fixed version but fail on the buggy version
    try:
        # On the base commit, this will raise TypeError because draggable
        # is not a valid parameter
        leg = legend_module.Legend(
            ax,
            [line],
            ['Test Line'],
            draggable=True
        )
        ax.add_artist(leg)

        # Verify that the legend is actually draggable
        assert leg.get_draggable() is True, "Legend should be draggable"

        print("✓ Test passed: Legend accepts draggable keyword and is draggable")
        return True

    except TypeError as e:
        # On the base commit, we expect a TypeError about unexpected keyword argument
        if "draggable" in str(e):
            print(f"✗ Test failed (expected on base commit): {e}")
            return False
        else:
            # Some other TypeError - re-raise it
            raise
    except Exception as e:
        print(f"✗ Test failed with unexpected error: {e}")
        raise

if __name__ == "__main__":
    result = test_legend_draggable_keyword()
    if not result:
        exit(1)
    else:
        exit(0)