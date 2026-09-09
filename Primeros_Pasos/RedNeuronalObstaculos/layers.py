"""
layers.py
---------
Bloque de construcción básico de la red: una capa densa (fully connected)
con su función de activación, y las funciones de activación disponibles.
Tanto forward como backward (propagación hacia adelante y hacia atrás) se
implementan a mano con NumPy, sin usar ningún framework de deep learning.
"""

import numpy as np


# =====================================================================
# FUNCIONES DE ACTIVACIÓN
# =====================================================================
def relu(z):
    """Activación ReLU: max(0, z). Se usa en las capas ocultas, tal como
    pide la consigna."""
    return np.maximum(0.0, z)


def relu_derivative(z):
    """Derivada de ReLU respecto a su entrada (evaluada en la
    pre-activación z, antes de aplicar la propia ReLU)."""
    return (z > 0).astype(z.dtype)


def linear(z):
    """Activación lineal (identidad). Se usa en la capa de salida: como
    P1 y P2 son coordenadas continuas normalizadas, no tiene sentido
    "aplastarlas" con una sigmoide u otra activación acotada; dejamos que
    la red produzca directamente el valor real (luego se compara contra
    las coordenadas normalizadas en [0, 1] mediante el error MSE)."""
    return z


def linear_derivative(z):
    """Derivada de la activación lineal: siempre 1."""
    return np.ones_like(z)


ACTIVATIONS = {
    "relu": (relu, relu_derivative),
    "linear": (linear, linear_derivative),
}


class DenseLayer:
    """Una capa totalmente conectada: y = activacion(x @ W + b).

    Guarda en caché la entrada y la pre-activación de la última llamada a
    forward(), porque backward() las necesita para calcular los gradientes
    (regla de la cadena).
    """

    def __init__(self, input_size, output_size, activation="relu", rng=None):
        rng = rng if rng is not None else np.random.default_rng()

        # Inicialización de pesos: "He" para ReLU (escala sqrt(2/entradas),
        # pensada para que la varianza de las activaciones no explote ni se
        # desvanezca al pasar por varias capas ReLU) y "Xavier" para la capa
        # lineal de salida (escala sqrt(1/entradas), la elección estándar
        # cuando no hay una no-linealidad después).
        if activation == "relu":
            scale = np.sqrt(2.0 / input_size)
        else:
            scale = np.sqrt(1.0 / input_size)

        self.weights = rng.normal(loc=0.0, scale=scale, size=(input_size, output_size))
        self.bias = np.zeros((1, output_size))

        self.activation_fn, self.activation_derivative_fn = ACTIVATIONS[activation]

        # Cachés para backward().
        self._last_input = None
        self._last_preactivation = None

    def forward(self, x):
        """Propagación hacia adelante: calcula y guarda z = xW + b y
        devuelve activacion(z)."""
        self._last_input = x
        z = x @ self.weights + self.bias
        self._last_preactivation = z
        return self.activation_fn(z)

    def backward(self, grad_output, learning_rate):
        """Propagación hacia atrás (regla de la cadena) + descenso por
        gradiente.

        `grad_output` es dL/d(salida_de_esta_capa), ya promediado sobre el
        batch (ver neural_network.py). A partir de ahí:
            grad_z       = dL/dz               (aplica la derivada de la activación)
            grad_weights = dL/dW = x^T @ grad_z
            grad_bias    = dL/db = suma de grad_z sobre el batch
            grad_input   = dL/dx = grad_z @ W^T  (se lo pasamos a la capa anterior)

        Actualiza los pesos con descenso por gradiente y devuelve grad_input
        para que la capa anterior pueda seguir retropropagando el error.
        """
        grad_z = grad_output * self.activation_derivative_fn(self._last_preactivation)

        grad_weights = self._last_input.T @ grad_z
        grad_bias = np.sum(grad_z, axis=0, keepdims=True)
        grad_input = grad_z @ self.weights.T

        self.weights -= learning_rate * grad_weights
        self.bias -= learning_rate * grad_bias

        return grad_input
