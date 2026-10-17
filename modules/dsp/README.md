# Модуль dsp — SigmaStudio и программирование JAB4

Источник: v8.0 §8. Параметры (источник истины): [`dsp-params.yaml`](dsp-params.yaml). Программирование: [`programming.md`](programming.md). Проект SigmaStudio: `sigmastudio/` (Git LFS).

## Структура схемы (2.1)
1. **Вход и громкость:** Input (0 — L, 1 — R) → External Volume (Single/Gain, Type 2) с управлением от Aux ADC (ADC0, потенциометр).
2. **Твитеры (L и R):** HPF Butterworth 24 дБ/окт на 2500 Гц → Gain −8.0 дБ → Peak Limiter (−3 дБ, release 50 мс) → DAC0 (L), DAC1 (R).
3. **Бас (SUB):** 2-Ch Merger (моно) → Subsonic HPF 60 Гц 24 дБ/окт → PEQ 95 Гц −4 дБ Q 1.2 → Low Shelf 300 Гц +3 дБ Q 0.7 → LPF Butterworth 24 дБ/окт 2500 Гц → Peak Limiter (−3 дБ, release 150 мс) → DAC2; DAC3 — тот же сигнал через Invert (мостовой выход).

## Обоснование
| Блок | Зачем |
|---|---|
| HPF твитеров 2500 Гц | защита твитеров от НЧ |
| Gain −8 дБ | компенсация чувствительности (95.8 − 88 = 7.8 дБ) |
| Subsonic 60 Гц | защита вуфера от перегрузки ниже резонанса |
| PEQ 95 Гц −4 дБ Q1.2 | подавление горба от Qtc≈1.05 |
| Low Shelf 300 Гц +3 дБ | компенсация баффл-степа |
| LPF вуфера 2500 Гц | подавление резонансов выше частоты раздела |
| Лимитер твитеров −3 дБ / 50 мс | быстрое восстановление |
| Лимитер баса −3 дБ / 150 мс | медленное восстановление |
| Invert на DAC3 | инверсия фазы для мостового усилителя |

## Замечания
- OQ-003: 24 дБ/окт на «General 2nd Order Filter» требует каскада двух блоков 2-го порядка.
- Требуется SigmaStudio 4.6 или 4.7, программатор [`CMP-icp3-programmer`](../../components/electronics/icp3-programmer.yaml).
- Любое изменение значений — сначала в `dsp-params.yaml`, затем в проекте SigmaStudio, затем в `params/acoustics.yaml` (если меняется частота раздела).
