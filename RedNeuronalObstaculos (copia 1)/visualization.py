"""
visualization.py
-----------------
Interfaz gráfica con Pygame para inspeccionar visualmente qué tan bien
generaliza la red: dibuja el punto A, el punto B, el obstáculo, la ruta
"ideal" (calculada por geometría) y la ruta predicha por la red, y permite
generar nuevos escenarios aleatorios con solo apretar una tecla, tal como
pide la consigna ("debe ser posible generar muchos escenarios distintos
para comprobar que la red generaliza correctamente").
"""

import numpy as np
import pygame

from geometry import generate_scenario, compute_ideal_waypoints, path_collides_with_obstacle
from utils import WORLD_SIZE

# --- Layout de la ventana ---
WINDOW_SIZE = 540
PADDING = 40                      # margen entre el mundo y el borde de la ventana
HUD_HEIGHT = 110                  # franja superior para texto informativo
WINDOW_WIDTH = 1040
WINDOW_HEIGHT = WINDOW_SIZE + HUD_HEIGHT
TARGET_FPS = 60

# Como WINDOW_WIDTH (1040) es más ancho que el área de dibujo (WINDOW_SIZE,
# 540), sobra espacio horizontal. OFFSET_X centra ese cuadrado de 540px en
# el medio de la ventana, en vez de dejarlo pegado al borde izquierdo con
# todo el resto vacío.
OFFSET_X = (WINDOW_WIDTH - WINDOW_SIZE) // 2

# --- Colores ---
COLOR_BG = (18, 18, 28)
COLOR_HUD_BG = (26, 26, 38)
COLOR_TEXT = (230, 230, 235)
COLOR_TEXT_DIM = (150, 150, 160)
COLOR_OBSTACLE = (220, 60, 70)
COLOR_POINT_A = (240, 200, 80)
COLOR_POINT_B = (70, 230, 130)
COLOR_IDEAL_PATH = (90, 170, 255)
COLOR_PREDICTED_PATH = (255, 140, 60)
COLOR_OK = (70, 230, 130)
COLOR_WARNING = (220, 60, 70)


def world_to_screen(point, world_size=WORLD_SIZE):
    """Convierte un punto en coordenadas del mundo ([0, world_size]) a
    coordenadas de píxel dentro del área de dibujo (debajo del HUD).
    Se suma OFFSET_X para que el cuadrado de dibujo quede centrado
    horizontalmente dentro de la ventana, en vez de pegado al borde
    izquierdo."""
    drawable_size = WINDOW_SIZE - 2 * PADDING
    x = OFFSET_X + PADDING + (point[0] / world_size) * drawable_size
    y = HUD_HEIGHT + PADDING + (point[1] / world_size) * drawable_size
    return int(x), int(y)


def draw_dashed_line(surface, color, start, end, dash_length=8, width=2):
    """Pygame no trae líneas punteadas por defecto; la dibujamos a mano
    para poder distinguir visualmente la ruta ideal de la predicha incluso
    si sus colores llegaran a confundirse."""
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    total_length = np.linalg.norm(end - start)
    if total_length < 1e-6:
        return
    direction = (end - start) / total_length

    distance_covered = 0.0
    draw_segment = True
    while distance_covered < total_length:
        segment_end = min(distance_covered + dash_length, total_length)
        if draw_segment:
            p1 = start + direction * distance_covered
            p2 = start + direction * segment_end
            pygame.draw.line(surface, color, p1, p2, width)
        distance_covered = segment_end
        draw_segment = not draw_segment


class Scenario:
    """Agrupa un escenario aleatorio (A, B, obstáculo) junto con su ruta
    ideal y la predicción actual de la red, para no repetir esta lógica en
    cada frame."""

    def __init__(self, rng, model):
        self.a, self.b, self.o1, self.o2 = generate_scenario(rng, WORLD_SIZE)
        self.ideal_p1, self.ideal_p2 = compute_ideal_waypoints(self.a, self.b, self.o1, self.o2)
        self.predicted_p1, self.predicted_p2 = self._predict(model)

    def _predict(self, model):
        features = np.concatenate([self.a, self.b, self.o1, self.o2]).reshape(1, -1) / WORLD_SIZE
        prediction = model.predict(features)[0] * WORLD_SIZE
        return prediction[0:2], prediction[2:4]

    def ideal_path(self):
        return [self.a, self.ideal_p1, self.ideal_p2, self.b]

    def predicted_path(self):
        return [self.a, self.predicted_p1, self.predicted_p2, self.b]

    def prediction_error(self):
        """Error promedio (distancia euclídea) entre P1/P2 predichos e
        ideales, en unidades del mundo."""
        error_p1 = np.linalg.norm(self.predicted_p1 - self.ideal_p1)
        error_p2 = np.linalg.norm(self.predicted_p2 - self.ideal_p2)
        return (error_p1 + error_p2) / 2.0

    def predicted_path_collides(self):
        return path_collides_with_obstacle(self.predicted_path(), self.o1, self.o2)


