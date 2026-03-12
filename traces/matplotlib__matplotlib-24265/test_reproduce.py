"""
Test to reproduce the issue with accessing seaborn-colorblind style from library.

The issue is that plt.style.library["seaborn-colorblind"] raises a KeyError
in matplotlib v3.6.1, but should work (with a deprecation warning) as it did
in v3.4.3.
"""

import matplotlib.pyplot as plt

def test_seaborn_colorblind_library_access():
    """
    Test that accessing seaborn-colorblind from the style library works.

    This should:
    - FAIL on base commit (e148998d9b) with KeyError
    - PASS on head commit (73909bcb40) with deprecation warning
    """
    try:
        # This is the code from the bug report that should work
        the_rc = plt.style.library["seaborn-colorblind"]
        print("SUCCESS: seaborn-colorblind style accessed successfully")
        print(f"Type of result: {type(the_rc)}")
        print(f"Number of keys in result: {len(the_rc)}")
        return True
    except KeyError as e:
        print(f"FAILURE: KeyError raised when accessing seaborn-colorblind: {e}")
        return False

if __name__ == "__main__":
    # Run the test
    success = test_seaborn_colorblind_library_access()
    
    if not success:
        print("\nTest FAILED - issue reproduced (expected on base commit)")
        exit(1)
    else:
        print("\nTest PASSED - issue is fixed (expected on head commit)")
        exit(0)