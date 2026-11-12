#!/usr/bin/env python3
"""Repère les questions dont la réponse se devine par la forme (longueur, mots absolus, propositions absurdes).

Usage : python3 tools/indices.py [fichier.json ...]   (par défaut : toutes les questions)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
ABSOLU = re.compile(r"\b(toujours|jamais|uniquement|seulement|dans tous les cas|aucun|n'importe|tous les)\b", re.I)
ABSURDE = re.compile(r"\b(klaxonn\w*|accél[eé]r\w*|fumer|pour lui montrer|rien ne|frôl\w*|piler)\b", re.I)


def problemes(q):
    out = []
    good = [q["c"][i] for i in q["ok"]]
    bad = [c for i, c in enumerate(q["c"]) if i not in q["ok"]]
    if not bad:
        return out
    lg, lb = min(len(c) for c in good), max(len(c) for c in bad)
    if len(q["ok"]) == 1 and lg > 1.25 * lb and lg - lb > 12:
        out.append(f"longueur ({lg} vs {lb})")
    ab = [c for c in bad if ABSOLU.search(c)]
    if ab and not any(ABSOLU.search(c) for c in good):
        out.append("mot absolu")
    if any(ABSURDE.search(c) for c in bad):
        out.append("proposition absurde")
    return out


def main(files):
    n = tot = 0
    for f in files:
        for q in json.load(open(f, encoding="utf-8")):
            tot += 1
            p = problemes(q)
            if p:
                n += 1
                if "-q" not in sys.argv:
                    print(f"{q['id']}  [{', '.join(p)}]\n  Q: {q['q']}")
                    for i, c in enumerate(q["c"]):
                        print(f"   {'✔' if i in q['ok'] else '·'} {c}")
    print(f"\n{n}/{tot} questions avec un indice de forme")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    main(args or sorted(glob.glob(os.path.join(ROOT, "data", "questions", "*.json"))))
