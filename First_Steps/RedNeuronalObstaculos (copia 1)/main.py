"""
main.py
-------
Punto de entrada del proyecto. Ejecuta el flujo completo pedido por la
consigna:

    1. Genera el dataset sintético (≈10.000 escenarios).
    2. Normaliza las coordenadas a [0, 1] y separa entrenamiento/prueba.
    3. Entrena una MLP (8 -> 16 -> 16 -> 4) con backpropagation y
       descenso por gradiente, desde cero.
    4. Evalúa el modelo (MSE, MAE, % de aciertos dentro del umbral).
    5. Guarda el modelo entrenado en disco.
    6. Abre la visualización interactiva con Pygame.

Ejecutar con:  python main.py
"""


import numpy as np


from dataset import generate_normalized_dataset
from neural_network import MultiLayerPerceptron
from metrics import evaluate_model
from visualization import run_visualization
import utils


def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():
    rng = utils.create_rng(utils.RANDOM_SEED)

    # -------------------------------------------------------------
    # 1. Generación del dataset
    # -------------------------------------------------------------
    print_header("1. Generando dataset sintético")
    X_norm, Y_norm, X_raw, Y_raw = generate_normalized_dataset(
        num_samples=utils.NUM_SAMPLES, world_size=utils.WORLD_SIZE, rng=rng
    )
    print(f"Se generaron {X_norm.shape[0]} ejemplos "
          f"({X_norm.shape[1]} entradas -> {Y_norm.shape[1]} salidas).")

    # -------------------------------------------------------------
    # 2. Separación entrenamiento / prueba
    # -------------------------------------------------------------
    X_train, y_train, X_test, y_test = utils.train_test_split(
        X_norm, Y_norm, test_ratio=utils.TEST_SPLIT_RATIO, rng=rng
    )
    print(f"Entrenamiento: {X_train.shape[0]} ejemplos | Prueba: {X_test.shape[0]} ejemplos")

    # -------------------------------------------------------------
    # 3. Entrenamiento de la red
    # -------------------------------------------------------------
    print_header("2. Entrenando la red neuronal (MLP con backpropagation)")
    layer_sizes = utils.build_layer_sizes()
    print(f"Arquitectura: {layer_sizes} | learning_rate={utils.LEARNING_RATE} | epochs={utils.EPOCHS}")

    model = MultiLayerPerceptron(layer_sizes, seed=utils.RANDOM_SEED)
    model.train(
        X_train, y_train,
        epochs=utils.EPOCHS,
        learning_rate=utils.LEARNING_RATE,
        X_val=X_test, y_val=y_test,
        log_every=utils.LOG_EVERY,
    )

    # -------------------------------------------------------------
    # 4. Evaluación
    # -------------------------------------------------------------
    print_header("3. Evaluando sobre el conjunto de prueba")
    results = evaluate_model(model, X_test, y_test, utils.WORLD_SIZE, utils.ERROR_THRESHOLD)
    print(f"MSE (normalizado, [0,1]):        {results['mse_normalizado']:.6f}")
    print(f"MAE (normalizado, [0,1]):        {results['mae_normalizado']:.6f}")
    print(f"MAE (unidades del mundo, 0-{utils.WORLD_SIZE:.0f}): {results['mae_mundo']:.4f}")
    print(f"Predicciones con error < {utils.ERROR_THRESHOLD} unidades: {results['precision_pct']:.2f}%")

    # -------------------------------------------------------------
    # 5. Guardado del modelo
    # -------------------------------------------------------------
    model.save(utils.MODEL_PATH)
    print(f"\nModelo guardado en '{utils.MODEL_PATH}'.")

    # -------------------------------------------------------------
    # 6. Visualización interactiva
    # -------------------------------------------------------------
    print_header("4. Abriendo visualizacion interactiva (Pygame)")
    print("Presiona [ESPACIO] para generar un nuevo escenario aleatorio, [ESC] para salir.")
    metrics_summary = (
        f"Metricas (test): MSE={results['mse_normalizado']:.4f}  "
        f"MAE={results['mae_mundo']:.3f}u  "
        f"Precision(<{utils.ERROR_THRESHOLD}u)={results['precision_pct']:.1f}%"
    )
    run_visualization(model, rng, metrics_summary=metrics_summary)


if __name__ == "__main__":
    main()
