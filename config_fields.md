# ML Worker Metrics Config

Этот файл описывает поля `config.json`, который хранит числовые параметры и вспомогательные значения для расчёта метрик качества речи, аудио и видео в `ml_worker`.

## Общая идея

`config.json` нужен для data-driven настройки метрик без правки кода. Вместо захардкоженных коэффициентов, порогов и весов сервис читает их из JSON и использует в расчётах.

Основные места использования:
- `app/config.py` — загрузка JSON в `metric_config`
- `app/logic/ml_engine.py` — audio/video/tempo/pause расчёты
- `app/logic/tasks.py` — итоговый `confidence_index`, filler score и long pauses

---

## `pauses`
Параметры пауз и сегментации транскрипта.

### `long_pause_threshold_sec`
- **Что делает:** задаёт минимальную длительность паузы, после которой пауза считается длинной.
- **Где используется:** `MLEngine.get_long_pauses()` и вызов из `tasks.py`.

### `sber_segment_pause_threshold_sec`
- **Что делает:** задаёт порог паузы между словами для разбиения распознанного Sber-текста на сегменты.
- **Где используется:** `_transcribe_sber_api_async()` в `ml_engine.py`.

### `sber_segment_max_words`
- **Что делает:** ограничивает длину сегмента по количеству слов перед принудительным разбиением.
- **Где используется:** `_transcribe_sber_api_async()` в `ml_engine.py`.

### `duration_round_digits`
- **Что делает:** определяет точность округления длительности найденных длинных пауз.
- **Где используется:** `MLEngine.get_long_pauses()`.

---

## `tempo`
Параметры расчёта темпа речи.

### `window_sec`
- **Что делает:** размер временного окна для подсчёта слов в минуту.
- **Где используется:** `MLEngine.calculate_tempo()`.

### `step_sec`
- **Что делает:** шаг по временной шкале, с которым строятся точки темпа.
- **Где используется:** `MLEngine.calculate_tempo()`.

### `wpm_multiplier`
- **Что делает:** переводит число слов в окне в значение words per minute.
- **Где используется:** `MLEngine.calculate_tempo()`.

### `wpm_round_digits`
- **Что делает:** задаёт точность округления WPM.
- **Где используется:** `MLEngine.calculate_tempo()`.

### `zones`
Правила раскраски темпа речи по зонам.

#### `zones.red.min_lt`
- **Что делает:** нижняя граница, ниже которой темп считается красной зоной.
- **Где используется:** `MLEngine.calculate_tempo()`.

#### `zones.red.max_gt`
- **Что делает:** верхняя граница, выше которой темп считается красной зоной.
- **Где используется:** `MLEngine.calculate_tempo()`.

#### `zones.yellow.min_lt`
- **Что делает:** нижняя граница жёлтой зоны темпа.
- **Где используется:** `MLEngine.calculate_tempo()`.

#### `zones.yellow.max_gt`
- **Что делает:** верхняя граница жёлтой зоны темпа.
- **Где используется:** `MLEngine.calculate_tempo()`.

---

## `score_labels`
Набор правил для преобразования числового score в текстовую оценку.

Каждый объект содержит:

### `min_score`
- **Что делает:** минимальный score, начиная с которого применяется label.
- **Где используется:** `MLEngine.get_score_label()`.

### `label`
- **Что делает:** текстовая интерпретация оценки.
- **Где используется:** `MLEngine.get_score_label()`.

---

## `audio`
Параметры расчёта аудио-метрик.

### `audio.volume`
Параметры оценки громкости.

#### `very_quiet_lt`
- **Что делает:** порог RMS, ниже которого аудио считается очень тихим.
- **Где используется:** `MLEngine.analyze_audio()`.

#### `quiet_lt`
- **Что делает:** порог RMS, ниже которого аудио считается тиховатым.
- **Где используется:** `MLEngine.analyze_audio()`.

#### `loud_gt`
- **Что делает:** порог RMS, выше которого аудио считается громким.
- **Где используется:** `MLEngine.analyze_audio()`.

#### `normalization_rms`
- **Что делает:** базовое RMS-значение для перевода громкости в score 0–100.
- **Где используется:** `MLEngine.analyze_audio()`.

