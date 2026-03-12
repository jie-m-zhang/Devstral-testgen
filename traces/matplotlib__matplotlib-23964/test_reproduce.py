"""
Test to reproduce the issue where a text label with empty line causes
a "TypeError: cannot unpack non-iterable NoneType object" in PostScript backend.

This test should:
- FAIL on base commit (269c0b94b4fcf8b1135011c1556eac29dc09de15) with TypeError
- PASS on head commit (73909bcb408886a22e2b84581d6b9e6d9907c813) after fix
"""

from matplotlib.figure import Figure
import tempfile
import os

def test_empty_line_in_text_label():
    """
    Test that a figure with a text label containing an empty line
    can be saved as PostScript without error.
    """
    # Create a figure with an annotation containing an empty line
    figure = Figure()
    ax = figure.add_subplot(111)
    ax.annotate(text='\nLower label', xy=(0, 0))

    # Try to save as PostScript - this should trigger the bug on base commit
    with tempfile.NamedTemporaryFile(suffix='.eps', delete=False) as tmp:
        try:
            figure.savefig(tmp.name)
            # If we get here, the save was successful
            print("Figure saved successfully - test PASSED")
            return True
        except TypeError as e:
            if "cannot unpack non-iterable NoneType object" in str(e):
                print(f"TypeError occurred as expected: {e}")
                print("Test FAILED (reproduced the bug)")
                return False
            else:
                # Different TypeError - re-raise
                raise
        finally:
            # Clean up
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

if __name__ == "__main__":
    success = test_empty_line_in_text_label()
    if not success:
        exit(1)  # Exit with non-zero code to indicate failure
    exit(0)  # Exit with zero code to indicate success