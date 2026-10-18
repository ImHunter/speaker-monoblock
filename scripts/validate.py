#!/usr/bin/env python3
"""Проверка репозитория.

1. components.yaml: поля, уникальные ID, позиции исходной спецификации 1..80 ровно по одному разу.
2. Числа с маркером `178<!--p:panels.front.woofer_x-->` в docs/*.md совпадают с params.yaml;
   параметры params.yaml без маркера в тексте — предупреждение.
3. Ссылки CMP-*, OQ-* ведут на существующие записи.
4. Ссылки Markdown и якоря существуют.
5. Все разделы исходника (по номерам заголовков архива) присутствуют в docs/*.md,
   ссылки «см. N.N» ведут на существующие разделы (известные битые — предупреждение, см. open-questions).
6. Таблица «Карта документов» в docs/project.md актуальна.
7. components.yaml: у каждого компонента есть `see` — номера разделов исходника, и они существуют в docs/.

`--fix` исправляет числа по params.yaml и перегенерирует карту разделов. Код возврата 1 при ошибках.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FIX = "--fix" in sys.argv
errors, warnings = [], []
err, warn = errors.append, warnings.append


def load(name):
    with open(ROOT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def rel(p):
    return str(Path(p).relative_to(ROOT))


params = load("params.yaml")
comps = load("components.yaml")["components"]
docs = sorted((ROOT / "docs").glob("*.md")) + [ROOT / "README.md", ROOT / "AGENTS.md"]
doc_text = {p: p.read_text(encoding="utf-8") for p in docs}

# ------------------------------------------------------------------ 1. components.yaml
ids, positions = {}, []
for c in comps:
    for key in ("id", "name", "qty", "module"):
        if key not in c:
            err(f"components.yaml: у {c.get('id', c)} нет поля {key}")
    cid = c.get("id", "")
    if not re.fullmatch(r"CMP-[a-z0-9]+(?:-[a-z0-9]+)*", cid):
        err(f"components.yaml: некорректный ID {cid}")
    if cid in ids:
        err(f"components.yaml: дубликат {cid}")
    ids[cid] = c
    if c.get("pos"):
        positions.append(c["pos"])
if sorted(positions) != list(range(1, 81)):
    err(f"components.yaml: позиции спецификации не 1..80 ровно по разу: "
        f"пропущены {sorted(set(range(1, 81)) - set(positions))}, "
        f"повторы {sorted({p for p in positions if positions.count(p) > 1})}")

# ------------------------------------------------------------------ 2. маркеры параметров
def lookup(path):
    node = params
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def leaf_paths(node, prefix=""):
    for k, v in node.items():
        p = f"{prefix}{k}"
        if isinstance(v, dict):
            yield from leaf_paths(v, p + ".")
        else:
            yield p


def fmt(v):
    return str(v).replace("-", "−")


SIGN = "-−–"
marker = re.compile(rf"((?<![\w>])[{SIGN}]?\d+(?:\.\d+)?)<!--p:([\w.]+)-->")
used, n_markers = set(), 0
for p in docs:
    text = doc_text[p]

    def repl(m):
        global n_markers
        n_markers += 1
        used.add(m.group(2))
        val = lookup(m.group(2))
        if val is None or isinstance(val, (dict, list)):
            err(f"{rel(p)}: параметр {m.group(2)} не найден в params.yaml")
            return m.group(0)
        shown = float(re.sub(f"[{SIGN}]", "-", m.group(1)))
        if shown == float(val):
            return m.group(0)
        if FIX:
            print(f"fix  {rel(p)}: {m.group(1)} → {fmt(val)} ({m.group(2)})")
            return f"{fmt(val)}<!--p:{m.group(2)}-->"
        err(f"{rel(p)}: {m.group(1)} ≠ params.{m.group(2)} = {val}")
        return m.group(0)

    new = marker.sub(repl, text)
    if FIX and new != text:
        p.write_text(new, encoding="utf-8")
        doc_text[p] = new
for path in leaf_paths(params):
    if path not in used:
        warn(f"params.yaml: {path} не привязан ни к одному числу в тексте")

# ------------------------------------------------------------------ 3. CMP / OQ
oq_text = (ROOT / "docs/open-questions.md").read_text(encoding="utf-8")
oq_ids = set(re.findall(r"^\| (OQ-\d+) \|", oq_text, re.M))
for p, text in doc_text.items():
    for m in set(re.findall(r"CMP-[a-z0-9]+(?:-[a-z0-9]+)*", text)):
        if m not in ids:
            err(f"{rel(p)}: неизвестный компонент {m}")
    if p.name != "open-questions.md":
        for m in set(re.findall(r"OQ-\d+", text)):
            if m not in oq_ids:
                err(f"{rel(p)}: неизвестный вопрос {m}")
for p in ROOT.glob("components.yaml"):
    for m in set(re.findall(r"OQ-\d+", p.read_text(encoding="utf-8"))):
        if m not in oq_ids:
            err(f"components.yaml: неизвестный вопрос {m}")


# ------------------------------------------------------------------ 4. ссылки и якоря
def slug(h):
    h = re.sub(r"<!--.*?-->", "", h).strip().lower()
    h = re.sub(r"[^\w\s-]", "", h)
    return re.sub(r"\s", "-", h)


def anchors(text):
    res, in_code = set(), False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not in_code:
            m = re.match(r"#{1,6}\s+(.*)", line)
            if m:
                res.add(slug(m.group(1)))
    return res


link = re.compile(r"\]\((?!https?://|mailto:)([^)\s]*)\)")
for p, text in doc_text.items():
    for target in link.findall(text):
        path_part, _, anchor = target.partition("#")
        dest = p if not path_part else (p.parent / path_part).resolve()
        if not dest.exists():
            err(f"{rel(p)}: битая ссылка {target}")
        elif anchor and dest.suffix == ".md":
            dt = doc_text.get(dest) or dest.read_text(encoding="utf-8")
            if anchor not in anchors(dt):
                err(f"{rel(p)}: нет якоря #{anchor} в {rel(dest)}")

# ------------------------------------------------------------------ 5. разделы исходника
src = (ROOT / "archive/проект-колонки-v8.0.md").read_text(encoding="utf-8").replace("\r", "")
src_sections = []
for line in src.split("\n"):
    m = re.match(r"#{2,4} (\d+(?:\.\d+)*)\.", line)
    if m:
        src_sections.append(m.group(1))
doc_heads = {}   # номер -> [файлы]
for p, text in doc_text.items():
    if p.parent.name != "docs":
        continue
    in_code = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
        m = None if in_code else re.match(r"#{2,4} (\d+(?:\.\d+)*)\.", line)
        if m:
            doc_heads.setdefault(m.group(1), []).append(p.name)
for n in src_sections:
    if n not in doc_heads and n != "5":      # §5 — это components.yaml
        err(f"раздел {n} исходника не найден в docs/")
# Этапы сборки (6.x) нумеруются словами «Этап N» — проверка ниже по числу этапов
if len(re.findall(r"^### Этап \d", doc_text[ROOT / "docs/assembly.md"], re.M)) != 8:
    err("docs/assembly.md: должно быть 8 этапов сборки")

KNOWN_BAD = {  # (файл, ссылка): OQ — заведомо битые ссылки исходника
    ("enclosure.md", "8.2"): "OQ-002", ("assembly.md", "5.3"): "OQ-002", ("assembly.md", "6.4"): "OQ-016",
    ("enclosure.md", "6.4"): "OQ-016",
}
ref_re = re.compile(r"(?:см\.|раздел[а-я]*|п\.|таблиц[аеыи]|разделу)\s+(\d+(?:\.\d+)+|\d+)\b")
for p, text in doc_text.items():
    if p.parent.name != "docs" or p.name in ("open-questions.md", "glossary.md"):
        continue
    for m in ref_re.finditer(text):
        n = m.group(1)
        if n in doc_heads or n in {str(i) for i in range(1, 13)} and n in {h.split(".")[0] for h in doc_heads}:
            continue
        issue = KNOWN_BAD.get((p.name, n))
        if issue:
            warn(f"{rel(p)}: ссылка «{m.group(0)}» ведёт в никуда (известно: {issue})")
        else:
            err(f"{rel(p)}: ссылка «{m.group(0)}» не найдена среди разделов")

# ------------------------------------------------------------------ 5b. ссылки see в components.yaml
valid_sections = set(doc_heads)
for name_file, pat, pref in (("assembly.md", r"^### Этап (\d+)\.", "6/Этап "), ("commissioning.md", r"^### Шаг (\d+)\.", "7/Шаг ")):
    for n in re.findall(pat, doc_text[ROOT / "docs" / name_file], re.M):
        valid_sections.add(f"{pref}{n}")
NOT_IN_TEXT = {25: "OQ-020", 48: "OQ-020"}      # позиции спецификации, которых нет в тексте проекта
n_see = 0
for c in comps:
    see = c.get("see")
    if not isinstance(see, list):
        err(f"components.yaml: у {c['id']} нет списка see")
        continue
    if not see:
        issue = NOT_IN_TEXT.get(c.get("pos"))
        if issue:
            warn(f"components.yaml: {c['id']} (поз. {c['pos']}) нигде не упомянут в тексте (известно: {issue})")
        else:
            err(f"components.yaml: у {c['id']} пустой see — укажите раздел исходника")
    for s in see:
        n_see += 1
        if s not in valid_sections:
            err(f"components.yaml: {c['id']}: раздел «{s}» из see не найден в docs/")

# ------------------------------------------------------------------ 6. карта документов
TITLES = {
    "project": "Идея, динамики, усилитель, характеристики, заключение",
    "enclosure": "Конструкция корпуса: размеры, детали, панели, уголки, бруски",
    "acoustics": "Закрытый ящик, демпфирующие маты",
    "power-input": "Сетевой ввод C14 → WAGO → БП",
    "shielding": "Экранирование и заземление",
    "electronics": "Рамка JAB4, индикатор, проводка 24 В и сигналов, цвета проводов",
    "dsp": "SigmaStudio и программирование JAB4",
    "techniques": "Приёмы монтажа",
    "assembly": "Пошаговая сборка (этапы 1–8; 5.1–5.5 вынесены к узлам)",
    "commissioning": "Первый запуск и проверка",
}


def num_key(s):
    return [int(x) for x in s.split(".")]


rows = []
for name, title in TITLES.items():
    nums = sorted({n for n, files in doc_heads.items() if f"{name}.md" in files}, key=num_key)
    rows.append(f"| [{name}.md]({name}.md) | {title} | {', '.join(nums)} |")
rows.append("| [../components.yaml](../components.yaml) | Спецификация и паспорта компонентов (80 позиций + недостающие) | 5 |")
index = "\n".join(rows)
pj = ROOT / "docs/project.md"
txt = doc_text[pj]
m = re.search(r"<!--index-->\n?(.*?)\n?<!--/index-->", txt, re.S)
if not m:
    err("docs/project.md: нет маркеров <!--index--> … <!--/index-->")
elif m.group(1).strip() != index.strip():
    if FIX:
        pj.write_text(txt[:m.start()] + "<!--index-->\n" + index + "\n<!--/index-->" + txt[m.end():], encoding="utf-8")
        print("fix  docs/project.md: карта документов обновлена")
    else:
        err("docs/project.md: карта документов устарела (make sync)")

# ------------------------------------------------------------------ итог
for w in warnings:
    print("WARN ", w)
for e in errors:
    print("ERROR", e)
print(f"\nкомпонентов: {len(ids)}, ссылок see: {n_see}, документов: {len(docs)}, маркеров: {n_markers}; "
      f"ошибок: {len(errors)}, предупреждений: {len(warnings)}")
sys.exit(1 if errors else 0)
