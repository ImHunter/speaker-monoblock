PY ?= python3

.PHONY: all validate bom cutlist clean

all: validate bom cutlist

validate:
	$(PY) scripts/validate.py

bom:
	$(PY) scripts/gen_bom.py

cutlist:
	$(PY) scripts/gen_cutlist.py

clean:
	rm -f procurement/*.generated.csv
