import pygame, sys, time, random

class SnakeGame:
    def __init__(self):
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
        self.difficulty = 10

        # Window size
        self.frame_size_x = 720
        self.frame_size_y = 480

        self.is_game_over = False

        # Checks for errors encountered
        check_errors = pygame.init()
        # pygame.init() example output -> (6, 0)
        # second number in tuple gives number of errors
        if check_errors[1] > 0:
            print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
            sys.exit(-1)
        else:
            print('[+] Game successfully initialised')


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
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]

        self.food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
        self.food_spawn = True

        self.direction = 'RIGHT'
        self.change_to = self.direction

        self.score = 0
        self.cycles = 0

    def get_current_state(self):
        return self.snake_pos, self.snake_body, self.food_pos, self.direction, self.score, self.cycles
    
    def snake_vision(self):
        snake_vision = [0, 0, 0, 0]  # Initialize vision in all four directions: up, down, left, right
        
        # Check upwards
        for i in range(self.snake_pos[1]-10, -10, -10):
            if [self.snake_pos[0], i] in self.snake_body or i < 0:
                break
            snake_vision[0] += 1
        
        # Check downwards
        for i in range(self.snake_pos[1]+10, self.frame_size_y, 10):
            if [self.snake_pos[0], i] in self.snake_body or i > self.frame_size_y - 10:
                break
            snake_vision[1] += 1
        
        # Check left
        for i in range(self.snake_pos[0]-10, -10, -10):
            if [i, self.snake_pos[1]] in self.snake_body or i < 0:
                break
            snake_vision[2] += 1
        
        # Check right
        for i in range(self.snake_pos[0]+10, self.frame_size_x, 10):
            if [i, self.snake_pos[1]] in self.snake_body or i > self.frame_size_x - 10:
                break
            snake_vision[3] += 1
        
        print(snake_vision)
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
            self.snake_pos[1] -= 10
        if self.direction == 'DOWN':
            self.snake_pos[1] += 10
        if self.direction == 'LEFT':
            self.snake_pos[0] -= 10
        if self.direction == 'RIGHT':
            self.snake_pos[0] += 10

        # Snake body growing mechanism
        self.snake_body.insert(0, list(self.snake_pos))
        if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
            self.score += 1
            self.food_spawn = False
        else:
            self.snake_body.pop()

        # Spawning food on the screen
        if not self.food_spawn:
            self.food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
        self.food_spawn = True

        # Game Over conditions
        # Getting out of bounds
        if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x-10:
            self.game_over()
        if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y-10:
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
        time.sleep(3)
        pygame.quit()
        sys.exit()


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
        fitness = self.score + self.cycles/100
        return fitness
    
    def draw(self):
        # GFX
        self.game_window.fill(self.black)
        for pos in self.snake_body:
            # Snake body
            # .draw.rect(play_surface, color, xy-coordinate)
            # xy-coordinate -> .Rect(x, y, size_x, size_y)
            pygame.draw.rect(self.game_window, self.green, pygame.Rect(pos[0], pos[1], 10, 10))

        # Snake food
        pygame.draw.rect(self.game_window, self.white, pygame.Rect(self.food_pos[0], self.food_pos[1], 10, 10))

        pygame.display.update()