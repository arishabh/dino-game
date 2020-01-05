import pygame
from time import time
import random

black = (0,0,0)
red = (255, 0, 0)
white = (255, 255, 255)

class Dino:
    size = 60
    def __init__(self, y=330):
        self.IMGS = list(map(lambda x: pygame.transform.scale(x, (self.size, self.size)), [pygame.image.load("run1.png"), pygame.image.load("run2.png")]))#Add 3 dinosor images, 2 legsi and duck 
        self.IMGS.append(pygame.transform.scale(pygame.image.load("duck.png"), (77, 36)))
        self.img = self.IMGS[0]
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]
        self.x = 50
        self.y = y-self.img.get_size()[1]
        self.vel = 0
        self.tick = 0
        self.gravity = 2
        self.ground = y
        
    def update(self, duck):
        self.tick += 1
        if(self.tick%10 == 5): self.img = self.IMGS[1]
        elif(self.tick%10 == 0): self.img = self.IMGS[0]
        if(self.get_bottom() < self.ground): self.img = self.IMGS[0]
        if duck: self.img = self.IMGS[2]

        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]

        if self.get_bottom() != self.ground: self.vel += self.gravity
        self.y = min(self.ground-self.img.get_size()[1], round(self.y+self.vel))

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def jump(self):
        if self.get_bottom() == self.ground:
            self.vel = -23

    def get_bottom(self):
        return self.y+self.height

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Obsticle:
    def __init__(self, y=330):
        self.IMGS = []
        for i in range(5):
            img = pygame.image.load("tree"+str(i+1)+".png")
            if i == 0: img = pygame.transform.scale(img, (25, 50))
            elif i == 1: img = pygame.transform.scale(img, (27, 60))
            elif i == 2: img = pygame.transform.scale(img, (100, 65))
            elif i > 2: img = pygame.transform.scale(img, (65, 65)) 
            self.IMGS.append(img)

        self.img = random.choice(self.IMGS)
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]
        self.x = 1200
        self.y = y-self.height
        self.ground = y

    def update(self):
        self.x -= 10

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

    def collided(self, dino):
        dino_mask = dino.get_mask()
        obs_mask = pygame.mask.from_surface(self.img)
        
        offset = (self.x - dino.x, self.y-dino.y)
        return dino_mask.overlap(obs_mask, offset) != None
    
    def crossed(self, dino):
        return dino.x > self.x+self.width

    def out(self):
        return self.x+self.width < 0
        
def main():
    pygame.init()

    size = [1200,400]
    ground = size[1]-40
    quit = False
    clock_spd = 30

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    dino = Dino(ground)
    obs = []
    freq = 0
    start = round(time(), 1)
    jump = False
    duck = False
    score = 0
    while not quit:
        if(round(time(), 1)-start > freq):
            obs.append(Obsticle(ground))
            freq = round(random.uniform(1.4, 2.6), 1)
            start = round(time(), 1)

        rem = []
        for ob in obs:
            if ob.collided(dino):
                # dino.jump()
                pass
            if ob.out() and ob not in rem:
                rem.append(ob)
        
        for ob in rem:
            obs.remove(ob)

        clock.tick(clock_spd)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    jump = True
                if event.key == pygame.K_DOWN:
                    duck = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    jump = False
                if event.key == pygame.K_DOWN:
                    duck = False

        if jump: dino.jump()
        dino.update(duck)

        screen.fill(white)
        for ob in obs:
            ob.update()
            ob.draw(screen)
        dino.draw(screen)
        pygame.display.update()
        score += 1

    pygame.quit()

main()
