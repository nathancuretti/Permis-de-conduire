#!/usr/bin/env python3
"""Échantillonne des photos Panoramax « vue conducteur » autour d'un point (pour trouver des situations sans panneau).

python3 tools/panoramax_zone.py nom lat lon dossier/ [rayon_deg]
-> planche de miniatures numérotées + métadonnées (nom.json)
"""
import json
import os
import sys
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw

INSTANCES = ["https://panoramax.ign.fr/api/search", "https://panoramax.openstreetmap.fr/api/search"]


def main(nom, lat, lon, outdir, r=0.006, n=24):
    os.makedirs(outdir, exist_ok=True)
    bbox = f"{lon - r},{lat - r},{lon + r},{lat + r}"
    feats = []
    for api in INSTANCES:
        try:
            q = urllib.parse.urlencode({"bbox": bbox, "limit": 120})
            feats += json.load(urllib.request.urlopen(f"{api}?{q}", timeout=90))["features"]
        except Exception as e:
            print(api, e)
    flat = [f for f in feats if (f["properties"].get("exif") or {}).get("Xmp.GPano.ProjectionType") != "equirectangular"
            and f["properties"].get("geovisio:image")  # garde-fou
            or (f["properties"].get("exif") or {}).get("Xmp.GPano.ProjectionType") is None]
    flat = [f for f in flat if (f["properties"].get("exif") or {}).get("Xmp.GPano.ProjectionType") != "equirectangular"]
    step = max(1, len(flat) // n)
    pick = flat[::step][:n]
    meta, thumbs = [], []
    for i, f in enumerate(pick):
        p = f["properties"]
        lic = next((l["title"] for l in f["links"] if l["rel"] == "license"), "")
        m = {"i": i, "id": f["id"], "sd": f["assets"]["sd"]["href"], "author": p.get("geovisio:producer") or "",
             "license": lic.replace("License for this object (", "").rstrip(")")}
        try:
            data = urllib.request.urlopen(f["assets"]["thumb"]["href"], timeout=60).read()
        except Exception as e:
            print("échec", e)
            continue
        fn = os.path.join(outdir, f"{nom}_t{i}.jpg")
        open(fn, "wb").write(data)
        im = Image.open(fn).convert("RGB")
        im.thumbnail((400, 300))
        ImageDraw.Draw(im).rectangle([0, 0, 40, 22], fill="black")
        ImageDraw.Draw(im).text((6, 5), str(i), fill="yellow")
        thumbs.append((i, im))
        meta.append(m)
    json.dump(meta, open(os.path.join(outdir, f"{nom}.json"), "w"), ensure_ascii=False, indent=1)
    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (400 * cols, 300 * max(rows, 1)), "white")
    for k, (i, im) in enumerate(thumbs):
        sheet.paste(im, ((k % cols) * 400, (k // cols) * 300))
    sheet.save(os.path.join(outdir, f"{nom}_planche.jpg"), quality=75)
    print(nom, len(flat), "photos à plat dans la zone,", len(thumbs), "miniatures")


if __name__ == "__main__":
    a = sys.argv
    main(a[1], float(a[2]), float(a[3]), a[4], float(a[5]) if len(a) > 5 else 0.006)
