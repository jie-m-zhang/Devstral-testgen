#!/usr/bin/env python
"""
Test to reproduce the issue with ResolverMatch.__repr__() not handling functools.partial() nicely.

The issue is that when a partial function is passed as the view, the __repr__ shows
"functools.partial" which isn't very helpful, especially as it doesn't reveal the
underlying function or arguments provided.
"""

import functools
from django.urls.resolvers import ResolverMatch

def test_view(request, arg1, arg2=None):
    """A simple test view function."""
    return None

def test_resolver_match_repr_with_partial():
    """Test that ResolverMatch.__repr__() handles functools.partial() properly."""

    # Create a partial function
    partial_func = functools.partial(test_view, arg2='default_value')

    # Create a ResolverMatch with the partial function
    match = ResolverMatch(
        func=partial_func,
        args=('test_arg',),
        kwargs={},
        url_name='test_url',
        app_names=['test_app'],
        namespaces=['test_namespace'],
        route='/test/path/'
    )

    # Get the repr string
    repr_str = repr(match)

    print("Repr string:", repr_str)

    # The issue is that on the buggy version, the repr will show:
    # "ResolverMatch(func=functools.partial, args=('test_arg',), kwargs={}, url_name='test_url', app_names=['test_app'], namespaces=['test_namespace'], route='/test/path/')"
    #
    # On the fixed version, it should show the actual partial object representation which includes
    # the underlying function and arguments:
    # "ResolverMatch(func=functools.partial(<function test_view at ...>, 'test_arg', arg2='default_value'), args=('test_arg',), kwargs={}, url_name='test_url', app_names=['test_app'], namespaces=['test_namespace'], route='/test/path/')"

    # Check if the repr contains information about the underlying function
    # On the buggy version, this will fail because it only shows "functools.partial"
    # On the fixed version, this will pass because it shows the actual partial representation
    assert 'test_view' in repr_str, f"Expected 'test_view' in repr string, got: {repr_str}"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_resolver_match_repr_with_partial()