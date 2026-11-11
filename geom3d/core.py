"""Géométrie de l'espace en calcul EXACT (sympy : fractions, racines, pi).

Aucun flottant n'est utilisé dans les calculs : 1/3 reste 1/3, sqrt(12) devient
2*sqrt(3). Les flottants n'apparaissent que pour l'affichage (degrés, 3D).

Points et vecteurs sont des matrices sympy 3x1 créées avec `vec(x, y, z)`.
"""
from __future__ import annotations

import sympy as sp
from sympy import Matrix, Rational, S, sqrt, pi, acos, asin, sympify

__all__ = [
    "vec", "pt", "vector", "midpoint", "centroid", "dot", "cross", "det3",
    "norm", "is_zero", "distance", "angle_vectors", "degrees",
    "are_collinear", "are_coplanar", "Line", "Plane", "Sphere",
]


def _num(x):
    # rational=True : 0.5 -> 1/2, "1/3" -> 1/3 (jamais de flottant).
    return sympify(x, rational=True)


def vec(x, y, z) -> Matrix:
    """Point ou vecteur de coordonnées (x, y, z). Accepte int, str ('1/3'), expr."""
    return Matrix([_num(x), _num(y), _num(z)])


pt = vec


def _v(u) -> Matrix:
    if isinstance(u, Matrix):
        return u
    return vec(*u)


def vector(A, B) -> Matrix:
    """Vecteur AB."""
    return _v(B) - _v(A)


def midpoint(A, B) -> Matrix:
    return (_v(A) + _v(B)) / 2


def centroid(*points) -> Matrix:
    """Isobarycentre des points donnés."""
    pts = [_v(p) for p in points]
    return sum(pts, sp.zeros(3, 1)) / len(pts)


def dot(u, v):
    return sp.simplify((_v(u).T * _v(v))[0])


def cross(u, v) -> Matrix:
    return _v(u).cross(_v(v)).applyfunc(sp.simplify)


def det3(u, v, w):
    """Produit mixte (u, v, w) = det de la matrice [u v w]."""
    return sp.simplify(Matrix.hstack(_v(u), _v(v), _v(w)).det())


def norm(u):
    u = _v(u)
    return sp.simplify(sqrt(sp.simplify((u.T * u)[0])))


def is_zero(e) -> bool:
    if isinstance(e, Matrix):
        return all(is_zero(c) for c in e)
    return sp.simplify(e) == 0


def distance(A, B):
    """Distance AB."""
    return norm(vector(A, B))


def angle_vectors(u, v):
    """Angle géométrique (entre 0 et pi) de deux vecteurs non nuls, exact."""
    u, v = _v(u), _v(v)
    c = sp.simplify(dot(u, v) / (norm(u) * norm(v)))
    return sp.simplify(acos(c))


def degrees(angle) -> float:
    """Valeur en degrés (float) d'un angle exact en radians."""
    return float(sp.N(angle * 180 / pi, 15))


def are_collinear(A, B, C) -> bool:
    return is_zero(cross(vector(A, B), vector(A, C)))


def are_coplanar(A, B, C, D) -> bool:
    return is_zero(det3(vector(A, B), vector(A, C), vector(A, D)))


