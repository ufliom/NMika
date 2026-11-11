"""Tests de la bibliothèque sur des résultats connus (à lancer avant de s'y fier).

    python3 -m unittest discover -s tests -v
"""
import itertools
import unittest

import sympy as sp
from sympy import Rational as R, sqrt

from geom3d import *  # noqa: F401,F403
from geom3d.check import Verifier, parse


class TestCube(unittest.TestCase):
    def setUp(self):
        self.c = cube(1)
        self.A, self.B, self.D, self.E, self.G = (self.c[k] for k in "ABDEG")

    def test_diagonal(self):
        self.assertEqual(distance(self.A, self.G), sqrt(3))

    def test_AG_perp_BDE_and_distance(self):
        p = Plane.through(self.B, self.D, self.E)
        self.assertEqual(p.equation(), (1, 1, 1, -1))
        self.assertTrue(Line.through(self.A, self.G).is_orthogonal(Line.through(self.B, self.D)))
        self.assertEqual(p.distance(self.A), sqrt(3) / 3)
        K = p.intersect_line(Line.through(self.A, self.G))
        self.assertEqual(list(K), [R(1, 3)] * 3)

    def test_tetra_ABDE_volume_two_ways(self):
        v1 = tetra_volume(self.A, self.B, self.D, self.E)
        base = polygon_area(self.B, self.D, self.E)
        v2 = base * Plane.through(self.B, self.D, self.E).distance(self.A) / 3
        self.assertEqual(v1, R(1, 6))
        self.assertEqual(sp.simplify(v2), R(1, 6))

    def test_plane_angles(self):
        a = Plane.through(self.B, self.D, self.E).angle_with_plane(Plane.through(*[self.c[k] for k in "ABC"]))
        self.assertEqual(a, sp.acos(sqrt(3) / 3))
        self.assertAlmostEqual(degrees(a), 54.7356103172, places=8)

    def test_skew_lines_distance(self):
        # (AB) et (CG)... (EF)/(DC): parallèles -> distance 1 ; (AC)/(BF): gauches -> sqrt(2)/2
        self.assertEqual(Line.through(self.c["A"], self.c["C"]).distance_to_line(
            Line.through(self.c["B"], self.c["F"])), sqrt(2) / 2)
        self.assertEqual(Line.through(self.c["E"], self.c["F"]).distance_to_line(
            Line.through(self.c["D"], self.c["C"])), sqrt(2))

    def test_volume_functions_agree(self):
        c = self.c
        self.assertEqual(prism_volume([c[k] for k in "ABCD"], vector(c["A"], c["E"])), 1)
        self.assertEqual(pyramid_volume([c[k] for k in "ABCD"], c["G"]), R(1, 3))


class TestSolids(unittest.TestCase):
    def test_regular_tetra(self):
        t = regular_tetrahedron(1)
        for p, q in itertools.combinations("ABCD", 2):
            self.assertEqual(sp.simplify(distance(t[p], t[q])), 1)
        self.assertEqual(sp.simplify(tetra_volume(*[t[k] for k in "ABCD"]) - sqrt(2) / 12), 0)

    def test_square_pyramid(self):
        p = square_pyramid(2, 3)
        self.assertEqual(pyramid_volume([p[k] for k in "ABCD"], p["S"]), 4)

    def test_sphere_volume(self):
        self.assertEqual(sphere_volume(3), 36 * sp.pi)


