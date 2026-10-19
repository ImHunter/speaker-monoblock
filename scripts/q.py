#!/usr/bin/env python3
"""Быстрые запросы к проекту без чтения больших файлов целиком.

  q.py section 4.4.9        текст раздела исходника по номеру (с указанием файла и строк)
  q.py section "Этап 5"     этап сборки / шаг запуска («Шаг 2»)
  q.py comp 12              компонент по номеру позиции §5, по ID или по части названия
  q.py param panels.front   значение параметра (или группы) и места в тексте, где число используется
  q.py oq OQ-004            открытый вопрос
  q.py find "текст"         поиск по docs/, components.yaml, params.yaml (без учёта регистра)

Работает одинаково в Linux, macOS и Windows (python scripts/q.py ...).
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = sorted((ROOT / "docs").glob("*.md"))


def rel(p):
    return p.relative_to(ROOT).as_posix()


def cmd_section(query):
    q = query.strip().rstrip(".")
    hits = []
    for p in DOCS:
        lines = p.read_text(encoding="utf-8").split("\n")
        in_code = False
        for i, line in enumerate(lines):
            if line.startswith("```"):
                in_code = not in_code
            m = None if in_code else re.match(r"(#{1,6}) (.*)", line)
            if not m:
                continue
            level, title = len(m.group(1)), m.group(2).strip()
            num = re.match(r"(\d+(?:\.\d+)*)\.?(?:\s|$)", title)
            if (num and num.group(1) == q) or title.lower().startswith(q.lower()):
                end = len(lines)
                in_code2 = False
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("```"):
                        in_code2 = not in_code2
                    mm = None if in_code2 else re.match(r"(#{1,6}) ", lines[j])
                    if mm and len(mm.group(1)) <= level:
                        end = j
                        break
                hits.append((p, i + 1, end, lines[i:end]))
    if not hits:
        sys.exit(f"раздел «{query}» не найден (номера как в заголовках docs/*.md, например 4.4.9 или «Этап 5»)")
    for p, a, b, body in hits:
        print(f"=== {rel(p)}, строки {a}-{b}")
        print("\n".join(body).rstrip())
        print()


def load_components():
    return yaml.safe_load((ROOT / "components.yaml").read_text(encoding="utf-8"))["components"]


def cmd_comp(query):
    comps = load_components()
    q = query.strip().lower()
    if q.isdigit():
        found = [c for c in comps if c.get("pos") == int(q)]
    else:
        found = [c for c in comps if q in c["id"].lower() or q in c["name"].lower()]
    if not found:
        sys.exit(f"компонент «{query}» не найден")
    for c in found:
        print(yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=110).rstrip())
        print()


def cmd_param(path):
    params = yaml.safe_load((ROOT / "params.yaml").read_text(encoding="utf-8"))
    node = params
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            sys.exit(f"параметр «{path}» не найден в params.yaml")
        node = node[part]
    print(yaml.safe_dump({path: node}, allow_unicode=True, sort_keys=False).rstrip())
    pat = re.compile(r"<!--p:" + re.escape(path) + r"(?:\.[\w.]+)?-->")
    print("\nИспользуется в тексте:")
    n = 0
    for p in DOCS:
        for i, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            if pat.search(line):
                n += 1
                print(f"  {rel(p)}:{i}: {re.sub(r'<!--.*?-->', '', line).strip()[:110]}")
    if not n:
        print("  (нигде)")


def cmd_oq(query):
    text = (ROOT / "docs/open-questions.md").read_text(encoding="utf-8")
    rows = [l for l in text.split("\n") if l.startswith("| OQ-") and l.split("|")[1].strip() == query.upper()]
    if not rows:
        sys.exit(f"вопрос «{query}» не найден")
    print(rows[0])


def cmd_find(needle):
    n = needle.lower()
    files = DOCS + [ROOT / "components.yaml", ROOT / "params.yaml"]
    count = 0
    for p in files:
        for i, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            if n in line.lower():
                count += 1
                print(f"{rel(p)}:{i}: {re.sub(r'<!--.*?-->', '', line).strip()[:150]}")
    if not count:
        sys.exit("ничего не найдено")


COMMANDS = {"section": cmd_section, "comp": cmd_comp, "param": cmd_param, "oq": cmd_oq, "find": cmd_find}

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in COMMANDS:
        sys.exit(__doc__)
    COMMANDS[sys.argv[1]](" ".join(sys.argv[2:]))
