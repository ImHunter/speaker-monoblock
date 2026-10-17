#!/usr/bin/env python3
"""Генерация таблиц: `gen.py bom` -> build/bom.csv, `gen.py cutlist` -> build/cutlist.csv"""
import csv
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
(ROOT / "build").mkdir(exist_ok=True)


def load(name):
    with open(ROOT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def bom():
    comps = load("components.yaml")["components"]
    out = ROOT / "build/bom.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["module", "id", "name", "qty", "price_hint_rub", "status", "pos", "note"])
        for c in sorted(comps, key=lambda c: (c["module"], c["id"])):
            pos = c.get("pos", "")
            if isinstance(pos, list):
                pos = " ".join(map(str, pos))
            w.writerow([c["module"], c["id"], c["name"], c["qty"], c.get("price", ""),
                        c.get("status", ""), pos, c.get("note", "")])
    print(f"{out.relative_to(ROOT)}: {len(comps)} позиций")


def cutlist():
    parts = load("params.yaml")["parts"]
    out = ROOT / "build/cutlist.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "material", "w_mm", "h_mm", "qty", "total_length_mm", "note"])
        for p in parts:
            w.writerow([p["id"], p["name"], p["material"], p["w"], p["h"], p["qty"],
                        p.get("total_length", ""), p.get("note", "")])
    print(f"{out.relative_to(ROOT)}: {len(parts)} деталей")


if __name__ == "__main__":
    cmds = {"bom": bom, "cutlist": cutlist}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        sys.exit("usage: gen.py bom|cutlist")
    cmds[sys.argv[1]]()
