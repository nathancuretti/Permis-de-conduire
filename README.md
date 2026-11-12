# Code de la route — appli de révision

Appli web (utilisable sur téléphone, installable sur l'écran d'accueil) pour réviser l'examen du code de la route (ETG).

- **Examen blanc** : 40 questions, 20 s par question, réussite à 35/40.
- **Entraînement** par thèmes et chapitres, avec correction et explication immédiates.
- **Suivi** : historique par question, « Mes erreurs » (une question en sort après 2 bonnes réponses de suite), répétition espacée (« À revoir »).
- **🚩** sur chaque question : ouvre un ticket GitHub prérempli pour signaler une erreur.

## Organisation

| Dossier | Contenu |
|---|---|
| `docs/notions.md` | Arbre des notions du programme officiel (10 thèmes). Chaque question est rattachée à une notion. |
| `data/questions/*.json` | Les questions |
| `data/themes.json` | Généré par `tools/build.py` (structure + nombre de questions par notion) |
| `img/panneaux`, `img/schemas` | Panneaux et schémas SVG, générés par `tools/panneaux.py` |
| `img/photos` | Photos Panoramax (licence indiquée sur chaque question) |

## Format d'une question

```json
{ "id": "L-PAN-04-f", "n": "L-PAN-04", "img": "img/panneaux/AB4.svg",
  "q": "À ce panneau, je dois :", "c": ["…", "…", "…"], "ok": [0, 1],
  "ex": "Explication…", "src": "Code de la route, art. R415-6" }
```

Après modification : `python3 tools/panneaux.py && python3 tools/build.py`.
