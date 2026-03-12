import sympy as sp
from pprint import pprint

def sub_in_matrixsymbols(exp, matrices):
    for matrix in matrices:
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                name = "%s_%d_%d" % (matrix.name, i, j)
                sym = sp.symbols(name)
                exp = exp.subs(sym, matrix[i, j])
    return exp

def t44(name):
    return sp.Matrix(4, 4, lambda i, j: sp.symbols('%s_%d_%d' % (name, i, j)))

def test_issue_reproduction():
    # Construct matrices of symbols that work with our expressions
    a = t44("a")
    b = t44("b")

    # Set up expression
    e = a * b

    # Put in matrixsymbols
    e2 = sub_in_matrixsymbols(e, [sp.MatrixSymbol("a", 4, 4), sp.MatrixSymbol("b", 4, 4)])
    cse_subs, cse_reduced = sp.cse(e2)

    # Check that we don't have unnecessary copies of the matrices
    # The bug creates x0 = a and x2 = b, which are just copies
    # After the fix, these should not be created

    # Count how many substitutions are just copying the entire matrix
    unnecessary_copies = 0
    for sym, expr in cse_subs:
        # Check if this is a copy of a MatrixSymbol (the bug)
        if (isinstance(expr, sp.MatrixSymbol) and
            sym != expr and
            sym.shape == expr.shape):
            unnecessary_copies += 1
            print(f"Found unnecessary copy: {sym} = {expr}")

    # The bug creates 2 unnecessary copies (x0 = a, x2 = b)
    # After the fix, there should be 0 unnecessary copies
    print(f"Number of unnecessary matrix copies: {unnecessary_copies}")

    # This assertion will fail on buggy code (unnecessary_copies > 0)
    # and pass on fixed code (unnecessary_copies == 0)
    assert unnecessary_copies == 0, f"Found {unnecessary_copies} unnecessary matrix copies in CSE result"

    print("Test passed - issue is fixed")

if __name__ == "__main__":
    test_issue_reproduction()