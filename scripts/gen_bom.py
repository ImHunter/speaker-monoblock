#!/usr/bin/env python3
"""Сводная спецификация: modules/*/bom.yaml + паспорта -> procurement/bom.generated.csv"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, module_boms, passports  # noqa: E402


def price_of(passport):
    for s in passport.get("sources", []):
        if "price_rub" in s:
            return s["price_rub"], s.get("vendor", ""), s.get("url", "")
    return "", "", ""


pp = {k: v[1] for k, v in passports().items()}
rows = []
for module, _, data in module_boms():
    for it in data.get("items", []):
        if "ref" in it:
            d = pp.get(it["ref"], {})
            price, vendor, url = price_of(d)
            rows.append([module, it["ref"], d.get("name", ""), it.get("qty", ""), price, vendor,
                         url, d.get("status", ""), it.get("note", "")])
        else:
            rows.append([module, "", it["name"], it.get("qty", ""), it.get("price_rub", ""), "",
                         it.get("url", ""), "no-passport", it.get("note", "")])

out = ROOT / "procurement/bom.generated.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["module", "component_id", "name", "qty", "price_rub_hint", "vendor", "url", "status", "note"])
    w.writerows(rows)
print(f"{out.relative_to(ROOT)}: {len(rows)} позиций; без паспорта: {sum(1 for r in rows if r[7] == 'no-passport')}")
