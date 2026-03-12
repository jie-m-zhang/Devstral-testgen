#!/usr/bin/env python
"""
Test to reproduce the bug in io.fits related to D exponents.

The bug is in the _scale_back_ascii method where the replace() method
is called on a chararray but the result is not assigned back, so the
replacement doesn't actually happen.
"""

import numpy as np
from numpy import char as chararray
from astropy.io import fits
import tempfile
import os

def test_d_exponent_replacement():
    """
    Test that 'E' exponents are properly replaced with 'D' exponents
    in ASCII tables with D format columns.

    This test reproduces the bug where the replace() method is called
    but not assigned, so the replacement doesn't happen.
    """
    # Create an ASCII table with a D format column
    # D format is for double-precision floats in ASCII tables
    # We'll create values that will be formatted with exponents
    values = np.array([1.23456789e-10, 2.34567890e+20, 3.45678901e-05])
    
    # Create a column with D format (double precision)
    # The D format means double precision with exponent notation
    col = fits.Column(name='D_COL', format='D25.17', array=values, ascii=True)
    
    # Create a Table HDU (ASCII table)
    hdu = fits.TableHDU.from_columns([col])
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.fits', delete=False) as f:
        filename = f.name
    
    try:
        hdu.writeto(filename, overwrite=True)
        
        # Read it back
        with fits.open(filename) as hdul:
            # Get the data - this will be in converted form (float64)
            data = hdul[1].data
            
            # Now we need to trigger _scale_back_ascii
            # The _scale_back_ascii method is called when we need to convert
            # the internal representation back to ASCII format
            # This happens when writing the data back to a file
            # But we can also call _scale_back directly
            
            # First, let's modify a value to ensure we trigger the conversion
            data['D_COL'][0] = 5.67890123e-15
            
            # Now call _scale_back to convert back to ASCII format
            hdul[1].data._scale_back()
            
            # Get the raw field (the actual ASCII data)
            # In ASCII tables, the raw data is stored as character arrays
            raw_field = hdul[1].data._coldefs._arrays[0]
            
            print(f"Raw field type: {type(raw_field)}")
            print(f"Raw field dtype: {raw_field.dtype}")
            print(f"Raw field shape: {raw_field.shape}")
            
            # The raw field should be a chararray for ASCII tables
            # Let's check if it's a chararray
            if isinstance(raw_field, chararray.chararray):
                print("Raw field is a chararray")
            else:
                print("Raw field is NOT a chararray - this might be the issue")
                
            # Convert to string to check contents
            raw_str = raw_field.tostring().decode('ascii')
            print(f"Raw field as string: {repr(raw_str)}")
            
            # Check if 'E' was replaced with 'D'
            # In the buggy version, the replace() is called but not assigned,
            # so 'E' will still be present
            # In the fixed version, 'E' should be replaced with 'D'
            
            has_e = 'E+' in raw_str or 'E-' in raw_str
            has_d = 'D+' in raw_str or 'D-' in raw_str
            
            print(f"Has 'E' exponent: {has_e}")
            print(f"Has 'D' exponent: {has_d}")
            
            # Let's also check each row individually
            for i in range(len(raw_field)):
                row = raw_field[i].tostring().decode('ascii').strip()
                print(f"Row {i}: '{row}'")
                if 'E+' in row or 'E-' in row:
                    print(f"  -> Found 'E' exponent in row {i}")
                if 'D+' in row or 'D-' in row:
                    print(f"  -> Found 'D' exponent in row {i}")
            
            # In the buggy version, we should find 'E' but not 'D'
            # In the fixed version, we should find 'D' but not 'E'
            # So the assertion should be:
            # - On buggy code: has_e is True (E was NOT replaced)
            # - On fixed code: has_d is True (E was replaced with D)
            
            # The test should fail on buggy code and pass on fixed code
            if has_e and not has_d:
                print("BUG DETECTED: 'E' exponents were NOT replaced with 'D'")
                print("This is the buggy behavior - replace() was called but not assigned")
                return False
            elif has_d and not has_e:
                print("CORRECT: 'E' exponents were replaced with 'D'")
                print("This is the fixed behavior - replace() result was assigned")
                return True
            else:
                print(f"UNEXPECTED: has_e={has_e}, has_d={has_d}")
                print("This might mean the test didn't trigger the bug properly")
                return False
    finally:
        # Clean up
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    result = test_d_exponent_replacement()
    if result:
        print("\nTest PASSED - issue is fixed")
        exit(0)
    else:
        print("\nTest FAILED - issue reproduced")
        exit(1)