# --------------------------------------------------------------------------
class Line:
    """Droite passant par A, de vecteur directeur u."""

    def __init__(self, A, u):
        self.A, self.u = _v(A), _v(u)
        if is_zero(self.u):
            raise ValueError("Vecteur directeur nul : ce n'est pas une droite.")

    @classmethod
    def through(cls, A, B):
        if is_zero(vector(A, B)):
            raise ValueError("A et B sont confondus.")
        return cls(A, vector(A, B))

    def at(self, t) -> Matrix:
        """Point de paramètre t : A + t*u."""
        return (self.A + _num(t) * self.u).applyfunc(sp.simplify)

    def contains(self, P) -> bool:
        return is_zero(cross(vector(self.A, P), self.u))

    def is_parallel(self, other: "Line") -> bool:
        return is_zero(cross(self.u, other.u))

    def is_orthogonal(self, other: "Line") -> bool:
        return is_zero(dot(self.u, other.u))

    def project(self, P) -> Matrix:
        """Projeté orthogonal de P sur la droite."""
        w = vector(self.A, P)
        return (self.A + dot(w, self.u) / dot(self.u, self.u) * self.u).applyfunc(sp.simplify)

    def distance_to_point(self, P):
        return sp.simplify(norm(cross(vector(self.A, P), self.u)) / norm(self.u))

    def distance_to_line(self, other: "Line"):
        if self.is_parallel(other):
            return self.distance_to_point(other.A)
        n = cross(self.u, other.u)
        return sp.simplify(abs(dot(vector(self.A, other.A), n)) / norm(n))

    def intersection(self, other: "Line"):
        """None (pas d'intersection), un point, ou la droite si confondues."""
        if self.is_parallel(other):
            return self if self.contains(other.A) else None
        if not is_zero(det3(vector(self.A, other.A), self.u, other.u)):
            return None  # non coplanaires
        t, s = sp.symbols("t s")
        sol = sp.solve(list(self.A + t * self.u - other.A - s * other.u), [t, s], dict=True)
        return self.at(sol[0][t]) if sol else None

    def relation(self, other: "Line") -> str:
        """'confondues' | 'parallèles' | 'sécantes' | 'non coplanaires'."""
        if self.is_parallel(other):
            return "confondues" if self.contains(other.A) else "parallèles"
        if is_zero(det3(vector(self.A, other.A), self.u, other.u)):
            return "sécantes"
        return "non coplanaires"

    def angle_with_line(self, other: "Line"):
        """Angle aigu (0..pi/2) entre deux droites, exact."""
        c = sp.simplify(abs(dot(self.u, other.u)) / (norm(self.u) * norm(other.u)))
        return sp.simplify(acos(c))

    def __repr__(self):
        return f"Line(A={list(self.A)}, u={list(self.u)})"


