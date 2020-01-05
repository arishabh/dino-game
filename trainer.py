import pygame
from time import time
import random

black = (0,0,0)
red = (255, 0, 0)
white = (255, 255, 255)
grey = (100, 100, 100)
path = "templates/"

class Dino:
    size = 60
    def __init__(self, y=330):
        self.IMGS = list(map(lambda x: pygame.transform.scale(x, (self.size, self.size)), [pygame.image.load(path+"run1.png"), pygame.image.load(path+"run2.png"), pygame.image.load(path+"jump.png")]))
        #Add 4 dinosor images, 2 legs, jump and duck 
        self.IMGS.append(pygame.transform.scale(pygame.image.load(path+"duck.png"), (77, 36)))
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
        if(self.tick%10 == 0): self.img = self.IMGS[0]
        elif(self.tick%10 == 5): self.img = self.IMGS[1]
        if(self.get_bottom() < self.ground): self.img = self.IMGS[2]
        if duck: self.img = self.IMGS[3]

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
    def __init__(self, y=330, score=0):
        self.IMGS = []
        for i in range(5):
            img = pygame.image.load(path+"tree"+str(i+1)+".png")
            if i == 0: img = pygame.transform.scale(img, (25, 50))
            elif i == 1: img = pygame.transform.scale(img, (27, 60))
            elif i == 2: img = pygame.transform.scale(img, (100, 65))
            elif i > 2: img = pygame.transform.scale(img, (65, 65)) 
            self.IMGS.append(img)
        self.IMGS.append(pygame.image.load(path+"bird.png"))

        self.img = random.choice(self.IMGS)
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1] 
        if self.IMGS.index(self.img) == 5: 
            self.height += 20
            if score > 400:
                self.height += 30
            if score > 1000:
                self.height += 65
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

class Ground:
    def __init__(self, y=400, x=0):
        self.img = pygame.image.load(path+"back.png")
        self.width = self.img.get_size()[0]
        self.height = self.img.get_size()[1]
        self.x = x
        self.y = y-self.height

    def update(self):
        self.x -= 10

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))
        
def main():
    pygame.init()

    size = [1200,400]
    ground = size[1]-115
    quit = False
    clock_spd = 30

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)

    dino = Dino(ground)
    obs = []
    gr = [Ground()]
    freq = 0
    start = round(time(), 1)
    jump = False
    duck = False
    score = 0
    while not quit:
        if(round(time(), 1)-start > freq):
            obs.append(Obsticle(ground, score))
            freq = round(random.uniform(1.4, 2.4), 1)
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

        rem = []
        for g in gr:
            if g.x+g.width == size[0]:
                gr.append(Ground(x=size[0]))
            if g.x+g.width <= 0 and g not in rem:
                rem.append(g)

        for g in rem:
            gr.remove(g)

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
        for g in gr:
            g.update()
            g.draw(screen)
        for ob in obs:
            ob.update()
            ob.draw(screen)
        dino.draw(screen)
        font = pygame.font.Font(path+'dpcomic.ttf', 30)
        mes = font.render(str(int(score)), True, grey)
        screen.blit(mes, [40, 40])
        pygame.display.update()
        score += 0.3
        if round(score%50) == 0 and score > 200: clock_spd += 2

    pygame.quit()

main()
