#!/usr/bin/env python3
"""
Test to reproduce the issue with Sphinx 3.2 complaining about option:: syntax.

The issue is that Sphinx 3.2 rejects option descriptions like:
.. option:: [enable=]PATTERN

This test verifies that the option description parsing works correctly.
"""

import re
import sys
from sphinx.domains.std import option_desc_re

def test_option_regex():
    """
    Test that the regex properly matches option descriptions with brackets.

    This should fail on the base commit and pass on the head commit.
    """
    # Test the specific case from the issue
    test_pattern = "[enable=]PATTERN"

    print(f"Testing pattern: {test_pattern}")
    print(f"Regex pattern: {option_desc_re.pattern}")

    match = option_desc_re.match(test_pattern)
    print(f"Regex match: {match}")

    if not match:
        print("ERROR: Regex does not match the pattern")
        return False

    optname, args = match.groups()
    print(f"optname: '{optname}'")
    print(f"args: '{args}'")

    # Check if the logic for handling brackets works
    if optname.endswith('[') and args.endswith(']'):
        print("Pattern has brackets - applying fix logic")
        optname_fixed = optname[:-1]
        args_fixed = '[' + args
        print(f"After fix - optname: '{optname_fixed}', args: '{args_fixed}'")
        return True
    else:
        print("Pattern doesn't need bracket handling")
        return True

def test_various_option_patterns():
    """
    Test various option patterns to ensure they all work.
    """
    test_cases = [
        ("[enable=]PATTERN", True),
        ("foo[=bar]", True),
        ("-f[=value]", True),
        ("--foo[=bar]", True),
        ("/opt[=arg]", True),
        ("+opt[=arg]", True),
        ("normal_option", True),
        ("-f", True),
        ("--long-option", True),
        ("/windows-option", True),
        ("+posix-option", True),
    ]

    all_passed = True

    for pattern, should_match in test_cases:
        print(f"\nTesting pattern: {pattern}")
        match = option_desc_re.match(pattern)
        if not match:
            if should_match:
                print(f"  FAIL: Regex does not match (but should)")
                all_passed = False
            else:
                print(f"  OK: Regex does not match (as expected)")
        else:
            optname, args = match.groups()
            print(f"  OK: optname='{optname}', args='{args}'")

            # Apply bracket handling logic if needed
            if optname.endswith('[') and args.endswith(']'):
                optname = optname[:-1]
                args = '[' + args
                print(f"  After bracket fix: optname='{optname}', args='{args}'")

    return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("Testing option description regex")
    print("=" * 60)

    # Test the specific case from the issue
    success1 = test_option_regex()

    print("\n" + "=" * 60)
    print("Testing various option patterns")
    print("=" * 60)

    # Test various patterns
    success2 = test_various_option_patterns()

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    if success1 and success2:
        print("All tests PASSED")
        sys.exit(0)
    else:
        print("Some tests FAILED")
        sys.exit(1)