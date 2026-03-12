#!/usr/bin/env python3
"""
Test to reproduce the issue where expr.atoms() should return objects with no args
instead of subclasses of Atom.

The issue: expr.atoms() with no arguments returns subclasses of Atom in expr.
But the correct definition of a leaf node should be that it has no .args.

This test creates an Atom subclass with args and verifies that:
1. On the buggy version (base commit): atoms() returns the Atom subclass (FAIL)
2. On the fixed version (head commit): atoms() does NOT return it (PASS)
"""

from sympy.core.basic import Atom, Basic
from sympy import Symbol, sin, I, pi, Mul, Integer

def test_atoms_with_no_args():
    """Test that atoms() returns objects with no args, not subclasses of Atom."""

    # Create a custom Atom subclass that has args
    # This demonstrates the issue: an Atom subclass can have args
    class AtomWithArgs(Atom):
        def __new__(cls, *args):
            obj = Basic.__new__(cls, *args)
            return obj

    # Create an instance with SymPy Integer args (not Python ints)
    atom_with_args = AtomWithArgs(Integer(1), Integer(2))
    print(f"Created AtomWithArgs: {atom_with_args}")
    print(f"  Type: {type(atom_with_args)}")
    print(f"  Args: {atom_with_args.args}")
    print(f"  Is Atom: {isinstance(atom_with_args, Atom)}")
    print()

    # Create an expression containing this atom using Mul
    x = Symbol('x')
    expr = Mul(x, atom_with_args)
    print(f"Expression: {expr}")
    print(f"Expression atoms(): {expr.atoms()}")
    print()

    # The bug: atoms() returns Atom subclasses even if they have args
    # The fix: atoms() should only return objects with no args
    atoms_result = expr.atoms()

    # Check if atom_with_args is in the result
    has_atom_with_args = atom_with_args in atoms_result

    print(f"Does atoms() include AtomWithArgs? {has_atom_with_args}")

    # On the buggy version (base commit), this will be True (FAIL)
    # On the fixed version (head commit), this will be False (PASS)
    assert not has_atom_with_args, (
        f"atoms() should not return objects with args, but it returned: {atoms_result}\n"
        f"AtomWithArgs {atom_with_args} has args {atom_with_args.args} and should not be included."
    )

    print("Test passed - atoms() correctly returns only objects with no args")

if __name__ == "__main__":
    test_atoms_with_no_args()