#!/usr/bin/env python
"""
Test to reproduce the issue with RepeatedKFold and RepeatedStratifiedKFold __repr__ strings.
"""

def test_repeated_kfold_repr():
    """Test that RepeatedKFold shows correct __repr__ string."""
    from sklearn.model_selection import RepeatedKFold

    # Create a RepeatedKFold instance with default parameters
    rkf = RepeatedKFold()

    # Get the repr string
    repr_str = repr(rkf)

    # Check that the repr contains the expected components (order may vary)
    assert "RepeatedKFold" in repr_str, f"Expected 'RepeatedKFold' in repr, got: {repr_str}"
    assert "n_splits=5" in repr_str, f"Expected 'n_splits=5' in repr, got: {repr_str}"
    assert "n_repeats=10" in repr_str, f"Expected 'n_repeats=10' in repr, got: {repr_str}"
    assert "random_state=None" in repr_str, f"Expected 'random_state=None' in repr, got: {repr_str}"

    # Make sure it doesn't contain the object address format
    assert "<sklearn.model_selection._split.RepeatedKFold object at" not in repr_str, f"Should not contain object address format, got: {repr_str}"

    print(f"[PASS] RepeatedKFold repr test passed: {repr_str}")

def test_repeated_stratified_kfold_repr():
    """Test that RepeatedStratifiedKFold shows correct __repr__ string."""
    from sklearn.model_selection import RepeatedStratifiedKFold

    # Create a RepeatedStratifiedKFold instance with default parameters
    rskf = RepeatedStratifiedKFold()

    # Get the repr string
    repr_str = repr(rskf)

    # Check that the repr contains the expected components (order may vary)
    assert "RepeatedStratifiedKFold" in repr_str, f"Expected 'RepeatedStratifiedKFold' in repr, got: {repr_str}"
    assert "n_splits=5" in repr_str, f"Expected 'n_splits=5' in repr, got: {repr_str}"
    assert "n_repeats=10" in repr_str, f"Expected 'n_repeats=10' in repr, got: {repr_str}"
    assert "random_state=None" in repr_str, f"Expected 'random_state=None' in repr, got: {repr_str}"

    # Make sure it doesn't contain the object address format
    assert "<sklearn.model_selection._split.RepeatedStratifiedKFold object at" not in repr_str, f"Should not contain object address format, got: {repr_str}"

    print(f"[PASS] RepeatedStratifiedKFold repr test passed: {repr_str}")

def test_repeated_kfold_custom_params_repr():
    """Test that RepeatedKFold with custom parameters shows correct __repr__ string."""
    from sklearn.model_selection import RepeatedKFold

    # Create a RepeatedKFold instance with custom parameters
    rkf = RepeatedKFold(n_splits=3, n_repeats=5, random_state=42)

    # Get the repr string
    repr_str = repr(rkf)

    # Check that the repr contains the expected components (order may vary)
    assert "RepeatedKFold" in repr_str, f"Expected 'RepeatedKFold' in repr, got: {repr_str}"
    assert "n_splits=3" in repr_str, f"Expected 'n_splits=3' in repr, got: {repr_str}"
    assert "n_repeats=5" in repr_str, f"Expected 'n_repeats=5' in repr, got: {repr_str}"
    assert "random_state=42" in repr_str, f"Expected 'random_state=42' in repr, got: {repr_str}"

    # Make sure it doesn't contain the object address format
    assert "<sklearn.model_selection._split.RepeatedKFold object at" not in repr_str, f"Should not contain object address format, got: {repr_str}"

    print(f"[PASS] RepeatedKFold custom params repr test passed: {repr_str}")

def test_repeated_stratified_kfold_custom_params_repr():
    """Test that RepeatedStratifiedKFold with custom parameters shows correct __repr__ string."""
    from sklearn.model_selection import RepeatedStratifiedKFold

    # Create a RepeatedStratifiedKFold instance with custom parameters
    rskf = RepeatedStratifiedKFold(n_splits=4, n_repeats=7, random_state=123)

    # Get the repr string
    repr_str = repr(rskf)

    # Check that the repr contains the expected components (order may vary)
    assert "RepeatedStratifiedKFold" in repr_str, f"Expected 'RepeatedStratifiedKFold' in repr, got: {repr_str}"
    assert "n_splits=4" in repr_str, f"Expected 'n_splits=4' in repr, got: {repr_str}"
    assert "n_repeats=7" in repr_str, f"Expected 'n_repeats=7' in repr, got: {repr_str}"
    assert "random_state=123" in repr_str, f"Expected 'random_state=123' in repr, got: {repr_str}"

    # Make sure it doesn't contain the object address format
    assert "<sklearn.model_selection._split.RepeatedStratifiedKFold object at" not in repr_str, f"Should not contain object address format, got: {repr_str}"

    print(f"[PASS] RepeatedStratifiedKFold custom params repr test passed: {repr_str}")

if __name__ == "__main__":
    print("Testing RepeatedKFold and RepeatedStratifiedKFold __repr__ strings...")

    try:
        test_repeated_kfold_repr()
        test_repeated_stratified_kfold_repr()
        test_repeated_kfold_custom_params_repr()
        test_repeated_stratified_kfold_custom_params_repr()
        print("\nAll tests passed!")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        exit(1)