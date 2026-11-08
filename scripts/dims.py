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
    d["h_inner"] = b["h_total"] - 2 * b["w_mdf"] - b["h_base"]
    d["d_side"] = b["d_acoustic"] + b["w_mdf"] + b["d_electric"]
    d["d_total"] = (b["w_overlay"] + b["w_mdf"] + b["w_ribbon"]
                    + d["d_side"] + b["w_ribbon"] + b["w_back_abs"])
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
    d["woofer_y"] = d["h_front"] / 2 + b["dy_wavecor"]
    d["tweeter_y"] = d["h_front"] / 2
    d["tweeter_left_x"] = d["woofer_x"] - b["dx_sica"]
    d["tweeter_right_x"] = d["woofer_x"] + b["dx_sica"]
    if "dd_divider" in b:
        d["x_baffle_e"] = b["w_total"] / 2 - b["w_mdf"] / 2 - b.get("dx_baffle_e", 0)
        d["baffle_e_x0"] = d["x_baffle_e"]
        d["baffle_e_x1"] = d["x_baffle_e"] + b["w_mdf"]
        d["baffle_e_len"] = b["d_electric"] - b["dd_divider"]
        d["baffle_e_h"] = d["h_baffle"]
        d["bay_jab_x0"] = b["w_mdf"]
        d["bay_jab_x1"] = d["baffle_e_x0"]
        d["bay_jab_w"] = d["bay_jab_x1"] - d["bay_jab_x0"]
        d["bay_el_x0"] = d["baffle_e_x1"]
        d["bay_el_x1"] = b["w_total"] - b["w_mdf"]
        d["bay_el_w"] = d["bay_el_x1"] - d["bay_el_x0"]
        d["w_bay_jab"] = b["w_total"] / 2 - b.get("dx_baffle_e", 0) - 3 * b["w_mdf"] / 2
        d["w_bay_el"] = b["w_total"] / 2 + b.get("dx_baffle_e", 0) - 3 * b["w_mdf"] / 2
    else:
        d["x_baffle_e"] = d["baffle_e_x0"] = d["baffle_e_x1"] = None
        d["baffle_e_len"] = d["baffle_e_h"] = None
        d["bay_jab_x0"] = d["bay_jab_x1"] = d["bay_jab_w"] = None
        d["bay_el_x0"] = d["bay_el_x1"] = d["bay_el_w"] = None
        d["w_bay_jab"] = d["w_bay_el"] = None
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
    ("x_baffle_e", "X_BAFFLE_E"), ("baffle_e_x0", "BAFFLE_E x0"), ("baffle_e_x1", "BAFFLE_E x1"),
    ("baffle_e_len", "BAFFLE_E L"), ("baffle_e_h", "BAFFLE_E H"),
    ("bay_jab_x0", "BAY_JAB x0"), ("bay_jab_x1", "BAY_JAB x1"), ("w_bay_jab", "W_BAY_JAB"),
    ("bay_el_x0", "BAY_EL x0"), ("bay_el_x1", "BAY_EL x1"), ("w_bay_el", "W_BAY_EL"),
]


def main(argv):
    versions = [a for a in argv[1:] if a in bases] or list(bases)
    for ver in versions:
        b = bases[ver]
        d = derive(b)
        check(b, d)
        print(f"\n== {ver} ==")
        for key, label in FIELDS:
            val = d[key]
            if val is None:
                print(f"  {label:14} {'—':>8}")
            else:
                print(f"  {label:14} {val:8.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
