#!/usr/bin/env python3
"""Construit data/themes.json à partir de docs/notions.md et vérifie les questions.

- thèmes → chapitres → notions (avec le nombre de questions par notion)
- liste des fichiers de questions à charger par l'appli
- rapport de couverture : notions sans question

Usage : python3 tools/build.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")


def parse_notions():
    themes, theme, chap = [], None, None
    for line in open(os.path.join(ROOT, "docs", "notions.md"), encoding="utf-8"):
        m = re.match(r"^## ([A-Z]) — (.+)$", line)
        if m:
            theme = {"code": m[1], "nom": m[2].strip(), "chapitres": []}
            themes.append(theme)
            chap = None
            continue
        m = re.match(r"^### ([A-Z]-[A-Z0-9]+) · (.+)$", line)
        if m and theme:
            chap = {"code": m[1], "nom": m[2].strip(), "notions": []}
            theme["chapitres"].append(chap)
            continue
        m = re.match(r"^- ([A-Z]-[A-Z0-9]+-\d+) (.+)$", line)
        if m and theme:
            if chap is None:  # thème sans sous-chapitre (ex. S)
                chap = {"code": m[1].rsplit("-", 1)[0], "nom": theme["nom"], "notions": []}
                theme["chapitres"].append(chap)
            chap["notions"].append({"id": m[1], "nom": m[2].strip()})
    return themes


# Thèmes affichés dans l'appli (regroupement des 10 thèmes officiels en 12 thèmes équilibrés).
# Une entrée d'une lettre = tous les chapitres de ce thème officiel.
APP_THEMES = [
    ("SIG", "Signalisation", ["L-PAN", "L-MAR", "L-FEU"]),
    ("PRI", "Priorités et intersections", ["L-PRI"]),
    ("VIT", "Vitesses", ["L-VIT"]),
    ("CIR", "Circulation et dépassement", ["L-CIR", "L-DEP"]),
    ("ARR", "Arrêt et stationnement", ["L-ARR"]),
    ("AUT", "Autoroute, tunnels et éclairage", ["L-AUT", "L-TUN", "L-ECL"]),
    ("CON", "Le conducteur", ["C"]),
    ("SEC", "Premiers secours", ["P"]),
    ("USA", "Les autres usagers", ["U"]),
    ("ROU", "La route", ["R"]),
    ("REG", "Réglementation", ["D"]),
    ("VEH", "Le véhicule", ["Q", "M", "S", "E"]),
]


def regroup(official):
    chaps = {c["code"]: dict(c, officiel=t["code"]) for t in official for c in t["chapitres"]}
    by_theme = {t["code"]: [c["code"] for c in t["chapitres"]] for t in official}
    used, out = set(), []
    for i, (code, nom, parts) in enumerate(APP_THEMES, 1):
        codes = [cc for p in parts for cc in (by_theme[p] if p in by_theme else [p])]
        out.append({"code": code, "num": i, "nom": nom, "chapitres": [chaps[c] for c in codes]})
        used.update(codes)
    missing = set(chaps) - used
    if missing:
        sys.exit(f"Chapitres non rattachés à un thème de l'appli : {sorted(missing)}")
    return out


def main():
    themes = regroup(parse_notions())
    notion_ids = {n["id"] for t in themes for c in t["chapitres"] for n in c["notions"]}
    files = sorted(glob.glob(os.path.join(ROOT, "data", "questions", "*.json")))
    count, errors, seen = {}, [], set()
    for f in files:
        for q in json.load(open(f, encoding="utf-8")):
            qid = q.get("id")
            if qid in seen:
                errors.append(f"id en double : {qid}")
            seen.add(qid)
            if q.get("n") not in notion_ids:
                errors.append(f"{qid} : notion inconnue {q.get('n')}")
            if not q.get("ok") or any(i >= len(q["c"]) for i in q["ok"]):
                errors.append(f"{qid} : réponses invalides")
            if q.get("img") and not os.path.exists(os.path.join(ROOT, q["img"])):
                errors.append(f"{qid} : image manquante {q['img']}")
            count[q["n"]] = count.get(q["n"], 0) + 1
    for t in themes:
        for c in t["chapitres"]:
            for n in c["notions"]:
                n["q"] = count.get(n["id"], 0)
    out = {
        "fichiers": [os.path.relpath(f, ROOT) for f in files],
        "themes": themes,
    }
    json.dump(out, open(os.path.join(ROOT, "data", "themes.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    total_n = len(notion_ids)
    covered = sum(1 for n in notion_ids if count.get(n))
    print(f"{len(seen)} questions · {covered}/{total_n} notions couvertes")
    for t in themes:
        tn = [n for c in t["chapitres"] for n in c["notions"]]
        print(f"  {t['num']:2} {t['nom'][:40]:40} {sum(n['q'] for n in tn):4} q · "
              f"{sum(1 for n in tn if n['q'])}/{len(tn)} notions")
    if errors:
        print("\nERREURS :\n  " + "\n  ".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
