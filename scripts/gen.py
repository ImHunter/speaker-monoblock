#!/usr/bin/env python3
"""Генерация таблиц: `gen.py bom` -> build/bom.csv, `gen.py cutlist` -> build/cutlist.csv

bom     — из components.yaml (как есть: pos, name, qty, note, source, price + паспортные поля).
cutlist — из таблицы 4.1 в docs/enclosure.md (источник единственный, дубля нет).
"""
import csv
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
(ROOT / "build").mkdir(exist_ok=True)


def bom():
    comps = yaml.safe_load((ROOT / "components.yaml").read_text(encoding="utf-8"))["components"]
    out = ROOT / "build/bom.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pos", "id", "module", "name", "qty", "note", "source", "price", "status"])
        for c in sorted(comps, key=lambda c: (c["pos"] is None, c["pos"] or 0)):
            w.writerow([c["pos"] or "", c["id"], c["module"], c["name"], c["qty"],
                        c.get("note", ""), c.get("source", ""), c.get("price", ""), c.get("status", "")])
    print(f"{out.relative_to(ROOT)}: {len(comps)} позиций")


def cutlist():
    text = (ROOT / "docs/enclosure.md").read_text(encoding="utf-8")
    start = text.index("### 4.1. Детали")
    rows = []
    for line in text[start:].split("\n")[1:]:
        if line.startswith("###") and not line.startswith("### 4.1"):
            break
        if not line.startswith("|") or re.match(r"\|[\s:|-]+\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "Деталь":
            continue
        name, material, size, qty, note = cells
        size = re.sub(r"<!--.*?-->|\*", "", size).strip()
        rows.append([name, re.sub(r"\*", "", material), size, qty, note])
    out = ROOT / "build/cutlist.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["part", "material", "size_mm", "qty", "note"])
        w.writerows(rows)
    print(f"{out.relative_to(ROOT)}: {len(rows)} деталей")


if __name__ == "__main__":
    cmds = {"bom": bom, "cutlist": cutlist}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        sys.exit("usage: gen.py bom|cutlist")
    cmds[sys.argv[1]]()
