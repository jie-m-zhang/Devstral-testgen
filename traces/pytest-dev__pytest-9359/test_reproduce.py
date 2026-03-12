"""
Test to reproduce and verify the fix for the decorator line issue in Python 3.9.

This test directly tests the get_statement_startend2 function behavior.
"""

import ast
import sys
import os
sys.path.insert(0, '/testbed/src')

from _pytest._code.source import get_statement_startend2

def test_decorator_in_statement_range():
    """
    Test that verifies decorator lines are included in statement range calculations.

    The bug: In Python 3.9, decorator lines were not included in the statement
    range calculation, causing extra lines to appear in error output.

    The fix: Add decorator lines to the values list in get_statement_startend2.
    """

    # Create a code snippet with a decorated function after an assertion
    code = '''def t(foo):
    return foo

def test_func():
    assert 1 == 2  # This assertion will fail

    @t
    def inner():
        return 2
'''

    # Parse the code into AST
    tree = ast.parse(code)

    # Find the assertion statement
    assert_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            assert_node = node
            break

    assert assert_node is not None, "Could not find assertion in AST"

    # Get the line number of the assertion (0-indexed)
    # In our code, the assertion is on line 4 (0-indexed: 3)
    assert_lineno = assert_node.lineno - 1  # Convert to 0-indexed

    # Find the decorated function node
    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'inner':
            func_node = node
            break

    assert func_node is not None, "Could not find inner function in AST"

    # Call the function that was patched
    # We need to pass the function node that contains the decorator
    start, end = get_statement_startend2(assert_lineno, func_node)

    # The key insight: with the bug, the decorator line is not properly handled
    # With the fix, the decorator line should be included

    # Let's check the actual behavior by looking at what lines are considered
    # We'll test by creating a Source object and checking the statement range

    from _pytest._code.source import Source

    source = Source(code.split('\n'))

    # Get the statement range for the assertion line
    ast_node, stmt_start, stmt_end = source.getstatementrange(assert_lineno)

    # The bug: without the patch, stmt_end might include the decorator line
    # With the patch, stmt_end should be correct

    # Let's check if the decorator line is within the statement range
    # The decorator is on line 6 (0-indexed: 5)
    decorator_line = 5

    # With the bug, the statement range might extend too far and include the decorator
    # With the fix, it should not

    # Check if decorator line is within the statement range
    decorator_in_range = stmt_start <= decorator_line < stmt_end

    # With the bug: decorator_in_range = True (statement range is too broad)
    # With the fix: decorator_in_range = False (statement range is correct)

    # The test should fail on buggy code (decorator_in_range = True)
    # and pass on fixed code (decorator_in_range = False)
    assert not decorator_in_range, f"Decorator line should not be in statement range. Start: {stmt_start}, End: {stmt_end}, Decorator: {decorator_line}"

    print(f"Test passed - decorator line is not in statement range")
    print(f"Statement range: {stmt_start} to {stmt_end}")

if __name__ == "__main__":
    test_decorator_in_statement_range()