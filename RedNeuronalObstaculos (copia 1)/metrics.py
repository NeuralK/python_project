"""
metrics.py
----------
Métricas para evaluar qué tan bien predice la red: error cuadrático medio
(MSE), error medio absoluto (MAE) y el porcentaje de predicciones cuyo
error (distancia euclídea a la solución ideal) es menor a un umbral dado,
tal como pide la consigna.
"""

import numpy as np


def mean_squared_error(y_true, y_pred):
    """Error cuadrático medio sobre todos los elementos."""
    return float(np.mean((y_true - y_pred) ** 2))


def mean_absolute_error(y_true, y_pred):
    """Error medio absoluto sobre todos los elementos."""
    return float(np.mean(np.abs(y_true - y_pred)))


def accuracy_within_threshold(y_true_world, y_pred_world, threshold):
    """Porcentaje de ejemplos cuyo error espacial es menor a `threshold`
    unidades del mundo.

    DECISIÓN DE DISEÑO: la consigna pide el "porcentaje de predicciones
    cuyo error sea menor a 0.5 unidades". Como cada predicción son en
    realidad DOS puntos (P1 y P2), se define el error de una muestra como
    el promedio de las distancias euclídeas predicho-vs-ideal de P1 y de
    P2, ambas en unidades del mundo (no normalizadas), ya que "0.5
    unidades" se interpreta como unidades del espacio original [0, 10],
    no del espacio normalizado [0, 1].
    """
    error_p1 = np.linalg.norm(y_true_world[:, 0:2] - y_pred_world[:, 0:2], axis=1)
    error_p2 = np.linalg.norm(y_true_world[:, 2:4] - y_pred_world[:, 2:4], axis=1)
    per_sample_error = (error_p1 + error_p2) / 2.0

    within_threshold = per_sample_error < threshold
    return float(np.mean(within_threshold) * 100.0)


def evaluate_model(model, X_test_norm, y_test_norm, world_size, threshold):
    """Corre el modelo sobre el conjunto de prueba y calcula todas las
    métricas pedidas por la consigna: MSE, MAE y porcentaje dentro del
    umbral de error. Devuelve un diccionario con los resultados."""
    y_pred_norm = model.predict(X_test_norm)

    mse_normalizado = mean_squared_error(y_test_norm, y_pred_norm)
    mae_normalizado = mean_absolute_error(y_test_norm, y_pred_norm)

    y_true_world = y_test_norm * world_size
    y_pred_world = y_pred_norm * world_size
    mae_mundo = mean_absolute_error(y_true_world, y_pred_world)
    precision_pct = accuracy_within_threshold(y_true_world, y_pred_world, threshold)

    return {
        "mse_normalizado": mse_normalizado,
        "mae_normalizado": mae_normalizado,
        "mae_mundo": mae_mundo,
        "precision_pct": precision_pct,
    }
