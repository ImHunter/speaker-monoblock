#!/usr/bin/env python3
"""Размерная модель корпуса: базовые размеры -> производные.

Базы — params.yaml, раздел dimensions (v8 — текущая разборная, v9 — малоразборная).
Правила и таблицы — docs/dimensions.md.
Запуск: python scripts/dims.py [v8|v9]
"""
import sys
from math import sqrt
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
params = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
bases = params["dimensions"]
comps = yaml.safe_load((ROOT / "components.yaml").read_text(encoding="utf-8"))["components"]
bass = next(c for c in comps if c["id"] == "CMP-wavecor-wf168om01")
QTS = bass["params"]["qts"]
VAS = bass["params"]["vas_l"]
FS = bass["params"]["fs_hz"]
G = params["global"]
V_BARS = G["v_bars_l"]
V_DRIVER = G["v_driver_l"]
V_WIRES = G["v_wires_l"]


def derive(b):
    d = {}
    d["w_inner"] = b["w_total"] - 2 * b["w_mdf"]
    d["h_inner"] = b["h_total"] - 2 * b["w_mdf"] - 2 * b["w_glue"] - b["h_base"]
    d["d_side"] = b["d_acoustic"] + b["w_mdf"] + b["d_electric"]
    d["d_total"] = (b["w_overlay"] + b["w_mdf"] + b["w_ribbon"]
                    + b["d_acoustic"] + b["w_mdf"] + b["d_electric"]
                    + b["w_ribbon"] + b["w_back_abs"])
    d["h_side"] = b["h_total"] - b["w_mdf"] - b["w_glue"]
    d["h_front"] = b["h_total"] - b["h_base"]
    d["w_front"] = b["w_total"]
    d["w_bottom"] = d["w_inner"] - 2 * b["w_glue"]
    d["d_bottom"] = d["d_side"]
    d["h_baffle"] = d["h_inner"] - 2 * b["w_glue"]
    d["w_baffle"] = d["w_inner"] - 2 * b["w_glue"]
    d["w_top"] = b["w_total"]
    d["d_top"] = d["d_side"]
    d["w_rear"] = b["w_total"]
    d["h_rear"] = d["h_front"]
    d["v_geom_l"] = d["w_inner"] * d["h_inner"] * (b["d_acoustic"] + b["w_ribbon"]) / 1e6
    d["v_eff_l"] = d["v_geom_l"] - V_BARS - V_DRIVER - V_WIRES
    d["qtc"] = QTS * sqrt(1 + VAS / d["v_eff_l"])
    d["fc_hz"] = FS * sqrt(1 + VAS / d["v_eff_l"])
    d["d_rebate"] = b["flange_t"] + b["rebate_gap"]
    d["woofer_x"] = b["w_total"] / 2
    d["woofer_y"] = d["h_front"] / 2 + b["woofer_shift_up"]
    d["tweeter_y"] = d["h_front"] / 2
    d["tweeter_left_x"] = b["tweeter_edge"]
    d["tweeter_right_x"] = b["w_total"] - b["tweeter_edge"]
    return d


def check(b, d):
    eps = 1e-9
    pairs = [
        ("D_side = D_bottom", d["d_side"], d["d_bottom"]),
        ("D_total", d["d_total"],
         b["w_overlay"] + b["w_mdf"] + 2 * b["w_ribbon"] + d["d_side"] + b["w_back_abs"]),
        ("H_side + W_mdf + W_glue = H_total", d["h_side"] + b["w_mdf"] + b["w_glue"], b["h_total"]),
        ("H_front = H_total - H_base", d["h_front"], b["h_total"] - b["h_base"]),
        ("W_bottom = W_baffle", d["w_bottom"], d["w_baffle"]),
        ("H_baffle", d["h_baffle"], d["h_inner"] - 2 * b["w_glue"]),
        ("D_rebate", d["d_rebate"], b["flange_t"] + b["rebate_gap"]),
    ]
    for name, a, c in pairs:
        if abs(a - c) > eps:
            raise SystemExit(f"{name}: {a} != {c}")


FIELDS = [
    ("w_inner", "W_inner"), ("h_inner", "H_inner"), ("d_side", "D_side"),
    ("d_total", "D_total"), ("h_side", "H_side"), ("h_front", "H_front"),
    ("w_bottom", "W_bottom"), ("d_bottom", "D_bottom"),
    ("h_baffle", "H_baffle"), ("w_baffle", "W_baffle"),
    ("v_geom_l", "V_geom, л"), ("v_eff_l", "V_eff, л"),
    ("qtc", "Qtc"), ("fc_hz", "Fc, Гц"),
    ("d_rebate", "цековка, мм"), ("woofer_x", "вуфер X"), ("woofer_y", "вуфер Y"),
    ("tweeter_left_x", "твитер L X"), ("tweeter_right_x", "твитер R X"),
    ("tweeter_y", "твитер Y"),
]


def main(argv):
    versions = [a for a in argv[1:] if a in bases] or list(bases)
    for ver in versions:
        b = bases[ver]
        d = derive(b)
        check(b, d)
        print(f"\n== {ver} ==")
        for key, label in FIELDS:
            print(f"  {label:14} {d[key]:8.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
