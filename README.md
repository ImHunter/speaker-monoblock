# speaker-monoblock

Активная колонка-моноблок: Wavecor WF168OM01 (6.5″) + 2 × Sica LP53x58.28 (1″), усилитель Wondom JAB4 (TPA3221 + ADAU1701), закрытый ящик 5.9 л, экранированный отсек электроники, питание через модуль C14.

Текст проекта v8.0 (`archive/проект-колонки-v8.0.md`) разнесён по документам **дословно**: нумерация разделов исходника сохранена, перекрёстные ссылки («см. 4.12», «раздел 8.2») работают. Карта «раздел исходника → файл» — в конце [docs/project.md](docs/project.md).

## Структура
```
AGENTS.md            правила для агентов
params.yaml          числа, на которые ссылается текст (маркеры <!--p:…--> в docs)
components.yaml      спецификация §5 (80 строк дословно) + 16 недостающих материалов + паспорта (see, params, constraints)
docs/
  project.md         идея, динамики, усилитель, характеристики, заключение, карта разделов
  enclosure.md       КОНСТРУКЦИЯ КОРПУСА: размеры, детали, панели, перегородка, уголки, бруски
                     (в начале — «Рабочая зона»: проверка размерной цепи и пробелы)
  acoustics.md       закрытый ящик, демпфирующие маты
  dsp.md             SigmaStudio, схема, программирование
  techniques.md      приёмы монтажа (раздел 10)
  power-input.md     сетевой ввод C14 → WAGO → БП
  shielding.md       экранирование и заземление
  electronics.md     рамка JAB4, индикатор, проводка 24 В и сигналов, цвета
  assembly.md        сборка по этапам 1–8
  commissioning.md   первый запуск
  open-questions.md  противоречия и пробелы исходника (OQ-001…020)
  glossary.md        термины
scripts/             validate.py, audit.py, gen.py, q.py (быстрые запросы)
schema/              JSON Schema для components.yaml (VS Code и validate.py)
.vscode/ .editorconfig   настройки редактора, задачи (Run Task), рекомендуемые расширения
datasheets/  dsp/sigmastudio/   тяжёлые файлы (Git LFS)
archive/             исходный монолит (не править)
```

## Команды
```bash
make validate   # ссылки, ID, числа в тексте против params.yaml, карта разделов
make sync       # исправить числа в тексте по params.yaml, обновить карту разделов
make audit      # каждая строка исходника есть в репозитории
make bom        # build/bom.csv
make cutlist    # build/cutlist.csv (из таблицы 4.1 в docs/enclosure.md)
make check      # validate + audit
python3 scripts/q.py section 4.4.9   # найти раздел / comp 12 / param … / oq OQ-004 / find текст
```
Нужен Python 3.10+ и `pip install pyyaml jsonschema` (jsonschema необязателен). Без make (Windows): `python scripts/…` или VS Code → Terminal → Run Task.

## Для агентов и VS Code
Правила — в [AGENTS.md](AGENTS.md) (`CLAUDE.md` и `.github/copilot-instructions.md` лишь ссылаются на него), формат обычный Markdown/YAML, без привязки к конкретному агенту. Папка открывается в VS Code как есть: рекомендованные расширения предложатся автоматически, `components.yaml` проверяется схемой, ссылки между документами — встроенной проверкой Markdown.

## Как это работает
- **Текст — источник истины.** Разделы переносятся без пересказа; добавленное при реорганизации помечено «Добавлено при реорганизации» (рабочая зона в `enclosure.md`, `open-questions.md`, `glossary.md`, указатели).
- **Числа с маркерами.** Ключевые размеры, координаты и параметры DSP в тексте стоят как `178<!--p:panels.front.woofer_x-->`. `make validate` сравнивает их с `params.yaml`.
- **Полнота.** `make audit` проверяет, что ни одна строка исходника не пропала: прозу построчно, спецификацию по ячейкам, ссылки по URL.
