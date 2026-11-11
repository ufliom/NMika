"""Cube ABCDEFGH ; I, J milieux de [AB], [BC]. Position relative de la droite (IJ) et du plan (HGF).
Réponse de l'élève : (IJ) parallèle au plan (HGF), car (IJ) ⊂ (ABC) et (ABC) // (EFG).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from geom3d import *

c = cube(1); P = c.v
I, J = midpoint(P["A"], P["B"]), midpoint(P["B"], P["C"])
IJ = Line.through(I, J)
HGF = Plane.through(P["H"], P["G"], P["F"])
ABC = Plane.through(P["A"], P["B"], P["C"])
print("plan (HGF) :", HGF.equation_str(), "| contient E :", HGF.contains(P["E"]),
      "| = plan (EGF) :", Plane.through(P["E"], P["G"], P["F"]).equation() == HGF.equation())
print("plan (ABC) :", ABC.equation_str(), "| (ABC) // (HGF) :", ABC.is_parallel(HGF), "| distincts :", HGF.intersect_plane(ABC) is None)
print("I, J ∈ (ABC) :", ABC.contains(I), ABC.contains(J), "| I ≠ J :", not is_zero(vector(I, J)), "| (IJ) ⊂ (ABC) :", all(ABC.contains(IJ.at(t)) for t in (-3, 0, 5)))
print("(IJ) ∩ (HGF) :", HGF.intersect_line(IJ), "| angle droite/plan :", HGF.angle_with_line(IJ), "| vecteur IJ . normale (HGF) :", dot(IJ.u, HGF.n))
print("distance de I au plan (HGF) :", HGF.distance(I))
print("HDCB est-elle une face (H,D,C,B coplanaires) ?", are_coplanar(P["H"], P["D"], P["C"], P["B"]))
print("ABCD est-elle une face ?", are_coplanar(P["A"], P["B"], P["C"], P["D"]), "| (ABC) = plan ABCD :", ABC.contains(P["D"]))

s = Scene("Cube — droite (IJ) et plan (HGF)")
s.add_solid(c); s.add_point("I", I, color="#7c3aed"); s.add_point("J", J, color="#7c3aed")
s.add_polygon(*[P[k] for k in "EFGH"], color="#2563eb", alpha=0.30, label="plan (HGF) = face EFGH")
s.add_polygon(*[P[k] for k in "ABCD"], color="#059669", alpha=0.30, label="plan (ABC) = face ABCD")
s.add_line(IJ, extent=1.0, color="#dc2626", label="droite (IJ)")
s.save(os.path.join(os.path.dirname(__file__), "cube_IJ_plan.html"))
