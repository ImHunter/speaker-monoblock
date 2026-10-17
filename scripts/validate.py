#!/usr/bin/env python3
"""Проверка репозитория: YAML, схемы паспортов, ID-ссылки, ссылки Markdown, порядок сборки.

Код возврата 1, если есть ошибки. Предупреждения (WARN) не ломают проверку.
"""
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_yaml, passports  # noqa: E402

try:
    import jsonschema
except ImportError:  # схема опциональна
    jsonschema = None

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def rel(p):
    return str(Path(p).relative_to(ROOT))


SKIP_DIRS = {"archive", ".git", "node_modules"}


def files(pattern):
    return [p for p in ROOT.rglob(pattern) if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS)]


# 1. YAML парсится
yaml_files = files("*.yaml")
for p in yaml_files:
    try:
        load_yaml(p)
    except yaml.YAMLError as e:
        err(f"{rel(p)}: ошибка YAML: {str(e).splitlines()[0]}")

# 2. Паспорта: схема, уникальность ID, имя файла
schema = None
if jsonschema:
    schema = json.loads((ROOT / "components/_schema.json").read_text(encoding="utf-8"))
else:
    warn("jsonschema не установлен: схема паспортов не проверена")

pp = {}
for p in sorted((ROOT / "components").rglob("*.yaml")):
    if p.name.startswith("_"):
        continue
    try:
        d = load_yaml(p)
    except yaml.YAMLError:
        continue
    if not isinstance(d, dict) or "id" not in d:
        err(f"{rel(p)}: нет поля id")
        continue
    if d["id"] in pp:
        err(f"{rel(p)}: дубликат ID {d['id']}")
    pp[d["id"]] = p
    if schema:
        d_json = json.loads(json.dumps(d, default=str))   # даты YAML -> строки
        for e in jsonschema.Draft202012Validator(schema).iter_errors(d_json):
            err(f"{rel(p)}: схема: {'/'.join(map(str, e.path)) or '<root>'}: {e.message}")
    ds = d.get("datasheet")
    if ds and not (ROOT / "components" / ds).exists():
        warn(f"{rel(p)}: datasheet {ds} ещё не добавлен")

# 3. Ссылки CMP-* в YAML и Markdown
cmp_re = re.compile(r"CMP-[a-z0-9]+(?:-[a-z0-9]+)*")
scan = files("*.yaml") + files("*.md")
for p in scan:
    if p.parent == ROOT / "components" and False:
        continue
    text = p.read_text(encoding="utf-8")
    for m in set(cmp_re.findall(text)):
        if m not in pp:
            err(f"{rel(p)}: неизвестный компонент {m}")

# 4. Ссылки ADR / T- / OQ-
adr_ids = {re.match(r"(ADR-\d+)", p.name).group(1) for p in (ROOT / "docs/decisions").glob("ADR-*.md")}
t_ids = {re.match(r"(T-\d+)", p.name).group(1) for p in (ROOT / "techniques").glob("T-*.md")}
oq_text = (ROOT / "docs/open-questions.md").read_text(encoding="utf-8")
oq_ids = set(re.findall(r"^\| (OQ-\d+) \|", oq_text, re.M))
for p in scan:
    t = p.read_text(encoding="utf-8")
    for m in set(re.findall(r"ADR-\d+", t)):
        if m not in adr_ids:
            err(f"{rel(p)}: неизвестный {m}")
    for m in set(re.findall(r"(?<![A-Za-z-])T-\d{3}", t)):
        if m not in t_ids:
            err(f"{rel(p)}: неизвестный приём {m}")
    if p.name != "open-questions.md":
        for m in set(re.findall(r"OQ-\d+", t)):
            if m not in oq_ids:
                err(f"{rel(p)}: неизвестный вопрос {m}")

# 5. Относительные ссылки Markdown
link_re = re.compile(r"\]\((?!https?://|mailto:|#)([^)\s]+)\)")
for p in files("*.md"):
    for m in link_re.findall(p.read_text(encoding="utf-8")):
        target = m.split("#")[0]
        if not target:
            continue
        if not (p.parent / target).resolve().exists():
            err(f"{rel(p)}: битая ссылка {m}")

# 6. Шаги сборки
step_def = {}   # id -> (file, requires)
for p in sorted((ROOT / "modules").glob("*/assembly.md")):
    req_col = None
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            req_col = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if "Требует" in cells:
            req_col = cells.index("Требует")
            continue
        m = re.match(r"(STEP-[A-Z]+-\d+)$", cells[0])
        if m:
            reqs = []
            if req_col is not None and req_col < len(cells):
                reqs = re.findall(r"STEP-[A-Z]+-\d+", cells[req_col])
            if m.group(1) in step_def:
                err(f"{rel(p)}: дубликат шага {m.group(1)}")
            step_def[m.group(1)] = (p, reqs)

seq = load_yaml(ROOT / "assembly/sequence.yaml")
order = {}
pos = 0
for st in seq["stages"]:
    if not (ROOT / "assembly" / st["doc"]).exists():
        err(f"assembly/{st['doc']}: файл этапа отсутствует")
    for s in st["steps"]:
        if s not in step_def:
            err(f"assembly/sequence.yaml: шаг {s} не определён в modules/*/assembly.md")
        if s in order:
            err(f"assembly/sequence.yaml: шаг {s} встречается дважды")
        order[s] = pos
        pos += 1
for s in step_def:
    if s not in order:
        warn(f"{s}: не включён в assembly/sequence.yaml")
for s, (p, reqs) in step_def.items():
    for r in reqs:
        if r not in step_def:
            err(f"{rel(p)}: {s} требует неизвестный {r}")
        elif s in order and r in order and order[r] >= order[s]:
            err(f"assembly/sequence.yaml: {s} стоит раньше или вместе со своей зависимостью {r}")
        elif s in order and r not in order:
            warn(f"{s}: зависимость {r} вне последовательности")

# 7. BOM модулей: ссылки на паспорта; позиции исходного BOM
covered = set()
for p in sorted((ROOT / "modules").glob("*/bom.yaml")):
    d = load_yaml(p)
    for it in d.get("items", []):
        if "ref" in it:
            if it["ref"] not in pp:
                err(f"{rel(p)}: ref {it['ref']} без паспорта")
        elif "name" not in it:
            err(f"{rel(p)}: позиция без ref и name: {it}")
        pos_ = it.get("source_bom_pos")
        if isinstance(pos_, int):
            covered.add(pos_)
for cid, path in pp.items():
    d = load_yaml(path)
    sp = d.get("source_bom_pos")
    for x in (sp if isinstance(sp, list) else [sp] if sp else []):
        covered.add(x)
missing = sorted(set(range(1, 81)) - covered)
if missing:
    warn(f"позиции исходного BOM без привязки: {missing}")

# 8. project.yaml
proj = load_yaml(ROOT / "project.yaml")
for name, m in proj["modules"].items():
    if not (ROOT / m["path"]).is_dir():
        err(f"project.yaml: нет каталога {m['path']}")
    if m["status"] not in {"draft", "reviewed", "frozen", "built", "tested"}:
        err(f"project.yaml: статус {m['status']} модуля {name}")
    for dep in m.get("depends_on", []):
        if dep not in proj["modules"]:
            err(f"project.yaml: {name} зависит от неизвестного {dep}")

# Итог
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print(f"\nПроверено: YAML={len(yaml_files)}, паспортов={len(pp)}, шагов={len(step_def)}; "
      f"ошибок={len(errors)}, предупреждений={len(warnings)}")
sys.exit(1 if errors else 0)
