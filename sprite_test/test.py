import pygame
from pygame.locals import *
import os
import sys
from copy import copy, deepcopy

BLOCK = 32
STEP = 2

TRANS = (0, 255, 0)
CLOCK = pygame.time.Clock()

DOWN = "Down"
LEFT = "Left"
RIGHT = "Right"
UP = "Up"

W = pygame.K_w
A = pygame.K_a
S = pygame.K_s
D = pygame.K_d
move_keys = [W, A, S, D]
SHIFT = pygame.K_LSHIFT

global table
table = {}
table[W] = UP
table[UP] = W
table[A] = LEFT
table[LEFT] = A
table[S] = DOWN
table[DOWN] = S
table[D] = RIGHT
table[RIGHT] = D

global keys
keys = {"move":[],"other":[]}

global playerpos, targetpos, player_rect
playerpos = [0,0]
targetpos = [0,0]
player_rect = (0,0)

path = ".\\"
img_dir = lambda fname: "{}{}".format(path, fname)
sprite_acts = ["Idle", "Walk", "Run"]
sprite_dirs = ["Up", "Left", "Down", "Right"]
loaded_sprites = {}

screen = pygame.display.set_mode((1024,512))
screen_rect = screen.get_rect()
screen_center = screen_rect.center

def pos2rect(pos, size=(64,64)):
    new_pos = deepcopy(pos)
    for x in xrange(2):
        new_pos[x] = pos[x] * 32
    rect = pygame.Rect(tuple(new_pos), size)
    return rect

def update_pos():
    global player_rect
    player_rect = pos2rect(playerpos)
    return None

def draw_world():
    CLOCK.tick(32)
    screen.fill((255,255,255))
    if len(keys["move"]):
        if SHIFT in keys["other"]:
            sprites["p"].animate("Run", table[keys["move"][0]])
        else:
            sprites["p"].animate("Walk", table[keys["move"][0]])
    else:
        sprites["p"].animate("Idle")
    for x in sprites:
        screen.blit(loaded_sprites[sprites[x].name][sprites[x].group][sprites[x].frame], sprites[x].get_rect())
    pygame.display.flip()

    for event in pygame.event.get():
        #print event
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key in move_keys:
                keys["move"].append(event.key)
                if SHIFT in keys["other"]:
                    sprites["p"].time_held["{}_{}".format("Run", table[event.key])] = 10
                else:
                    sprites["p"].time_held["{}_{}".format("Walk", table[event.key])] = 10
            else:
                keys["other"].append(event.key)
        elif event.type == pygame.KEYUP:
            if event.key in move_keys:
                try:
                    keys["move"].remove(event.key)
                except:
                    None
                sprites["p"].reset_idle()
            else:
                try:
                    keys["other"].remove(event.key)
                except:
                    None
    if SHIFT in keys["other"]:
        STEP = 4
    else:
        STEP = 2
    for i in xrange(len(keys["move"])):
        if keys["move"][i] == W:
            sprites["p"].pos = (sprites["p"].pos[0], sprites["p"].pos[1] - (STEP / (i + 1)))
        if keys["move"][i] == A:
            sprites["p"].pos = (sprites["p"].pos[0] - (STEP / (i + 1)), sprites["p"].pos[1])
        if keys["move"][i] == S:
            sprites["p"].pos = (sprites["p"].pos[0], sprites["p"].pos[1] + (STEP / (i + 1)))
        if keys["move"][i] == D:
            sprites["p"].pos = (sprites["p"].pos[0] + (STEP / (i + 1)), sprites["p"].pos[1])
    
class Sprite(object):
    def __init__(self, name, transparent=TRANS):
        self.name = name
        self.group = "Idle_Down"
        self.frame = 0
        self.time_held = {}
        for x in sprite_acts:
            for y in sprite_dirs:
                self.time_held["{}_{}".format(x, y)] = 0
        self.pos = screen.get_rect().center
        self.trans = transparent
        self.facing = "Down"

        if not self.name in loaded_sprites:
            loaded_sprites[self.name] = {}
            img_path = lambda filename: img_dir("{}\\sprites\\{}".format(self.name, filename))
            for action in sprite_acts:
                for direction in sprite_dirs:
                    folder = "{}_{}".format(action, direction)
                    loaded_sprites[self.name][folder] = []
                    if os.path.isdir(img_path(folder)):
                        x = 0
                        while True:
                            file = img_path("{}\\{}.png".format(folder, x))
                            if os.path.isfile(file):
                                loaded_sprites[self.name][folder].append(pygame.image.load(file).convert())
                                loaded_sprites[self.name][folder][-1].set_colorkey(self.trans)
                            else:
                                break
                            x += 1
                    if not len(loaded_sprites[self.name][folder]):
                        loaded_sprites[self.name][folder].append(pygame.image.load(img_dir("default.png")))
                        loaded_sprites[self.name][folder][-1].set_colorkey(self.trans)

    def animate(self, action="Idle", heading=None):
        if heading is not None:
            self.facing = heading
        self.group = "{}_{}".format(action, self.facing)
        self.frame = (self.time_held[self.group] / 10) % len(loaded_sprites[self.name][self.group])
        self.time_held[self.group] += 1
        return loaded_sprites[self.name][self.group][self.frame]

    def get_rect(self):
        return pygame.Rect(self.pos, loaded_sprites[self.name][self.group][0].get_size())

    def reset_idle(self):
        for x in sprite_dirs:
            self.time_held["Idle_{}".format(x)] = 0

global heading_hold, speed
heading_hold = [0,0,0,0]
speed = [0,0,0,0]

global sprite_group, sprite_frame, frame
sprite_group, sprite_frame, frame = 0, 0, 0
cont = True
sprites = {"p":Sprite("Test")}

while cont:
    draw_world()