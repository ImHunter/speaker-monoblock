# Агентская работа

## Роли

Зоны — в [roles.yaml](roles.yaml). Один файл — один владелец. Реестры (`params.yaml`, `components.yaml`, `open-questions.md`, `CHANGELOG.md`, `project.md`) правит только `integrator`.

## Как подключить роль

1. Задача в [tasks.md](tasks.md): ID, роль, разделы, вход и выход.
2. Запуск — субагент с промптом:

   > Ты — роль enclosure. Прочитай `agents/enclosure.md`, `agents/roles.yaml`, `agents/tasks.md`; возьми T-NNN. Работай только в своей зоне, реестры не трогай. Верни отчёт по форме из роли.

   В DSH это `subagent` из основной сессии; основная сессия — `integrator`.
3. Роль работает, гоняет `validate` + `audit`, возвращает отчёт.
4. Интегратор: проверяет диф, правит реестры, мержит, закрывает задачу.

В отдельной сессии достаточно сказать: «работай по `agents/enclosure.md`, задача T-NNN» — контракт лежит в репозитории, а не в переписке.

## Ограничения

- Субагенты видят общую файловую систему: параллельно — только разные файлы.
- Роль не запускает `sync` и `validate --fix` (переписывают все `docs/`), не трогает `archive/` и `build/`.
- Гейт после merge перезапускает интегратор.

## Зависимости

```bash
python -m venv .venv
.venv\Scripts\pip install pyyaml jsonschema   # Windows
# .venv/bin/pip install pyyaml jsonschema     # Linux/macOS
```

Если `python scripts/validate.py` падает на `import yaml` — используй `.venv\Scripts\python`.