# --------------------------------------------------------------------------
class Plane:
    """Plan passant par A, de vecteur normal n."""

    def __init__(self, A, n):
        self.A, self.n = _v(A), _v(n)
        if is_zero(self.n):
            raise ValueError("Vecteur normal nul : ce n'est pas un plan.")

    @classmethod
    def through(cls, A, B, C):
        n = cross(vector(A, B), vector(A, C))
        if is_zero(n):
            raise ValueError("A, B, C sont alignés : ils ne définissent pas un plan.")
        return cls(A, n)

    @classmethod
    def from_equation(cls, a, b, c, d):
        """Plan d'équation ax + by + cz + d = 0."""
        a, b, c, d = map(_num, (a, b, c, d))
        n = Matrix([a, b, c])
        if is_zero(n):
            raise ValueError("a, b, c ne peuvent pas être tous nuls.")
        k = 0 if a != 0 else (1 if b != 0 else 2)
        A = sp.zeros(3, 1)
        A[k] = -d / n[k]
        return cls(A, n)

    def equation(self):
        """(a, b, c, d) entiers premiers entre eux avec ax+by+cz+d=0."""
        a, b, c = self.n
        d = -dot(self.n, self.A)
        coeffs = [sp.nsimplify(x) for x in (a, b, c, d)]
        den = sp.ilcm(*[sp.fraction(sp.Rational(x))[1] for x in coeffs if x.is_rational] or [1])
        coeffs = [x * den for x in coeffs]
        if all(x.is_integer for x in coeffs):
            g = 0
            for x in coeffs:
                g = sp.igcd(g, int(x))      # igcd(0, n) = |n| : fonctionne aussi avec un seul coefficient non nul
            coeffs = [x / g for x in coeffs]
        first = next(x for x in coeffs if x != 0)
        if first < 0:
            coeffs = [-x for x in coeffs]
        return tuple(sp.simplify(x) for x in coeffs)

    def equation_str(self) -> str:
        a, b, c, d = self.equation()
        x, y, z = sp.symbols("x y z")
        return f"{sp.sstr(a*x + b*y + c*z + d)} = 0"

    def contains(self, P) -> bool:
        return is_zero(dot(self.n, vector(self.A, P)))

    def is_parallel(self, other: "Plane") -> bool:
        return is_zero(cross(self.n, other.n))

    def is_perpendicular(self, other: "Plane") -> bool:
        return is_zero(dot(self.n, other.n))

    def distance(self, P):
        return sp.simplify(abs(dot(self.n, vector(self.A, P))) / norm(self.n))

    def project(self, P) -> Matrix:
        """Projeté orthogonal de P sur le plan."""
        k = dot(self.n, vector(self.A, P)) / dot(self.n, self.n)
        return (_v(P) - k * self.n).applyfunc(sp.simplify)

    def intersect_line(self, L: Line):
        """None (parallèle, hors du plan), un point, ou la droite (incluse)."""
        den = dot(self.n, L.u)
        if is_zero(den):
            return L if self.contains(L.A) else None
        t = dot(self.n, vector(L.A, self.A)) / den
        return L.at(t)

    def intersect_plane(self, other: "Plane"):
        """None (parallèles distincts), le plan (confondus), ou la droite d'intersection."""
        if self.is_parallel(other):
            return self if self.contains(other.A) else None
        u = cross(self.n, other.n)
        M = Matrix.vstack(self.n.T, other.n.T, u.T)
        rhs = Matrix([dot(self.n, self.A), dot(other.n, other.A), 0])
        return Line(M.LUsolve(rhs).applyfunc(sp.simplify), u)

    def angle_with_line(self, L: Line):
        """Angle aigu (0..pi/2) entre une droite et le plan, exact."""
        s = sp.simplify(abs(dot(self.n, L.u)) / (norm(self.n) * norm(L.u)))
        return sp.simplify(asin(s))

    def angle_with_plane(self, other: "Plane"):
        """Angle aigu (0..pi/2) entre deux plans, exact."""
        c = sp.simplify(abs(dot(self.n, other.n)) / (norm(self.n) * norm(other.n)))
        return sp.simplify(acos(c))

    def __repr__(self):
        return f"Plane({self.equation_str()})"


# --------------------------------------------------------------------------
class Sphere:
    def __init__(self, center, radius):
        self.c, self.r = _v(center), _num(radius)
        if self.r <= 0:
            raise ValueError("Le rayon doit être strictement positif.")

    def contains(self, P) -> bool:
        return is_zero(dot(vector(self.c, P), vector(self.c, P)) - self.r ** 2)

    def intersect_plane(self, plane: Plane):
        """('vide', None, None) | ('point', P, 0) | ('cercle', centre, rayon)."""
        d = plane.distance(self.c)
        H = plane.project(self.c)
        diff = sp.simplify(self.r ** 2 - d ** 2)
        if diff.is_negative:
            return ("vide", None, None)
        if diff == 0:
            return ("point", H, S.Zero)
        return ("cercle", H, sp.simplify(sqrt(diff)))

    def intersect_line(self, L: Line):
        """Liste des points d'intersection (0, 1 ou 2)."""
        t = sp.symbols("t", real=True)
        P = L.A + t * L.u
        eq = sp.expand(dot(P - self.c, P - self.c) - self.r ** 2)
        return [L.at(s) for s in sp.solve(eq, t)]

    def tangent_plane_at(self, P) -> Plane:
        if not self.contains(P):
            raise ValueError("Le point n'est pas sur la sphère.")
        return Plane(P, vector(self.c, P))

    def __repr__(self):
        return f"Sphere(c={list(self.c)}, r={self.r})"
