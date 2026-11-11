"""Aires, volumes et solides usuels (sommets nommés à la française)."""
from __future__ import annotations

import sympy as sp
from sympy import sqrt, Rational, Matrix

__all__ = ["polygon_area", "tetra_volume", "pyramid_volume", "prism_volume",
           "sphere_volume", "sphere_area", "Solid", "cube", "parallelepiped",
           "regular_tetrahedron", "square_pyramid"]

from .core import (_v, _num, vec, vector, cross, dot, det3, norm, is_zero,
                   are_coplanar, Plane, midpoint)


def polygon_area(*points):
    """Aire d'un polygone PLAN donné par ses sommets dans l'ordre."""
    pts = [_v(p) for p in points]
    if len(pts) < 3:
        raise ValueError("Il faut au moins 3 sommets.")
    for p in pts[3:]:
        if not are_coplanar(pts[0], pts[1], pts[2], p):
            raise ValueError("Les sommets ne sont pas coplanaires.")
    total = sp.zeros(3, 1)
    for i, p in enumerate(pts):
        total += cross(p, pts[(i + 1) % len(pts)])
    return sp.simplify(norm(total) / 2)


def tetra_volume(A, B, C, D):
    """Volume du tétraèdre ABCD = |det(AB, AC, AD)| / 6."""
    return sp.simplify(abs(det3(vector(A, B), vector(A, C), vector(A, D))) / 6)


def pyramid_volume(base, apex):
    """Volume (1/3) * aire(base) * hauteur. `base` : liste de sommets coplanaires."""
    plane = Plane.through(*base[:3])
    return sp.simplify(polygon_area(*base) * plane.distance(apex) / 3)


def prism_volume(base, translation):
    """Prisme (ou parallélépipède) : base * |composante normale du vecteur de translation|."""
    plane = Plane.through(*base[:3])
    h = sp.simplify(abs(dot(plane.n, translation)) / norm(plane.n))
    return sp.simplify(polygon_area(*base) * h)


def sphere_volume(r):
    return sp.simplify(Rational(4, 3) * sp.pi * _num(r) ** 3)


def sphere_area(r):
    return sp.simplify(4 * sp.pi * _num(r) ** 2)


# --- Solides : dict {nom: point}, arêtes, faces (pour le calcul ET l'affichage) ---
class Solid:
    def __init__(self, vertices: dict, edges: list, faces: list):
        self.v, self.edges, self.faces = vertices, edges, faces

    def __getitem__(self, name):
        return self.v[name]


def cube(a=1) -> Solid:
    """Cube ABCDEFGH d'arête a. ABCD en bas (sens direct vu de dessus),
    EFGH au-dessus : E au-dessus de A, F de B, G de C, H de D.
    Repère (A; AB, AD, AE)."""
    return parallelepiped(a, a, a)


def parallelepiped(a=1, b=1, c=1) -> Solid:
    """Pavé droit ABCDEFGH : AB=a (axe x), AD=b (axe y), AE=c (axe z)."""
    V = {"A": vec(0, 0, 0), "B": vec(a, 0, 0), "C": vec(a, b, 0), "D": vec(0, b, 0),
         "E": vec(0, 0, c), "F": vec(a, 0, c), "G": vec(a, b, c), "H": vec(0, b, c)}
    edges = ["AB", "BC", "CD", "DA", "EF", "FG", "GH", "HE", "AE", "BF", "CG", "DH"]
    faces = ["ABCD", "EFGH", "ABFE", "BCGF", "CDHG", "DAEH"]
    return Solid(V, edges, faces)


def regular_tetrahedron(a=1) -> Solid:
    """Tétraèdre régulier ABCD d'arête a ; ABC dans le plan z=0."""
    a = _num(a)
    V = {"A": vec(0, 0, 0), "B": vec(a, 0, 0),
         "C": Matrix([a / 2, a * sqrt(3) / 2, 0]),
         "D": Matrix([a / 2, a * sqrt(3) / 6, a * sqrt(6) / 3])}
    return Solid(V, ["AB", "AC", "AD", "BC", "BD", "CD"], ["ABC", "ABD", "ACD", "BCD"])


def square_pyramid(a=1, h=1) -> Solid:
    """Pyramide régulière SABCD : base carrée ABCD de côté a, sommet S à la hauteur h
    au-dessus du centre."""
    a, h = _num(a), _num(h)
    V = {"A": vec(0, 0, 0), "B": vec(a, 0, 0), "C": vec(a, a, 0), "D": vec(0, a, 0),
         "S": Matrix([a / 2, a / 2, h])}
    edges = ["AB", "BC", "CD", "DA", "SA", "SB", "SC", "SD"]
    return Solid(V, edges, ["ABCD", "SAB", "SBC", "SCD", "SDA"])
