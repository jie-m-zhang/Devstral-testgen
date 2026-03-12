from sympy import *
from sympy.matrices.expressions.blockmatrix import BlockMatrix

def test_blockmatrix_element_access():
    """
    Test that BlockMatrix element access returns the correct unevaluated form
    when the index is symbolic and could refer to elements from different blocks.
    """
    n, i = symbols('n, i', integer=True)
    A = MatrixSymbol('A', 1, 1)
    B = MatrixSymbol('B', n, 1)
    C = BlockMatrix([[A], [B]])

    # Get the element C[i, 0]
    element = C[i, 0]

    # The bug is that on the buggy version, element.args[0] is A (the submatrix)
    # On the fixed version, element.args[0] should be C (the BlockMatrix itself)
    print(f"Element: {element}")
    print(f"Element args[0]: {element.args[0]}")
    print(f"Type of args[0]: {type(element.args[0])}")

    # Check that the element is from the BlockMatrix C, not from submatrix A
    # On buggy version: element.args[0] == A
    # On fixed version: element.args[0] == C
    is_buggy = element.args[0] == A

    # The test should fail on buggy version (is_buggy == True)
    # and pass on fixed version (is_buggy == False)
    assert not is_buggy, f"Bug detected: C[i, 0].args[0] is {element.args[0]}, should be the BlockMatrix C, not submatrix A"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_blockmatrix_element_access()