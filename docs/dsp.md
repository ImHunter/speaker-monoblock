# DSP: схема SigmaStudio и программирование JAB4

Значения — в [`params.yaml`](../params.yaml), секция `dsp`. Проект SigmaStudio хранится в `dsp/sigmastudio/` (Git LFS). Нужны: программатор `CMP-icp3-programmer`, ПК с Windows, SigmaStudio 4.6 или 4.7. Параметры динамиков — [acoustics.md](acoustics.md).

## 1. Схема 2.1 (Schematic)

**Вход и громкость.** Input (0 — левый, 1 — правый) → External Volume (Volume Controls → Ext Gain → External Volume → Single/Gain (Type 2)). Управляющий контакт — Aux ADC Input, канал ADC0 (потенциометр).

**Твитеры (L и R), каждый канал:**
1. High-Pass, Butterworth, 24<!--p:dsp.slope_db_oct--> дБ/окт, 2500<!--p:dsp.crossover_hz--> Гц (два каскада «General 2nd Order Filter», OQ-003).
2. Gain −8.0<!--p:dsp.tweeter_gain_db--> дБ (компенсация чувствительности: 95.8 − 88 = 7.8 дБ).
3. Peak Limiter: порог −3.0<!--p:dsp.limiter_tweeter_threshold_db--> дБ, release 50<!--p:dsp.limiter_tweeter_release_ms--> мс.
4. Выход: левый — DAC0, правый — DAC1.

**Бас (SUB):**
1. 2-Ch Merger (сумма L+R в моно).
2. Subsonic HPF: Butterworth, 24 дБ/окт, 60<!--p:dsp.subsonic_hz--> Гц.
3. PEQ (Peaking): 95<!--p:dsp.peq_hz--> Гц, −4.0<!--p:dsp.peq_gain_db--> дБ, Q 1.2<!--p:dsp.peq_q--> — подавление горба от Qtc ≈ 1.05.
4. Low Shelf: 300<!--p:dsp.shelf_hz--> Гц, +3.0<!--p:dsp.shelf_gain_db--> дБ, Q 0.7<!--p:dsp.shelf_q--> — компенсация баффл-степа.
5. Low-Pass Butterworth 24 дБ/окт, 2500 Гц — подавление резонансов вуфера выше частоты раздела.
6. Peak Limiter: порог −3.0<!--p:dsp.limiter_bass_threshold_db--> дБ, release 150<!--p:dsp.limiter_bass_release_ms--> мс.
7. Выход: DAC2; на DAC3 тот же сигнал через блок Invert (мостовой выход).

Подъём 45 Гц эквалайзером не применять: перегрузка диффузора и клиппинг усилителя. Все значения PEQ и shelf — стартовые, подтвердить измерением АЧХ после сборки (`verified_by_measurement` не выставлять без данных).

## 2. Подключение программатора
1. DIP-переключатель №1 на ICP3 в положение I2C (обычно ON).
2. Обесточить JAB4 (выключатель C14 OFF); соединить ICP3 и разъём PROGRAM на JAB4 6-пиновым шлейфом; ICP3 в USB ПК (Micro-USB).
3. Включить колонку (C14 ON): плата должна быть запитана от своего БП.
4. SigmaStudio: File → New Project. Вкладка Hardware Configuration: блоки USBi, ADAU1701, E2Prom; I2C-шина от нижнего синего контакта USBi к верхнему синему контакту ADAU1701, затем от той же линии к верхнему синему контакту E2Prom. Зелёная полоса над USBi — связь есть; красная — проверить драйверы USBi, питание JAB4, переключатель I2C/SPI.

## 3. Запись в EEPROM
1. Link-Compile-Download (синяя стрелка).
2. Hardware Configuration → ПКМ на ADAU1701 → «Write Latest Compilation to E2Prom».
3. В окне протокола оставить стандартные параметры (I2C), OK; дождаться зелёной шкалы.

## 4. Проверка автономности
C14 OFF → отсоединить шлейф → C14 ON. Колонка стартует, сопрягается по Bluetooth, регулирует громкость, каналы разделены правильно.

## 5. Внешняя антенна
Если Bluetooth слабый: отверстие ∅6.5 мм в задней панели (X = 175, Y = 100), розетка SMA снаружи, изнутри изолирующая шайба и гайка (корпус разъёма не касается экрана); пигтейл U.FL → SMA к разъёму ANT/U.FL на JAB4; штыревая антенна 2.4 ГГц.

## 6. Правила изменения
1. Сначала `params.yaml → dsp`, затем проект SigmaStudio, затем этот документ (`make sync`).
2. Изменение частоты раздела: пересмотреть [acoustics.md](acoustics.md) и сделать запись в [project.md](project.md).
3. Не отключать subsonic и лимитеры.
