# Размерная модель корпуса

> **Добавлено при реорганизации** (2026-10-20). Правила вычисления размеров: что задаётся, что считается. Не заменяет §4.1–4.10 — там текст v8.0; здесь модель и расчёт для двух версий. Базовые числа — [params.yaml](../params.yaml) (`dimensions`), пересчёт — [scripts/dims.py](../scripts/dims.py).

## Схема

- Боковины стоят на полу и на 10 мм ниже дна — это ножки.
- Дно и перегородка — между боковинами.
- Верх — накладной, лежит на боковинах.
- Передняя и задняя панели — накладные, на торцах основы; между панелью и основой — прокладка.
- Клей 0.5 — слой в полости сверху и снизу (малоразборная версия); в v8.0 клея нет.

## Базовые размеры

Задаются, не вычисляются. Меняются только здесь — вместе с `params.yaml`.

| Параметр | v8.0 | v9 | Смысл |
|---|---|---|---|
| `H_total` | 236<!--p:dimensions.v8.h_total--> | 240<!--p:dimensions.v9.h_total--> | высота общая, с ножками |
| `W_total` | 356<!--p:dimensions.v8.w_total--> | 360<!--p:dimensions.v9.w_total--> | ширина общая |
| `H_base` | 10<!--p:dimensions.v8.h_base--> | 10<!--p:dimensions.v9.h_base--> | ножки: боковина ниже дна |
| `W_mdf` | 16<!--p:dimensions.v8.w_mdf--> | 16<!--p:dimensions.v9.w_mdf--> | толщина МДФ |
| `W_glue` | 0<!--p:dimensions.v8.w_glue--> | 0.5<!--p:dimensions.v9.w_glue--> | клей в полости, сверху и снизу |
| `W_back_abs` | 5<!--p:dimensions.v8.w_back_abs--> | 5<!--p:dimensions.v9.w_back_abs--> | задняя панель, ABS |
| `W_ribbon` | 0.5<!--p:dimensions.v8.w_ribbon--> | 1.5<!--p:dimensions.v9.w_ribbon--> | прокладка, на сторону |
| `W_overlay` | 3<!--p:dimensions.v8.w_overlay--> | 0<!--p:dimensions.v9.w_overlay--> | накладка переда; 0 — без неё |
| `D_acoustic` | 110<!--p:dimensions.v8.d_acoustic--> | 110<!--p:dimensions.v9.d_acoustic--> | акустика: от торца основы до перегородки |
| `D_electric` | 58<!--p:dimensions.v8.d_electric--> | 60<!--p:dimensions.v9.d_electric--> | электроника: от торца основы до перегородки |
| `woofer_hole` | 143<!--p:dimensions.v8.woofer_hole--> | 144<!--p:dimensions.v9.woofer_hole--> | посадочное НЧ |
| `tweeter_hole` | 48.4<!--p:dimensions.v8.tweeter_hole--> | 50<!--p:dimensions.v9.tweeter_hole--> | посадочное ВЧ |
| `flange_w` | 58<!--p:dimensions.v8.flange_w--> | 58<!--p:dimensions.v9.flange_w--> | фланец твитера, ширина |
| `flange_h` | 53<!--p:dimensions.v8.flange_h--> | 53<!--p:dimensions.v9.flange_h--> | фланец твитера, высота |
| `flange_t` | 3<!--p:dimensions.v8.flange_t--> | 3<!--p:dimensions.v9.flange_t--> | толщина фланца |
| `rebate_gap` | 0.2<!--p:dimensions.v8.rebate_gap--> | 0.2<!--p:dimensions.v9.rebate_gap--> | зазор цековки на сторону |
| `tweeter_edge` | 50<!--p:dimensions.v8.tweeter_edge--> | 50<!--p:dimensions.v9.tweeter_edge--> | от края до центра твитера |
| `woofer_shift_up` | 5<!--p:dimensions.v8.woofer_shift_up--> | 5<!--p:dimensions.v9.woofer_shift_up--> | сдвиг вуфера вверх от центра |

## Формулы

```text
W_inner  = W_total − 2·W_mdf
H_inner  = H_total − 2·W_mdf − 2·W_glue − H_base
D_side   = D_acoustic + W_mdf + D_electric
D_total  = W_overlay + W_mdf + W_ribbon + D_acoustic + W_mdf + D_electric + W_ribbon + W_back_abs
H_side   = H_total − W_mdf − W_glue
H_front  = H_total − H_base
W_front  = W_total
W_bottom = W_inner − 2·W_glue
D_bottom = D_side
H_baffle = H_inner − 2·W_glue
W_baffle = W_inner − 2·W_glue
W_top    = W_total;  D_top = D_side
W_rear   = W_total;  H_rear = H_front
V_geom   = W_inner · H_inner · (D_acoustic + W_ribbon) / 10^6
V_eff    = V_geom − V_bars − V_driver − V_wires
Qtc      = Qts · sqrt(1 + Vas / V_eff)
Fc       = Fs  · sqrt(1 + Vas / V_eff)
d_rebate = flange_t + rebate_gap
```

## Производные

