# Программирование как шаг сборки

Процедура — [`programming.md`](programming.md). Параметры — [`dsp-params.yaml`](dsp-params.yaml).

| ID | Шаг | Требует |
|---|---|---|
| STEP-DSP-01 | Собрать схему SigmaStudio по `dsp-params.yaml` | — |
| STEP-DSP-02 | Подключить ICP3, проверить связь (зелёная полоса USBi) | STEP-AMP-07, питание JAB4 |
| STEP-DSP-03 | Compile-Download, запись в E2Prom | STEP-DSP-01, STEP-DSP-02 |
| STEP-DSP-04 | Проверка автономности (без программатора) | STEP-DSP-03 |
