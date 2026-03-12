"""
Test to reproduce the issue with "WARNING: no number is assigned for table" warnings.

The issue is that Sphinx 3.3 started generating warnings when using :numref: to reference
tables that don't have a number assigned. The warning message format was changed in the fix.

This test verifies that:
1. On the base commit (buggy version): The old warning message format is used
2. On the head commit (fixed version): The new warning message format is used

The test expects the NEW warning message format (fixed version).
It will FAIL on the base commit (buggy version) and PASS on the head commit (fixed version).
"""

import tempfile
import shutil
from pathlib import Path
from sphinx.testing import restructuredtext
from sphinx.testing.util import assert_node
from sphinx import addnodes
from unittest import mock
from docutils import nodes
from sphinx.domains.std import StandardDomain
from sphinx.util import logging

def test_numref_warning_message():
    """
    Test that the correct warning message is generated when a table has no number assigned.

    This test creates a scenario where:
    1. A table is referenced with :numref:
    2. The table doesn't have a number assigned (ValueError in get_fignumber)
    3. The warning message should match the expected format

    The test expects the NEW warning message format (fixed version):
    "Failed to create a cross reference. Any number is not assigned: %s"

    It will FAIL on the base commit (buggy version) which uses:
    "no number is assigned for %s: %s"
    """

    # Create a mock environment
    env = mock.Mock(domaindata={})
    env.app.registry.enumerable_nodes = {}
    env.config.numfig = True
    env.config.numfig_format = {}

    # Create a mock builder
    builder = mock.Mock()
    builder.name = 'html'

    # Create a mock document with a table node
    table_node = nodes.table('', nodes.title('Test Table', 'Test Table'))
    table_node['ids'] = ['test-table']

    # Create a mock doctree
    doctree = mock.Mock()
    doctree.ids = {'test-table': table_node}

    # Mock the environment to return the doctree
    env.get_doctree.return_value = doctree

    # Create the domain
    domain = StandardDomain(env)

    # Add a label for the table
    domain.labels['test-table'] = ('testdoc', 'test-table', 'Test Table')

    # Create a pending_xref node for numref
    fromdocname = 'testdoc'
    target = 'test-table'
    node = addnodes.pending_xref('', reftype='numref', refdomain='std', reftarget=target)
    contnode = nodes.inline('test', 'test')

    # Mock get_fignumber to raise ValueError (simulating no number assigned)
    original_get_fignumber = domain.get_fignumber
    def mock_get_fignumber(*args, **kwargs):
        raise ValueError("No number assigned")
    domain.get_fignumber = mock_get_fignumber

    # Capture warnings
    logger = logging.getLogger(__name__)
    with mock.patch('sphinx.domains.std.logger') as mock_logger:
        result = domain._resolve_numref_xref(env, fromdocname, builder, 'numref', target, node, contnode)

        # Verify that the warning was called
        assert mock_logger.warning.called, "Warning should have been called"

        # Get the warning call arguments
        warning_call = mock_logger.warning.call_args
        warning_message = warning_call[0][0]

        print(f"Warning message: {warning_message}")
        print(f"Warning args: {warning_call[0]}")
        print(f"Warning kwargs: {warning_call[1]}")

        # The warning message should contain the NEW format (fixed version)
        # Expected: "Failed to create a cross reference. Any number is not assigned: %s"
        expected_message = "Failed to create a cross reference. Any number is not assigned: %s"
        assert expected_message in str(warning_message), f"Expected new warning message format not found. Got: {warning_message}"

        # Verify the arguments - should only have the labelid, not figtype and labelid
        warning_args = warning_call[0][1:]
        assert len(warning_args) == 1, f"Expected 1 argument (labelid), got {len(warning_args)}: {warning_args}"
        assert warning_args[0] == 'test-table', f"Expected labelid 'test-table', got {warning_args[0]}"

        # Verify that contnode is returned (no cross-reference created)
        assert result == contnode, "Should return contnode when no number is assigned"

    print("Test passed - warning message format is correct (fixed version)")

if __name__ == "__main__":
    test_numref_warning_message()