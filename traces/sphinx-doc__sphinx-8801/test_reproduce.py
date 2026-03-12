#!/usr/bin/env python3
"""
Test to reproduce the issue where annotation-only members in superclass
are treated as "undocumented" when using :inherited-members:.
"""

import sys
import tempfile
import os
from pathlib import Path

# Add the testbed to the path
sys.path.insert(0, '/testbed')

from sphinx.testing.util import SphinxTestApp
from sphinx.ext.autodoc import ObjectMember

def test_inherited_annotation_with_docstring():
    """
    Test that annotation-only members in superclass with docstrings
    are properly documented when using :inherited-members:.
    """
    from sphinx.ext.autodoc.importer import get_class_members
    from sphinx.util.inspect import safe_getattr

    # Import the test module
    import test_annotation_inheritance

    # Get members of Bar class with inherited members
    objpath = ['test_annotation_inheritance', 'Bar']
    members = get_class_members(test_annotation_inheritance.Bar, objpath, safe_getattr)

    # Check that attr1 (inherited from Foo) is in members
    assert 'attr1' in members, "attr1 should be in Bar's members"

    # Check that attr1 has a docstring
    attr1_member = members['attr1']
    print(f"attr1 member: {attr1_member}")
    print(f"attr1 docstring: {attr1_member.docstring}")

    # This is the key assertion - attr1 should have a docstring
    # In the buggy version, it will be None
    # In the fixed version, it will be "docstring"
    assert attr1_member.docstring is not None, \
        f"attr1 should have a docstring, but got: {attr1_member.docstring}"

    assert "docstring" in attr1_member.docstring, \
        f"attr1 docstring should contain 'docstring', but got: {attr1_member.docstring}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_inherited_annotation_with_docstring()