#!/usr/bin/env python
"""
Test to reproduce the issue with header_rows in RestructuredText output.

The issue is that the RST writer doesn't support the header_rows parameter,
which causes a TypeError when trying to use it.
"""

import sys
import inspect

# Read the RST class source code directly
with open('/testbed/astropy/io/ascii/rst.py', 'r') as f:
    rst_source = f.read()

def test_rst_init_signature():
    """Test that RST.__init__ accepts header_rows parameter."""

    # Check if the __init__ method signature includes header_rows
    if 'def __init__(self, header_rows=None):' in rst_source:
        print("✓ RST.__init__ accepts header_rows parameter")
        return True
    elif 'def __init__(self):' in rst_source and 'header_rows' not in rst_source.split('def __init__')[1].split('def ')[0]:
        print("✗ RST.__init__ does NOT accept header_rows parameter")
        print("This is the bug - it should accept header_rows parameter")
        return False
    else:
        print("? Could not determine RST.__init__ signature")
        return False

def test_rst_write_method():
    """Test that RST.write method uses header_rows correctly."""

    # Check if the write method uses len(self.header.header_rows)
    if 'idx = len(self.header.header_rows)' in rst_source:
        print("✓ RST.write method uses header_rows correctly")
        return True
    else:
        print("✗ RST.write method does NOT use header_rows correctly")
        return False

def test_rst_read_method():
    """Test that RST.read method exists and uses header_rows."""

    # Check if the read method exists and sets start_line based on header_rows
    if 'def read(self, table):' in rst_source and 'self.data.start_line = 2 + len(self.header.header_rows)' in rst_source:
        print("✓ RST.read method exists and uses header_rows")
        return True
    else:
        print("✗ RST.read method does NOT exist or does not use header_rows")
        return False

if __name__ == "__main__":
    print("Testing RST class for header_rows support...")
    print("=" * 60)

    test1 = test_rst_init_signature()
    test2 = test_rst_write_method()
    test3 = test_rst_read_method()

    print("=" * 60)

    if test1 and test2 and test3:
        print("✓ All tests passed - header_rows is fully supported!")
        sys.exit(0)
    else:
        print("✗ Some tests failed - header_rows is NOT fully supported")
        print("This is expected on the buggy version.")
        sys.exit(1)