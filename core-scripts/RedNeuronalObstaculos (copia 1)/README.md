# Red Neuronal para Navegación con Obstáculos

Implementación desde cero (sin frameworks de deep learning) de un
**perceptrón multicapa (MLP)** entrenado con **backpropagation** y
**descenso por gradiente**, que aprende a predecir dos puntos de paso
(P1, P2) que permiten ir de un punto A a un punto B **rodeando un
obstáculo rectilíneo**, siguiendo la consigna *"Red Neuronal para
Navegación con Obstáculos"*.

No usa NEAT, algoritmos genéticos ni ninguna otra técnica evolutiva: toda
la red (capas, activaciones, forward, backward y actualización de pesos)
está implementada a mano con NumPy.

## Instalación

Requiere Python 3.9+.

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

Esto va a, en orden:

1. Generar ~10.000 escenarios sintéticos (A, B, obstáculo + solución ideal).
2. Normalizar las coordenadas a [0, 1] y separar 80% entrenamiento / 20% prueba.
3. Entrenar la MLP (arquitectura 8 → 16 → 16 → 4, ReLU en las ocultas)
   durante 1000 épocas, imprimiendo el MSE de entrenamiento y validación
   cada 200 épocas.
4. Evaluar el modelo sobre el conjunto de prueba (MSE, MAE, % de aciertos
   con error < 0.5 unidades) e imprimir los resultados en la consola.
5. Guardar el modelo entrenado en `modelo_entrenado.pkl`.
6. Abrir una ventana de **Pygame** con la visualización interactiva.

### Controles de la visualización

| Tecla     | Acción                                             |
|-----------|-----------------------------------------------------|
| `ESPACIO` | Generar un escenario nuevo (A, B y obstáculo al azar) |
| `ESC`     | Cerrar la ventana                                   |

En cada escenario se dibujan: el punto **A** (amarillo), el punto **B**
(verde), el **obstáculo** (línea roja), la **ruta ideal** calculada por
geometría (azul, punteada) y la **ruta que predice la red** (naranja). El
HUD superior muestra el error de ese escenario puntual y si la ruta
predicha llega a cruzar el obstáculo.

## Estructura del proyecto

```
main.py             # Orquesta todo el flujo: dataset -> entrenamiento -> evaluación -> visualización
utils.py             # Constantes globales (hiperparámetros, geometría del mundo) y funciones auxiliares
geometry.py          # Generación aleatoria de escenarios y cálculo de la solución ideal (P1, P2)
dataset.py           # Generación del dataset sintético y normalización de coordenadas
layers.py            # Capa densa (DenseLayer): forward, backward y funciones de activación
neural_network.py    # Clase MultiLayerPerceptron: compone capas, MSE, backprop, entrenamiento
metrics.py           # MSE, MAE y porcentaje de aciertos dentro del umbral de error
visualization.py     # Interfaz gráfica con Pygame
requirements.txt     # Dependencias (numpy, pygame)
```

## Qué hace cada módulo

- **`utils.py`**: reúne todos los "números mágicos" del proyecto (tamaño
  del mundo, longitud del obstáculo, hiperparámetros de entrenamiento,
  umbral de error, semilla aleatoria, etc.) en un único lugar, además de
  `train_test_split` y `create_rng`.

- **`geometry.py`**: genera escenarios aleatorios (`generate_scenario`) y
  calcula la solución "ideal" (`compute_ideal_waypoints`) que la red debe
  aprender a imitar, mediante un heurístico geométrico simple (ver la
  sección *Decisiones de diseño* más abajo). También incluye
  `segments_intersect` / `path_collides_with_obstacle`, usadas para
  detectar si una ruta predicha choca contra el obstáculo.

- **`dataset.py`**: usa `geometry.py` para generar miles de ejemplos
  (`generate_raw_dataset`) y los normaliza a [0, 1]
  (`generate_normalized_dataset`).

- **`layers.py`**: implementa `DenseLayer`, una capa totalmente conectada
  con `forward()` (propagación hacia adelante) y `backward()`
  (retropropagación del error + actualización de pesos por descenso de
  gradiente), y las funciones de activación ReLU (capas ocultas) y lineal
  (capa de salida).

- **`neural_network.py`**: la clase `MultiLayerPerceptron` compone varias
  `DenseLayer`, calcula el error MSE, retropropaga el gradiente por todas
  las capas y expone `train()`, `predict()`, `save()` y `load()`.

- **`metrics.py`**: `mean_squared_error`, `mean_absolute_error` y
  `accuracy_within_threshold` (porcentaje de ejemplos cuyo error espacial
  promedio de P1 y P2, en unidades del mundo, es menor a 0.5).

