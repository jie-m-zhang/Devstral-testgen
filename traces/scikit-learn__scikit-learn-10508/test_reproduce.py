"""
Test to reproduce the LabelEncoder transform issue with empty lists.

The issue is that LabelEncoder.transform([]) fails when the encoder was fitted
with string data, but works fine when fitted with numeric data.
"""
import numpy as np
from sklearn.preprocessing import LabelEncoder

def test_label_encoder_empty_transform():
    """
    Test that LabelEncoder.transform([]) works consistently regardless of
    the data type used for fitting.
    """
    # Test with numeric data - this should work
    le_numeric = LabelEncoder()
    le_numeric.fit([1, 2])
    result_numeric = le_numeric.transform([])
    print(f"Numeric fit transform result: {result_numeric}")
    print(f"Numeric fit transform result type: {type(result_numeric)}")
    print(f"Numeric fit transform result dtype: {result_numeric.dtype}")
    assert isinstance(result_numeric, np.ndarray), "Result should be numpy array"
    assert len(result_numeric) == 0, "Result should be empty"

    # Test with string data - this should also work but currently fails
    le_string = LabelEncoder()
    le_string.fit(["a", "b"])
    print(f"String fit classes: {le_string.classes_}")
    print(f"String fit classes dtype: {le_string.classes_.dtype}")

    try:
        result_string = le_string.transform([])
        print(f"String fit transform result: {result_string}")
        print(f"String fit transform result type: {type(result_string)}")
        print(f"String fit transform result dtype: {result_string.dtype}")
        assert isinstance(result_string, np.ndarray), "Result should be numpy array"
        assert len(result_string) == 0, "Result should be empty"
        print("Test passed - issue is fixed")
    except TypeError as e:
        print(f"TypeError occurred: {e}")
        raise AssertionError(f"LabelEncoder.transform([]) failed with TypeError when fitted with string data: {e}")

if __name__ == "__main__":
    test_label_encoder_empty_transform()