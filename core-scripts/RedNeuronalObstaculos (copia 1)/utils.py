"""
utils.py
--------
Constantes globales y funciones auxiliares compartidas por el resto de los
módulos del proyecto.

Reunir acá todos los "números mágicos" (tamaño del mundo, longitud del
obstáculo, hiperparámetros de entrenamiento, etc.) permite ajustarlos desde
un único lugar, sin tener que buscarlos dispersos en cada archivo.
"""

import numpy as np


# =====================================================================
# GEOMETRÍA DEL MUNDO
# =====================================================================
# Todo el proyecto trabaja en un mundo cuadrado [0, WORLD_SIZE] x [0, WORLD_SIZE].
# Elegimos 10.0 porque es la escala que usa el ejemplo de la consigna
# (A = (1,1), B = (9,9)).
WORLD_SIZE = 10.0

# Margen mínimo respecto al borde del mundo al generar A y B, para que la
# red nunca tenga que predecir puntos fuera del mapa.
DOMAIN_MARGIN = 0.5

# Longitud fija del segmento-obstáculo, tal como pide la consigna
# ("obstáculos como segmentos rectos de longitud fija").
OBSTACLE_LENGTH = 2.0

# Distancia mínima entre A y B. Evita escenarios triviales donde el
# obstáculo ocuparía casi todo el trayecto o A y B quedarían pegados.
MIN_AB_DISTANCE = 4.0

# Cuánto se alejan los puntos de paso (P1, P2) del obstáculo al rodearlo.
# Es la "distancia de seguridad" del heurístico geométrico (ver geometry.py).
CLEARANCE_MARGIN = 0.8

# El obstáculo se genera aproximadamente alineado con la dirección A->B
# (para que quede "en el trayecto", como en el ejemplo de la consigna),
# con una pequeña variación aleatoria de ángulo y de posición perpendicular,
# para no generar siempre el mismo tipo de escenario.
OBSTACLE_ANGLE_JITTER_DEG = 20.0
OBSTACLE_PERP_JITTER = 0.6
OBSTACLE_CENTER_T_RANGE = (0.35, 0.65)  # posición del centro del obstáculo a lo largo de A->B

# =====================================================================
# DATASET
# =====================================================================
NUM_SAMPLES = 10_000  # cantidad de escenarios a generar para el dataset sintético
TEST_SPLIT_RATIO = 0.2
RANDOM_SEED = 42

# =====================================================================
# ARQUITECTURA Y ENTRENAMIENTO DE LA RED
# =====================================================================
INPUT_SIZE = 8           # Ax, Ay, Bx, By, Ox1, Oy1, Ox2, Oy2
HIDDEN_LAYER_SIZE = 16
NUM_HIDDEN_LAYERS = 2
OUTPUT_SIZE = 4           # P1x, P1y, P2x, P2y
# DECISIÓN DE DISEÑO: la consigna sugiere learning_rate ≈ 0.01. En la
# práctica, con descenso por gradiente de LOTE COMPLETO (no estocástico,
# como pide la consigna) y solo 1000 épocas, 0.01 converge muy lento y no
# llega a un error "aceptable (< 1 unidad)" como pide la sección 5.1. Se
# sube a 0.05 -manteniéndose en el mismo orden de magnitud ("aproximadamente
# 0.01")- para que el modelo sí alcance ese objetivo dentro de las 1000
# épocas sugeridas. Con LEARNING_RATE=0.01 el proyecto igual funciona
# (y podés volver a ese valor acá si querés reproducir el resultado
# "literal" de la consigna), solo que converge más lento.
LEARNING_RATE = 0.05
EPOCHS = 1000
LOG_EVERY = 1          # cada cuántas épocas se imprime el progreso

# =====================================================================
# EVALUACIÓN
# =====================================================================
ERROR_THRESHOLD = 0.5     # unidades del mundo (ver consigna, sección 3.2.4)

# =====================================================================
# ARCHIVOS DE SALIDA
# =====================================================================
MODEL_PATH = "modelo_entrenado.pkl"


def build_layer_sizes():
    """Arma la lista de tamaños de capa [entrada, oculta, oculta, ..., salida]
    a partir de las constantes de arquitectura definidas arriba."""
    return [INPUT_SIZE] + [HIDDEN_LAYER_SIZE] * NUM_HIDDEN_LAYERS + [OUTPUT_SIZE]


def create_rng(seed=RANDOM_SEED):
    """Crea un generador de números aleatorios de NumPy con semilla fija,
    para que el dataset y la inicialización de pesos sean reproducibles."""
    return np.random.default_rng(seed)


def train_test_split(X, Y, test_ratio=TEST_SPLIT_RATIO, rng=None):
    """Divide (X, Y) en conjuntos de entrenamiento y de prueba, mezclando
    los índices antes de partir para que ambos conjuntos sean representativos.
    """
    rng = rng if rng is not None else np.random.default_rng()
    num_samples = X.shape[0]
    shuffled_indices = rng.permutation(num_samples)
    num_test = int(num_samples * test_ratio)

    test_idx = shuffled_indices[:num_test]
    train_idx = shuffled_indices[num_test:]

    return X[train_idx], Y[train_idx], X[test_idx], Y[test_idx]
