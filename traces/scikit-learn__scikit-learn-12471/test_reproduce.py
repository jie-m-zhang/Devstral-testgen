import numpy as np
from sklearn.preprocessing import OneHotEncoder

def test_onehot_encoder_string_unknown_ignore():
    """
    Test for OneHotEncoder with handle_unknown='ignore' and string categories.

    This test reproduces the issue where OneHotEncoder incorrectly handles
    unknown string values when the first category (alphabetically sorted)
    is longer than the unknown strings in the test data.

    The bug causes a ValueError because the longer category string cannot
    fit into the array space allocated for shorter strings.
    """

    # Create training data with strings of varying lengths
    # Note: '11111111' is the longest and will be first alphabetically
    # when sorted, but '22' is shorter
    train = np.array(['22', '333', '4444', '11111111']).reshape((-1, 1))

    # Create test data with an unknown value '55555' (shorter than '11111111')
    # and a known value '22'
    test = np.array(['55555', '22']).reshape((-1, 1))

    # Create OneHotEncoder with handle_unknown='ignore'
    ohe = OneHotEncoder(dtype=bool, handle_unknown='ignore')

    # Fit on training data
    ohe.fit(train)

    # Transform test data - this should work without errors
    # Expected: sparse matrix 2x4 with False everywhere except at (1, 1) for '22'
    try:
        enc_test = ohe.transform(test)
        print("Transform succeeded")

        # Verify the shape is correct (2 samples, 4 categories)
        assert enc_test.shape == (2, 4), f"Expected shape (2, 4), got {enc_test.shape}"

        # Convert to dense array for easier verification
        dense_result = enc_test.toarray()

        # The first row (unknown '55555') should be all False
        assert not dense_result[0].any(), f"First row should be all False, got {dense_result[0]}"

        # The second row should have True only at position 1 (for '22')
        # Categories are sorted alphabetically: ['11111111', '22', '333', '4444']
        # So '22' is at index 1
        expected_second_row = np.array([False, True, False, False])
        assert np.array_equal(dense_result[1], expected_second_row), \
            f"Second row should be {expected_second_row}, got {dense_result[1]}"

        print("Test passed - issue is fixed")
        return True

    except ValueError as e:
        print(f"ValueError occurred: {e}")
        print("This is the expected error on the buggy version")
        raise

if __name__ == "__main__":
    test_onehot_encoder_string_unknown_ignore()