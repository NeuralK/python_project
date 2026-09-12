import pygame
import neat
import os
import math
import sys
import pickle # Asegurate de que esto esté arriba del todo
# Dimensiones y posiciones
WIDTH, HEIGHT = 600, 400
START_POS = (50, 200)
GOAL_POS = (550, 200)
OBSTACLE = pygame.Rect(250, 100, 50, 200)

class Ball:
    def __init__(self):
        self.x, self.y = START_POS
        self.radius = 10
        self.vel = 5
        self.dead = False

    def draw(self, win):
        color = (0, 150, 255) if not self.dead else (70, 70, 70)
        pygame.draw.circle(win, color, (int(self.x), int(self.y)), self.radius)

    def move(self, action):
        if self.dead: return
        if action[0] > 0.5: self.y -= self.vel 
        if action[1] > 0.5: self.y += self.vel 
        if action[2] > 0.5: self.x += self.vel 
        if action[3] > 0.5: self.x -= self.vel 
        
        # Límites de ventana (Rebotan)
        if self.x < 10: self.x = 10
        if self.x > WIDTH - 10: self.x = WIDTH - 10
        if self.y < 10: self.y = 10
        if self.y > HEIGHT - 10: self.y = HEIGHT - 10

        # Muro Rojo
        if OBSTACLE.collidepoint(self.x, self.y):
            self.dead = True

def eval_genomes(genomes, config):
    nets, ge, balls = [], [], []
    for _, g in genomes:
        nets.append(neat.nn.FeedForwardNetwork.create(g, config))
        balls.append(Ball())
        g.fitness = 0
        ge.append(g)

    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    
    run = True
    while run and len(balls) > 0:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()


        for i in range(len(balls) - 1, -1, -1):
            ball = balls[i]
            
            # --- SENSORES ---
            dx = (GOAL_POS[0] - ball.x) / WIDTH
            dy = (GOAL_POS[1] - ball.y) / HEIGHT
            dm = (OBSTACLE.left - ball.x) / WIDTH
            b_sup = ball.y / HEIGHT
            b_inf = (HEIGHT - ball.y) / HEIGHT
            
            # --- ACTIVAR RED ---
            output = nets[i].activate((dx, dy, dm, b_sup, b_inf))
            ball.move(output)

            # --- CÁLCULO DE DISTANCIA (ESTO ES LO QUE TE FALTA) ---
            dist = math.sqrt((ball.x - GOAL_POS[0])**2 + (ball.y - GOAL_POS[1])**2)
            ge[i].fitness = (600 - dist) / 10 

            if ball.dead:
                ge[i].fitness -= 100
                balls.pop(i); nets.pop(i); ge.pop(i)
            elif dist < 20: # Ahora 'dist' ya existe y no va a dar error
                ge[i].fitness += 2000
                run = False; break
        win.fill((20, 20, 20))
        pygame.draw.rect(win, (255, 50, 50), OBSTACLE)
        pygame.draw.circle(win, (0, 255, 0), GOAL_POS, 15)
        for b in balls: b.draw(win)
        pygame.display.update()

def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    
    # 1. ACÁ ENTRENA
    winner = p.run(eval_genomes, 1000) 

    # 2. ACÁ GUARDA (TIENE QUE TENER ESTA SANGRÍA SÍ O SÍ)
    with open("mejor_bola1.pkl", "wb") as f:
        pickle.dump(winner, f)
        print("\n--- ARCHIVO GUARDADO CON ÉXITO ---")

   
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)
