"""Test to reproduce the issue with rst_prolog removing top level headings containing domain directives."""

import tempfile
import shutil
import os
import sys
from pathlib import Path
from docutils.statemachine import StringList

# Add the testbed to the path so we can import sphinx
sys.path.insert(0, '/testbed')

from sphinx.util.rst import prepend_prolog

def test_rst_prolog_with_domain_directive():
    """
    Test that prepend_prolog correctly handles domain directives in headings.

    The bug: When rst_prolog is set, domain directives like :mod: are incorrectly
    identified as docinfo fields (because they start with ':'), causing the
    function to skip past them and insert the prolog in the wrong place.

    This test creates a StringList with a domain directive as the first heading
    and checks where the prolog is inserted.
    """
    # Create content with a domain directive as the first heading
    content = StringList([
        ':mod:`mypackage2`',  # This is a domain directive, not docinfo
        '=================',
        '',
        'Content',
        '',
        'Subheading',
        '----------'
    ], 'dummy.rst')

    # Set a prolog
    prolog = '.. |psf| replace:: Python Software Foundation'

    # Call prepend_prolog
    prepend_prolog(content, prolog)

    # Get the resulting content
    result = list(content)

    # The bug: In the buggy version, the domain directive line is treated as docinfo
    # and skipped, so the prolog is inserted AFTER the domain directive line but
    # BEFORE the underline, breaking the heading structure.
    #
    # Expected behavior: The domain directive should NOT be treated as docinfo,
    # so the prolog should be inserted BEFORE the domain directive heading.

    # In the buggy version, the result would be:
    # 0: ':mod:`mypackage2`' (treated as docinfo, skipped)
    # 1: '=================' (heading underline)
    # 2: '' (blank line after docinfo)
    # 3: '.. |psf| replace:: Python Software Foundation' (prolog inserted here - WRONG!)
    # 4: ''
    # 5: 'Content'
    #
    # In the fixed version, the result should be:
    # 0: '.. |psf| replace:: Python Software Foundation' (prolog inserted at top)
    # 1: ''
    # 2: ':mod:`mypackage2`' (domain directive heading)
    # 3: '================='
    # 4: ''
    # 5: 'Content'

    # Check if the prolog was inserted in the correct position
    # The first non-empty line after prolog should be the domain directive heading
    found_prolog = False
    found_heading = False
    prolog_line_index = -1
    heading_line_index = -1

    for i, line in enumerate(result):
        if 'Python Software Foundation' in line:
            found_prolog = True
            prolog_line_index = i
        if ':mod:`mypackage2`' in line:
            found_heading = True
            heading_line_index = i

    # Both should be found
    assert found_prolog, "Prolog not found in result"
    assert found_heading, "Domain directive heading not found in result"

    # In the buggy version, prolog_line_index > heading_line_index (prolog comes after heading)
    # In the fixed version, prolog_line_index < heading_line_index (prolog comes before heading)
    print(f"Prolog line index: {prolog_line_index}")
    print(f"Heading line index: {heading_line_index}")
    print(f"Result content:")
    for i, line in enumerate(result):
        print(f"  {i}: {repr(line)}")

    # The fix: prolog should come BEFORE the domain directive heading
    assert prolog_line_index < heading_line_index, \
        f"Prolog inserted after domain directive heading. " \
        f"Prolog at line {prolog_line_index}, heading at line {heading_line_index}. " \
        f"This breaks the heading structure."

    print("Test passed - prolog correctly inserted before domain directive heading")

if __name__ == "__main__":
    test_rst_prolog_with_domain_directive()