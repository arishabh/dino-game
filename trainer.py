import pygame
import neat
from time import time
import random

black = (0, 0, 0)
red = (255, 0, 0)
white = (255, 255, 255)
grey = (100, 100, 100)
path = "templates/"


class Dino:
    size = 60

    def __init__(self, y=330):
        self.IMGS = list(map(lambda x: pygame.transform.scale(x, (self.size, self.size)),
                             [pygame.image.load(path + "run1.png"), pygame.image.load(path + "run2.png"),
                              pygame.image.load(path + "jump.png")]))
        # Add 4 dinosaur images, 2 legs, jump and duck
        self.IMGS.append(pygame.transform.scale(pygame.image.load(path + "duck.png"), (77, 36)))
        self.img = self.IMGS[0]
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]
        self.x = 50
        self.y = y - self.img.get_size()[1]
        self.vel = 0
        self.tick = 0
        self.gravity = 2
        self.ground = y

    def update(self, duck=False):
        self.tick += 1
        if self.tick % 10 == 0:
            self.img = self.IMGS[0]
        elif self.tick % 10 == 5:
            self.img = self.IMGS[1]
        if self.get_bottom() < self.ground: self.img = self.IMGS[2]
        if duck: self.img = self.IMGS[3]

        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]

        if self.get_bottom() != self.ground: self.vel += self.gravity
        self.y = min(self.ground - self.img.get_size()[1], round(self.y + self.vel))

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def jump(self):
        if self.get_bottom() == self.ground:
            self.vel = -23

    def get_bottom(self):
        return self.y + self.height

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Obstacle:
    def __init__(self, y=330, score=0):
        self.IMGS = []
        for i in range(5):
            img = pygame.image.load(path + "tree" + str(i + 1) + ".png")
            if i == 0:
                img = pygame.transform.scale(img, (25, 50))
            elif i == 1:
                img = pygame.transform.scale(img, (27, 60))
            elif i == 2:
                img = pygame.transform.scale(img, (100, 65))
            elif i > 2:
                img = pygame.transform.scale(img, (65, 65))
            self.IMGS.append(img)
        self.IMGS.append(pygame.image.load(path + "bird.png"))

        self.img = random.choice(self.IMGS)
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]
        if self.IMGS.index(self.img) == 5:
            self.height += 20
            if score > 400:
                self.height += 30
        self.x = 1200
        self.y = y - self.height
        self.ground = y

    def update(self):
        self.x -= 10

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def collided(self, dino):
        dino_mask = dino.get_mask()
        obs_mask = pygame.mask.from_surface(self.img)

        offset = (self.x - dino.x, self.y - dino.y)
        return dino_mask.overlap(obs_mask, offset) is not None

    def crossed(self, dino):
        return dino.x > self.x + self.width

    def out(self):
        return self.x + self.width < 0


class Ground:
    def __init__(self, y=400, x=0):
        self.img = pygame.image.load(path + "back.png")
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]
        self.x = x
        self.y = y - self.height

    def update(self):
        self.x -= 10

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))


def main(genomes, config):
    pygame.init()

    size = [1200, 400]
    ground = size[1] - 115
    quit = False
    clock_spd = 30

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    dinos = []
    nets = []
    ge = []
    obs = []
    gr = [Ground()]
    freq = 0
    start = 0
    score = 0
    tick = 0

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinos.append(Dino(ground))
        g.fitness = 0
        ge.append(g)

    while not quit:
        clock.tick(clock_spd)
        tick += 1
        obs_ind = 0

        if tick >= freq:
            obs.append(Obstacle(ground, score))
            freq = random.randint(35, 130)
            tick = 0

        if len(dinos) > 0:
            if len(obs) > 1 and dinos[0].x > obs[0].x + obs[0].width:
                obs_ind = 1
        else:
            quit = True

        for x, dino in enumerate(dinos):
            dino.update()
            ge[x].fitness += 0.1

            if obs:
                output = nets[x].activate((dino.y, abs(dino.x - obs[obs_ind].x)))

            else:
                output = [0]

            if output[0] > 0.5:
                dino.jump()

        rem = []
        for ob in obs:
            for x, dino in enumerate(dinos):
                if ob.collided(dino):
                    ge[x].fitness -= 1
                    dinos.pop(x)
                    nets.pop(x)
                    ge.pop(x)

            if ob.out() and ob not in rem:
                rem.append(ob)

        for ob in rem:
            obs.remove(ob)

        rem = []
        for g in gr:
            if g.x + g.width == size[0]:
                gr.append(Ground(x=size[0]))
            if g.x + g.width <= 0 and g not in rem:
                rem.append(g)

        for g in rem:
            gr.remove(g)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
                pygame.quit()

        screen.fill(white)
        for g in gr:
            g.update()
            g.draw(screen)
        for ob in obs:
            ob.update()
            ob.draw(screen)
        for dino in dinos:
            dino.draw(screen)
        font = pygame.font.Font(path + 'dpcomic.ttf', 30)
        mes = font.render(str(int(score)), True, grey)
        screen.blit(mes, [40, 40])
        pygame.display.update()
        score += 0.3
        if round(score) % 50 == 0 and score > 200: clock_spd += 2

    pygame.quit()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == '__main__':
    config_path = "config.txt"
    run(config_path)
