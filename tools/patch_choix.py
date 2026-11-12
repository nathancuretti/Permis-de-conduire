#!/usr/bin/env python3
"""Applique des réécritures de propositions : python3 tools/patch_choix.py fichier.json patch.json
patch.json = {"id": ["prop 1", "prop 2", ...]} — même nombre de propositions, mêmes indices de bonnes réponses."""
import json
import sys

qf, pf = sys.argv[1], sys.argv[2]
qs = json.load(open(qf, encoding="utf-8"))
patch = json.load(open(pf, encoding="utf-8"))
byid = {q["id"]: q for q in qs}
for qid, c in patch.items():
    q = byid[qid]
    if isinstance(c, dict):
        q.update(c)
        continue
    assert len(c) == len(q["c"]), f"{qid} : {len(c)} propositions au lieu de {len(q['c'])}"
    q["c"] = c
json.dump(qs, open(qf, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"{len(patch)} questions modifiées dans {qf}")
