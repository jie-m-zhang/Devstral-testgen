#!/usr/bin/env python
"""
Test to reproduce the issue with partitions() reusing output dictionaries.

The issue is that partitions() yields the same dictionary object each time,
causing all elements in a list comprehension to be the same (the last one yielded).
"""

from sympy.utilities.iterables import partitions

def test_partitions_dict_reuse():
    """Test that partitions() returns unique dictionary objects.

    This test should FAIL on the buggy version (base commit) because all
    dictionaries in the list will be the same object (the last one yielded).

    It should PASS on the fixed version (head commit) where each partition
    is a separate dictionary object.
    """
    # Get partitions of 6 with k=2
    result = list(partitions(6, k=2))

    # The expected partitions (from the docstring)
    expected = [
        {2: 3},
        {1: 2, 2: 2},
        {1: 4, 2: 1},
        {1: 6}
    ]

    # Check that we have the right number of partitions
    assert len(result) == len(expected), \
        f"Expected {len(expected)} partitions, got {len(result)}"

    # Check that each partition is different (this is the key test)
    # On the buggy version, all partitions will be {1: 6} (the last one)
    # On the fixed version, each partition will be different
    for i, (actual, exp) in enumerate(zip(result, expected)):
        assert actual == exp, \
            f"Partition {i}: Expected {exp}, got {actual}. " \
            f"All partitions: {result}"

    # Additional check: verify that the dictionaries are actually different objects
    # (not just the same object with modified contents)
    for i in range(len(result) - 1):
        assert result[i] is not result[i + 1], \
            f"Partitions {i} and {i+1} are the same object!"

    print("Test passed - partitions() returns unique dictionary objects")

if __name__ == "__main__":
    test_partitions_dict_reuse()