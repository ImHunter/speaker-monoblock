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
| `H_total` | 236<!--p:dimensions.v8.h_total--> | 200<!--p:dimensions.v9.h_total--> | высота общая, с ножками |
| `W_total` | 356<!--p:dimensions.v8.w_total--> | 392<!--p:dimensions.v9.w_total--> | ширина общая |
| `H_base` | 10<!--p:dimensions.v8.h_base--> | 10<!--p:dimensions.v9.h_base--> | ножки: боковина ниже дна |
| `W_mdf` | 16<!--p:dimensions.v8.w_mdf--> | 16<!--p:dimensions.v9.w_mdf--> | толщина МДФ |
| `W_glue` | 0<!--p:dimensions.v8.w_glue--> | 0.5<!--p:dimensions.v9.w_glue--> | клей в полости, сверху и снизу |
| `W_back_abs` | 5<!--p:dimensions.v8.w_back_abs--> | 5<!--p:dimensions.v9.w_back_abs--> | задняя панель, ABS |
| `W_ribbon` | 0.5<!--p:dimensions.v8.w_ribbon--> | 1.5<!--p:dimensions.v9.w_ribbon--> | прокладка, на сторону |
| `W_overlay` | 3<!--p:dimensions.v8.w_overlay--> | 0<!--p:dimensions.v9.w_overlay--> | накладка переда; 0 — без неё |
| `D_acoustic` | 110<!--p:dimensions.v8.d_acoustic--> | 120<!--p:dimensions.v9.d_acoustic--> | акустика: от торца основы до перегородки |
| `D_electric` | 58<!--p:dimensions.v8.d_electric--> | 60<!--p:dimensions.v9.d_electric--> | электроника: от торца основы до перегородки |
| `woofer_hole` | 143<!--p:dimensions.v8.woofer_hole--> | 144<!--p:dimensions.v9.woofer_hole--> | посадочное НЧ |
| `tweeter_hole` | 48.4<!--p:dimensions.v8.tweeter_hole--> | 50<!--p:dimensions.v9.tweeter_hole--> | посадочное ВЧ |
| `flange_w` | 58<!--p:dimensions.v8.flange_w--> | 58<!--p:dimensions.v9.flange_w--> | фланец твитера, ширина |
| `flange_h` | 53<!--p:dimensions.v8.flange_h--> | 53<!--p:dimensions.v9.flange_h--> | фланец твитера, высота |
| `flange_t` | 3<!--p:dimensions.v8.flange_t--> | 3<!--p:dimensions.v9.flange_t--> | толщина фланца |
| `rebate_gap` | 0.2<!--p:dimensions.v8.rebate_gap--> | 0.2<!--p:dimensions.v9.rebate_gap--> | зазор цековки на сторону |
| `DX_Sica` | 128<!--p:dimensions.v8.dx_sica--> | 141<!--p:dimensions.v9.dx_sica--> | смещение центра твитера от центра панели |
| `DY_Wavecor` | 5<!--p:dimensions.v8.dy_wavecor--> | 5<!--p:dimensions.v9.dy_wavecor--> | сдвиг вуфера вверх от середины |
| `DY_c14` | 81.5<!--p:dimensions.v8.dy_c14--> | 80<!--p:dimensions.v9.dy_c14--> | низ окна C14 от пола |
| `DZ_c14` | — | 10<!--p:dimensions.v9.dz_c14--> | от перегородки до окна C14 |
| `DD_divider` | — | 10<!--p:dimensions.v9.dd_divider--> | разделитель электроники: не доходит до торца на |

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

tweeter_L = W_total/2 − DX_Sica
tweeter_R = W_total/2 + DX_Sica
woofer_X  = W_total/2
woofer_Y  = H_front/2 + DY_Wavecor
tweeter_Y = H_front/2

baffle_rear      = W_overlay + W_mdf + W_ribbon + D_acoustic + W_mdf
C14_window_front = baffle_rear + DZ_c14
C14_flange_front = C14_window_front − 5   (фланец 40 шире окна 30)
C14_flange_bottom = DY_c14 − 1.5          (фланец 65 выше окна 62)
C14_window_top    = DY_c14 + 62
C14_flange_top    = DY_c14 − 1.5 + 65
C14_window_to_side = H_side − (DY_c14 + 62)

