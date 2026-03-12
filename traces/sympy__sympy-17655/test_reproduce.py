point1 + point2 * sympy.sympify(2.0)  # works fine
point1 + sympy.sympify(2.0) * point2  # raises GeometryError