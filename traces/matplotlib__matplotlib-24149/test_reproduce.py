import numpy as np
import matplotlib.pyplot as plt

def test_issue_reproduction():
    """
    Test that ax.bar handles all-NaN data without raising StopIteration.

    This test reproduces the issue where ax.bar raises StopIteration
    when passed only nan data in matplotlib 3.6.1.
    """
    # Create figure and axes
    f, ax = plt.subplots()

    # This should not raise StopIteration
    try:
        result = ax.bar([np.nan], [np.nan])
        print("Test passed - ax.bar handled all-NaN data successfully")
        print(f"Result type: {type(result)}")
        print(f"Number of bars: {len(result)}")
        return True
    except StopIteration as e:
        print(f"Test failed - StopIteration raised: {e}")
        return False
    except Exception as e:
        print(f"Test failed - Unexpected exception: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_issue_reproduction()
    if not success:
        exit(1)
    else:
        exit(0)