import pygame
import os
import sys
import random

########################## OPTIONS ##########################
tile_size = 64
zoom = 5
sprite_acts = ["Idle", "Walk", "Run"]
#############################################################

loaded_sprites = {}
sprite_dirs = ["Down", "Left", "Right", "Up"]
img_dir = lambda fname: ".\\{}".format(fname)
keys = []
sprite_img_extension = ".png"

class Sprite(object):
    def __init__(self, name, position=(0,0)):
        self.name = name
        self.group = "Idle_Down"
        self.frame = 0
        self.time_held = {}
        for x in sprite_acts:
            for y in sprite_dirs:
                self.time_held["{}_{}".format(x, y)] = 0
        self.pos = position
        self.facing = "Down"

        if not self.name in loaded_sprites:
            loaded_sprites[self.name] = {}
            img_path = lambda filename: img_dir("{}\\sprites\\{}".format(self.name, filename))
            for action in sprite_acts:
                img_pack = img_path("{}{}".format(action, sprite_img_extension))
                if os.path.isfile(img_pack):
                    for direction in sprite_dirs:
                        tmp = pygame.image.load(img_pack)
                        y = sprite_dirs.index(direction) * tile_size
                        folder = "{}_{}".format(action, direction)
                        loaded_sprites[self.name][folder] = []
                        for x in xrange(0, tmp.get_width(), tile_size):
                            print action, direction, x, y
                            tmp2 = load_sprite(img_pack, (x, y), (tile_size, tile_size))
                            loaded_sprites[self.name][folder].append(tmp2)
                    print loaded_sprites[self.name]
                    del tmp, tmp2, direction, folder, x, y, img_pack
                else:
                    for direction in sprite_dirs:
                        folder = "{}_{}".format(action, direction)
                        loaded_sprites[self.name][folder] = []
                        if os.path.isdir(img_path(folder)):
                            x = 0
                            while True:
                                file = img_path("{}\\{}{}".format(folder, x, sprite_img_extension))
                                if os.path.isfile(file):
                                    loaded_sprites[self.name][folder].append(load_sprite(file))
                                else:
                                    break
                                x += 1
                        if not len(loaded_sprites[self.name][folder]):
                            loaded_sprites[self.name][folder].append(load_sprite(img_dir("sprite_error.png")))

    def animate(self, action="Idle", heading=None):
        if heading is not None:
            self.facing = heading
        self.group = "{}_{}".format(action, self.facing)
        self.frame = (self.time_held[self.group] / (40 / len(loaded_sprites[self.name][self.group]))) % len(loaded_sprites[self.name][self.group])
        self.time_held[self.group] += 1

    def get_rect(self):
        return pygame.Rect(self.pos, loaded_sprites[self.name][self.group][0].get_size())

    def reset_idle(self):
        for x in sprite_dirs:
            self.time_held["Idle_{}".format(x)] = 0

    def draw(self, pos=None):
        if pos is not None:
            self.pos = pos
        screen.blit(loaded_sprites[self.name][self.group][self.frame], self.pos)

def load_sprite(file, topleft=(0,0), size=(64,64)):
    tmp = pygame.image.load(file).convert()
    img = pygame.Surface(size)
    img.blit(tmp, (0,0), topleft+size)
    del tmp
    img.set_colorkey((0, 255, 0)) # Completely Transparent
    img = img.convert_alpha()
    px = pygame.PixelArray(img)
    px.replace((0, 254, 0), (  0,   0,   0, 128)) # Half transparent black.
    px.replace((0, 253, 0), (255, 255, 255, 128)) # Half transparent white.
    px.replace((0, 252, 0), (  0,   0, 255, 128)) # Half transparent blue.
    px.replace((0, 251, 0), (  0, 255,   0, 128)) # Half transparent green.
    px.replace((0, 250, 0), (255,   0,   0, 128)) # Half transparent red.
    del px
    return img

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
clock = pygame.time.Clock()
path = os.path.curdir
screen = pygame.display.set_mode((64*zoom,64*zoom))
sprite = Sprite("Test")
for i1 in loaded_sprites:
    for i2 in loaded_sprites[i1]:
        for i3 in xrange(len(loaded_sprites[i1][i2])):
            loaded_sprites[i1][i2][i3] = pygame.transform.scale(loaded_sprites[i1][i2][i3], screen.get_size())
frame=0
while True:
    clock.tick(32)
    frame += 1
    color_phase = frame / 255 % 6
    x = frame % 255
    if color_phase == 0:
        screen.fill((x,0,0))
    elif color_phase == 1:
        screen.fill((255,x,x))
    elif color_phase == 2:
        screen.fill((0,x,0))
    elif color_phase == 3:
        screen.fill((x,255,x))
    elif color_phase == 4:
        screen.fill((0,0,x))
    elif color_phase == 5:
        screen.fill((x,x,255))
    if frame % 1000 == 0:
        print clock.get_fps()
    if pygame.K_LSHIFT in keys:
        act = "Run"
    else:
        act = "Walk"
    if pygame.K_w in keys:
        sprite.animate(act, "Up")
    elif pygame.K_a in keys:
        sprite.animate(act, "Left")
    elif pygame.K_s in keys:
        sprite.animate(act, "Down")
    elif pygame.K_d in keys:
        sprite.animate(act, "Right")
    else:
        sprite.animate()
    sprite.draw()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            keys.append(event.key)
        elif event.type == pygame.KEYUP:
            keys.remove(event.key)
