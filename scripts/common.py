"""Общие функции для скриптов репозитория."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def passports():
    """Возвращает {id: (path, data)} для всех паспортов компонентов."""
    result = {}
    for p in sorted((ROOT / "components").rglob("*.yaml")):
        if p.name.startswith("_"):
            continue
        data = load_yaml(p)
        if isinstance(data, dict) and "id" in data:
            result[data["id"]] = (p, data)
    return result


def module_boms():
    """Возвращает [(module, path, data)] для modules/*/bom.yaml."""
    out = []
    for p in sorted((ROOT / "modules").glob("*/bom.yaml")):
        out.append((p.parent.name, p, load_yaml(p)))
    return out
