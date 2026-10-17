#!/usr/bin/env python3
"""Карта раскроя: modules/enclosure/parts.yaml -> procurement/cutlist.generated.csv"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_yaml  # noqa: E402

data = load_yaml(ROOT / "modules/enclosure/parts.yaml")
out = ROOT / "procurement/cutlist.generated.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["id", "name", "material", "size_mm", "thickness_mm", "qty", "note"])
    for p in data["parts"]:
        size = "x".join(str(x) for x in p["size"]) if "size" in p else (
            f"{p['section'][0]}x{p['section'][1]}, всего {p['total_length']}")
        w.writerow([p["id"], p["name"], p["material"], size, p.get("thickness", ""), p["qty"], p.get("note", "")])
print(f"{out.relative_to(ROOT)}: {len(data['parts'])} деталей")