#### `max_score`
- **Что делает:** верхняя граница для `volume_score`.
- **Где используется:** `MLEngine.analyze_audio()`.

#### `levels`
Текстовые уровни громкости.

##### `levels.very_quiet`
- **Что делает:** текст для очень тихого аудио.
- **Где используется:** `MLEngine.analyze_audio()`.

##### `levels.quiet`
- **Что делает:** текст для тиховатого аудио.
- **Где используется:** `MLEngine.analyze_audio()`.

##### `levels.loud`
- **Что делает:** текст для громкого аудио.
- **Где используется:** `MLEngine.analyze_audio()`.

##### `levels.normal`
- **Что делает:** текст для нормального уровня громкости.
- **Где используется:** `MLEngine.analyze_audio()`.

### `audio.tone`
Параметры оценки вариативности тона.

#### `pitch_fmin_note`
- **Что делает:** нижняя музыкальная нота для анализа pitch.
- **Где используется:** `MLEngine.analyze_audio()` через `librosa.note_to_hz()`.

#### `pitch_fmax_note`
- **Что делает:** верхняя музыкальная нота для анализа pitch.
- **Где используется:** `MLEngine.analyze_audio()` через `librosa.note_to_hz()`.

#### `normalization_std`
- **Что делает:** базовое значение стандартного отклонения pitch для нормализации `tone_score`.
- **Где используется:** `MLEngine.analyze_audio()`.

#### `max_score`
- **Что делает:** верхняя граница для `tone_score`.
- **Где используется:** `MLEngine.analyze_audio()`.

#### `empty_pitch_std`
- **Что делает:** fallback-значение pitch variability, если валидный pitch не найден.
- **Где используется:** `MLEngine.analyze_audio()`.

---

## `video`
Параметры расчёта видео-метрик.

### `target_frame_width`
- **Что делает:** целевая ширина кадра при ресайзе перед анализом.
- **Где используется:** `MLEngine.analyze_video()`.

### `visual_deviation`
- **Что делает:** максимально допустимое относительное отклонение взгляда от центра лица для засчитывания зрительного контакта.
- **Где используется:** `MLEngine.analyze_video()`.

### `movement_threshold`
- **Что делает:** минимальный порог движения кистей, после которого движение учитывается.
- **Где используется:** `MLEngine.analyze_video()`.

### `frame_sample_every`
- **Что делает:** указывает, каждый какой кадр анализировать.
- **Где используется:** `MLEngine.analyze_video()`.

### `min_frames_with_face`
- **Что делает:** минимальное число кадров с лицом для расчёта `gaze_score`.
- **Где используется:** `MLEngine.analyze_video()`.

### `min_frames_with_pose`
- **Что делает:** минимальное число кадров с позой для расчёта `gesture_score`.
- **Где используется:** `MLEngine.analyze_video()`.

### `gesture_scale`
- **Что делает:** коэффициент перевода среднего движения рук в итоговый `gesture_score`.
- **Где используется:** `MLEngine.analyze_video()`.

### `gesture_low_lt`
- **Что делает:** нижний порог для определения слишком слабой жестикуляции.
- **Где используется:** `MLEngine.analyze_video()`.

### `gesture_high_gt`
- **Что делает:** верхний порог для определения чрезмерной жестикуляции.
- **Где используется:** `MLEngine.analyze_video()`.

### `max_score`
- **Что делает:** верхняя граница видео-метрик `gaze_score` и `gesture_score`.
- **Где используется:** `MLEngine.analyze_video()`.

### `default_scores`
Fallback-значения score, если данных недостаточно.

#### `default_scores.gaze`
- **Что делает:** значение `gaze_score` по умолчанию.
- **Где используется:** `MLEngine.analyze_video()`.

#### `default_scores.gesture`
- **Что делает:** значение `gesture_score` по умолчанию.
- **Где используется:** `MLEngine.analyze_video()`.

### `default_advice`
- **Что делает:** текст рекомендации по жестикуляции, если анализ не удался или данных мало.
- **Где используется:** `MLEngine.analyze_video()`.

### `advice`
Текстовые рекомендации по жестикуляции.

#### `advice.low`
- **Что делает:** совет при слишком слабой жестикуляции.
- **Где используется:** `MLEngine.analyze_video()`.

