"""Cube ABCDEFGH ; I, J, K milieux de [AB], [BC], [AE].
Q1 : deux droites sécantes ; Q2 : deux droites parallèles ; Q3 : deux droites non coplanaires.
Réponses de l'élève : (EA, AB) ; (EF, AB) ; (AB, HD).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from geom3d import *

c = cube(1)
I, J, K = midpoint(c["A"], c["B"]), midpoint(c["B"], c["C"]), midpoint(c["A"], c["E"])
L = lambda p, q: Line.through(c[p], c[q])
for q, attendu, (d1, d2) in [("Q1 sécantes", "sécantes", ("EA", "AB")),
                              ("Q2 parallèles", "parallèles", ("EF", "AB")),
                              ("Q3 non coplanaires", "non coplanaires", ("AB", "HD"))]:
    r = L(*d1).relation(L(*d2))
    print(f"{q:20s} ({d1})/({d2}) -> {r:16s}", "✔" if r == attendu else "✘")
    # recoupement indépendant : coplanarité de 4 points (déterminant) + point commun éventuel
    A_, B_, C_, D_ = c[d1[0]], c[d1[1]], c[d2[0]], c[d2[1]]
    print("    4 points coplanaires :", are_coplanar(A_, B_, C_, D_),
          "| intersection :", L(*d1).intersection(L(*d2)))

s = Scene("Cube — droites de l'exercice")
s.add_solid(c)
for n, P in (("I", I), ("J", J), ("K", K)):
    s.add_point(n, P, color="#7c3aed")
s.add_segment(c["E"], c["A"], color="#2563eb", thick=True, label="Q1 : (EA) et (AB) sécantes en A")
s.add_segment(c["A"], c["B"], color="#2563eb", thick=True)
s.add_segment(c["E"], c["F"], color="#059669", thick=True, label="Q2 : (EF) // (AB)")
s.add_segment(c["H"], c["D"], color="#dc2626", thick=True, label="Q3 : (AB) et (HD) non coplanaires")
s.save(os.path.join(os.path.dirname(__file__), "cube_IJK.html"))
