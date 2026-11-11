"""Cube ABCDEFGH ; I milieu de [AB]. Position relative (avec justification) de :
a) (FC) et (AF)   b) (CI) et (AE)   c) (EB) et (HC)
Réponses de l'élève : a) sécantes en F ET non coplanaires ; b) non coplanaires ; c) parallèles.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from geom3d import *

c = cube(1)
I = midpoint(c["A"], c["B"])
P = dict(c.v, I=I)
L = lambda p, q: Line.through(P[p], P[q])

for nom, d1, d2 in [("a", "FC", "AF"), ("b", "CI", "AE"), ("c", "EB", "HC")]:
    l1, l2 = L(*d1), L(*d2)
    pts = [P[d1[0]], P[d1[1]], P[d2[0]], P[d2[1]]]
    print(f"{nom}) ({d1}) / ({d2}) : {l1.relation(l2)}")
    print("   u =", list(l1.u), " v =", list(l2.u), "| colinéaires :", l1.is_parallel(l2))
    print("   intersection :", l1.intersection(l2), "| 4 points coplanaires :", are_coplanar(*pts))
    print("   produit mixte (d1.A d2.A, u, v) :", det3(vector(l1.A, l2.A), l1.u, l2.u))

# a) plan contenant (FC) et (AF) ; est-ce une face ?
pl = Plane.through(P["A"], P["F"], P["C"])
print("\na) plan (AFC) :", pl.equation_str(), "| contient B ?", pl.contains(P["B"]),
      "| contient D ?", pl.contains(P["D"]))
# c) EBCH est-il un parallélogramme ?  vecteur EB = vecteur HC ?
print("c) vecteur EB =", list(vector(P["E"], P["B"])), " vecteur HC =", list(vector(P["H"], P["C"])),
      "| égaux :", is_zero(vector(P["E"], P["B"]) - vector(P["H"], P["C"])))
print("   plans (ABF) et (DCG) parallèles :", Plane.through(P["A"], P["B"], P["F"]).is_parallel(Plane.through(P["D"], P["C"], P["G"])))
# c) contre-exemple : dans deux faces opposées, deux droites ne sont pas forcément parallèles
print("   contre-exemple : (EB) et (DG)  [DG diagonale de la face opposée] :", L("E","B").relation(L("D","G")))
# b) A appartient-il à (CI) ?
print("b) A ∈ (CI) ?", L("C", "I").contains(P["A"]), "| (CI) ⊂ plan (ABC) :", Plane.through(P["A"],P["B"],P["C"]).contains(P["I"]))

s = Scene("Cube — position relative de droites")
s.add_solid(c); s.add_point("I", I, color="#7c3aed")
for (p, q, col, lab) in [("F","C","#2563eb","a) (FC)"),("A","F","#2563eb","a) (AF)"),
                          ("C","I","#059669","b) (CI)"),("A","E","#059669","b) (AE)"),
                          ("E","B","#dc2626","c) (EB)"),("H","C","#dc2626","c) (HC)")]:
    s.add_segment(P[p], P[q], color=col, thick=True, label=lab)
s.save(os.path.join(os.path.dirname(__file__), "cube_positions.html"))
