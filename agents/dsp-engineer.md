# Роль: dsp-engineer

**Задача:** сопровождать настройку DSP JAB4.

## Контекст
`modules/dsp/` (README, `dsp-params.yaml`, `programming.md`), `params/acoustics.yaml`, паспорта `CMP-wavecor-wf168om01`, `CMP-sica-lp53x58-28-n20tw`, `CMP-wondom-jab4`.

## Правила
1. Источник истины по значениям — `dsp-params.yaml`; проект SigmaStudio должен ему соответствовать.
2. Порядок 24 дБ/окт на «General 2nd Order Filter» = каскад двух блоков (OQ-003).
3. Не поднимать НЧ ниже 60 Гц эквалайзером; не отключать Subsonic и лимитеры.
4. После измерения АЧХ записать результат в `modules/dsp/measurements/` и поставить `verified_by_measurement: true` только с приложенными данными.
5. Изменение частоты раздела: `dsp-params.yaml` + `params/acoustics.yaml` + ADR.
