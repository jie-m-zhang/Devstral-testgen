#!/usr/bin/env python
"""
Test to reproduce the issue where get_backend() clears figures from Gcf.figs
if they were created under rc_context.
"""

import matplotlib.pyplot as plt
from matplotlib import get_backend, rc_context

def test_get_backend_clears_figures():
    """
    Test that get_backend() does not clear figures from Gcf.figs
    when figures were created under rc_context.
    """
    # Clear any existing figures
    plt.close('all')

    # Create a figure inside an rc_context
    with rc_context():
        fig2 = plt.figure()

    # Get the state before calling get_backend()
    before = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'

    # Call get_backend() - this is where the bug occurs
    backend = get_backend()

    # Get the state after calling get_backend()
    after = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'

    # The assertion should fail on buggy code, pass on fixed code
    assert before == after, (
        f'get_backend() cleared figures from Gcf.figs!\n'
        f'Before: {before}\n'
        f'After:  {after}\n'
        f'Backend: {backend}'
    )

    # Additional check: ensure the figure is still in Gcf.figs
    assert len(plt._pylab_helpers.Gcf.figs) > 0, (
        f'Gcf.figs should not be empty after get_backend()!\n'
        f'Backend: {backend}'
    )

    # Clean up
    plt.close('all')

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_get_backend_clears_figures()