divider_len = D_electric − DD_divider
divider_h   = H_baffle
divider_x   = W_total/2
```

## Производные

| Величина | v8.0 | v9 |
|---|---|---|
| `W_inner` | 324 | 360 |
| `H_inner` | 194 | 157 |
| `D_side` | 184 | 196 |
| `D_total` | 209 | 220 |
| `H_side` | 220 | 183.5 |
| `H_front` | 226 | 190 |
| `W_bottom` | 324 | 359 |
| `D_bottom` | 184 | 196 |
| `H_baffle` | 194 | 156 |
| `W_baffle` | 324 | 359 |
| `V_geom`, л | 6.95 | 6.87 |
| `V_eff`, л | 6.00 | 5.92 |
| `Qtc` | 1.09 | 1.10 |
| `Fc`, Гц | 94.9 | 95.4 |
| `divider_len` | — | 50 |
| `divider_h` | — | 156 |
| `divider_x` | — | 196 |

## Детали

| Деталь | v8.0 | v9 |
|---|---|---|
| Боковина | 184 × 220 | 196 × 183.5 |
| Низ | 324 × 184 | 359 × 196 |
| Перегородка | 324 × 194 | 359 × 156 |
| Передняя | 356 × 226 | 392 × 190 |
| Верх | 356 × 184 | 392 × 196 |
| Задняя | 356 × 226 × 5 | 392 × 190 × 5 |
| Разделитель электроники | — | 50 × 156 |
| Накладка | 356 × 226 × 3 | нет |

- Передняя панель: R8 на боковые торцы (радиус 8<!--p:panels.front.edge_radius-->), 4.6; скругление — до покрытия.

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
- v9: 6.87 л, 5.92 л, Qtc 1.10, Fc 95.4 Гц.

Текст v8.0 заявляет 6.87 л и Qtc 1.05; расчёт при 322 × 194 × 110 даёт 1.10 — это OQ-006. Модель подтверждает расчёт, а не заявленное 1.05. Для v9 принято: 5.92 / 1.10 / 95.4; PEQ 95 Гц −0.8 дБ, Q 1.1; OQ-006 закрыт.

## Раскладка динамиков

Правила:

- X вуфера — середина панели: `W_total / 2`.
- Твитеры — на середине панели по Y и симметрично по X: `W_total/2 ± DX_Sica`.
- Y вуфера — `H_front/2 + DY_Wavecor`; твитеров — `H_front/2`.

| | v8.0 | v9 |
|---|---|---|
| Вуфер X | 178 | 196 |
| Вуфер Y | 118 | 100 |
| Твитер L X | 50 | 55 |
| Твитер R X | 306 | 337 |
| Твитер Y | 113 | 95 |
| Цековка | нет (накладка) | 3.2 |

## C14

- `DY_c14` — **низ окна** от пола (80); `DZ_c14` — от перегородки до окна (10).
- Окно 30 × 62; фланец 40 × 65; глубина 50 в боковину (55 с клеммами) — паспорт [components/CMP-dl-1dz2kr.md](../components/CMP-dl-1dz2kr.md).
- Цепь Z: перегородка 153.5 → окно 163.5…193.5 → кромка отсека 213.5 (20) → панель 215; фланец 158.5…198.5; до панели 16.5.
- Цепь Y: низ фланца 78.5; низ окна **80**; верх окна **142**; верх фланца 143.5; верх боковины 183.5; от верха окна до верха боковины **41.5**, от верха фланца — 40.

## Разделитель электроники

- МДФ 16; длина 50, высота 156, толщина 16; X 188…204 (центр 196); Y 27…183 (как акустическая перегородка); Z 153.5…203.5.
- `DD_divider = 10`: задняя кромка 203.5; до задней панели 215 — 11.5.
- Крепление: клей + 2 шканта 8×30 к акустической перегородке, по 1 к верху и низу; 2 длинных 4×60 из задней кромки в перегородку; 2 винта 4×40 в верх/низ (верх — пробка, низ — скрыто).
- Экран: медь на левой (JAB4) стороне; внизу на нижнюю панель; звезда FG.
- JAB4 — X 56…148; БП — 219…316; C14 — 326…376.

## JAB4

- `DX_JAB = 40<!--p:jab.dx_mm-->` — от внутренней плоскости боковины У (левой) до края платы; плата 92 → X 56…148.
- `DY_JAB = 35.2<!--p:jab.dy_mm-->` — зазор снизу; низ платы 61.7 от пола, верх 130.7 (40% / 60% от свободных 88 мм).
- `ST_JAB = 15<!--p:jab.standoff_mm-->` — нейлоновые стойки M3 мама-папа; 4 шт.; в резьбовые втулки M3 в перегородке акустики.
- Окно BT: X 61<!--p:jab.bt_window_x_mm--> (под антенну JAB4; OQ-021), Y 143, 50×50.
- Рамка и уголки не применяются; винты M3×8, шайбы нейлон/сталь.

## БП

- `X_MEAN_DIV = 60<!--p:psu.x_from_vv_mm-->` — от боковины ВВ до правого края БП; БП 97 → X 219…316; до C14 (X 326) — 10; до разделителя (X 204) — 15.

## Накладка и цековка

- **v8.0:** накладка **3 мм**, не 4. Глубина сходится: `3 + 16 + 0.5 + 110 + 16 + 58 + 0.5 + 5 = 209`. В тексте 4 мм и нет прокладки — тоже 209, поэтому ошибка толщины была незаметна.
- **v9:** накладки нет (`W_overlay = 0`), общая глубина 220. Вместо неё — цековка под твитер: глубина **3.2** (фланец 3 + зазор 0.2), план **58.2 × 53.2**, отверстие 50, под цековкой остаётся 12.8 мм МДФ. Вуфер без цековки.
- Передняя панель v9 снаружи — заводское чёрное покрытие, без накладки; кромки — чёрная кромка или лак.

## Версии

- **v8.0** — текущий текст в `docs/`. Модель даёт 324 / 184 / 220 вместо 322 / 182 / 219 и верх 356 × 184 вместо 356 × 182; это OQ-004. Перенос в `docs/`, `params.yaml` и раскрой — отдельным шагом, после решения по версии.
- **v9** — принята к разработке 2026-10-20: неразборная, клей 0.5, **392 × 200**, глубина 220, без накладки; корпус на клее, евровинтах и шкантах, снимаются только передняя и задняя стенки; разделитель электроники из МДФ 16. Конструкция — [enclosure-v9.md](enclosure-v9.md); §4.8 и §6 v8.0 требуют отдельной ревизии.

## Как менять

1. Правь базовые числа в `params.yaml` → `dimensions.<версия>` (включая `DD_divider`).
2. Пересчитай: `python scripts/dims.py` (Windows: `.venv\Scripts\python`).
3. Обнови таблицы «Производные» и «Детали» по выводу.
4. `python scripts/validate.py` и `python scripts/audit.py`.
5. Если меняется текущая версия — обнови `docs/enclosure.md`, маркеры `<!--p:…-->`, раскрой и [open-questions.md](open-questions.md).