class TestObjects(unittest.TestCase):
    def test_line_line_intersection(self):
        d1 = Line(vec(0, 0, 0), vec(1, 1, 0))
        d2 = Line(vec(2, 0, 0), vec(-1, 1, 0))
        self.assertEqual(list(d1.intersection(d2)), [1, 1, 0])
        self.assertIsNone(Line(vec(0, 0, 1), vec(1, 0, 0)).intersection(Line(vec(0, 0, 0), vec(0, 1, 0))))
        self.assertIsNone(d1.intersection(Line(vec(0, 1, 0), vec(1, 1, 0))))   # parallèles

    def test_relation(self):
        c = cube(1)
        L = lambda x, y: Line.through(c[x], c[y])
        self.assertEqual(L("A", "B").relation(L("A", "B")), "confondues")
        self.assertEqual(L("E", "F").relation(L("A", "B")), "parallèles")
        self.assertEqual(L("E", "A").relation(L("A", "B")), "sécantes")
        self.assertEqual(L("A", "B").relation(L("H", "D")), "non coplanaires")

    def test_plane_plane_intersection(self):
        L = Plane.from_equation(1, 0, 0, -1).intersect_plane(Plane.from_equation(0, 1, 0, -2))
        self.assertTrue(L.contains(vec(1, 2, 7)))
        self.assertTrue(L.is_parallel(Line(vec(0, 0, 0), vec(0, 0, 1))))

    def test_equation_normalisation(self):
        self.assertEqual(Plane(vec(0, 0, 0), vec("1/2", "1/2", "1/2")).equation(), (1, 1, 1, 0))
        self.assertEqual(Plane.through(vec(2, 0, 0), vec(0, 2, 0), vec(0, 0, 2)).equation(), (1, 1, 1, -2))

    def test_equation_axis_planes(self):
        # un seul coefficient non nul (plans parallèles aux faces du repère)
        self.assertEqual(Plane(vec(0, 0, 0), vec(0, 0, 5)).equation(), (0, 0, 1, 0))
        self.assertEqual(Plane(vec(0, 0, 3), vec(0, 0, -2)).equation(), (0, 0, 1, -3))
        self.assertEqual(Plane.through(vec(0, 0, 0), vec(1, 0, 0), vec(0, 1, 0)).equation_str(), "z = 0")
        self.assertEqual(Plane.from_equation(0, 2, 0, -4).equation(), (0, 1, 0, -2))

    def test_project_and_distance(self):
        p = Plane.from_equation(1, 2, 2, -3)         # |n| = 3
        P = vec(1, 1, 1)
        self.assertEqual(p.distance(P), R(2, 3))
        self.assertTrue(p.contains(p.project(P)))
        self.assertEqual(distance(P, p.project(P)), p.distance(P))

    def test_sphere_section_and_tangent(self):
        S = Sphere(vec(0, 0, 0), 5)
        kind, c, r = S.intersect_plane(Plane.from_equation(0, 0, 1, -3))
        self.assertEqual((kind, list(c), r), ("cercle", [0, 0, 3], 4))
        self.assertEqual(S.intersect_plane(Plane.from_equation(0, 0, 1, -5))[0], "point")
        self.assertEqual(S.intersect_plane(Plane.from_equation(0, 0, 1, -6))[0], "vide")
        pts = S.intersect_line(Line(vec(0, 0, 0), vec(0, 0, 1)))
        self.assertEqual(sorted(p[2] for p in pts), [-5, 5])
        self.assertEqual(S.tangent_plane_at(vec(3, 4, 0)).equation(), (3, 4, 0, -25))

    def test_errors(self):
        with self.assertRaises(ValueError):
            Plane.through(vec(0, 0, 0), vec(1, 1, 1), vec(2, 2, 2))
        with self.assertRaises(ValueError):
            polygon_area(vec(0, 0, 0), vec(1, 0, 0), vec(0, 1, 0), vec(0, 0, 1))


class TestVerifier(unittest.TestCase):
    def test_parse_and_check(self):
        v = Verifier()
        self.assertTrue(v.check("a", "sqrt(3)/3", sqrt(3) / 3))
        self.assertTrue(v.check("b", "1/sqrt(3)", sqrt(3) / 3))        # forme différente
        self.assertTrue(v.check("c", "0,577", sqrt(3) / 3))            # arrondi correct
        self.assertFalse(v.check("d", "0.58", sqrt(3) / 3 + R(1, 10)))
        self.assertFalse(v.check("e", "1/3", sqrt(3) / 3))
        self.assertTrue(v.check("f", "2√3", 2 * sqrt(3)))
        self.assertTrue(v.check("g", "3.14", sp.pi))                   # arrondi à 10^-2 accepté
        self.assertFalse(v.check("h", "bla bla", 1))
        self.assertFalse(v.check("i", "x+1", 1))                       # symbole inconnu : rejeté
        self.assertTrue(v.check("j", "√3/3", sqrt(3) / 3))

    def test_cross_check_detects_disagreement(self):
        v = Verifier()
        v.cross_check("ok", "1/2", R(1, 2))
        with self.assertRaises(AssertionError):
            v.cross_check("ko", "1/2", R(1, 3))


if __name__ == "__main__":
    unittest.main()
