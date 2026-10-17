#!/usr/bin/env python3
"""Проверка репозитория.

1. params.yaml и components.yaml парсятся; ID компонентов уникальны, обязательные поля на месте.
2. Числа с маркером `178<!--p:panels.front.woofer_x-->` в docs/*.md совпадают с params.yaml
   (`--fix` исправляет текст по params.yaml).
3. Ссылки CMP-*, OQ-*, T-* ведут на существующие записи.
4. Относительные ссылки Markdown и якоря существуют.
5. Позиции исходной спецификации 1..80 покрыты в components.yaml (предупреждение).

Код возврата 1 при ошибках.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FIX = "--fix" in sys.argv
errors, warnings = [], []


def load(name):
    with open(ROOT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def rel(p):
    return str(p.relative_to(ROOT))


params = load("params.yaml")
comps = load("components.yaml")["components"]

# --- 1. components.yaml
ids = {}
covered = set()
for c in comps:
    for key in ("id", "name", "qty", "module"):
        if key not in c:
            errors.append(f"components.yaml: у записи {c.get('id', c)} нет поля {key}")
    cid = c.get("id", "")
    if not re.fullmatch(r"CMP-[a-z0-9]+(?:-[a-z0-9]+)*", cid):
        errors.append(f"components.yaml: некорректный ID {cid}")
    if cid in ids:
        errors.append(f"components.yaml: дубликат {cid}")
    ids[cid] = c
    pos = c.get("pos")
    covered.update(pos if isinstance(pos, list) else [pos] if pos else [])
missing = sorted(set(range(1, 81)) - covered)
if missing:
    warnings.append(f"позиции исходной спецификации без записи: {missing}")

# --- Markdown-файлы
md_files = [p for p in ROOT.rglob("*.md") if "archive" not in p.relative_to(ROOT).parts]


def lookup(path):
    node = params
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def fmt(v):
    return str(v).replace("-", "−")    # YAML-значение как есть, минус типографский


marker = re.compile(r"(−?\d+(?:\.\d+)?)<!--p:([\w.\-]+)-->")
n_markers = 0
for p in md_files:
    text = p.read_text(encoding="utf-8")

    def repl(m):
        global n_markers
        n_markers += 1
        val = lookup(m.group(2))
        if val is None or isinstance(val, (dict, list)):
            errors.append(f"{rel(p)}: параметр {m.group(2)} не найден в params.yaml")
            return m.group(0)
        try:
            same = float(m.group(1).replace("−", "-")) == float(val)
        except (TypeError, ValueError):
            errors.append(f"{rel(p)}: параметр {m.group(2)} не число")
            return m.group(0)
        if same:
            return m.group(0)
        if FIX:
            print(f"fix  {rel(p)}: {m.group(1)} → {fmt(val)} ({m.group(2)})")
            return f"{fmt(val)}<!--p:{m.group(2)}-->"
        errors.append(f"{rel(p)}: {m.group(1)} ≠ params.{m.group(2)} = {val}")
        return m.group(0)

    new = marker.sub(repl, text)
    if FIX and new != text:
        p.write_text(new, encoding="utf-8")
        text = new

    # --- 3. ссылки CMP / OQ / T
    for m in set(re.findall(r"CMP-[a-z0-9]+(?:-[a-z0-9]+)*", text)):
        if m not in ids:
            errors.append(f"{rel(p)}: неизвестный компонент {m}")

oq_text = (ROOT / "docs/open-questions.md").read_text(encoding="utf-8")
oq_ids = set(re.findall(r"^\| (OQ-\d+) \|", oq_text, re.M))
tech_text = (ROOT / "docs/techniques.md").read_text(encoding="utf-8")
t_ids = set(re.findall(r"^## (T-\d+)", tech_text, re.M))
for p in md_files:
    text = p.read_text(encoding="utf-8")
    for m in set(re.findall(r"OQ-\d+", text)):
        if m not in oq_ids:
            errors.append(f"{rel(p)}: неизвестный вопрос {m}")
    for m in set(re.findall(r"(?<![A-Za-z0-9-])T-\d{3}", text)):
        if m not in t_ids:
            errors.append(f"{rel(p)}: неизвестный приём {m}")


# --- 4. ссылки и якоря
def slug(h):
    h = h.strip().lower()
    h = re.sub(r"[^\w\s-]", "", h)
    return re.sub(r"\s", "-", h)


def anchors(path):
    res = set()
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code:
            m = re.match(r"#{1,6}\s+(.*)", line)
            if m:
                res.add(slug(m.group(1)))
    return res


link = re.compile(r"\]\((?!https?://|mailto:)([^)\s]*)\)")
for p in md_files:
    for target in link.findall(p.read_text(encoding="utf-8")):
        path_part, _, anchor = target.partition("#")
        dest = p if not path_part else (p.parent / path_part).resolve()
        if not dest.exists():
            errors.append(f"{rel(p)}: битая ссылка {target}")
        elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
            errors.append(f"{rel(p)}: нет якоря #{anchor} в {rel(dest)}")

for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print(f"\nкомпонентов: {len(ids)}, документов: {len(md_files)}, маркеров параметров: {n_markers}; "
      f"ошибок: {len(errors)}, предупреждений: {len(warnings)}")
sys.exit(1 if errors else 0)
