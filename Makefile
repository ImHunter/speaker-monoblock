PY ?= python3

.PHONY: all check validate sync audit bom cutlist dims

all: validate audit bom cutlist

check: validate audit   # перед коммитом

validate:        # ссылки, ID, числа в тексте против params.yaml, карта разделов
	$(PY) scripts/validate.py

sync:            # исправить числа в docs/*.md по params.yaml и обновить карту разделов
	$(PY) scripts/validate.py --fix

audit:           # полнота: каждая строка исходника v8.0 есть в репозитории
	$(PY) scripts/audit.py

bom:             # build/bom.csv из components.yaml
	$(PY) scripts/gen.py bom

cutlist:         # build/cutlist.csv из таблицы 4.1 в docs/enclosure.md
	$(PY) scripts/gen.py cutlist

dims:            # пересчёт размерной модели из params.yaml
	$(PY) scripts/dims.py
