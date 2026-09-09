"""
dataset.py
----------
Generación del conjunto de datos sintético: miles de escenarios aleatorios
(A, B, obstáculo) junto con su solución ideal (P1, P2) calculada por
geometría (ver geometry.py), y las funciones de normalización necesarias
para entrenar la red con valores en el rango [0, 1].
"""

import numpy as np

from geometry import generate_scenario, compute_ideal_waypoints
from utils import WORLD_SIZE, NUM_SAMPLES, CLEARANCE_MARGIN


def generate_raw_dataset(num_samples=NUM_SAMPLES, world_size=WORLD_SIZE, rng=None):
    """Genera `num_samples` ejemplos sintéticos en coordenadas "del mundo"
    (sin normalizar).

    Devuelve:
        X_raw: array (num_samples, 8) con [Ax, Ay, Bx, By, Ox1, Oy1, Ox2, Oy2]
        Y_raw: array (num_samples, 4) con [P1x, P1y, P2x, P2y]
    """
    rng = rng if rng is not None else np.random.default_rng()

    X_raw = np.zeros((num_samples, 8), dtype=np.float64)
    Y_raw = np.zeros((num_samples, 4), dtype=np.float64)

    for i in range(num_samples):
        a, b, o1, o2 = generate_scenario(rng, world_size)
        p1, p2 = compute_ideal_waypoints(a, b, o1, o2, CLEARANCE_MARGIN)

        X_raw[i] = np.concatenate([a, b, o1, o2])
        Y_raw[i] = np.concatenate([p1, p2])

    return X_raw, Y_raw


def normalize(array, world_size=WORLD_SIZE):
    """Lleva coordenadas del mundo ([0, world_size]) al rango [0, 1],
    tal como pide la consigna ("normalización de coordenadas a [0, 1]")."""
    return array / world_size


def denormalize(array, world_size=WORLD_SIZE):
    """Operación inversa a normalize(): vuelve del rango [0, 1] a
    coordenadas del mundo."""
    return array * world_size


def generate_normalized_dataset(num_samples=NUM_SAMPLES, world_size=WORLD_SIZE, rng=None):
    """Genera el dataset y lo devuelve ya normalizado, junto con las
    versiones "crudas" (en unidades del mundo), que son útiles después para
    la visualización y para calcular métricas en unidades reales."""
    X_raw, Y_raw = generate_raw_dataset(num_samples, world_size, rng)
    X_norm = normalize(X_raw, world_size)
    Y_norm = normalize(Y_raw, world_size)
    return X_norm, Y_norm, X_raw, Y_raw
