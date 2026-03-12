#!/usr/bin/env python
"""
Test to reproduce the issue with separability_matrix not computing separability
correctly for nested CompoundModels.

The issue is that when nesting compound models like:
    m.Pix2Sky_TAN() & cm
where cm is itself a compound model (m.Linear1D(10) & m.Linear1D(5)),
the separability matrix incorrectly shows dependencies between inputs and outputs
that should be independent.
"""

import numpy as np
from astropy.modeling import models as m
from astropy.modeling.separable import separability_matrix

def test_nested_compound_model_separability():
    """
    Test that separability_matrix correctly handles nested compound models.

    The expected behavior is that when we have:
    - cm = m.Linear1D(10) & m.Linear1D(5)
    - nested = m.Pix2Sky_TAN() & cm

    The separability matrix should show that:
    - Pix2Sky_TAN outputs depend on Pix2Sky_TAN inputs (top-left 2x2 block)
    - Linear1D(10) output depends only on its input (bottom-left element)
    - Linear1D(5) output depends only on its input (bottom-right element)
    - There should be NO cross-dependencies between the two Linear1D models
    """
    # Create a simple compound model
    cm = m.Linear1D(10) & m.Linear1D(5)

    # Test the simple compound model first - this should work correctly
    result_simple = separability_matrix(cm)
    expected_simple = np.array([[True, False],
                                [False, True]])
    assert np.array_equal(result_simple, expected_simple), \
        f"Simple compound model failed. Expected:\n{expected_simple}\nGot:\n{result_simple}"

    # Now test the nested compound model - this is where the bug occurs
    nested = m.Pix2Sky_TAN() & cm
    result_nested = separability_matrix(nested)

    # The expected matrix should be:
    # - Pix2Sky_TAN has 2 inputs and 2 outputs, so top-left 2x2 should be all True
    # - Linear1D(10) has 1 input and 1 output, should be independent (True at [2, 2])
    # - Linear1D(5) has 1 input and 1 output, should be independent (True at [3, 3])
    # - NO cross-dependencies between the two Linear1D models
    expected_nested = np.array([
        [True, True, False, False],  # Pix2Sky_TAN outputs depend on Pix2Sky_TAN inputs
        [True, True, False, False],  # Pix2Sky_TAN outputs depend on Pix2Sky_TAN inputs
        [False, False, True, False],  # Linear1D(10) output depends only on its input
        [False, False, False, True]   # Linear1D(5) output depends only on its input
    ])

    print("Result matrix:")
    print(result_nested)
    print("\nExpected matrix:")
    print(expected_nested)

    # Check if the result matches expected
    if not np.array_equal(result_nested, expected_nested):
        print("\nMISMATCH DETECTED!")
        print("The bug is present: inputs and outputs are incorrectly shown as dependent")
        assert False, f"Nested compound model failed. Expected:\n{expected_nested}\nGot:\n{result_nested}"

    print("\nTest passed - separability matrix is correct!")

if __name__ == "__main__":
    test_nested_compound_model_separability()