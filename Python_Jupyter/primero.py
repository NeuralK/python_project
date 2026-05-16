import pygame
import neat
import os
import math
import sys

# Configuración
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
        self.reached = False

    def draw(self, win):
        color = (0, 150, 255) if not self.dead else (100, 100, 100)
        pygame.draw.circle(win, color, (int(self.x), int(self.y)), self.radius)

    def move(self, action):
        if self.dead or self.reached: return

        # Movimiento basado en la red neuronal
        if action[0] > 0.5: self.y -= self.vel 
        if action[1] > 0.5: self.y += self.vel 
        if action[2] > 0.5: self.x += self.vel 
        if action[3] > 0.5: self.x -= self.vel 
        
        # Colisión con bordes
        if (self.x - self.radius < 0 or self.x + self.radius > WIDTH or 
            self.y - self.radius < 0 or self.y + self.radius > HEIGHT):
            self.dead = True

        # Colisión con muro rojo
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        if OBSTACLE.colliderect(ball_rect):
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
    
    gen_run = True
    while gen_run and len(balls) > 0:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        for i in range(len(balls) - 1, -1, -1):
            ball = balls[i]
            
            # --- SENSORES MEJORADOS ---
            # 1 y 2: Distancia relativa al objetivo
            dx = (GOAL_POS[0] - ball.x) / WIDTH
            dy = (GOAL_POS[1] - ball.y) / HEIGHT
            
            # 3, 4 y 5: Distancia a los bordes del muro rojo
            d_wall_left = (OBSTACLE.left - ball.x) / WIDTH
            d_wall_top = (OBSTACLE.top - ball.y) / HEIGHT
            d_wall_bottom = (OBSTACLE.bottom - ball.y) / HEIGHT
            
            output = nets[i].activate((dx, dy, d_wall_left, d_wall_top, d_wall_bottom))
            ball.move(output)

            # FITNESS
            dist_to_goal = math.sqrt((ball.x - GOAL_POS[0])**2 + (ball.y - GOAL_POS[1])**2)
            
            # Penalizar por estar lejos, premiar por acercarse
            ge[i].fitness = (600 - dist_to_goal) / 10 

            if ball.dead:
                ge[i].fitness -= 200
                balls.pop(i); nets.pop(i); ge.pop(i)
            elif dist_to_goal < 20:
                ge[i].fitness += 2000
                ball.reached = True
                gen_run = False # Si uno llega, pasamos a la siguiente fase

        # Dibujo limpio
        win.fill((20, 20, 20))
        pygame.draw.rect(win, (255, 50, 50), OBSTACLE) # Muro
        pygame.draw.circle(win, (50, 255, 50), GOAL_POS, 15) # Punto B
        for b in balls: b.draw(win)
        pygame.display.update()

def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.run(eval_genomes, 100000)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)
import pickle

def run_neat(config_path):
    # 1. Cargamos la configuración
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    
    # 2. Creamos la población
    p = neat.Population(config)
    
    # 3. Agregamos el reportero para ver el progreso en la consola
    p.add_reporter(neat.StdOutReporter(True))
    
    # 4. LANZAMOS EL ENTRENAMIENTO (Aquí es donde ocurre la magia)
    # Cambiamos el 100000 por 100 para que sea razonable
    winner = p.run(eval_genomes, 15000) 
    
    # 5. CUANDO TERMINA (porque alguien llegó o pasaron las 100 gen), GUARDA:
    with open("mejor_bola.pkl", "wb") as f:
        pickle.dump(winner, f)
    
    print("\n¡Entrenamiento finalizado! Cerebro ganador guardado en 'mejor_bola.pkl'")

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)