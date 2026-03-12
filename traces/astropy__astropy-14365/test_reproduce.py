#!/usr/bin/env python
"""
Test to reproduce the issue where ascii.qdp Table format assumes QDP commands are upper case.

This test should FAIL on the base commit (7269fa3e33e8d02485a647da91a5a2a60a06af61)
and PASS on the head commit (5f74eacbcc7fff707a44d8eb58adaa514cb7dcb5).
"""

import tempfile
import os
from astropy.table import Table

def test_lowercase_qdp_commands():
    """Test that lowercase QDP commands are properly recognized.

    The issue is that ascii.qdp assumes commands are uppercase, but QDP itself
    is case insensitive. This test creates a QDP file with lowercase commands
    and verifies it can be read successfully.
    """
    # Create a temporary QDP file with lowercase commands
    qdp_content = """read serr 1 2
1 0.5 1 0.5
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.qdp', delete=False) as f:
        f.write(qdp_content)
        temp_file = f.name

    try:
        # Try to read the QDP file
        # On base commit: this should raise ValueError with "Unrecognized QDP line"
        # On head commit: this should work fine
        table = Table.read(temp_file, format='ascii.qdp')

        # Verify the table was read correctly
        assert len(table) == 1, f"Expected 1 row, got {len(table)}"
        assert len(table.colnames) == 4, f"Expected 4 columns, got {len(table.colnames)}"

        # Verify the data values
        assert table['col1'][0] == 1.0, f"Expected col1[0] = 1.0, got {table['col1'][0]}"
        assert table['col1_err'][0] == 0.5, f"Expected col1_err[0] = 0.5, got {table['col1_err'][0]}"
        assert table['col2'][0] == 1.0, f"Expected col2[0] = 1.0, got {table['col2'][0]}"
        assert table['col2_err'][0] == 0.5, f"Expected col2_err[0] = 0.5, got {table['col2_err'][0]}"

        print("Test passed - lowercase QDP commands are now supported!")

    except ValueError as e:
        if "Unrecognized QDP line" in str(e):
            print(f"Test failed (as expected on base commit) - {e}")
            raise  # Re-raise to get non-zero exit code
        else:
            print(f"Unexpected ValueError: {e}")
            raise
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    test_lowercase_qdp_commands()