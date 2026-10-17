PY ?= python3

.PHONY: all validate sync bom cutlist

all: validate bom cutlist

validate:        # проверка ссылок, ID и чисел в тексте
	$(PY) scripts/validate.py

sync:            # исправить числа в docs/*.md по params.yaml
	$(PY) scripts/validate.py --fix

bom:             # build/bom.csv из components.yaml
	$(PY) scripts/gen.py bom

cutlist:         # build/cutlist.csv из params.yaml
	$(PY) scripts/gen.py cutlist
