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


# Thèmes affichés dans l'appli : 12 thèmes, chacun découpé en sous-parties (au moins 3).
# Une sous-partie est une liste de sélecteurs : code de chapitre officiel (« L-PAN »)
# ou identifiant de notion (« L-PAN-02 »). Nom None = reprendre le nom du chapitre officiel.
def n(prefix, *nums):
    return [f"{prefix}-{k:02d}" for k in nums]


APP_THEMES = [
    ("SIG", "Signalisation", [
        ("Panneaux de danger et d'intersection", n("L-PAN", 1, 2, 3, 4, 15, 16)),
        ("Interdiction, obligation et fin", n("L-PAN", 5, 6, 7, 8, 14)),
        ("Indication, direction et panonceaux", n("L-PAN", 9, 10, 11, 12, 13)),
        ("Marquages au sol", ["L-MAR"]),
        ("Feux et agents", ["L-FEU"]),
    ]),
    ("PRI", "Priorités et intersections", [
        ("Règles de base : stop, cédez, priorité à droite", n("L-PRI", 1, 2, 3, 4, 9, 11, 13)),
        ("Giratoires", n("L-PRI", 5, 6)),
        ("Passages à niveau et tramways", n("L-PRI", 8, 10)),
        ("Piétons et véhicules prioritaires", n("L-PRI", 7, 12)),
    ]),
    ("VIT", "Vitesses", [
        ("Limitations selon la route", n("L-VIT", 1, 2, 3, 4, 8)),
        ("Pluie, visibilité et jeunes conducteurs", n("L-VIT", 5, 6, 7)),
        ("Sanctions, radars et gravité des chocs", n("L-VIT", 9, 10, 11)),
    ]),
    ("CIR", "Circulation et dépassement", [
        ("Placement, voies et manœuvres", n("L-CIR", 1, 2, 3, 4, 5, 7, 8)),
        ("Distances de sécurité et distances latérales", n("L-CIR", 6) + n("L-DEP", 4)),
        ("Dépassement et croisement", n("L-DEP", 1, 2, 3, 5, 6, 7)),
    ]),
    ("ARR", "Arrêt et stationnement", [
        ("Arrêt ou stationnement", n("L-ARR", 1)),
        ("Stationnement dangereux, gênant ou interdit", n("L-ARR", 2, 3)),
        ("Zones, durées et fourrière", n("L-ARR", 4, 5, 6)),
    ]),
    ("AUT", "Autoroute, tunnels et éclairage", [
        (None, ["L-AUT"]), (None, ["L-TUN"]), (None, ["L-ECL"]),
    ]),
    ("CON", "Le conducteur", [
        (None, ["C-ALC"]), (None, ["C-DRO"]), (None, ["C-FAT"]), (None, ["C-DIS"]),
        (None, ["C-PER"]), (None, ["C-COM"]), (None, ["C-SAN"]),
    ]),
    ("SEC", "Premiers secours", [
        ("Protéger", n("P-PAS", 1, 10, 12)),
        ("Alerter", n("P-PAS", 2, 3, 11)),
        ("Secourir", n("P-PAS", 4, 5, 6, 7, 8, 9)),
    ]),
    ("USA", "Les autres usagers", [
        (None, ["U-PIE"]), (None, ["U-VEL"]), (None, ["U-2RM"]), (None, ["U-LOU"]), (None, ["U-ANI"]),
    ]),
    ("ROU", "La route", [
        ("Types de routes et virages", ["R-TYP", "R-VIR"]),
        ("Météo et adhérence", ["R-MET"]),
        ("Conduite de nuit", ["R-NUI"]),
        ("Travaux et bouchons", ["R-TRA"]),
    ]),
    ("REG", "Réglementation", [
        ("Permis et points", ["D-PER"]),
        ("Papiers du véhicule", ["D-DOC"]),
        ("Assurance et accidents", ["D-ASS", "D-ACC"]),
        ("Infractions et sanctions", ["D-INF", "D-PRO"]),
    ]),
    ("VEH", "Le véhicule", [
        ("Poste de conduite", ["Q-INS"]),
        ("Passagers, enfants et sortie du véhicule", ["Q-PAS", "Q-SOR"]),
        ("Remorques et chargement", ["Q-REM"]),
        ("Tableau de bord et entretien", ["M-TAB", "M-ENT"]),
        ("Pneus, freins et direction", ["M-PNE", "M-FRE"]),
        ("Aides et équipements de sécurité", ["M-AID", "S-EQU"]),
        ("Éco-conduite et environnement", ["E-ECO", "E-POL"]),
    ]),
]
MIN_SOUS_PARTIES = 3