#### `advice.high`
- **Что делает:** совет при слишком активной жестикуляции.
- **Где используется:** `MLEngine.analyze_video()`.

#### `advice.normal`
- **Что делает:** совет при нормальной жестикуляции.
- **Где используется:** `MLEngine.analyze_video()`.

### `mediapipe`
Параметры MediaPipe Holistic, влияющие на качество детекции.

#### `mediapipe.min_detection_confidence`
- **Что делает:** минимальная уверенность детекции.
- **Где используется:** `MLEngine.analyze_video()`.

#### `mediapipe.min_tracking_confidence`
- **Что делает:** минимальная уверенность трекинга.
- **Где используется:** `MLEngine.analyze_video()`.

#### `mediapipe.model_complexity`
- **Что делает:** уровень сложности модели MediaPipe.
- **Где используется:** `MLEngine.analyze_video()`.

#### `mediapipe.static_image_mode`
- **Что делает:** включает или выключает режим статичных изображений.
- **Где используется:** `MLEngine.analyze_video()`.

### `landmarks`
Индексы ключевых landmark-точек MediaPipe.

#### `landmarks.nose`
- **Что делает:** индекс landmark носа.
- **Где используется:** `MLEngine.analyze_video()` для расчёта направления взгляда.

#### `landmarks.left_face_edge`
- **Что делает:** индекс левой опорной точки лица.
- **Где используется:** `MLEngine.analyze_video()`.

#### `landmarks.right_face_edge`
- **Что делает:** индекс правой опорной точки лица.
- **Где используется:** `MLEngine.analyze_video()`.

#### `landmarks.left_wrist`
- **Что делает:** индекс левого запястья.
- **Где используется:** `MLEngine.analyze_video()`.

#### `landmarks.right_wrist`
- **Что делает:** индекс правого запястья.
- **Где используется:** `MLEngine.analyze_video()`.

### `file_size_divisors`
Служебные коэффициенты для логирования размера файла в MB.

#### `file_size_divisors.bytes_per_kb`
- **Что делает:** коэффициент перевода байт в килобайты.
- **Где используется:** `MLEngine.analyze_video()`.

#### `file_size_divisors.kb_per_mb`
- **Что делает:** коэффициент перевода килобайт в мегабайты.
- **Где используется:** `MLEngine.analyze_video()`.

---

## `confidence_index`
Параметры расчёта итогового confidence score.

### `empty_text_fallback_words`
- **Что делает:** fallback-количество слов, если текст отсутствует.
- **Где используется:** `tasks.py` при расчёте filler ratio.

### `empty_ratio`
- **Что делает:** fallback-значение ratio, если деление выполнить нельзя.
- **Где используется:** `tasks.py`.

### `filler_ratio_precision`
- **Что делает:** точность округления `fillers_summary.ratio`.
- **Где используется:** `tasks.py`.

### `filler_score`
Параметры расчёта оценки за отсутствие слов-паразитов.

#### `filler_score.base_score`
- **Что делает:** базовая максимальная оценка до штрафа.
- **Где используется:** `tasks.py`.

#### `filler_score.penalty_multiplier`
- **Что делает:** множитель штрафа для доли слов-паразитов.
- **Где используется:** `tasks.py`.

#### `filler_score.min_score`
- **Что делает:** нижняя граница `filler_score`.
- **Где используется:** `tasks.py`.

### `weights`
Веса компонент в итоговом confidence index.

#### `weights.filler`
- **Что делает:** вес `filler_score`.
- **Где используется:** `tasks.py`.

#### `weights.tone`
- **Что делает:** вес `tone_score`.
- **Где используется:** `tasks.py`.

#### `weights.volume`
- **Что делает:** вес `volume_score`.
- **Где используется:** `tasks.py`.

#### `weights.gaze`
- **Что делает:** вес `gaze_score`.
- **Где используется:** `tasks.py`.

#### `weights.gesture`
- **Что делает:** вес `gesture_score`.
- **Где используется:** `tasks.py`.

### `max_total`
- **Что делает:** верхняя граница итогового `confidence_index.total`.
- **Где используется:** `tasks.py`.

---


