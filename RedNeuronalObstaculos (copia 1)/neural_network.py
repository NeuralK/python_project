"""
neural_network.py
------------------
La red neuronal multicapa (MLP) completa: compone varias DenseLayer,
implementa la propagación hacia adelante, el cálculo del error (MSE), la
retropropagación del error (backpropagation) y el ciclo de entrenamiento
por descenso por gradiente. Todo implementado a mano con NumPy.
"""

import pickle

import numpy as np

from layers import DenseLayer


class MultiLayerPerceptron:
    """MLP genérico: la cantidad y el tamaño de las capas se definen con
    `layer_sizes`, por ejemplo [8, 16, 16, 4] para la arquitectura pedida
    en la consigna (8 entradas, dos capas ocultas de 16, 4 salidas).
    """

    def __init__(self, layer_sizes, hidden_activation="relu", output_activation="linear", seed=None):
        rng = np.random.default_rng(seed)

        self.layer_sizes = list(layer_sizes)
        self.layers = []

        num_layers = len(layer_sizes) - 1
        for i in range(num_layers):
            is_output_layer = (i == num_layers - 1)
            activation = output_activation if is_output_layer else hidden_activation
            self.layers.append(
                DenseLayer(layer_sizes[i], layer_sizes[i + 1], activation=activation, rng=rng)
            )

    # -----------------------------------------------------------------
    # Propagación hacia adelante
    # -----------------------------------------------------------------
    def forward(self, x):
        """Pasa `x` por todas las capas en orden y devuelve la predicción
        final."""
        activation = x
        for layer in self.layers:
            activation = layer.forward(activation)
        return activation

    # -----------------------------------------------------------------
    # Función de error (MSE) y su gradiente
    # -----------------------------------------------------------------
    @staticmethod
    def compute_mse_loss(y_pred, y_true):
        """Error cuadrático medio sobre todos los elementos (todas las
        muestras y las 4 coordenadas de salida)."""
        return np.mean((y_pred - y_true) ** 2)

    def backward(self, y_pred, y_true, learning_rate):
        """Retropropaga el gradiente del error MSE a través de todas las
        capas (de la última a la primera) y actualiza los pesos de cada una
        con descenso por gradiente.

        dMSE/dy_pred = 2 * (y_pred - y_true) / N, donde N es la cantidad
        total de elementos (muestras x salidas). Dividir por N acá hace que
        cada capa reciba un gradiente ya promediado sobre el batch, así
        DenseLayer.backward() no necesita conocer el tamaño del batch.
        """
        total_elements = y_true.size
        grad = 2.0 * (y_pred - y_true) / total_elements

        for layer in reversed(self.layers):
            grad = layer.backward(grad, learning_rate)

    # -----------------------------------------------------------------
    # Entrenamiento
    # -----------------------------------------------------------------
    def train(self, X_train, y_train, epochs, learning_rate, X_val=None, y_val=None, log_every=100):
        """Entrena la red durante `epochs` épocas usando descenso por
        gradiente por lote completo (full-batch): en cada época se calcula
        la predicción y el error sobre TODO el conjunto de entrenamiento, y
        se hace un único paso de actualización de pesos.

        (La consigna pide "descenso de gradiente", no "descenso de
        gradiente estocástico", por eso se usa el lote completo en cada
        época en vez de mini-batches; con 10.000 ejemplos y NumPy
        vectorizado esto sigue siendo rápido.)

        Devuelve un historial con la pérdida de entrenamiento (y de
        validación, si se pasó X_val/y_val) en cada época, útil para
        graficar la curva de aprendizaje.
        """
        history = {"train_loss": [], "val_loss": []}

        for epoch in range(1, epochs + 1):
            y_pred = self.forward(X_train)
            train_loss = self.compute_mse_loss(y_pred, y_train)
            self.backward(y_pred, y_train, learning_rate)
            history["train_loss"].append(train_loss)

            val_loss = None
            if X_val is not None and y_val is not None:
                val_pred = self.forward(X_val)
                val_loss = self.compute_mse_loss(val_pred, y_val)
                history["val_loss"].append(val_loss)

            if epoch == 1 or epoch % log_every == 0 or epoch == epochs:
                message = f"Época {epoch:4d}/{epochs} - MSE entrenamiento: {train_loss:.6f}"
                if val_loss is not None:
                    message += f" - MSE validación: {val_loss:.6f}"
                print(message)

        return history

    # -----------------------------------------------------------------
    # Predicción
    # -----------------------------------------------------------------
    def predict(self, X):
        """Alias de forward(), pensado para usarse fuera del entrenamiento
        (no modifica ningún estado más allá de los cachés internos de cada
        capa)."""
        return self.forward(X)

    # -----------------------------------------------------------------
    # Persistencia del modelo
    # -----------------------------------------------------------------
    def save(self, path):
        """Guarda los pesos, sesgos y la arquitectura de la red en un
        archivo pickle, para poder reutilizar el modelo entrenado sin
        volver a entrenar (por ejemplo, en la visualización)."""
        state = {
            "layer_sizes": self.layer_sizes,
            "weights": [layer.weights for layer in self.layers],
            "biases": [layer.bias for layer in self.layers],
        }
        with open(path, "wb") as f:
            pickle.dump(state, f)

    @classmethod
    def load(cls, path):
        """Reconstruye una MultiLayerPerceptron a partir de un archivo
        guardado con save()."""
        with open(path, "rb") as f:
            state = pickle.load(f)

        model = cls(state["layer_sizes"])
        for layer, weights, bias in zip(model.layers, state["weights"], state["biases"]):
            layer.weights = weights
            layer.bias = bias

        return model
