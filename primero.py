import pygame
import neat
import os
import math
import sys

# Configuración de la simulación
WIDTH, HEIGHT = 600, 400
START_POS = (50, 200)   
GOAL_POS = (550, 200)    
OBSTACLE = pygame.Rect(250, 100, 50, 200) # El muro rojo

class Ball:
    def __init__(self):
        self.x, self.y = START_POS
        self.radius = 10
        self.vel = 5
        self.dead = False

    def draw(self, win):
        pygame.draw.circle(win, (0, 150, 255), (int(self.x), int(self.y)), self.radius)

    def move(self, action):
        # 4 salidas para movimiento total
        if action[0] > 0.5: self.y -= self.vel # Arriba
        if action[1] > 0.5: self.y += self.vel # Abajo
        if action[2] > 0.5: self.x += self.vel # Derecha
        if action[3] > 0.5: self.x -= self.vel # Izquierda
        
        # 1. LÍMITES DE LA PANTALLA (No permite salir y mata a la IA si toca el borde)
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.dead = True
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.dead = True
            
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dead = True
        elif self.y + self.radius >= HEIGHT:
            self.y = HEIGHT - self.radius
            self.dead = True

        # 2. COLISIÓN CON EL MURO ROJO (Cálculo más preciso usando un rectángulo virtual)
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
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
    pygame.display.set_caption("Red Neuronal - Reto UTU")
    clock = pygame.time.Clock()
    
    run = True
    while run and len(balls) > 0:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Iterar al revés para evitar errores al eliminar elementos de la lista
        for i in range(len(balls) - 1, -1, -1):
            ball = balls[i]
            
            # SENSORES: Normalizados entre 0 y 1 para que la Red Neuronal los entienda
            dist_x = (GOAL_POS[0] - ball.x) / WIDTH
            dist_y = (GOAL_POS[1] - ball.y) / HEIGHT
            
            # Sensor de distancia al obstáculo (mejora para que detecte mejor)
            dist_to_wall_x = abs(OBSTACLE.centerx - ball.x) / WIDTH
            
            output = nets[i].activate((dist_x, dist_y, dist_to_wall_x))
            ball.move(output)

            # Cálculo de distancia a la meta para la Fitness
            dist_to_goal = math.sqrt((ball.x - GOAL_POS[0])**2 + (ball.y - GOAL_POS[1])**2)
            
            # RECOMPENSAS
            ge[i].fitness += 0.1  # Recompensa por seguir vivo un frame más
            
            if ball.dead:
                ge[i].fitness -= 50 # Castigo fuerte por chocar contra un límite o muro
                balls.pop(i)
                nets.pop(i)
                ge.pop(i)
            elif dist_to_goal < 15:
                ge[i].fitness += 1000 # ¡Premio por llegar a la meta!
                run = False
                break

        # Renderizado visual
        win.fill((30, 30, 30)) 
        pygame.draw.rect(win, (255, 50, 50), OBSTACLE) # Muro
        pygame.draw.circle(win, (0, 255, 0), GOAL_POS, 15) # Punto B
        for b in balls: 
            b.draw(win)
        pygame.display.update()

def run_neat(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    
    # Muestra el progreso en la consola
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    # Corre 50 generaciones como máximo
    p.run(eval_genomes, 50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)