"""Vérification des réponses d'un élève contre la valeur EXACTE + garde-fous.

Deux mécanismes :
  * `cross_check` : une même grandeur est calculée par DEUX méthodes
    indépendantes ; si elles divergent, on lève une erreur (le bug est de mon
    côté, pas de celui de l'élève).
  * `check` : compare la réponse de l'élève à la valeur exacte.
"""
from __future__ import annotations

import re

import sympy as sp
from sympy import sympify

_LOCALS = {"sqrt": sp.sqrt, "pi": sp.pi, "acos": sp.acos, "asin": sp.asin,
           "atan": sp.atan, "arccos": sp.acos, "arcsin": sp.asin,
           "racine": sp.sqrt, "√": sp.sqrt}


def parse(x):
    """Texte ('sqrt(3)/3', '1/3', '0,577') ou nombre -> expression sympy."""
    if isinstance(x, str):
        s = x.strip().replace("^", "**").replace(",", ".")
        s = re.sub(r"√\s*(\d+(?:\.\d+)?)", r"sqrt(\1)", s)   # √3 -> sqrt(3)
        s = s.replace("√", "sqrt")                               # √(3) -> sqrt(3)
        s = re.sub(r"(\d)\s*(sqrt|pi|acos|asin)", r"\1*\2", s)  # 2sqrt(3) -> 2*sqrt(3)
        e = sympify(s, locals=_LOCALS, rational=True)
    else:
        e = sympify(x, rational=True)
    if getattr(e, "free_symbols", None):
        raise ValueError(f"symboles inconnus : {sorted(map(str, e.free_symbols))}")
    return e


def _decimals(x):
    if isinstance(x, str):
        s = x.strip().replace(",", ".")
        if re.fullmatch(r"-?\d+\.\d+", s):
            return len(s.split(".")[1])
    elif isinstance(x, float):
        return len(repr(x).split(".")[1]) if "." in repr(x) else 0
    return None


class Verifier:
    def __init__(self, title: str = "Vérification"):
        self.title, self.rows = title, []

    # -- recoupement interne ------------------------------------------------
    def cross_check(self, label, value_a, value_b):
        """Deux méthodes indépendantes doivent donner la même valeur exacte."""
        a, b = parse(value_a), parse(value_b)
        ok = sp.simplify(a - b) == 0 or float(abs(sp.N(a - b, 30))) < 1e-20
        if not ok:
            raise AssertionError(f"[{label}] méthodes en désaccord : {a} ≠ {b}")
        self.rows.append(("cross", label, a, b, True, ""))
        return a

    # -- comparaison avec l'élève -------------------------------------------
    def check(self, label, student, exact):
        """Compare `student` (str/nombre) à `exact` (expression sympy)."""
        exact = parse(exact)
        try:
            s = parse(student)
        except Exception as e:                                # noqa: BLE001
            self.rows.append(("check", label, student, exact, False, f"réponse illisible ({e})"))
            return False
        if sp.simplify(s - exact) == 0:
            note = "exact"
            ok = True
        else:
            d = _decimals(student)
            diff = float(abs(sp.N(s - exact, 30)))
            if d is not None and diff <= 0.5 * 10.0 ** (-d) + 1e-12:
                ok, note = True, f"valeur approchée correcte à 10^-{d} (forme exacte : {sp.sstr(exact)})"
            elif diff < 1e-12:
                ok, note = True, "égal (forme différente)"
            else:
                ok, note = False, f"écart = {sp.N(s - exact, 6)}"
        self.rows.append(("check", label, student, exact, ok, note))
        return ok

    # -- rapport --------------------------------------------------------------
    def report(self) -> str:
        out = [f"=== {self.title} ==="]
        for kind, label, a, b, ok, note in self.rows:
            if kind == "cross":
                out.append(f"  ⚙ {label} : 2 méthodes concordent → {sp.sstr(a)}  (≈ {sp.N(a, 8)})")
            else:
                mark = "✔" if ok else "✘"
                out.append(f"  {mark} {label} : élève = {a}  |  exact = {sp.sstr(b)} (≈ {sp.N(b, 8)})"
                           + (f"  — {note}" if note else ""))
        return "\n".join(out)

    def all_ok(self) -> bool:
        return all(r[4] for r in self.rows)
