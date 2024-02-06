import pygame
import numpy as np

frames_x = 1080
frames_y = 720

class Game:
    def __init__(self, frames_x, frames_y):
        self.frames_x = frames_x
        self.frames_y = frames_y

        self.course = Course(frames_x, frames_y)

    def draw(self, screen):
        self.course.draw(screen)

class Course:
    def __init__(self, frames_x, frames_y):
        self.frames_x = frames_x
        self.frames_y = frames_y

        t = 0
        self.points = []

        while t < 2.1 * np.pi:
            x = 300 * np.cos(t) + frames_x / 2
            y = 300 * np.sin(2*t) + frames_y / 2
            self.points.append([x, y])
            t += 0.1 * np.pi
    def draw(self, screen):
        for i in range(len(self.points) - 1):
            pygame.draw.line(screen, (255, 255, 255), self.points[i], self.points[i+1])

def main():
    pygame.init()
    screen = pygame.display.set_mode((frames_x, frames_y))
    pygame.display.set_caption("Orbits")

    game = Game(frames_x, frames_y)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 0))
        game.draw(screen)
        pygame.display.flip()


if __name__ == '__main__':
    main()