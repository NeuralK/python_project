import pygame
import neat
import pickle
import os
import math

# --- CONFIGURACIÓN IGUAL AL ORIGINAL ---
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
OBSTACLE = pygame.Rect(400, 200, 50, 200)
GOAL_POS = [700, 300]

# (Acá deberías tener tu clase Ball, la que ya usás siempre)
# class Ball: ....

def test_ai(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # 1. CARGAMOS EL CEREBRO
    with open("mejor_bola.pkl", "rb") as f:
        winner_genome = pickle.load(f)

    # 2. CREAMOS LA RED NEURONAL CON ESE CEREBRO
    net = neat.nn.FeedForwardNetwork.create(winner_genome, config)

    # 3. BUCLE DE PYGAME
    clock = pygame.time.Clock()
    ball = Ball(100, 300) # Creamos UNA sola pelota
    run = True
    
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # SENSORES (los mismos que usaste para entrenar)
        inputs = (ball.x / WIDTH, ball.y / HEIGHT, ...) 
        
        # LA IA DECIDE
        output = net.activate(inputs)
        ball.move(output)

        # DIBUJAR TODO
        win.fill((20, 20, 20))
        pygame.draw.rect(win, (255, 50, 50), OBSTACLE)
        pygame.draw.circle(win, (0, 255, 0), GOAL_POS, 15)
        ball.draw(win)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    test_ai(config_path)