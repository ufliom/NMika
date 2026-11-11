"""EXEMPLE — Cube ABCDEFGH d'arête 1, repère (A; AB, AD, AE).

1) Montrer que (AG) est orthogonale au plan (BDE) ; donner une équation de (BDE).
2) Soit K l'intersection de (AG) et (BDE). Calculer AK.
3) Calculer le volume de ABDE de deux façons.
4) Angle entre les plans (BDE) et (ABC).

Lancer :  python3 exercises/exemple_cube.py   ->  écrit exemple_cube.html
Les réponses « élève » ci-dessous sont des exemples (certaines volontairement fausses).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import sympy as sp  # noqa: E402
from geom3d import *  # noqa: E402,F401,F403

c = cube(1)
A, B, C, D, E, G = (c[k] for k in "ABCDEG")
v = Verifier("Exemple — cube ABCDEFGH")

# 1) (AG) ⟂ (BDE)
BDE = Plane.through(B, D, E)
AG = Line.through(A, G)
orth = AG.is_orthogonal(Line.through(B, D)) and AG.is_orthogonal(Line.through(B, E))
print("(AG) ⟂ (BD) et (AG) ⟂ (BE) :", orth, "| (BDE) :", BDE.equation_str())
v.check("équation de (BDE) : coefficient d", "-1", BDE.equation()[3])

# 2) K = (AG) ∩ (BDE) ; AK
K = BDE.intersect_line(AG)
AK = v.cross_check("AK (norme de AK  vs  distance de A au plan)", distance(A, K), BDE.distance(A))
v.check("AK", "sqrt(3)/3", AK)
v.check("AK (élève : 1/3 — faux)", "1/3", AK)
v.check("AK (élève : 0,58 arrondi)", "0,58", AK)

# 3) Volume de ABDE par deux méthodes
V1 = tetra_volume(A, B, D, E)                                   # déterminant
V2 = polygon_area(B, D, E) * BDE.distance(A) / 3                # (1/3) * base * hauteur
V = v.cross_check("volume ABDE (déterminant  vs  base×hauteur/3)", V1, V2)
v.check("volume ABDE", "1/6", V)

# 4) Angle entre (BDE) et (ABC)
ang = BDE.angle_with_plane(Plane.through(A, B, C))
print("angle (BDE),(ABC) =", ang, "≈", round(degrees(ang), 4), "°")
v.check("cos(angle)", "sqrt(3)/3", sp.cos(ang))

print(v.report())

# --- Scène 3D ---
s = Scene("Cube — plan (BDE) et diagonale (AG)")
s.add_solid(c)
s.add_plane(BDE, around=centroid(*c.v.values()), size=1.0, color="#2563eb", alpha=0.10, label="plan (BDE)")
s.add_polygon(B, D, E, color="#2563eb", alpha=0.35, label="triangle BDE")
s.add_segment(A, G, color="#dc2626", thick=True, label="diagonale [AG]")
s.add_point("K", K, color="#dc2626")
out = os.path.join(os.path.dirname(__file__), "exemple_cube.html")
s.save(out)
print("scène 3D :", out)
