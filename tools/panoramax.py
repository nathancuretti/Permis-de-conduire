#!/usr/bin/env python3
"""Recherche de photos Panoramax « vue conducteur » contenant un panneau donné.

python3 tools/panoramax.py FR:AB4 sortie/   -> télécharge les meilleures candidates + planche contact + métadonnées
Les candidates sont triées par taille du panneau dans l'image (panneau proche = situation lisible).
"""
import json
import os
import sys
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw

BBOX = "-5,42,8.5,51.2"  # France métropolitaine


INSTANCES = ["https://panoramax.ign.fr/api/search", "https://panoramax.openstreetmap.fr/api/search"]


def search(code, limit=60):
    """Interroge directement les instances (plus rapides que le catalogue fédéré)."""
    import time
    feats = []
    for api in INSTANCES:
        q = urllib.parse.urlencode({"filter": f"\"semantics.osm|traffic_sign\"='{code}'", "limit": limit, "bbox": BBOX})
        for essai in range(3):
            try:
                feats += json.load(urllib.request.urlopen(f"{api}?{q}", timeout=90))["features"]
                break
            except Exception as e:
                print(f"  {api} : nouvel essai ({e})")
                time.sleep(5 * (essai + 1))
    return feats


def candidates(code, n=8):
    out = []
    for f in search(code):
        p = f["properties"]
        ex = p.get("exif") or {}
        if ex.get("Xmp.GPano.ProjectionType") == "equirectangular":
            continue
        W = int(ex.get("Exif.Photo.PixelXDimension") or 0) or 2048
        best = 0
        for a in p.get("annotations") or []:
            if any(s.get("key") == "osm|traffic_sign" and s.get("value") == code for s in a.get("semantics", [])):
                xs = [c[0] for c in a["shape"]["coordinates"][0]]
                best = max(best, (max(xs) - min(xs)) / W)
        if best < 0.02:
            continue
        lic = next((l["title"] for l in f["links"] if l["rel"] == "license"), "")
        out.append({"id": f["id"], "collection": f["collection"], "size": round(best, 3),
                    "sd": f["assets"]["sd"]["href"], "author": p.get("geovisio:producer") or "",
                    "license": lic.replace("License for this object (", "").rstrip(")"), "date": p.get("datetime", "")[:10]})
    out.sort(key=lambda c: -c["size"])
    # une photo par séquence, pour varier les lieux
    seen, res = set(), []
    for c in out:
        if c["collection"] in seen:
            continue
        seen.add(c["collection"])
        res.append(c)
        if len(res) >= n:
            break
    return res


def main(code, outdir, n=8):
    os.makedirs(outdir, exist_ok=True)
    tag = code.replace(":", "_").replace("[", "_").replace("]", "")
    cs = candidates(code, n)
    thumbs = []
    for i, c in enumerate(cs):
        fn = os.path.join(outdir, f"{tag}_{i}.jpg")
        try:
            open(fn, "wb").write(urllib.request.urlopen(c["sd"], timeout=60).read())
        except Exception as e:
            print("échec", c["id"], e)
            continue
        c["file"] = fn
        im = Image.open(fn).convert("RGB")
        im.thumbnail((520, 390))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 34, 26], fill="black")
        d.text((8, 6), str(i), fill="white")
        thumbs.append(im)
    json.dump(cs, open(os.path.join(outdir, f"{tag}.json"), "w"), ensure_ascii=False, indent=1)
    if thumbs:
        cols = 3
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (520 * cols, 390 * rows), "white")
        for k, im in enumerate(thumbs):
            sheet.paste(im, ((k % cols) * 520, (k // cols) * 390))
        sheet.save(os.path.join(outdir, f"{tag}_planche.jpg"), quality=80)
    print(code, len(thumbs), "photos")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
