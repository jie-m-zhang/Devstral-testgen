#!/usr/bin/env python
"""
Test to reproduce the issue where napoleon_use_param doesn't affect
the "Other Parameters" section.

The test should FAIL on the base commit and PASS on the head commit.
"""

from sphinx.ext.napoleon import Config
from sphinx.ext.napoleon.docstring import NumpyDocstring

def test_napoleon_use_param_other_parameters():
    """
    Test that napoleon_use_param affects the "Other Parameters" section.

    When napoleon_use_param=True, both Parameters and Other Parameters
    sections should use the same formatting (param/type directives).
    """
    # Test docstring with both Parameters and Other Parameters sections
    docstring = """
Parameters
----------
x : int
    Description of x

Other Parameters
---------------
y : float
    Description of y
"""

    # Test with napoleon_use_param=True
    config = Config(napoleon_use_param=True)
    result = str(NumpyDocstring(docstring, config=config))

    print("Result with napoleon_use_param=True:")
    print(result)
    print()

    # When napoleon_use_param=True, both sections should use :param and :type directives
    # The Parameters section should look like:
    # :param x:
    # :type x: int
    #
    # The Other Parameters section should ALSO look like:
    # :param y:
    # :type y: float
    #
    # But in the buggy version, Other Parameters uses the field list format:
    # :Other Parameters: **y** (*float*)

    # Check that Parameters section uses param/type format
    assert ":param x:" in result, "Parameters section should use :param directive"
    assert ":type x: int" in result, "Parameters section should use :type directive"

    # Check that Other Parameters section ALSO uses param/type format (this is the fix)
    assert ":param y:" in result, "Other Parameters section should use :param directive when napoleon_use_param=True"
    assert ":type y: float" in result, "Other Parameters section should use :type directive when napoleon_use_param=True"

    # In the buggy version, this would be present instead:
    # :Other Parameters: **y** (*float*)
    assert ":Other Parameters:" not in result, "Other Parameters should NOT use field list format when napoleon_use_param=True"

    print("Test passed - napoleon_use_param correctly affects Other Parameters section")

if __name__ == "__main__":
    test_napoleon_use_param_other_parameters()