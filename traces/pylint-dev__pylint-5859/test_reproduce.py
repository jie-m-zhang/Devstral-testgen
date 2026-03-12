#!/usr/bin/env python3
"""
Test to reproduce the issue where "--notes" option ignores note tags that are entirely punctuation.

The issue: If a note tag specified with the `--notes` option is entirely punctuation,
pylint won't report a fixme warning (W0511) because the regex pattern uses \b (word boundary)
which doesn't match punctuation-only tags.

The fix changes the pattern from rf"#\s*({notes})\b" to rf"#\s*({notes})(?=(:|\s|\Z))"
which uses a lookahead to match if followed by colon, whitespace, or end of string.
"""

import re
import sys

def test_punctuation_notes_regex():
    """Test that the regex pattern correctly matches punctuation-only note tags."""

    # Simulate the notes configuration
    notes = ["YES", "???"]

    # Create the regex patterns - old (buggy) and new (fixed)
    notes_escaped = "|".join(re.escape(note) for note in notes)

    # Old pattern (buggy) - uses \b which fails for punctuation
    old_pattern = re.compile(rf"#\s*({notes_escaped})\b", re.I)

    # New pattern (fixed) - uses lookahead
    new_pattern = re.compile(rf"#\s*({notes_escaped})(?=(:|\s|\Z))", re.I)

    # Test cases
    test_cases = [
        "# YES: yes",
        "# ???: no",
        "# yes: something",  # Should not match
        "# ??? something",   # Should not match (no colon)
    ]

    print("Testing regex patterns:")
    print(f"Notes: {notes}")
    print(f"Old pattern: {old_pattern.pattern}")
    print(f"New pattern: {new_pattern.pattern}")
    print()

    # Test old pattern (should fail to match ???)
    print("Old pattern results:")
    old_matches = []
    for test_case in test_cases:
        match = old_pattern.search(test_case)
        if match:
            old_matches.append(match.group(1))
            print(f"  MATCH: {test_case} -> {match.group(1)}")
        else:
            print(f"  NO MATCH: {test_case}")

    # Test new pattern (should match both YES and ???)
    print("\nNew pattern results:")
    new_matches = []
    for test_case in test_cases:
        match = new_pattern.search(test_case)
        if match:
            new_matches.append(match.group(1))
            print(f"  MATCH: {test_case} -> {match.group(1)}")
        else:
            print(f"  NO MATCH: {test_case}")

    # Verify the fix
    print("\nVerification:")

    # Old pattern should only match YES (not ???)
    yes_in_old = any(m == "YES" for m in old_matches)
    punctuation_in_old = any(m == "???" for m in old_matches)

    print(f"Old pattern matches YES: {yes_in_old}")
    print(f"Old pattern matches ???: {punctuation_in_old}")

    # New pattern should match both
    yes_in_new = any(m == "YES" for m in new_matches)
    punctuation_in_new = any(m == "???" for m in new_matches)

    print(f"New pattern matches YES: {yes_in_new}")
    print(f"New pattern matches ???: {punctuation_in_new}")

    # The test: new pattern should detect ??? but old pattern should not
    if punctuation_in_new and not punctuation_in_old:
        print("\n✓ Test PASSED - New pattern correctly detects punctuation-only tags!")
        return 0
    else:
        print(f"\n✗ Test FAILED - Expected new pattern to detect ??? but old pattern not to")
        print(f"  punctuation_in_new={punctuation_in_new}, punctuation_in_old={punctuation_in_old}")
        return 1

if __name__ == "__main__":
    sys.exit(test_punctuation_notes_regex())