import pygame
import neat
import pickle
import os
import math


# 1. MISMAS DIMENSIONES DE TU REFERENCIA
WIDTH, HEIGHT = 600, 400
START_POS = (50, 200)
GOAL_POS = (550, 200)
OBSTACLE = pygame.Rect(250, 100, 50, 200)

# 2. TU CLASE BALL ORIGINAL (La que sí funciona)
class Ball:
    def __init__(self):
        self.x, self.y = START_POS
        self.radius = 10
        self.vel = 1
        self.dead = False

    def draw(self, win):
        color = (0, 150, 255) if not self.dead else (70, 100, 200)
        pygame.draw.circle(win, color, (int(self.x), int(self.y)), self.radius)

    def move(self, action):
        if self.dead: return
        # Lógica de activación por neuronas
        if action[0] > 0.6: self.y -= self.vel 
        if action[1] > 0.4: self.y += self.vel 
        if action[2] > 0.5: self.x += self.vel 
        if action[3] > 0.3: self.x -= self.vel 
        # Límites de ventana (Rebotan)
        if self.x < 10: self.x = 10
        if self.x > WIDTH - 10: self.x = WIDTH - 10
        if self.y < 10: self.y = 10
        if self.y > HEIGHT - 10: self.y = HEIGHT - 10

        # Colisión con el muro rojo
        if OBSTACLE.collidepoint(self.x, self.y):
            self.dead = True

def test_ai(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # CARGA DEL PESO APRENDIDO
    with open("velocidad_bola.pkl", "rb") as f:
        winner_genome = pickle.load(f)

    # CREACIÓN DE LA RED BASADA EN EL GANADOR
    net = neat.nn.FeedForwardNetwork.create(winner_genome, config)

    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Testeo de IA - Bola Ganadora")
    clock = pygame.time.Clock()
    
    ball = Ball() # Creamos la pelota única
    
    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # SENSORES IDÉNTICOS A TU ENTRENAMIENTO
        dx = (GOAL_POS[0] - ball.x) / WIDTH
        dy = (GOAL_POS[1] - ball.y) / HEIGHT
        dm = (OBSTACLE.left - ball.x) / WIDTH
        b_sup = ball.y / HEIGHT
        b_inf = (HEIGHT - ball.y) / HEIGHT
        
        # LA IA PROCESA LOS SENSORES
        output = net.activate((dx, dy, dm, b_sup, b_inf))
        ball.move(output)

        # SI TOCA EL VERDE, REINICIA PARA SEGUIR VIÉNDOLA
        dist = math.sqrt((ball.x - GOAL_POS[0])**2 + (ball.y - GOAL_POS[1])**2)
        if dist < 20 or ball.dead:
            ball = Ball() # Se resetea para que la veas de nuevo

        # DIBUJADO
        win.fill((20, 20, 20))
        pygame.draw.rect(win, (255, 50, 50), OBSTACLE)
        pygame.draw.circle(win, (222, 255, 255), GOAL_POS, 15)
        ball.draw(win)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    test_ai(config_path)