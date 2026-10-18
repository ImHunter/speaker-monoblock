#!/usr/bin/env python3
"""Аудит полноты: каждая строка исходника (archive/проект-колонки-v8.0.md) должна быть в репозитории.

Строки таблицы §5 сверяются по ячейкам с components.yaml, остальные — построчно с docs/*.md.
Нормализация: без разметки (**, `, ссылок, маркеров <!--p:-->), все виды дефисов и тире равны.
Дополнительно: все URL исходника присутствуют; в docs перечисляются добавленные строки (не из исходника).
Код возврата 1, если что-то из исходника не найдено.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def norm(s):
    s = re.sub(r"<!--.*?-->", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("*", "").replace("`", "")
    s = re.sub(r"[‑–—−]", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


src = (ROOT / "archive/проект-колонки-v8.0.md").read_text(encoding="utf-8").replace("\r", "").split("\n")

corpus = {}
for p in sorted((ROOT / "docs").glob("*.md")):
    corpus[p.name] = p.read_text(encoding="utf-8").split("\n")
doc_set = {norm(l) for lines in corpus.values() for l in lines}
doc_blob = "\n".join(doc_set)
comp_text = (ROOT / "components.yaml").read_text(encoding="utf-8")
comp_blob = norm(comp_text.replace("\n", " "))
all_text = "\n".join("\n".join(v) for v in corpus.values()) + "\n" + comp_text

# границы таблицы §5: строки, начинающиеся с "| <число> |"
missing, checked, bom_rows = [], 0, 0
for i, line in enumerate(src, 1):
    s = line.strip()
    if not s or re.fullmatch(r"-{3,}", s) or re.fullmatch(r"\|[\s:|-]+\|", s):
        continue
    is_bom = bool(re.match(r"\| \d+ \|", s)) and 459 <= i <= 538
    if is_bom:
        bom_rows += 1
        for cell in [c.strip() for c in s.strip("|").split("|")]:
            if cell and norm(cell) not in comp_blob:
                missing.append((i, f"[ячейка спецификации] {cell}"))
        continue
    checked += 1
    n = norm(s)
    if n and n not in doc_set and n not in doc_blob and n not in comp_blob:
        missing.append((i, s))

# заголовок таблицы §5 и её шапка проверяются как обычные строки (они в components.yaml комментарием)
urls = set(re.findall(r"https?://[^\s)\]>]+", "\n".join(src)))
lost_urls = sorted(u for u in urls if u not in all_text)

# добавленные строки (в docs, но не из исходника)
src_set = {norm(l) for l in src}
added = {}
for name, lines in corpus.items():
    cnt = sum(1 for l in lines if norm(l) and norm(l) not in src_set and not re.fullmatch(r"-{3,}|\|[\s:|-]+\|", l.strip()))
    added[name] = cnt

print(f"Строк исходника проверено: {checked} (+ {bom_rows} строк спецификации по ячейкам)")
print(f"Не найдено: {len(missing)}; URL потеряно: {len(lost_urls)} из {len(urls)}")
for i, s in missing:
    print(f"  строка {i}: {s[:140]}")
for u in lost_urls:
    print("  URL:", u)
print("\nДобавлено при реорганизации (строк, не из исходника) по файлам:")
for name, c in sorted(added.items()):
    print(f"  {name:20} {c}")
sys.exit(1 if (missing or lost_urls) else 0)