def _draw_scenario(screen, font, small_font, scenario, metrics_summary):
    screen.fill(COLOR_BG)

    # --- HUD ---
    pygame.draw.rect(screen, COLOR_HUD_BG, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
    lines = [
        "Red Neuronal para Navegacion con Obstaculos (MLP entrenado con backpropagation)",
        f"Error de este escenario (P1/P2 vs. ideal): {scenario.prediction_error():.3f} unidades"
        + ("  |  RUTA PREDICHA CHOCA CON EL OBSTACULO" if scenario.predicted_path_collides() else ""),
        metrics_summary,
        "[ESPACIO] generar nuevo escenario     [ESC] salir",
    ]
    for i, line in enumerate(lines):
        color = COLOR_WARNING if "CHOCA" in line else COLOR_TEXT
        rendered = (font if i == 0 else small_font).render(line, True, color)
        screen.blit(rendered, (14, 10 + i * 24))

    # --- Obstáculo ---
    pygame.draw.line(screen, COLOR_OBSTACLE, world_to_screen(scenario.o1), world_to_screen(scenario.o2), 6)

    # --- Rutas ---
    ideal_points = [world_to_screen(p) for p in scenario.ideal_path()]
    predicted_points = [world_to_screen(p) for p in scenario.predicted_path()]

    for p1, p2 in zip(ideal_points, ideal_points[1:]):
        draw_dashed_line(screen, COLOR_IDEAL_PATH, p1, p2, dash_length=10, width=3)
    for p1, p2 in zip(predicted_points, predicted_points[1:]):
        pygame.draw.line(screen, COLOR_PREDICTED_PATH, p1, p2, 3)

    for point in ideal_points[1:-1]:
        pygame.draw.circle(screen, COLOR_IDEAL_PATH, point, 5)
    for point in predicted_points[1:-1]:
        pygame.draw.circle(screen, COLOR_PREDICTED_PATH, point, 5, width=2)

    # --- Puntos A y B ---
    a_screen = world_to_screen(scenario.a)
    b_screen = world_to_screen(scenario.b)
    pygame.draw.circle(screen, COLOR_POINT_A, a_screen, 9)
    pygame.draw.circle(screen, COLOR_POINT_B, b_screen, 9)
    screen.blit(small_font.render("A", True, COLOR_TEXT), (a_screen[0] + 10, a_screen[1] - 10))
    screen.blit(small_font.render("B", True, COLOR_TEXT), (b_screen[0] + 10, b_screen[1] - 10))

    # --- Leyenda (centrada dentro del nuevo ancho de la ventana) ---
    legend_y = WINDOW_HEIGHT - 24
    legend_x = OFFSET_X
    pygame.draw.line(screen, COLOR_IDEAL_PATH, (legend_x, legend_y), (legend_x + 30, legend_y), 3)
    screen.blit(small_font.render("Ruta ideal (geometria)", True, COLOR_TEXT_DIM), (legend_x + 36, legend_y - 8))
    legend_x2 = legend_x + 246
    pygame.draw.line(screen, COLOR_PREDICTED_PATH, (legend_x2, legend_y), (legend_x2 + 30, legend_y), 3)
    screen.blit(small_font.render("Ruta predicha (red neuronal)", True, COLOR_TEXT_DIM), (legend_x2 + 36, legend_y - 8))

    pygame.display.flip()


def run_visualization(model, rng, metrics_summary=""):
    """Abre la ventana de Pygame y arranca el bucle interactivo. Cada vez
    que el usuario presiona ESPACIO se genera un escenario nuevo (A, B y
    obstáculo aleatorios) y se muestra, lado a lado, la ruta ideal y la que
    predice la red — así se puede comprobar visualmente que la red
    generaliza a escenarios que nunca vio durante el entrenamiento.
    """
    pygame.init()
    pygame.display.set_caption("Red Neuronal para Navegacion con Obstaculos")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 18, bold=True)
    small_font = pygame.font.SysFont("consolas", 15)

    scenario = Scenario(rng, model)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    scenario = Scenario(rng, model)

        _draw_scenario(screen, font, small_font, scenario, metrics_summary)
        clock.tick(TARGET_FPS)

    pygame.quit()