| Величина | v8.0 | v9 |
|---|---|---|
| `W_inner` | 324 | 328 |
| `H_inner` | 194 | 197 |
| `D_side` | 184 | 186 |
| `D_total` | 209 | 210 |
| `H_side` | 220 | 223.5 |
| `H_front` | 226 | 230 |
| `W_bottom` | 324 | 327 |
| `D_bottom` | 184 | 186 |
| `H_baffle` | 194 | 196 |
| `W_baffle` | 324 | 327 |
| `V_geom`, л | 6.95 | 7.20 |
| `V_eff`, л | 6.00 | 6.25 |
| `Qtc` | 1.09 | 1.08 |
| `Fc`, Гц | 94.9 | 93.2 |

## Детали

| Деталь | v8.0 | v9 |
|---|---|---|
| Боковина | 184 × 220 | 186 × 223.5 |
| Низ | 324 × 184 | 327 × 186 |
| Перегородка | 324 × 194 | 327 × 196 |
| Передняя | 356 × 226 | 360 × 230 |
| Верх | 356 × 184 | 360 × 186 |
| Задняя | 356 × 226 × 5 | 360 × 230 × 5 |
| Накладка | 356 × 226 × 3 | нет (опция 3) |

## Проверки

- `D_side = D_bottom` — боковина и низ одной глубины.
- `D_total = W_overlay + W_mdf + 2·W_ribbon + D_side + W_back_abs`.
- `H_side + W_mdf + W_glue = H_total`.
- `H_front = H_total − H_base`.
- `W_bottom = W_baffle`.
- `H_baffle = H_inner − 2·W_glue`.
- `d_rebate = flange_t + rebate_gap`.
- `W_top = W_rear = W_total`; `D_top = D_side`; `H_rear = H_front`.

## Объём и Qtc

`V_geom` считается по внутренним ширине и высоте и глубине `D_acoustic + W_ribbon` (полость доходит до внутренней плоскости передней панели). Вычеты — 0.30 л бруски, 0.50 л корзина и магнит, 0.15 л провода — из `params.yaml` (`global`).

- v8.0: 6.95 л геометрических, 6.00 л эффективных, Qtc 1.09, Fc 94.9 Гц.
- v9: 7.20 л, 6.25 л, Qtc 1.08, Fc 93.2 Гц.

Текст v8.0 заявляет 6.87 л и Qtc 1.05; расчёт при 322 × 194 × 110 даёт 1.10 — это OQ-006. Модель подтверждает расчёт, а не заявленное 1.05.

## Раскладка динамиков

Правила:

- X вуфера — середина панели: `W_total / 2`.
- Твитеры симметричны: `tweeter_edge` от каждого края, то есть `tweeter_edge` и `W_total − tweeter_edge`.
- Y отсчитывается от нижнего края передней панели: вуфер — `H_front / 2 + woofer_shift_up`, твитеры — `H_front / 2`.

| | v8.0 | v9 |
|---|---|---|
| Вуфер X | 178 | 180 |
| Вуфер Y | 118 | 120 |
| Твитер L X | 50 | 50 |
| Твитер R X | 306 | 310 |
| Твитер Y | 113 | 115 |
| Цековка | нет (накладка) | 3.2 |

## Накладка и цековка

- **v8.0:** накладка **3 мм**, не 4. Глубина сходится: `3 + 16 + 0.5 + 110 + 16 + 58 + 0.5 + 5 = 209`. В тексте 4 мм и нет прокладки — тоже 209, поэтому ошибка толщины была незаметна.
- **v9:** накладки нет (`W_overlay = 0`), общая глубина 210. Вместо неё — цековка под твитер: глубина **3.2** (фланец 3 + зазор 0.2), план **58.2 × 53.2**, отверстие 50, под цековкой остаётся 12.8 мм МДФ. Вуфер без цековки.
- Если накладку 3 мм всё же оставить, общая глубина v9 станет 213; цековка тогда не нужна.
- Без накладки наружная плоскость передней панели становится лицевой: её надо ламинировать или красить. Текст 4.6 («наружная сторона без ламината под накладку») в этом случае меняется.

## Версии

- **v8.0** — текущий текст в `docs/`. Модель даёт 324 / 184 / 220 вместо 322 / 182 / 219 и верх 356 × 184 вместо 356 × 182; это OQ-004. Перенос в `docs/`, `params.yaml` и раскрой — отдельным шагом, после решения по версии.
- **v9** — принята к разработке 2026-10-20: малоразборная, клей 0.5, 360 × 240, без накладки; корпус неразборный (клей, евровинты, шканты), снимаются только передняя и задняя стенки. Конструкция — [enclosure-v9.md](enclosure-v9.md); §4.8 и §6 v8.0 требуют отдельной ревизии.

## Как менять

1. Правь базовые числа в `params.yaml` → `dimensions.<версия>`.
2. Пересчитай: `python scripts/dims.py` (Windows: `.venv\Scripts\python`).
3. Обнови таблицы «Производные» и «Детали» по выводу.
4. `python scripts/validate.py` и `python scripts/audit.py`.
5. Если меняется текущая версия — обнови `docs/enclosure.md`, маркеры `<!--p:…-->`, раскрой и [open-questions.md](open-questions.md).
