#!/usr/bin/env python3
"""Параметрическая модель корпуса v9 для FreeCAD.

Запуск (headless):
  freecadcmd.exe scripts/freecad_v9.py
  # или: make model

Читает params.yaml (dimensions.v9, jab, psu, panels.front, panels.top),
строит панели v9 и выгружает STEP/STL/FCStd в models/v9/.

Что строится:
  - передняя панель 392×190×16: вуфер Ø144, твитеры Ø50 с цековкой 58.2×53.2×3.2,
    R8 на боковых торцах;
  - боковины У/ВВ 196×183.5×16 (ВВ — с окном C14 30×62 и 2×M3);
  - дно 359×196×16, верх 392×196×16 (с окном BT 50×50, OQ-021);
  - перегородка 359×156×16; разделитель 16×156×50;
  - задняя панель 392×190×5;
  - 4 отверстия M3 (Ø6×10) под стойки JAB4 в перегородке.
Сетка евровинтов/шкантов в этой версии не вырезается.
"""
from pathlib import Path

import FreeCAD as App
import Mesh
import Part

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "models" / "v9"


def load(path):
    """Минимальный парсер params.yaml: вложенные словари + скаляры."""
    root = {}
    stack = [(-1, root)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        key, sep, val = line.strip().partition(":")
        while stack and stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if sep and val.strip():
            v = val.strip().strip("'\"")
            try:
                v = float(v)
            except ValueError:
                pass
            parent[key] = v
        else:
            node = {}
            parent[key] = node
            stack.append((indent, node))
    return root


P = load(ROOT / "params.yaml")
V = P["dimensions"]["v9"]
J = P["jab"]
FR = P["panels"]["front"]
TOP = P["panels"]["top"]

WM = V["w_mdf"]
WG = V["w_glue"]
WB = V["w_back_abs"]
WR = V["w_ribbon"]
WO = V["w_overlay"]
HB = V["h_base"]
WT = V["w_total"]
HT = V["h_total"]
DA = V["d_acoustic"]
DE = V["d_electric"]
DD = V["dd_divider"]

W_IN = WT - 2 * WM
H_IN = HT - 2 * WM - 2 * WG - HB
D_SIDE = DA + WM + DE
H_SIDE = HT - WM - WG
H_FRONT = HT - HB
W_BOT = W_IN - 2 * WG
H_BAF = H_IN - 2 * WG

Z0 = WO + WM + WR
Z1 = Z0 + D_SIDE
ZR0 = Z1 + WR
ZB0 = Z0 + DA
ZB1 = ZB0 + WM
Y0 = HB + WM + WG

OUT.mkdir(parents=True, exist_ok=True)
doc = App.newDocument("v9-enclosure")


def box(name, x, y, z, dx, dy, dz):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = Part.makeBox(dx, dy, dz, App.Vector(x, y, z))
    return obj


def cyl(obj, x, y, z, r, h, axis):
    c = Part.makeCylinder(r, h, App.Vector(x, y, z), App.Vector(*axis))
    obj.Shape = obj.Shape.cut(c)


def fbox(obj, x, y, z, dx, dy, dz):
    obj.Shape = obj.Shape.cut(Part.makeBox(dx, dy, dz, App.Vector(x, y, z)))


# ---------------------------------------------------------------- панели
front = box("Front", 0, HB, 0, WT, H_FRONT, WM)
side_u = box("Side_U", 0, 0, Z0, WM, H_SIDE, D_SIDE)
side_vv = box("Side_VV", WT - WM, 0, Z0, WM, H_SIDE, D_SIDE)
bottom = box("Bottom", WM + WG, HB, Z0, W_BOT, WM, D_SIDE)
top = box("Top", 0, HT - WM, Z0, WT, WM, D_SIDE)
baffle = box("Baffle", WM + WG, Y0 + WG, ZB0, W_BOT, H_BAF, WM)
divider = box("Divider", WT / 2 - WM / 2, Y0 + WG, ZB1, WM, H_BAF, DE - DD)
rear = box("Rear", 0, HB, ZR0, WT, H_FRONT, WB)

# ---------------------------------------------------------------- передняя панель
WOO_Y = HB + H_FRONT / 2 + V["dy_wavecor"]      # 110 от пола
TWE_Y = HB + H_FRONT / 2                         # 105
WOO_X = WT / 2
TWE_X = (WOO_X - V["dx_sica"], WOO_X + V["dx_sica"])

cyl(front, WOO_X, WOO_Y, -1, V["woofer_hole"] / 2, WM + 2, (0, 0, 1))
for tx in TWE_X:
    fbox(front, tx - 58.2 / 2, TWE_Y - 53.2 / 2, 0, 58.2, 53.2, V["flange_t"] + V["rebate_gap"])
    cyl(front, tx, TWE_Y, -1, V["tweeter_hole"] / 2, WM + 2, (0, 0, 1))

# R8 на боковых торцах передней панели
edges = []
for e in front.Shape.Edges:
    bb = e.BoundBox
    if bb.YLength > H_FRONT - 1 and bb.ZLength > WM - 1:
        if abs(bb.XMin) < 1e-6 or abs(bb.XMin - WT) < 1e-6:
            edges.append(e)
if len(edges) == 2:
    front.Shape = front.Shape.makeFillet(FR["edge_radius"], edges)

# ---------------------------------------------------------------- C14 (боковина ВВ)
WIN_Z = ZB1 + V["dz_c14"]
WIN_Y = V["dy_c14"]
fbox(side_vv, WT - WM, WIN_Y, WIN_Z, WM, 62, 30)
for zc in (WIN_Z - 5, WIN_Z + 30 + 5):
    cyl(side_vv, WT - WM, WIN_Y + 31, zc, 1.9, WM, (1, 0, 0))

# ---------------------------------------------------------------- JAB4: втулки M3 в перегородке
JAB_X0 = WM + J["dx_mm"]                 # 56
JAB_Y0 = Y0 + J["dy_mm"]                 # 61.7
for x in (JAB_X0 + 4, JAB_X0 + 92 - 4):
    for y in (JAB_Y0 + 4, JAB_Y0 + 69 - 4):
        cyl(baffle, x, y, ZB1 - 10, 3, 10, (0, 0, 1))

# ---------------------------------------------------------------- окно BT (OQ-021)
BT_X = J["bt_window_x_mm"]
BT_Z = TOP["bt_window_y"]
fbox(top, BT_X - 25, HT - WM, BT_Z - 25, 50, WM, 50)

# ---------------------------------------------------------------- экспорт
doc.recompute()
objs = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
part = Part.makeCompound([o.Shape for o in objs])
bb = part.BoundBox
Part.export(objs, str(OUT / "v9.step"))
Mesh.export(objs, str(OUT / "v9.stl"))
doc.saveAs(str(OUT / "v9.FCStd"))

print(f"FreeCAD {App.Version()[0]}.{App.Version()[1]}")
print(f"v9: {bb.XLength:.1f} x {bb.YLength:.1f} x {bb.ZLength:.1f} mm")
print(f"STEP: {OUT / 'v9.step'}")
print(f"STL : {OUT / 'v9.stl'}")
print(f"FCStd: {OUT / 'v9.FCStd'}")
App.closeDocument(doc.Name)
