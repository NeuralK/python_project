"""
geometry.py
-----------
Toda la geometría del problema: generación aleatoria de escenarios
(A, B y un obstáculo) y el cálculo de la solución "ideal" (P1, P2) que la
red neuronal debe aprender a imitar.

DECISIÓN DE DISEÑO (ambigüedad de la consigna):
La consigna no especifica un algoritmo exacto para calcular P1 y P2, solo
que deben "desviar el trayecto de A a B sin atravesar el obstáculo". Acá
se implementa un heurístico geométrico simple y determinista:

    1. Se calcula la dirección A->B y su perpendicular.
    2. Se identifica qué extremo del obstáculo está más cerca de A
       (proyectándolo sobre la dirección A->B) y cuál más cerca de B.
    3. P1 y P2 son esos extremos "empujados" una distancia CLEARANCE_MARGIN
       en la dirección perpendicular a A->B, del mismo lado para ambos.

Como el obstáculo se genera aproximadamente alineado con la línea A-B (ver
generate_scenario), este heurístico produce un desvío que "bordea" el
obstáculo por un costado, de forma consistente y sin atravesarlo, siempre
que CLEARANCE_MARGIN sea mayor que cero. Es una solución razonable, no la
única posible, y se documenta acá para que quede claro qué se decidió y por qué.
"""

import math
import numpy as np

from utils import (
    OBSTACLE_LENGTH,
    MIN_AB_DISTANCE,
    DOMAIN_MARGIN,
    CLEARANCE_MARGIN,
    OBSTACLE_ANGLE_JITTER_DEG,
    OBSTACLE_PERP_JITTER,
    OBSTACLE_CENTER_T_RANGE,
)


def normalize_vector(vector):
    """Devuelve el vector unitario en la misma dirección que `vector`.
    Si la magnitud es ~0 (vector nulo), lo devuelve sin cambios para
    evitar una división por cero."""
    magnitude = np.linalg.norm(vector)
    if magnitude < 1e-8:
        return vector
    return vector / magnitude


def perpendicular(vector):
    """Devuelve el vector perpendicular a `vector`, rotado 90° en sentido
    antihorario. Se usa para "empujar" puntos hacia un costado del trayecto."""
    return np.array([-vector[1], vector[0]])


def random_point_in_domain(rng, world_size, margin=DOMAIN_MARGIN):
    """Genera un punto (x, y) aleatorio dentro del mundo, respetando un
    margen mínimo respecto a los bordes."""
    return rng.uniform(margin, world_size - margin, size=2)


def generate_scenario(rng, world_size):
    """Genera un escenario aleatorio completo: A, B y un obstáculo.

    El obstáculo se centra sobre (o cerca de) el segmento A-B, con una
    orientación cercana a la dirección A->B y una pequeña variación
    aleatoria de ángulo y de posición perpendicular. Esto garantiza que el
    obstáculo realmente interfiera con el trayecto directo (si no, el
    problema de "evitarlo" sería trivial) y a la vez introduce variedad
    entre escenarios, tal como pide la consigna ("configuraciones
    geométricas variadas").

    Devuelve cuatro arrays de NumPy de forma (2,): a, b, o1, o2.
    """
    while True:
        a = random_point_in_domain(rng, world_size)
        b = random_point_in_domain(rng, world_size)
        if np.linalg.norm(b - a) >= MIN_AB_DISTANCE:
            break

    direction_ab = normalize_vector(b - a)
    perpendicular_ab = perpendicular(direction_ab)

    # Centro del obstáculo: un punto sobre el segmento A-B (con t entre
    # 0.35 y 0.65, para que quede lejos de A y de B), más un pequeño
    # desplazamiento perpendicular aleatorio.
    t = rng.uniform(*OBSTACLE_CENTER_T_RANGE)
    center_on_segment = a + t * (b - a)
    perpendicular_offset = rng.uniform(-OBSTACLE_PERP_JITTER, OBSTACLE_PERP_JITTER)
    obstacle_center = center_on_segment + perpendicular_ab * perpendicular_offset

    # Orientación del obstáculo: la dirección A->B rotada un ángulo
    # aleatorio pequeño, para que no todos los obstáculos sean idénticos.
    angle_jitter = math.radians(rng.uniform(-OBSTACLE_ANGLE_JITTER_DEG, OBSTACLE_ANGLE_JITTER_DEG))
    cos_a, sin_a = math.cos(angle_jitter), math.sin(angle_jitter)
    obstacle_direction = np.array([
        direction_ab[0] * cos_a - direction_ab[1] * sin_a,
        direction_ab[0] * sin_a + direction_ab[1] * cos_a,
    ])

    half_length = OBSTACLE_LENGTH / 2.0
    o1 = obstacle_center - obstacle_direction * half_length
    o2 = obstacle_center + obstacle_direction * half_length

    # Recortamos los extremos del obstáculo para que no queden fuera del mundo.
    o1 = np.clip(o1, 0.0, world_size)
    o2 = np.clip(o2, 0.0, world_size)

    return a, b, o1, o2


