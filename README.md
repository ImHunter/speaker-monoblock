# speaker-monoblock

Активная колонка-моноблок: Wavecor WF168OM01 (6.5″) + 2 × Sica LP53x58.28 (1″), усилитель Wondom JAB4 (TPA3221 + ADAU1701), закрытый ящик ~5.9 л, экранированный отсек электроники, питание через модуль C14.

## Структура
```
AGENTS.md            правила для агентов
params.yaml          все числа (размеры, координаты, моменты, параметры DSP)
components.yaml      компоненты, паспорта и спецификация
docs/
  project.md         идея, решения, карта документов
  enclosure.md       конструкция корпуса
  acoustics.md       ЗЯ и демпфирование
  dsp.md             SigmaStudio и программирование
  power-input.md     сетевой ввод
  shielding.md       экранирование и заземление
  electronics.md     усилитель, проводка, индикатор
  techniques.md      приёмы монтажа T-001…T-008
  assembly-order.md  порядок сборки
  commissioning.md   первый запуск
  open-questions.md  противоречия и нерешённое
datasheets/ dsp/sigmastudio/   тяжёлые файлы (Git LFS)
archive/             исходный монолит v8.0
```

## Команды
```bash
make validate   # ссылки, ID, числа в тексте против params.yaml
make sync       # исправить числа в тексте по params.yaml
make bom        # build/bom.csv
make cutlist    # build/cutlist.csv
```
Нужен Python 3.10+ и `pip install pyyaml`.

## Как это работает
Число меняется один раз в `params.yaml`. В тексте оно стоит с невидимым маркером: `178<!--p:panels.front.woofer_x-->`. `make validate` покажет места, где текст разошёлся с данными; `make sync` исправит их.
