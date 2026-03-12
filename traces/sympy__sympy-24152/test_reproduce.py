#!/usr/bin/env python
"""
Test to reproduce the TensorProduct expansion bug.

The bug: When a TensorProduct has summands with scalar factors,
the expansion stops incomplete.

Expected behavior: 
TensorProduct(2*U - V, U + V).expand(tensorproduct=True)
should expand to: 2*UxU + 2*UxV - VxU - VxV

Buggy behavior:
It only expands to: 2*Ux(U + V) - Vx(U + V)
(missing the expansion of the second tensor factor)
"""

from sympy import *
from sympy.physics.quantum import *

def test_tensorproduct_expand_with_scalar_factors():
    """Test that TensorProduct expansion works correctly with scalar factors."""
    U = Operator('U')
    V = Operator('V')

    # Create tensor product with scalar factors in summands
    P = TensorProduct(2*U - V, U + V)

    # Expand the tensor product
    expanded = P.expand(tensorproduct=True)

    print("Original:", P)
    print("Expanded:", expanded)

    # Expected result: complete expansion
    # 2*U⊗U + 2*U⊗V - V⊗U - V⊗V
    expected = 2*TensorProduct(U, U) + 2*TensorProduct(U, V) - TensorProduct(V, U) - TensorProduct(V, V)

    print("Expected:", expected)

    # The test: expanded should equal expected
    # On buggy version: this will fail because expansion is incomplete
    # On fixed version: this will pass because expansion is complete
    assert expanded == expected, f"Expected {expected}, but got {expanded}"

    print("Test passed - TensorProduct expansion works correctly!")

if __name__ == "__main__":
    test_tensorproduct_expand_with_scalar_factors()