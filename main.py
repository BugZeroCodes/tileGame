import pygame as pyg
from pygame.locals import *

pyg.init()

clock = pyg.time.Clock()
fps = 60

width = 1000
height = 1000

src = pyg.display.set_mode((width, height))
pyg.display.set_caption('Platformer')

# define game variables
tileSize = 50
gameRun = 0

# load images
sunImage = pyg.image.load('img/sun.png')
bgImage = pyg.image.load('img/sky.png')

class World(object):
    def __init__(self, data):
        self.tiles = []
        # load images
        dirtImage = pyg.image.load("img/dirt.png")
        grassImage = pyg.image.load("img/grass.png")

        rowCount = 0
        for row in data:
            col = 0
            for t in row:
                if t == 1:
                    img = pyg.transform.scale(dirtImage, (tileSize, tileSize))
                    imgRect = img.get_rect()
                    imgRect.x = col * tileSize
                    imgRect.y = rowCount * tileSize
                    tile = (img, imgRect)
                    self.tiles.append(tile)
                if t == 2:
                    img = pyg.transform.scale(grassImage, (tileSize, tileSize))
                    imgRect = img.get_rect()
                    imgRect.x = col * tileSize
                    imgRect.y = rowCount * tileSize
                    tile = (img, imgRect)
                    self.tiles.append(tile)
                if t == 3:
                    blob = Enemy(col*tileSize, rowCount*tileSize+15)
                    blobGroup.add(blob)
                if t == 6:
                    lava = Lava(col*tileSize, rowCount*tileSize+(tileSize//2))
                    lavaGroup.add(lava)
                col += 1
            rowCount += 1

    def draw(self):
        for tile in self.tiles:
            src.blit(tile[0], tile[1])

class Player(object):
    def __init__(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for n in range(1, 5):
            img_right = pyg.image.load(f'img/guy{n}.png')
            img_right = pyg.transform.scale(img_right, (40, 80))
            img_left = pyg.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.deadImg = pyg.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.dir = 0

    def update(self, gameRun):
        dx = 0
        dy = 0
        walkCooldown = 5

        if gameRun == 0:
            # get keypresses
            key = pyg.key.get_pressed()
            if key[pyg.K_SPACE] and self.jumped == False:
                self.vel_y = -15
                self.jumped = True
            if not key[pyg.K_SPACE]:
                self.jumped = False
            if key[pyg.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.dir = -1
            if key[pyg.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.dir = 1
            if key[pyg.K_LEFT] == False  and key[pyg.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.dir == 1:
                    self.image = self.images_right[self.index]
                else:
                    self.image = self.images_left[self.index]

            # animation
            if self.counter > walkCooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.dir == 1:
                    self.image = self.images_right[self.index]
                if self.dir == -1:
                    self.image = self.images_left[self.index]

            # add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # check collisions
            for t in world.tiles:
                #collision in x direction
                if t[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # collision in y direction
                if t[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # below the ground?
                    if self.vel_y < 0:
                        dy = t[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = t[1].top - self.rect.bottom
                        self.vel_y = 0

            # check enemy collisions
            if pyg.sprite.spritecollide(self, blobGroup, False):
                gameRun = -1
            if pyg.sprite.spritecollide(self, lavaGroup, False):
                gameRun = -1

            # update coordinates
            self.rect.x += dx
            self.rect.y += dy
        elif gameRun == -1:
            self.image = self.deadImg
            if self.rect.y > 200:
                self.rect.y -= 5

        # draw player on screen
        src.blit(self.image, self.rect)

        return gameRun

class Enemy(pyg.sprite.Sprite):
    def __init__(self, x, y):
        pyg.sprite.Sprite.__init__(self)
        self.image = pyg.image.load('img/blob.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.moveDir = 1
        self.moveCounter = 0

    def update(self):
        self.rect.x += self.moveDir
        self.moveCounter += 1
        if self.moveCounter > 50:
            self.moveDir *= -1
            self.moveCounter *= -1

class Lava(pyg.sprite.Sprite):
    def __init__(self, x, y):
        pyg.sprite.Sprite.__init__(self)
        img = pyg.image.load('img/lava.png')
        self.image = pyg.transform.scale(img, (tileSize, tileSize // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

worldData = [
[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
[1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
[1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
[1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
[1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
[1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

lavaGroup = pyg.sprite.Group()
blobGroup = pyg.sprite.Group()

world = World(worldData)
plr = Player(100, height - 130)

run = True
while run:

    clock.tick(fps)

    src.blit(bgImage, (0, 0))
    src.blit(sunImage, (100, 100))

    world.draw()

    if gameRun == 0:
        blobGroup.update()

    gameRun = plr.update(gameRun)

    blobGroup.draw(src)
    lavaGroup.draw(src)

    for e in pyg.event.get():
        if e.type == pyg.QUIT:
            run = False

    pyg.display.update()

pyg.quit()