- **`visualization.py`**: dibuja el escenario, la ruta ideal y la ruta
  predicha con Pygame, y permite regenerar escenarios con la tecla
  `ESPACIO` para comprobar visualmente la generalización de la red.

- **`main.py`**: conecta todos los módulos anteriores en el flujo
  completo descrito en *Uso*.

## Decisiones de diseño (ambigüedades de la consigna)

La consigna deja algunos puntos abiertos a interpretación. Estas son las
decisiones tomadas y su justificación:

1. **Cómo se calculan P1 y P2 ("lógica geométrica")**: no hay un algoritmo
   único especificado. Se implementó un heurístico simple y determinista
   (ver el docstring de `geometry.compute_ideal_waypoints`): se identifica
   qué extremo del obstáculo está más cerca de A y cuál de B, y se
   desplaza cada uno `CLEARANCE_MARGIN` unidades en la dirección
   perpendicular a A→B. Para que el heurístico tenga sentido, el
   obstáculo se genera aproximadamente alineado con la recta A-B (con
   variación aleatoria de ángulo y posición), de modo que realmente
   interfiera con el trayecto directo — igual que en el ejemplo de la
   consigna, donde el obstáculo (4,4)-(6,6) queda sobre la misma diagonal
   que A=(1,1) y B=(9,9). Se verificó empíricamente que, con este
   heurístico, la ruta ideal nunca cruza el obstáculo (0 colisiones en
   2000 escenarios de prueba).

2. **Activación de la capa de salida**: la consigna especifica ReLU para
   las capas ocultas pero no dice nada sobre la salida. Se usó activación
   **lineal** (identidad), porque P1/P2 son coordenadas continuas
   normalizadas y una salida acotada (por ejemplo, sigmoide) restringiría
   innecesariamente el rango de valores que la red puede aprender a
   producir durante el entrenamiento.

3. **Tipo de descenso por gradiente**: la consigna pide "descenso por
   gradiente" (no menciona mini-batches ni SGD), así que se implementó
   **descenso por gradiente de lote completo**: en cada época se calcula
   la predicción y el gradiente sobre las 8.000 muestras de entrenamiento
   a la vez.

4. **Tasa de aprendizaje**: la consigna sugiere `learning_rate ≈ 0.01`.
   Con descenso de lote completo y solo 1000 épocas, ese valor converge
   muy lento y no alcanza el resultado esperado en la sección 5.1 de la
   consigna ("error aceptable en desviaciones < 1 unidad"). Se subió a
   **0.05** (mismo orden de magnitud) para cumplir ese objetivo dentro de
   las 1000 épocas sugeridas. El valor es una constante en `utils.py`
   (`LEARNING_RATE`) y se puede volver a 0.01 fácilmente si se prefiere
   reproducir el valor literal de la consigna (va a converger, solo que
   más lento).

5. **Longitud fija del obstáculo y escala del mundo**: se usó un mundo
   cuadrado de 10×10 unidades (la misma escala que el ejemplo de la
   consigna, A=(1,1), B=(9,9)) y un obstáculo de longitud fija = 2
   unidades, tal como pide la consigna.

6. **Interpretación de "error < 0.5 unidades"**: como cada predicción son
   dos puntos (P1 y P2), el error de un ejemplo se define como el
   promedio de las distancias euclídeas (predicho vs. ideal) de P1 y de
   P2, calculado en unidades del mundo (0–10), no en el espacio
   normalizado [0, 1].

## Resultados esperados

Con la configuración por defecto (10.000 ejemplos, arquitectura
8-16-16-4, learning_rate=0.05, 1000 épocas), un entrenamiento típico
converge a:

- MSE (normalizado): ≈ 0.003
- MAE (unidades del mundo): ≈ 0.4 (por debajo del "< 1 unidad" esperado
  en la consigna)
- Predicciones con error < 0.5 unidades: ≈ 30%

Como anticipa la propia consigna (sección 5.1), es normal que la red
falle más seguido en **configuraciones cercanas al obstáculo** (donde el
margen de error para no chocar es más chico) y generalice mejor en
escenarios "despejados". Podés confirmarlo visualmente generando varios
escenarios seguidos con `ESPACIO` en la visualización.

## Limitaciones (heredadas de la consigna)

- Solo se considera **un** obstáculo por escenario.
- Los datos son sintéticos, generados por la propia lógica geométrica del
  proyecto (no provienen de sensores reales).
- No hay navegación en tiempo real ni entornos dinámicos: cada escenario
  es estático y se resuelve "de una", no paso a paso.
