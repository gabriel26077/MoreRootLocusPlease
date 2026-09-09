import sympy as sp
import numpy as np

def array_to_sym(coeffs, var):
    """Convert numpy coefficient array to sympy polynomial."""
    return sum(c * var**i for i, c in enumerate(reversed(coeffs)))

def sym_to_latex(expr_sym, decimals=4):
    """Clean format sympy floats then return latex string."""
    if not isinstance(expr_sym, sp.Basic):
        expr_sym = sp.sympify(expr_sym)
    repl = {}
    for x in expr_sym.atoms(sp.Float):
        v = round(float(x), decimals)
        repl[x] = sp.Integer(int(v)) if v.is_integer() else sp.Float(v)
    return sp.latex(expr_sym.xreplace(repl))

def fatorar_numerico(polinomio, var):
    """Numerically factorize a polynomial."""
    if sp.degree(polinomio, var) < 1:
        return polinomio
    roots = sp.nroots(polinomio)
    terms = [var - sp.N(r, 3, chop=True) for r in roots]
    leading_coeff = sp.LC(polinomio, var)
    return leading_coeff * sp.Mul(*terms, evaluate=False)

def get_multiplicity_info(points, tol=1e-4):
    """Return a dict mapping each unique point to its multiplicity."""
    from collections import Counter
    rounded = [complex(round(p.real, 4), round(p.imag, 4)) for p in points]
    counts = Counter(rounded)
    return counts

def parse_to_coeffs(expr_str, s_var):
    """Parse algebraic expressions into numpy coefficients array."""
    from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
    transformations = (standard_transformations + (implicit_multiplication_application,))
    
    expr_str = expr_str.replace('^', '**')
    expr = parse_expr(expr_str, local_dict={'s': s_var, 'i': sp.I, 'j': sp.I}, transformations=transformations)
    poly = sp.Poly(sp.expand(expr), s_var)
    
    coeffs = []
    for c in poly.all_coeffs():
        c_eval = complex(c.evalf())
        if abs(c_eval.imag) > 1e-7:
            raise ValueError("Os pólos/zeros complexos não estão em pares conjugados!")
        coeffs.append(c_eval.real)
        
    return np.array(coeffs)
