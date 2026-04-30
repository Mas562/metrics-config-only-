# Пороговые значения и обоснование метрики жестикуляции

## Выбранный алгоритм

**Алгоритм:** `charisma_master_baseline` — подтверждён по итогам обратной связи, baseline оставляем.

На текущей выборке этот алгоритм показывает лучший `стандартизированный_разрыв_good_vs_bad` в `video_metrics/gesture/comparison_table.csv`:
- `charisma_master_baseline`: `1.3594`
- `llm_simple_normalized`: `0.4295`
- `llm_cpu_structured`: `0.2384`

То есть по главному обязательному критерию сравнения baseline сейчас лидер. По итогам фидбэка baseline оставляем как выбранный алгоритм. При необходимости расширения выборки сравнение можно будет повторить, но текущий выбор зафиксирован.

## Почему предварительно выбран именно этот алгоритм

### 1. Разделение `good_professional` и `bad`

По текущей выборке baseline дал лучший стандартизированный разрыв между `good_professional` и `bad`.

Это означает, что на имеющихся данных он лучше других кандидатов отделяет хорошие выступления от плохих по сырой метрике.

### 2. Поведение на `self_recorded`

Проверка среднего `raw_metric` по группам из `video_metrics/gesture/results/per_video_metrics.csv` показывает:
- `charisma_master_baseline`: `good_mean = 0.0429`, `bad_mean = 0.0171`, `self_mean = 0.0111`
- `llm_simple_normalized`: `good_mean = 2.5926`, `bad_mean = 2.3927`, `self_mean = 0.9266`
- `llm_cpu_structured`: `good_mean = 2.4709`, `bad_mean = 2.3490`, `self_mean = 1.2565`

На текущей выборке тезис **«self_recorded ближе к good_professional, чем к bad» не выполняется ни для одного из трёх методов**. Во всех трёх случаях среднее значение `self_recorded` ближе к `bad`, чем к `good`.

Это подтверждено по итогам обратной связи: для текущих роликов вывод корректный, жестикуляция действительно ближе к плохой, чем к хорошей.

### 3. Чувствительность к расстоянию

В `video_metrics/gesture/results/distance_sensitivity.csv` текущие значения такие:
- `charisma_master_baseline`: `0.0056`
- `llm_simple_normalized`: `0.2421`
- `llm_cpu_structured`: `0.4163`

На текущей self-выборке baseline показывает наименьший разброс между `near`, `mid` и `far`, то есть выглядит наиболее устойчивым к изменению расстояния до камеры.

### 4. Время обработки

Все три метода укладываются примерно в один класс времени на текущей выборке:
- `charisma_master_baseline`: `955.78` сек
- `llm_simple_normalized`: `955.36` сек
- `llm_cpu_structured`: `948.10` сек

Существенного преимущества по runtime, которое перевешивало бы текущее качество separation, у альтернативных методов не видно.

## Определение метрики

Для текущего подтверждённого выбора используется baseline из Charisma Master.

Логика метрики:
1. Из видео извлекаются pose landmarks через MediaPipe Holistic.
2. Используются ключевые точки:
   - `left_shoulder`
   - `right_shoulder`
   - `left_elbow`
   - `right_elbow`
   - `left_wrist`
   - `right_wrist`
3. Видео предварительно уменьшается до `gesture_preprocessing_target_width = 480`.
4. Обрабатывается не каждый кадр, а каждый `5`-й кадр (`gesture_preprocessing_frame_sample_every = 5`).
5. Для каждой пары соседних sampled-кадров считается суммарное движение левого и правого запястий.
6. Если движение выше `movement_threshold = 0.002`, оно добавляется в накопленную сумму движения.
7. Затем считается среднее движение на кадр с позой (`avg_move`).
8. Итоговый `gesture_score` получается как `avg_move * gesture_scale`, где `gesture_scale = 3500`, с ограничением сверху `max_score = 100`.

Именно этот `avg_move` используется как `raw_metric`, а масштабированное значение — как `score`.

## Пороги

- `gesture_threshold_bad`: `15`
- `gesture_threshold_good`: `85`
- `gesture_distance_stability_tolerance`: `0.005616618388312837`

### Как интерпретировать пороги

- Значения ниже `gesture_threshold_bad = 15` трактуются как слабая жестикуляция.
- Значения выше `gesture_threshold_good = 85` трактуются как уверенная / сильная жестикуляция.
- Значения между ними — промежуточная зона, требующая аккуратной интерпретации.

### Откуда взялись эти значения

`gesture_threshold_bad = 15` и `gesture_threshold_good = 85` не были придуманы заново: это текущие baseline-пороги из логики Charisma Master, и по итогам обратной связи они сохраняются без изменений.

`gesture_distance_stability_tolerance = 0.005616618388312837` взят из текущего observed spread для `charisma_master_baseline` на self-видео (`near`, `mid`, `far`). На текущем этапе он также сохраняется как baseline-ориентир.

Дополнительно все ключевые baseline-параметры зафиксированы в `video_metrics/gesture/config.json`:
- `gesture_movement_threshold = 0.002`
- `gesture_scale = 3500`
- `gesture_max_score = 100`
- `gesture_low_lt = 15`
- `gesture_high_gt = 85`

### Ограничения текущих порогов

На текущей выборке диапазоны score частично пересекаются:
- `bad`: примерно `22.0` и `98.0`
- `self_recorded`: примерно `29.9`, `37.5`, `49.6`
- `good_professional`: примерно `57.5`, `100`, `100`, `100`

Пороги подтверждены по итогам обратной связи. При расширении выборки их можно будет пересмотреть.

## Коэффициенты и веса

Для `charisma_master_baseline` отдельные веса признаков вида `gesture_weight_activity`, `gesture_weight_amplitude`, `gesture_weight_rhythm`, `gesture_weight_variability`, `gesture_weight_pointing_bonus` не используются.

Вместо этого ключевыми параметрами baseline являются:
- `movement_threshold = 0.002`
- `gesture_scale = 3500`
- `gesture_low_lt = 15`
- `gesture_high_gt = 85`
- `max_score = 100`

Именно эти параметры определяют чувствительность baseline и интерпретацию его результата.

## Обратная связь

Обратная связь получена и зафиксирована.

Статус секции: `reviewed and confirmed`.

Зафиксированные решения:
- baseline оставляем;
- пороги оставляем те же, что использовались для вычислений;
- все baseline-пороги и ключевые baseline-параметры занесены в `config.json`;
- вывод по `self_recorded` подтверждён: в текущих роликах жестикуляция ближе к плохой, чем к хорошей.

## Примечание про baseline

Текущий baseline в Charisma Master использует `gesture_score`, который считается из среднего движения рук, масштабируется коэффициентом из конфига и затем сравнивается с нижним и верхним порогом.

Референсная реализация:
- `charisma-master/services/ml_worker/app/logic/ml_engine.py`
- `charisma-master/services/ml_worker/app/config.json`
- `charisma-master/services/ml_worker/app/config_fields.md`

## Что остаётся после фидбэка тимлида

По итогам полученного фидбэка уже зафиксировано следующее:
1. выбор `charisma_master_baseline` подтверждён;
2. пороги подтверждены без изменений;
3. интерпретация по `self_recorded` подтверждена: текущие ролики ближе к `bad`, чем к `good`.
