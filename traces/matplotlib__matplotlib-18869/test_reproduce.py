#!/usr/bin/env python
"""
Test to reproduce the issue: Add easily comparable version info to toplevel

This test verifies that matplotlib exposes __version_info__ as a namedtuple
that can be easily compared with other version tuples.
"""

import sys

def test_version_info_exists():
    """Test that __version_info__ attribute exists and is accessible."""
    import matplotlib

    # Try to access __version_info__
    try:
        version_info = matplotlib.__version_info__
        print(f"✓ Successfully accessed __version_info__: {version_info}")
        return True
    except AttributeError as e:
        print(f"✗ Failed to access __version_info__: {e}")
        return False

def test_version_info_is_namedtuple():
    """Test that __version_info__ is a namedtuple with expected fields."""
    import matplotlib
    from collections import namedtuple

    try:
        version_info = matplotlib.__version_info__
    except AttributeError:
        print("✗ __version_info__ not accessible")
        return False

    # Check if it's a namedtuple
    if not isinstance(version_info, tuple):
        print(f"✗ __version_info__ is not a tuple, got {type(version_info)}")
        return False

    # Check if it has the expected fields (major, minor, micro, releaselevel, serial)
    expected_fields = ['major', 'minor', 'micro', 'releaselevel', 'serial']
    if not hasattr(version_info, '_fields'):
        print("✗ __version_info__ is not a namedtuple (no _fields attribute)")
        return False

    if list(version_info._fields) != expected_fields:
        print(f"✗ __version_info__ has wrong fields: {version_info._fields}, expected: {expected_fields}")
        return False

    print(f"✓ __version_info__ is a namedtuple with correct fields: {version_info._fields}")
    return True

def test_version_info_comparable():
    """Test that __version_info__ can be compared with other version tuples."""
    import matplotlib

    try:
        version_info = matplotlib.__version_info__
    except AttributeError:
        print("✗ __version_info__ not accessible")
        return False

    # Test comparison with a tuple
    try:
        result = version_info >= (3, 0, 0)
        print(f"✓ __version_info__ is comparable: {version_info} >= (3, 0, 0) = {result}")
        return True
    except Exception as e:
        print(f"✗ __version_info__ comparison failed: {e}")
        return False

def test_version_info_values():
    """Test that __version_info__ has reasonable values."""
    import matplotlib

    try:
        version_info = matplotlib.__version_info__
    except AttributeError:
        print("✗ __version_info__ not accessible")
        return False

    # Check that major, minor, micro are integers
    if not all(isinstance(getattr(version_info, field), int)
               for field in ['major', 'minor', 'micro', 'serial']):
        print(f"✗ __version_info__ numeric fields are not integers: {version_info}")
        return False

    # Check that releaselevel is a string
    if not isinstance(version_info.releaselevel, str):
        print(f"✗ __version_info__.releaselevel is not a string: {version_info.releaselevel}")
        return False

    print(f"✓ __version_info__ has valid values: {version_info}")
    return True

def test_version_consistency():
    """Test that __version_info__ is consistent with __version__."""
    import matplotlib
    from packaging.version import parse as parse_version

    try:
        version_str = matplotlib.__version__
        version_info = matplotlib.__version_info__
    except AttributeError as e:
        print(f"✗ Failed to access version attributes: {e}")
        return False

    # Parse the version string
    parsed = parse_version(version_str)

    # Check that the major, minor, micro match
    if (version_info.major != parsed.major or
        version_info.minor != parsed.minor or
        version_info.micro != parsed.micro):
        print(f"✗ Version info doesn't match version string: {version_info} vs {parsed}")
        return False

    print(f"✓ __version_info__ is consistent with __version__: {version_info} ~ {version_str}")
    return True

def main():
    """Run all tests."""
    print("Testing matplotlib version_info feature...")
    print("=" * 60)

    tests = [
        ("Version info exists", test_version_info_exists),
        ("Version info is namedtuple", test_version_info_is_namedtuple),
        ("Version info is comparable", test_version_info_comparable),
        ("Version info has valid values", test_version_info_values),
        ("Version info consistent with __version__", test_version_consistency),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        print("-" * 60)
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    for (test_name, _), result in zip(tests, results):
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed - issue is fixed!")
        return 0
    else:
        print("\n✗ Some tests failed - issue still exists")
        return 1

if __name__ == "__main__":
    sys.exit(main())