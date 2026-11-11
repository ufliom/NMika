# NMika — correction d'exercices de géométrie de l'espace, sans approximation

Objectif : ne **jamais** se fier à un « calcul de tête » de LLM. Chaque exercice est
traduit en code, calculé en **arithmétique exacte** (fractions, racines, π — via sympy),
**recoupé par une seconde méthode indépendante**, puis visualisé en **3D**.

## Ce qu'il y a dedans

| Fichier | Rôle |
|---|---|
| `geom3d/core.py` | Points, vecteurs, `Line`, `Plane`, `Sphere` : intersections, distances, projetés, angles, équations de plans — tout en exact |
| `geom3d/solids.py` | Aires, volumes (tétraèdre, pyramide, prisme, sphère) et solides prêts à l'emploi : `cube`, `parallelepiped`, `regular_tetrahedron`, `square_pyramid` |
| `geom3d/check.py` | `Verifier` : compare la réponse de l'élève à la valeur exacte (`✔`/`✘`, accepte `√3/3`, `0,577`, `1/sqrt(3)`…) et `cross_check` (2 méthodes qui doivent concorder, sinon erreur) |
| `geom3d/viewer.py` | `Scene` : exporte un fichier HTML 3D interactif autonome (glisser = tourner, molette = zoom) |
| `tests/` | Tests de la bibliothèque sur des résultats connus |
| `exercises/exemple_cube.py` | Exercice type, de bout en bout |

## Utilisation

```bash
pip install -r requirements.txt
python3 -m unittest discover -s tests      # la bibliothèque elle-même est testée
python3 exercises/exemple_cube.py          # rapport texte + exercises/exemple_cube.html
```

```python
from geom3d import *
c = cube(1); A, B, D, E, G = (c[k] for k in "ABDEG")
BDE = Plane.through(B, D, E)
BDE.equation_str()                 # 'x + y + z - 1 = 0'
BDE.distance(A)                    # sqrt(3)/3   (exact)
tetra_volume(A, B, D, E)           # 1/6
degrees(BDE.angle_with_plane(Plane.through(A, B, c["C"])))   # 54.7356...
```

## Conventions (à garder en tête pour ne pas se tromper de repère)

* Cube / pavé `ABCDEFGH` : `ABCD` en bas, `EFGH` au-dessus, `E` au-dessus de `A`, `F` de `B`,
  `G` de `C`, `H` de `D`. Repère `(A ; AB, AD, AE)` : `A=(0,0,0)`, `B=(a,0,0)`, `D=(0,b,0)`, `E=(0,0,c)`.
* Si l'énoncé impose un autre repère ou un autre codage des sommets, on **redéfinit les points
  à la main** avec `vec(x, y, z)` — c'est l'énoncé qui fait foi, pas ces conventions.
* Les angles renvoyés sont exacts (`acos(sqrt(3)/3)`) ; `degrees(...)` donne la valeur décimale.
  Angles droite/droite, droite/plan et plan/plan sont **aigus** (0 à 90°) ; `angle_vectors` donne l'angle géométrique (0 à 180°).

## Limites connues

* Les solides sont donnés par coordonnées : c'est à la mise en équation de l'énoncé qu'une
  erreur peut encore se glisser (mauvais repère, mauvais sommet). D'où la **scène 3D** : on
  vérifie visuellement que la figure correspond au sujet.
* Pas de rendu des arêtes cachées en pointillés (la scène est faite pour être tournée).
* Les sections de solides par un plan (polygone de section) ne sont pas encore automatisées.
