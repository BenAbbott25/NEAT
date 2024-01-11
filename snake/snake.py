import pygame, sys, time, random
import numpy as np

class Game:
    def __init__(self, blocks_x, blocks_y, pixels_per_block=10, title = 'Snake Eater'):
        """
        Snake Eater
        Made with PyGame
        """

        # Difficulty settings
        # Easy      ->  10
        # Medium    ->  25
        # Hard      ->  40
        # Harder    ->  60
        # Impossible->  120
        # difficulty = 25
        self.difficulty = 0

        # Window size
        self.frame_size_x = blocks_x * pixels_per_block
        self.frame_size_y = blocks_y * pixels_per_block
        self.pixel_size = pixels_per_block

        self.is_game_over = False
        self.cycles_since_last_food = 0

        # Checks for errors encountered
        check_errors = pygame.init()
        # pygame.init() example output -> (6, 0)
        # second number in tuple gives number of errors
        if check_errors[1] > 0:
            print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
            sys.exit(-1)
        # else:
            # print('[+] Game successfully initialised')


        # Initialise game window
        pygame.display.set_caption('Snake Eater')
        self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y))


        # Colors (R, G, B)
        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.red = pygame.Color(255, 0, 0)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)


        # FPS (frames per second) controller
        self.fps_controller = pygame.time.Clock()


        # Game variables
        self.snake_pos = [int(np.floor(blocks_x/2)*pixels_per_block), int(np.floor(blocks_y/2)*pixels_per_block)]
        self.snake_body = [[self.snake_pos[0], self.snake_pos[1]], [self.snake_pos[0]-pixels_per_block, self.snake_pos[1]], [self.snake_pos[0]-(2*pixels_per_block), self.snake_pos[1]]]

        self.food_pos = [random.randrange(1, (self.frame_size_x//pixels_per_block)) * pixels_per_block, random.randrange(1, (self.frame_size_y//pixels_per_block)) * pixels_per_block]
        self.food_spawn = True

        self.direction = 'RIGHT'
        self.change_to = self.direction

        self.score = 0
        self.cycles = 0

    def get_current_state(self):
        return self.snake_pos, self.snake_body, self.food_pos, self.direction, self.score, self.cycles
    
    def snake_vision(self):
        snake_vision = [0, 0, 0, 0, 0, 0, 0, 0]  # Initialize vision in all eight directions: up, down, left, right, up-right, up-left, down-right, down-left
        count = 1

        # Check upwards
        for i in range(self.snake_pos[1]-self.pixel_size, -self.pixel_size, -self.pixel_size):
            if [self.snake_pos[0], i] == self.food_pos:
                snake_vision[0] = 10/count
                break
            if [self.snake_pos[0], i] in self.snake_body or i < 0:
                snake_vision[0] = -10/count
                break
            count += 1
        count = 1
        
        # Check downwards
        for i in range(self.snake_pos[1]+self.pixel_size, self.frame_size_y, self.pixel_size):
            if [self.snake_pos[0], i] == self.food_pos:
                snake_vision[1] = 10/count
                break
            if [self.snake_pos[0], i] in self.snake_body or i > self.frame_size_y - self.pixel_size:
                snake_vision[1] = -10/count
                break
            count += 1
        count = 1
        
        # Check right
        for i in range(self.snake_pos[0]+self.pixel_size, self.frame_size_x, self.pixel_size):
            if [i, self.snake_pos[1]] == self.food_pos:
                snake_vision[3] = 10/count
                break
            if [i, self.snake_pos[1]] in self.snake_body or i > self.frame_size_x - self.pixel_size:
                snake_vision[3] = -10/count
                break
            count += 1
        count = 1

        # Check left
        for i in range(self.snake_pos[0]-self.pixel_size, -self.pixel_size, -self.pixel_size):
            if [i, self.snake_pos[1]] == self.food_pos:
                snake_vision[2] = 10/count
                break
            if [i, self.snake_pos[1]] in self.snake_body or i < 0:
                snake_vision[2] = -10/count
                break
            count += 1
        count = 1

        # Check up-right
        for i, j in zip(range(self.snake_pos[0]+self.pixel_size, self.frame_size_x, self.pixel_size), range(self.snake_pos[1]-self.pixel_size, -self.pixel_size, -self.pixel_size)):
            if [i, j] == self.food_pos:
                snake_vision[4] = 10/count
                break
            if [i, j] in self.snake_body or i > self.frame_size_x - self.pixel_size or j < 0:
                snake_vision[4] = -10/count
                break
            count += 1
        count = 1

        # Check up-left
        for i, j in zip(range(self.snake_pos[0]-self.pixel_size, -self.pixel_size, -self.pixel_size), range(self.snake_pos[1]-self.pixel_size, -self.pixel_size, -self.pixel_size)):
            if [i, j] == self.food_pos:
                snake_vision[5] = 10/count
                break
            if [i, j] in self.snake_body or i < 0 or j < 0:
                snake_vision[5] = -10/count
                break
            count += 1
        count = 1

        # Check down-right
        for i, j in zip(range(self.snake_pos[0]+self.pixel_size, self.frame_size_x, self.pixel_size), range(self.snake_pos[1]+self.pixel_size, self.frame_size_y, self.pixel_size)):
            if [i, j] == self.food_pos:
                snake_vision[6] = 10/count
                break
            if [i, j] in self.snake_body or i > self.frame_size_x - self.pixel_size or j > self.frame_size_y - self.pixel_size:
                snake_vision[6] = -10/count
                break
            count += 1
        count = 1

        # Check down-left
        for i, j in zip(range(self.snake_pos[0]-self.pixel_size, -self.pixel_size, -self.pixel_size), range(self.snake_pos[1]+self.pixel_size, self.frame_size_y, self.pixel_size)):
            if [i, j] == self.food_pos:
                snake_vision[7] = 10/count
                break
            if [i, j] in self.snake_body or i < 0 or j > self.frame_size_y - self.pixel_size:
                snake_vision[7] = -10/count
                break
            count += 1
        count = 1
    
        return snake_vision


    def perform_action(self, action):
        self.change_to = action

        # Making sure the snake cannot move in the opposite direction instantaneously
        if self.change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        if self.change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        if self.change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        if self.change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'

        # Moving the snake
        if self.direction == 'UP':
            self.snake_pos[1] -= self.pixel_size
        if self.direction == 'DOWN':
            self.snake_pos[1] += self.pixel_size
        if self.direction == 'LEFT':
            self.snake_pos[0] -= self.pixel_size
        if self.direction == 'RIGHT':
            self.snake_pos[0] += self.pixel_size

        # Snake body growing mechanism
        self.snake_body.insert(0, list(self.snake_pos))
        if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
            self.score += 1
            self.food_spawn = False
            self.cycles_since_last_food = 0
        else:
            self.snake_body.pop()

        # Spawning food on the screen
        if not self.food_spawn:
            self.food_pos = [random.randrange(1, (self.frame_size_x//self.pixel_size)) * self.pixel_size, random.randrange(1, (self.frame_size_y//self.pixel_size)) * self.pixel_size]
        self.food_spawn = True

        # Game Over conditions
        # Getting out of bounds
        if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x-self.pixel_size:
            self.game_over()
        if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y-self.pixel_size:
            self.game_over()
        # Touching the snake body
        for block in self.snake_body[1:]:
            if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                self.game_over()

        # Refresh game screen
        pygame.display.update()
        # Refresh rate
        self.fps_controller.tick(self.difficulty)

    # Game Over
    def game_over(self):
        self.is_game_over = True
        my_font = pygame.font.SysFont('times new roman', 90)
        game_over_surface = my_font.render('YOU DIED', True, self.red)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.frame_size_x/2, self.frame_size_y/4)
        self.game_window.fill(self.black)
        self.game_window.blit(game_over_surface, game_over_rect)
        self.show_score(0, self.red, 'times', 20)
        self.show_cycles(0, self.red, 'times', 20)
        pygame.display.flip()
        # time.sleep(3)


    # Score
    def show_score(self, choice, color, font, size):
        score_font = pygame.font.SysFont(font, size)
        score_surface = score_font.render('Score : ' + str(self.score), True, color)
        score_rect = score_surface.get_rect()
        if choice == 1:
            score_rect.midtop = (self.frame_size_x/10, 15)
        else:
            score_rect.midtop = (self.frame_size_x/3, self.frame_size_y/1.25)
        self.game_window.blit(score_surface, score_rect)
        # pygame.display.flip()

    #  Cycles
    def show_cycles(self, choice, color, font, size):
        cycles_font = pygame.font.SysFont(font, size)
        cycles_surface = cycles_font.render('Cycles : ' + str(self.cycles), True, color)
        cycles_rect = cycles_surface.get_rect()
        if choice == 1:
            cycles_rect.midtop = (self.frame_size_x/3, 15)
        else:
            cycles_rect.midtop = (2*self.frame_size_x/3, self.frame_size_y/1.25)
        self.game_window.blit(cycles_surface, cycles_rect)
        # pygame.display.flip()

    def calculate_fitness(self):
        fitness = 10*self.score + self.cycles/1000 - self.cycles_since_last_food/1000

        if self.score == 0:
            fitness -= 10

        return fitness
    
    def draw(self):
        # GFX
        self.game_window.fill(self.black)
        for pos in self.snake_body:
            # Snake body
            # .draw.rect(play_surface, color, xy-coordinate)
            # xy-coordinate -> .Rect(x, y, size_x, size_y)
            pygame.draw.rect(self.game_window, self.green, pygame.Rect(pos[0], pos[1], self.pixel_size, self.pixel_size))

        # Snake food
        pygame.draw.rect(self.game_window, self.white, pygame.Rect(self.food_pos[0], self.food_pos[1], self.pixel_size, self.pixel_size))

        pygame.display.update()

    def handle_inputs(self, inputs):
        max_input_index = inputs.index(max(inputs))
        if max_input_index == 0:
            self.perform_action('UP')
        elif max_input_index == 1:
            self.perform_action('RIGHT')
        elif max_input_index == 2:
            self.perform_action('DOWN')
        elif max_input_index == 3:
            self.perform_action('LEFT')

    def run(self, inputs, lag=0):
        self.handle_inputs(inputs)
        self.draw()
        self.cycles += 1
        self.cycles_since_last_food += 1
        time.sleep(lag)