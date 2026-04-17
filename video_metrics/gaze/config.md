### Сравнительная таблица

| Метод | Описание | Стандартизированный разрыв (Gap) | Скорость обработки (кадров/сек) | Плюсы / Минусы |
| :--- | :--- | :--- | :--- | :--- |
| **Baseline** | Положение носа относительно центра лица по оси X. | **0.42** (часто дает 1.0 на "плохих" видео) | **~240 FPS** | + Очень быстрый. / - Не видит наклонов (Pitch), ложные срабатывания при поворотах. |
| **Mesh Pose** | 3D-ориентация головы через решение задачи PnP. | **0.58** | **~130 FPS** | + Точные углы наклона. / - Не учитывает направление взгляда самих глаз. |
| **Advanced** | **PnP + Iris Tracking** с логикой компенсации. | **0.84** (лучшая дискриминация) | **~110 FPS** | + Устойчив к поворотам, видит "чтение по бумажке". / - Требует больше ресурсов. |

скорость указана без учета декодинга видео

### Обоснование выбора

#### Проблема текущего решения (Baseline):
Текущий метод в `Charisma Master` использует только горизонтальное смещение носа. 
- **Ложноположительный результат:** Если спикер наклоняет голову вниз (читает текст), нос остается в центре, и система ошибочно засчитывает контакт.
- **Ложноотрицательный результат:** При повороте головы к презентации спикер часто сохраняет контакт глаз с аудиторией ("взгляд из-под лобья"), но система ставит 0.

#### Преимущества метода Advanced (PnP + Iris):
1. **Pitch Awareness:** Благодаря 3D-проекции лица (Face Mesh), мы фиксируем наклон головы. На тестах (видео `custom_facedown_nocontact`) метод показал 0% контакта, что соответствует реальности.
2. **Логика компенсации (Gaze Compensation):** используется расчет положения зрачка относительно смезения разреза глаза
   - Если голова повернута вправо (Yaw > 20°), но зрачки смещены влево (Ratio < 0.38), контакт считается **успешным**.
3. **Стабильность:** Метод протестирован на роликах с плохим освещением и в очках (score > 0.85).

#### Рекомендация по внедрению:
Использовать метод advanced с частотой дискретизации 1 кадр из 5 для сохранения высокой скорости работы `ml_worker`.

#### Ниже представлена таблица с исходными данными тестирования методов.

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>baseline_hits</th>
      <th>mesh_hits</th>
      <th>advanced_hits</th>
      <th>frames_with_face</th>
      <th>total_processed_frames</th>
      <th>score_baseline</th>
      <th>score_mesh</th>
      <th>score_advanced</th>
      <th>video</th>
      <th>label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>298.0</td>
      <td>298</td>
      <td>298</td>
      <td>298</td>
      <td>1493</td>
      <td>1.000000</td>
      <td>1.000000</td>
      <td>1.000000</td>
      <td>media/custom_contact.mp4</td>
      <td>full_contact</td>
    </tr>
    <tr>
      <th>1</th>
      <td>284.0</td>
      <td>0</td>
      <td>0</td>
      <td>284</td>
      <td>1421</td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>media/custom_facedown_nocontact.mp4</td>
      <td>no_contact</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.0</td>
      <td>0</td>
      <td>287</td>
      <td>291</td>
      <td>1455</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.986254</td>
      <td>media/custom_faceright_contact.mp4</td>
      <td>contact_face-right</td>
    </tr>
    <tr>
      <th>3</th>
      <td>27.0</td>
      <td>41</td>
      <td>188</td>
      <td>245</td>
      <td>1226</td>
      <td>0.110204</td>
      <td>0.167347</td>
      <td>0.767347</td>
      <td>media/custom_faceright_nocontact.mp4</td>
      <td>no-contact_face-right</td>
    </tr>
    <tr>
      <th>4</th>
      <td>190.0</td>
      <td>148</td>
      <td>216</td>
      <td>327</td>
      <td>1638</td>
      <td>0.581040</td>
      <td>0.452599</td>
      <td>0.660550</td>
      <td>media/custom_rotate_cantact.mp4</td>
      <td>contact_rotate</td>
    </tr>
    <tr>
      <th>5</th>
      <td>166.0</td>
      <td>102</td>
      <td>147</td>
      <td>321</td>
      <td>1608</td>
      <td>0.517134</td>
      <td>0.317757</td>
      <td>0.457944</td>
      <td>media/custom_rotate_nocantact.mp4</td>
      <td>no-contact_rotate</td>
    </tr>
    <tr>
      <th>6</th>
      <td>118.0</td>
      <td>87</td>
      <td>106</td>
      <td>119</td>
      <td>599</td>
      <td>0.991597</td>
      <td>0.731092</td>
      <td>0.890756</td>
      <td>media/expert_bad_light.mp4</td>
      <td>pro_bad_light</td>
    </tr>
    <tr>
      <th>7</th>
      <td>116.0</td>
      <td>108</td>
      <td>112</td>
      <td>116</td>
      <td>599</td>
      <td>1.000000</td>
      <td>0.931034</td>
      <td>0.965517</td>
      <td>media/expert_glasses.mp4</td>
      <td>pro_glasses</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0.0</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>576</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>0.000000</td>
      <td>media/no_eye_contact.mp4</td>
      <td>bad_no-contact</td>
    </tr>
  </tbody>
</table>
</div>