def regroup(official):
    chaps = {c["code"]: c for t in official for c in t["chapitres"]}
    notions = {nn["id"]: nn for c in chaps.values() for nn in c["notions"]}
    used, out, errors = {}, [], []
    for i, (code, nom, parts) in enumerate(APP_THEMES, 1):
        if len(parts) < MIN_SOUS_PARTIES:
            errors.append(f"{code} : seulement {len(parts)} sous-parties (minimum {MIN_SOUS_PARTIES})")
        subs = []
        for j, (snom, sels) in enumerate(parts, 1):
            ids = []
            for sel in sels:
                if sel in chaps:
                    ids += [nn["id"] for nn in chaps[sel]["notions"]]
                elif sel in notions:
                    ids.append(sel)
                else:
                    errors.append(f"{code} : sélecteur inconnu {sel}")
            if snom is None:
                snom = chaps[sels[0]]["nom"]
            scode = f"{code}-{j}"
            for nid in ids:
                if nid in used:
                    errors.append(f"notion {nid} dans {used[nid]} et {scode}")
                used[nid] = scode
            subs.append({"code": scode, "nom": snom, "notions": [notions[x] for x in ids]})
        out.append({"code": code, "num": i, "nom": nom, "chapitres": subs})
    missing = sorted(set(notions) - set(used))
    if missing:
        errors.append(f"notions sans sous-partie : {missing}")
    if errors:
        sys.exit("Découpage invalide :\n  " + "\n  ".join(errors))
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
        tn = [x for c in t["chapitres"] for x in c["notions"]]
        print(f"  {t['num']:2} {t['nom'][:40]:40} {sum(x['q'] for x in tn):4} q · "
              f"{sum(1 for x in tn if x['q'])}/{len(tn)} notions · "
              + " | ".join(f"{c['nom'][:22]} {sum(x['q'] for x in c['notions'])}" for c in t["chapitres"]))
    if errors:
        print("\nERREURS :\n  " + "\n  ".join(errors))
        sys.exit(1)


def stamp_assets():
    """Ajoute à index.html une version (empreinte) des fichiers CSS/JS pour éviter de mélanger
    une ancienne et une nouvelle version en cache dans le navigateur."""
    import hashlib
    h = hashlib.sha1()
    for f in ("css/app.css", "js/store.js", "js/app.js"):
        h.update(open(os.path.join(ROOT, f), "rb").read())
    v = h.hexdigest()[:10]
    p = os.path.join(ROOT, "index.html")
    html = re.sub(r"\?v=[0-9a-z]+", f"?v={v}", open(p, encoding="utf-8").read())
    open(p, "w", encoding="utf-8").write(html)
    sw = os.path.join(ROOT, "sw.js")
    s = re.sub(r'const CACHE = "permis-[^"]*";', f'const CACHE = "permis-{v}";', open(sw, encoding="utf-8").read())
    open(sw, "w", encoding="utf-8").write(s)


def rapport_indices():
    """Avertit (sans bloquer) si des questions laissent deviner la réponse par la forme."""
    sys.path.insert(0, os.path.dirname(__file__))
    from indices import problemes
    flag = [q["id"] for f in sorted(glob.glob(os.path.join(ROOT, "data", "questions", "*.json")))
            for q in json.load(open(f, encoding="utf-8")) if problemes(q)]
    print(f"Indices de forme : {len(flag)} question(s) à surveiller (détail : python3 tools/indices.py)")


if __name__ == "__main__":
    main()
    stamp_assets()
    rapport_indices()