def compute_ideal_waypoints(a, b, o1, o2, clearance=CLEARANCE_MARGIN):
    """Calcula los puntos de paso ideales P1 y P2 que rodean el obstáculo
    (ver la explicación del heurístico al principio del archivo).

    P1 corresponde al extremo del obstáculo más cercano a A, y P2 al más
    cercano a B, ambos desplazados `clearance` unidades en la dirección
    perpendicular a A->B.
    """
    direction_ab = normalize_vector(b - a)
    perpendicular_ab = perpendicular(direction_ab)

    projection_o1 = np.dot(o1 - a, direction_ab)
    projection_o2 = np.dot(o2 - a, direction_ab)

    if projection_o1 <= projection_o2:
        obstacle_near_a, obstacle_near_b = o1, o2
    else:
        obstacle_near_a, obstacle_near_b = o2, o1

    p1 = obstacle_near_a + perpendicular_ab * clearance
    p2 = obstacle_near_b + perpendicular_ab * clearance

    return p1, p2


def segments_intersect(p1, p2, p3, p4):
    """Indica si el segmento (p1, p2) cruza al segmento (p3, p4).

    Se usa como herramienta de evaluación/visualización adicional (no pedida
    explícitamente por la consigna, pero útil para "reflexionar sobre...
    limitaciones del enfoque"): permite detectar si el trayecto PREDICHO
    por la red efectivamente choca contra el obstáculo.

    Implementación estándar basada en orientación de tríos de puntos.
    """

    def orientation(p, q, r):
        value = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if abs(value) < 1e-9:
            return 0
        return 1 if value > 0 else 2

    def on_segment(p, q, r):
        return (min(p[0], r[0]) - 1e-9 <= q[0] <= max(p[0], r[0]) + 1e-9 and
                min(p[1], r[1]) - 1e-9 <= q[1] <= max(p[1], r[1]) + 1e-9)

    o1 = orientation(p1, p2, p3)
    o2 = orientation(p1, p2, p4)
    o3 = orientation(p3, p4, p1)
    o4 = orientation(p3, p4, p2)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and on_segment(p1, p3, p2):
        return True
    if o2 == 0 and on_segment(p1, p4, p2):
        return True
    if o3 == 0 and on_segment(p3, p1, p4):
        return True
    if o4 == 0 and on_segment(p3, p2, p4):
        return True

    return False


def path_collides_with_obstacle(points, o1, o2):
    """Recorre una polilínea (lista de puntos consecutivos) y verifica si
    alguno de sus tramos cruza el segmento-obstáculo (o1, o2)."""
    for i in range(len(points) - 1):
        if segments_intersect(points[i], points[i + 1], o1, o2):
            return True
    return False
