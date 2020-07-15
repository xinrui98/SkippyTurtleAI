import pygame
import time
import os
import random
import neat

pygame.font.init()
pygame.init()
pygame.display.set_caption('Skippy Turtle')

WIN_WIDTH = 1000
WIN_HEIGHT = 800

TURTLE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "cute_turtle.png")))
MONSTER_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "monster_cup.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "new_ground.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bgbg.jpg")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Turtle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0
        self.image = TURTLE_IMG
        self.tick_count = 0
        self.jumpCount = 10
        self.isJump = False

    def jump(self):
        if self.isJump:
            if self.jumpCount >= -10:
                self.y -= (self.jumpCount * abs(self.jumpCount)) * 0.5
                self.jumpCount -= 0.5
            else:  # This will execute if our jump is finished
                self.jumpCount = 10
                self.isJump = False
                # Resetting our Variables

    def move(self):
        self.tick_count += 1

        # simple physics formula to emulate gravity
        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        # if off ground
        if self.y <= 630:
            self.y = self.y + d

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Monster:
    VEL = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.passed = False
        self.top = 0
        self.image = MONSTER_IMG

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.image, (self.x, self.y))

    def collide(self, turtle):
        turtle_mask = turtle.get_mask()
        monster_mask = pygame.mask.from_surface(self.image)

        offset = (self.x - turtle.x, self.y - round(turtle.y))

        # returns None if don't collide
        bottom_point = turtle_mask.overlap(monster_mask, offset)

        if bottom_point:
            return True
        return False


class Base:
    VEL = 10
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        # 2 use bases and keep cycling between them while moving to appear as 1 coherent base
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, turtles, monsters, base, score, AI_or_NAH):
    win.blit(BG_IMG, (0, 0))
    for monster in monsters:
        monster.draw(win)

    score_text = STAT_FONT.render("Score: " + str(score), 1, (128, 128, 128))
    win.blit(score_text, (WIN_WIDTH - 10 - score_text.get_width(), 10))

    base.draw(win)
    if AI_or_NAH:
        for turtle in turtles:
            turtle.draw(win)
    else:
        turtles.draw(win)
    pygame.display.update()


def main_manual():
    score = 0
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    turtle = Turtle(230, 630)
    base = Base(730)
    monsters = [Monster(800, 630)]
    clock = pygame.time.Clock()

    run = True
    while run:
        # for every second at most 60 frames should pass
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            turtle.isJump = True
        # check if turtle should jump
        if turtle.isJump:
            turtle.jump()

        remove_monsters = []
        add_monster = False
        for monster in monsters:
            monster.move()

            # check if turtle has passed the monster. if passed, need to generate a new monster
            if not monster.passed and monster.x < turtle.x:
                add_monster = True
                monster.passed = True
                print("passed")

            if monster.x + monster.image.get_width() < 0:
                remove_monsters.append(monster)

            # check for collision
            if monster.collide(turtle):
                print("collided")
                time.sleep(1)
                pygame.quit()

        # after passing monster, add score and add a new monster in place of the old monster
        if add_monster:
            score += 1
            monsters.append(Monster(random.randrange(550, 1000), 630))
        for r in remove_monsters:
            monsters.remove(r)

        base.move()
        draw_window(win, turtle, monsters, base, score, False)
        pygame.display.update()

    pygame.quit()
    quit()


def main_ai(genomes, config):
    nets = []
    ge = []
    turtles = []

    # genomes is a tuple (index, genome_object)
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        turtles.append(Turtle(230, 630))
        g.fitness = 0
        ge.append(g)

    score = 0
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    # turtle = Turtle(230, 630)
    base = Base(730)
    monsters = [Monster(800, 630)]
    clock = pygame.time.Clock()

    run = True
    while run:
        # for every second at most 60 frames should pass
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_SPACE]:
        #     turtle.isJump=True
        # #check if turtle should jump
        # if turtle.isJump:
        #     turtle.jump()

        # there could be 2 monsters, so use distance of turtle and monsters to find out which pipe to reference, either 1st or 2nd
        monster_index = 0
        if len(turtles) > 0:
            if len(monsters) > 1 and turtles[0].x > monsters[0].x + monsters[0].image.get_width():
                monster_index = 1
        # if no turtles left, quit the game
        else:
            run = False
            break

        for x, turtle in enumerate(turtles):
            ge[x].fitness += 0.1

            output = nets[x].activate(
                (turtle.x, abs(turtle.x - monsters[monster_index].x)))
            # output is a list, but there is only 1 value, hence we use ouput[0]
            if output[0] > 0.5:
                turtle.isJump = True
            if turtle.isJump:
                turtle.jump()

        remove_monsters = []
        add_monster = False
        for monster in monsters:
            for x, turtle in enumerate(turtles):
                # check for collision
                if monster.collide(turtle):
                    # reduce fitness score for turtles that hit the monsters and remove them
                    ge[x].fitness -= 1
                    turtles.pop(x)
                    ge.pop(x)
                    nets.pop(x)

                # check if turtle has passed the monster. if passed, need to generate a new monster
                if not monster.passed and monster.x < turtle.x:
                    add_monster = True
                    monster.passed = True
                    print("passed")

            if monster.x + monster.image.get_width() < 0:
                remove_monsters.append(monster)
            monster.move()

        # after passing monster, add score and add a new monster in place of the old monster
        if add_monster:
            score += 1
            # any genomes that are still in this list are still alive, so increase their fitness by 5 after they pass a monster
            for g in ge:
                g.fitness += 5
            # respawn next monsters at random x positions
            monsters.append(Monster(random.randrange(550, 1000), 630))

        for r in remove_monsters:
            monsters.remove(r)

        base.move()
        draw_window(win, turtles, monsters, base, score, True)
        pygame.display.update()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    population = neat.Population(config)

    # give us some stats
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # run the fitness function 50 times
    # winner returns the best genome
    winner = population.run(
        main_ai, 100)


if __name__ == "__main__":
    user_input = int(input("Do you want to play Skippy Turtle manually (1) or watch the AI do its work (2): "))
    # give us path to current directory
    local_directory = os.path.dirname(__file__)
    # finding the absolute path to our file
    config_path = os.path.join(local_directory, "config-feedforward.txt")
    if user_input == 2:
        run(config_path)
    elif user_input == 1:
        main_manual()
    else:
        print("I didn't get that, please try again")
