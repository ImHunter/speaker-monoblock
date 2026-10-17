# speaker-monoblock

Активная колонка-моноблок: 1 × Wavecor WF168OM01 (6.5″) + 2 × Sica LP53x58.28 (1″), усилитель Wondom JAB4 (TPA3221 + ADAU1701), закрытый ящик ~5.9 л, локальное экранирование отсека электроники, питание 220–250 В через модуль C14.

Репозиторий — это **проектная документация как код**: числа лежат в YAML, пояснения — в Markdown, решения — в ADR, паспорта компонентов — в `components/`. Документ-монолит `проект колонки.md` (версия 8.0, 22.09.2026) разнесён по этим файлам, исходник сохранён в `archive/`.

## Как читать (человеку)

1. [`docs/concept.md`](docs/concept.md) — идея и принципиальные решения.
2. [`docs/decisions/`](docs/decisions/) — почему выбрано именно так.
3. [`modules/`](modules/) — подсистемы: конструкция, схема, сборка, проверки.
4. [`assembly/`](assembly/) — порядок сборки по этапам.
5. [`commissioning/`](commissioning/) — первый запуск и приёмка.
6. [`docs/open-questions.md`](docs/open-questions.md) — что ещё не решено или противоречиво.

## Как работать (агенту)

Читай [`AGENTS.md`](AGENTS.md). Коротко: числа берём только из `params/` и `components/`, модули со статусом `frozen` не меняем без ADR, перед коммитом запускаем `make validate`.

## Команды

```bash
make validate   # схемы, ссылки, битые ID
make bom        # procurement/bom.generated.csv
make cutlist    # procurement/cutlist.generated.csv
make all
```

Нужен Python 3.10+ и `pip install pyyaml jsonschema`.

## Статус

См. [`project.yaml`](project.yaml). Версии проекта — git-теги (`v8.0`, `v8.1`…), история изменений — [`CHANGELOG.md`](CHANGELOG.md).
