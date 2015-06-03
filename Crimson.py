import pygame
#from pygame.locals import *
#from pygame import *
#import pygame
import math
import random
import os
import pickle
import pygame._view # Allows py2exe to function properly.
import sys # When running an exe file, other Python methods don't work.
from copy import copy, deepcopy

# TEMP
enitity_img_extension = ".png"
sprite_img_extension = ".png"
block_img_extension = ".jpg"

crimson_version = "v0.0.7"

global errors
errors = []

os.environ['SDL_VIDEO_CENTERED'] = '1'

class Debug(object):
    def __init__(self):
        self.enable = True
        self.player_sprite = None
        self.sprite_select = None
        self.sprite_index = 0

    def change_player_sprite(self, new=None):
        self.sprite_select = sprites.keys()
        self.sprite_select.remove("Player")
        self.sprite_select = ["Player"] + self.sprite_select # Makes sure Player is index position 0.
        if new is not None:
            self.player_sprite = Sprite(new)
        else:
            if self.enable:
                self.player_sprite = Sprite(self.sprite_select[self.sprite_index % len(self.sprite_select)])
                self.sprite_index += 1

SEMICOLON = pygame.K_SEMICOLON
debug = Debug()
debug.enable = False

def to_color(value): # Just in case, not actually used yet.
    """Converts either String ("0xFFFFFF") or Number (16777215) to Color ((255,255,255))"""
    if type(value) is not str:
        try:
            value = hex(value)
        except TypeError:
            print "Error: Value must be String or Number!"
            value = "0xFFF"
    string = value.split("x")[-1].split("#")[-1] # Removes leading '#' and '0x'.
    digits = len(string)

    if digits == 3:
        string = "{a}{a}{b}{b}{c}{c}FF".format(a=string[0], b=string[1], c=string[2])
    elif digits == 4:
        string = "{a}{a}{b}{b}{c}{c}{d}{d}".format(a=string[0], b=string[1], c=string[2], d=string[3])
    elif digits == 6:
        string += "FF"
    elif digits < 8:
        while len(string) < 8:
            string += "F"
    elif digits > 8:
        string = string[-8:] # Last eight digits. Ex: "Color = 0xFFFFFFFF"
    hex_str = string.upper()
    int_list = []
    for x in xrange(4):
        try:
            int_list.append(int(hex_str[x*2:x*2+2], 16))
        except ValueError:
            print "Error: '{}' is not a valid hexadecimal pair!".format(hex_str[x*2:x*2+2])
            int_list.append(255)
    color = tuple(int_list)
    return color

# Define Constants
# Colors
BLACK = to_color("0x000")
WHITE = to_color("0xFFF")
HPRED = to_color("0xF00")
MPBLU = to_color("0x07F")
XPGRN = to_color("0x0B0")
TRANS = to_color("0x0F0")

# pygame.MOUSEBUTTONDOWN/UP event.button values are left(1), middle(2), or right(3) mouse buttons, scrollup(4) or scrolldown(5).
LMB = 1 # Left Mouse Button
MMB = 2 # Middle Mouse Button
RMB = 3 # Right Mouse Button
MWU = 4 # Mouse Wheel Up
MWD = 5 # Mouse Wheel Down

DOWN = "Down"
LEFT = "Left"
RIGHT = "Right"
UP = "Up"

W = pygame.K_w
A = pygame.K_a
S = pygame.K_s
D = pygame.K_d
move_keys = [W, A, S, D]

QUIT = pygame.QUIT
TAB = pygame.K_TAB
SHIFT = pygame.K_LSHIFT
ESC = pygame.K_ESCAPE
SPACE = pygame.K_SPACE

SQUARE = pygame.Surface((1,1))

CLOCK = pygame.time.Clock()

STEP = 2 # Pixels per step.
BLOCK = 32 # Size of induvidual blocks in maps.
SPRITE = 64 # Size of normal sprites.

table = {}
table[W] = UP
table[UP] = W
table[A] = LEFT
table[LEFT] = A
table[S] = DOWN
table[DOWN] = S
table[D] = RIGHT
table[RIGHT] = D

# Acronyms:
#  - bs: Battle Screen
#  - tr: Top-Right
#  - lp: Left Panel
#  - tb: Text Box
#  - pm: Party Member
class Settings(object):
    def __init__(self):
        object.__init__(self) # Values are in percent of window size unless otherwise stated.
        self.player_name = "Player One"
        self.bs_draw_enemy_xp = False
        self.win_size = [1024, 512] # Size of the game window in pixels.
        self.top_panel_y = 15 # Height of the Top Panel.
        self.left_panel_x = 15 # Width of the Left Panel.
        self.tr_logo_y = 50 # Height of the Crimson Logo in the topright corner. Width is automatically determined.
        self.lp_bar_y = 7 # Height of Health/Mana/XP bars on the Left Panel
        self.lp_pm_box_x = self.left_panel_x / 6.0 # Width of individual party member selector buttons. Six represents the maximum size of a party.
        self.font_size_x = 1.86 # Max width of normal font.
        self.bs_id_box_x = 12.5 # Width of Battle Screen boxes containing entity images.
        self.bs_id_box_y = 25 # Height of Battle Screen boxes containing entity images.
        self.bs_id_box_marg = [1, 1] # Space between Battle Screen boxes. [x,y]
        self.bs_button_x = 12 # Width of Battle Screen Action buttons.
        self.bs_button_y = 7 # Height of Battle Screen Action buttons.
        self.bs_bar_y = 1 # Height of mini health/mana/XP bars above and below entity images on the Battle Screen.
        self.popup_offset_px = [8, 16]
        self.menu_options = ["Continue", "Save", "Load", "Options", "Quit"]
        self.battle_menu_options = ["End Turn", "Options", "Return to Game", "Quit"] # "Quicksave", "Quickload", "Auto-Battle"?
        self.menu_options += ["Battle", "Add Entity"]##, "Add Item"] #### DEBUG ####
        self.entity_img_types = ["full_health", "half_health", "low_health", "fainted", "sleeping"]
        self.entity_animation_wait = 15
        self.tb_y = 25
        self.tb_name_append = ":"
        self.menu_rgba = to_color("0x222C")
        self.title_buttons = ["New Game", "Load Game", "Settings", "Quit"]

    def change_player_name(self, new_name):
        new_name = str(new_name)
        if new_name != "":
            self.player_name = new_name

settings = Settings()
##settings.change_player_name(raw_input("Enter your name: "))

print "Loading..."

# Creates the pygame window.
pygame.init()
screen = pygame.display.set_mode(settings.win_size)##, FULLSCREEN)
pygame.display.set_caption("Crimson - The Game {}".format(crimson_version))
##pygame.display.toggle_fullscreen()

# Loads the images and prepares the screen.
game_dir = os.path.realpath(".") + "\\"
main_dir = lambda fname="": "{}{}".format(game_dir, fname)
data_dir = lambda fname="": main_dir("data\\{}".format(fname))
img_dir = lambda fname="": main_dir("images\\{}".format(fname))
save_dir = lambda fname="": main_dir("save\\{}".format(fname))
logo =       pygame.image.load(img_dir("Logo.png")).convert_alpha()
background = pygame.transform.smoothscale(pygame.image.load(img_dir("Background.png")), settings.win_size).convert()

def simplify(string):
    #print "Receive: {}".format(repr(string)) #DEBUG
    nums = ["0","1","2","3","4","5","6","7","8","9"]
    if len(string) > 0 and type(string) is str:
        while string[0] == " " or string[0] == "\t":
	    string = string[1:]
	    if len(string) == 0:
		#print 'Return: ""'
		return ""
        if string[0] == "[" and string[-1] == "]":
            if string == "[]":
                string = []
            else:
                string = simplify(string[1:-1] + ",")
        elif string[0] == "'" and string[-1] == "'":
	    if string == "''":
		string = ""
	    else:
		string = string[1:-1]
        elif string.find(",") > 0:
            string = string.split(",")
            for x in xrange(len(string)):
                if len(string[x]) > 0:
                    string[x] = simplify(string[x])
                else:
                    string.pop(x)
        elif string.find("(") != -1 and string.find(")") > string.find("("):
            string = [simplify(string[:string.find("(")]), simplify(string[string.find("(") + 1 : string.find(")")].replace(" ", ","))]
        elif string[0] in nums + [".", "-", "+"]:
            for char in string[1:]:
                if char not in nums + ["."]:
                    #print "Return: {}".format(repr(string)) #DEBUG
                    return string
            if string.find(".") != -1:
                if string.count(".") == 1:
                    if string[0] == ".":
                        if len(string) > 1:
                            if string[1] in nums:
                                string = float(string)
                    else:
                        string = float(string)
            else:
                string = int(string)
        if string == "None" or string == "none":
            string = None
    #print "Return {}".format(repr(string)) #DEBUG
    return string

def read_cdat(fname):
    dat = open(fname)
    l = []
    bracket_open = False
    for line in dat:
        a = line.split("{")
        #print a
        for x in a:
            if x.find("}") == -1:
                a.pop(a.index(x))
                bracket_open = True
            else:
		bracket_open = False
	if bracket_open:
	    continue
        for y in xrange(len(a)):
            a[y] = a[y].split("}")[0]
        l.append(a)
    for x in xrange(len(l)):
        for y in xrange(len(l[x])):
            l[x][y] = simplify(l[x][y])
    dat.close()
    return l

entities, Entities =   {}, {}
attacks, Attacks =     {}, {}
skills, Skills =       {}, {}
items, Items =         {}, {}
sprites, Sprites =     {}, {}
locations, Locations = {}, {}
blocks, Blocks =       {}, {}

raw_entities = read_cdat(data_dir("entities.cdat"))[1:]
for x in xrange(len(raw_entities)):
    if len(raw_entities[x]) > 0:
        n = raw_entities[x][0]
        name = n.replace(" ", "_").lower()
        entities[n] = {}
        entities[n]["base_health"] =       raw_entities[x][1]
        entities[n]["base_energy"] =       raw_entities[x][2]
        entities[n]["base_strength"] =     raw_entities[x][3]
        entities[n]["base_defense"] =      raw_entities[x][4]
        entities[n]["base_dexterity"] =    raw_entities[x][5]
        entities[n]["base_agility"] =      raw_entities[x][6]
        entities[n]["base_intelligence"] = raw_entities[x][7]
        entities[n]["element"] =           raw_entities[x][8]
        entities[n]["attacks"] =           raw_entities[x][9]
        entities[n]["skills"] =            raw_entities[x][10]
        entities[n]["frames"] =            raw_entities[x][11]
        entities[n]["delay"] =             raw_entities[x][12]
        entities[n]["expressions"] =       raw_entities[x][13]
        entities[n]["name_color"] =        raw_entities[x][14][0:-1]
        entities[n]["text_color"] =        raw_entities[x][15]#[0:-1]
del raw_entities
#print entities #TEMP

# Note: str_mod(+1) increases strength by 1, while str_mod(+1.0) increases strength by 100% {str+(str*n)}.
raw_attacks = read_cdat(data_dir("attacks.cdat"))[1:]
for x in xrange(len(raw_attacks)):
    if len(raw_attacks[x]) > 0:
        n = raw_attacks[x][0]
        attacks[n] = {}
        attacks[n]["damage"] = raw_attacks[x][1]
        attacks[n]["accuracy"] = raw_attacks[x][2]
        attacks[n]["type"] = raw_attacks[x][3]
        attacks[n]["element"] = raw_attacks[x][4]
        attacks[n]["energy_cost"] = raw_attacks[x][5]
        attacks[n]["target"] = raw_attacks[x][6]
del raw_attacks

raw_skills = read_cdat(data_dir("skills.cdat"))[1:]
for x in xrange(len(raw_skills)):
    if len(raw_skills[x]) > 0:
        n = raw_skills[x][0]
        skills[n] = {}
        skills[n]["energy_cost"] = raw_skills[x][1]
        skills[n]["target"] =      raw_skills[x][2]
        skills[n]["effect"] =      raw_skills[x][3]
del raw_skills

raw_items = read_cdat(data_dir("items.cdat"))[1:]
for x in xrange(len(raw_items)):
    if len(raw_items[x]) > 0:
        n = raw_items[x][0]
        items[n] = {}
        items[n]["target"] = raw_items[x][1]
        items[n]["effect"] = raw_items[x][2]
del raw_items

raw_sprites = read_cdat(data_dir("sprites.cdat"))[1:]
for x in xrange(len(raw_sprites)):
    if len(raw_sprites[x]) > 0:
        n = raw_sprites[x][0]
        sprites[n] = {}
        sprites[n]["type"] =     raw_sprites[x][1]
        sprites[n]["width"] =    raw_sprites[x][2]
        sprites[n]["height"] =   raw_sprites[x][3]
        sprites[n]["default"] =  raw_sprites[x][4]
        sprites[n]["movement"] = raw_sprites[x][5]
del raw_sprites

raw_locations = read_cdat(data_dir("locations.cdat"))[1:]
for x in xrange(len(raw_locations)):
    if len(raw_locations[x]) > 0:
        n = raw_locations[x][0]
        locations[n] = {}
        locations[n]["blocks"] =  raw_locations[x][1]
        locations[n]["border"] =  raw_locations[x][2]
        locations[n]["sprites"] = raw_locations[x][3]
        locations[n]["items"] =   raw_locations[x][4]
del raw_locations
#print locations

raw_blocks = read_cdat(data_dir("blocks.cdat"))[1:]
for x in xrange(len(raw_blocks)):
    if len(raw_blocks[x]) > 0:
        id = raw_blocks[x][0]
        blocks[id] = {}
        blocks[id]["name"] =     raw_blocks[x][1]
        blocks[id]["type"] =     raw_blocks[x][2]
        blocks[id]["movement"] = raw_blocks[x][3]

#DIRT =       pygame.image.load(img_dir("World\\terrain\\dirt.jpg")).convert()
#SAND =       pygame.image.load(img_dir("World\\terrain\\sand.jpg")).convert()
#GRAVEL =       pygame.image.load(img_dir("World\\terrain\\gravel.jpg")).convert()
#FLAT_STONE =       pygame.image.load(img_dir("World\\terrain\\flat_stone.jpg")).convert()
#SNOW =       pygame.image.load(img_dir("World\\terrain\\snow.jpg")).convert()
#blocks =     {0:DIRT,1:SAND,2:GRAVEL,3:FLAT_STONE,4:SNOW}

# For maintaining aspect ratio when scaling.
# Usage: pygame.transform.smoothscale(image, x_y(image, new_x) or y_x(image, new_y))
x_y = lambda img, new_x: int((new_x / float(img.get_width())) * img.get_height())
y_x = lambda img, new_y: int((new_y / float(img.get_height())) * img.get_width())
wp_x_y = lambda img, new_x: (wp(x=new_x), x_y(img, wp(x=new_x)))
wp_y_x = lambda img, new_y: (y_x(img, wp(y=new_y)), wp(y=new_y))

# Stands for window percent.
def wp(x=None, y=None):
    """Returns the number of pixels, given a percentage of the screen."""
    if x is not None and y is not None:
        newx = (x / 100.0) * settings.win_size[0]
        newy = (y / 100.0) * settings.win_size[1]
        newxy = [int(newx), int(newy)]
    elif x is not None and y is None:
        newx = (x / 100.0) * settings.win_size[0]
        newxy = int(newx)
    elif x is None and y is not None:
        newy = newy = (y / 100.0) * settings.win_size[1]
        newxy = int(newy)
    else:
        newxy = None

    return newxy

def load_game(profile_name):
    data = pickle.load(file(saved_games[profile_name]))
    start_game(data)

#############################################################################
################################# SETTINGS! #################################
#############################################################################

settings.bs_draw_enemy_xp = True

# Define the values to be used when drawing the UI (%).

top_right_logo = pygame.transform.smoothscale(logo, wp_y_x(logo, settings.tr_logo_y))
font = pygame.font.SysFont("Arial", wp(x=settings.font_size_x))
entity_images = {}
saved_games = {}
loaded_sprites = {}
loaded_blocks =  {}
sprite_acts = ["Idle", "Walk", "Run"]
sprite_dirs = ["Down", "Left", "Right", "Up"]

#############################################################################
#############################################################################
#############################################################################

class Crimson(object):
    def __init__(self, player, allies=None, party=None):
        object.__init__(self)
        player.team = player.name
        self.allies = [player]
        self.enemies = [None, None, None]
        if allies is not None:
            self.allies += allies
        if party is None:
            self.party = [0, None, None, None, None, None]
        else:
            self.party = party
        self.items = []
        self.running = True
        self.in_battle = False
        self.has_acted = [] # Tracks all allies who have already done something during the current turn.
        self.animating = False ########## USE THIS!!! #### Or maybe not....?
        self.menu_open = False
        self.bs_center_x, self.bs_center_y = 100, 100
        self.turn = [0, "Player"]
        self.player_team = player.team
        self.bs_selected_button = None
        self.bs_selected_ally =   None
        self.bs_selected_action = None
        self.bs_item_page = 0
        self.bs_button = []
        self.bs_button_text = []
        self.bs_button_text_rect = []
        self.lp_selected_ally = self.allies[self.party[0]]
        self.frame = 0
        self.on_title = True
        self.title_button = []
        self.title_button_text = []
        self.title_button_text_rect = []
        self.title_button_state = 0
        self.is_story_time = False
        self.return_screen = "title"
        self.in_world = False
        self.world = "test"
        self.keys = {"move":[],"other":[]} # Keys currently being pressed.
        self.grid = []
        for x in xrange(settings.win_size[0] / BLOCK):
            self.grid.append([])
            for y in xrange(settings.win_size[1] / BLOCK):
                self.grid[x].append((x*BLOCK,y*BLOCK))
        self.draw_sprites = [] # Draw first, second, third.
        self.cur_map = Location("Test")

        self.bs_id_box, self.bs_id_health_rect, self.bs_id_energy_rect, self.bs_id_xp_rect, self.bs_id_name_rect, self.bs_id_name = [], [], [], [], [], []
        for x in xrange(6): # Gets coordinates for all parts of the battle screen IDs.
            if x < 3:
                top_corner = wp(settings.left_panel_x + settings.bs_id_box_marg[0] * (x+1) + settings.bs_id_box_x * x, settings.top_panel_y + settings.bs_id_box_marg[1] * (((x+1) % 2) * 2 + 1) + settings.bs_bar_y * (2 + 1 * int(settings.bs_draw_enemy_xp)))
            else:
                top_corner = (wp(x=settings.left_panel_x + settings.bs_id_box_marg[0] * (x-2) + settings.bs_id_box_x * (x-3)), wp(y=100 - (settings.bs_id_box_marg[1] * ((x % 2) * 2 + 1) + settings.bs_bar_y * 3 + settings.bs_id_box_y)) + 2)
            self.bs_id_box.append(pygame.Rect(top_corner, wp(settings.bs_id_box_x, settings.bs_id_box_y)))
            pygame.draw.rect(screen, 0, self.bs_id_box[x], 2)
            self.bs_id_health_rect.append(pygame.Rect((0,0), (wp(x=settings.bs_id_box_x) + 1, wp(y=settings.bs_bar_y))))
            self.bs_id_health_rect[x].center = self.bs_id_box[x].center
            self.bs_id_energy_rect.append(pygame.Rect((0,0), (wp(x=settings.bs_id_box_x) + 1, wp(y=settings.bs_bar_y))))
            self.bs_id_energy_rect[x].center = self.bs_id_box[x].center
            self.bs_id_xp_rect.append(pygame.Rect((0,0),     (wp(x=settings.bs_id_box_x) + 1, wp(y=settings.bs_bar_y))))
            self.bs_id_xp_rect[x].center =     self.bs_id_box[x].center
            self.bs_id_name.append(None)
            self.bs_id_name_rect.append(None)

        self.bs_button, self.bs_button_text, self.bs_button_text_rect, self.bs_button_state = [], [], [], 0
        for index in xrange(4): # Gets coordinates for battle screen action buttons.
            self.bs_button.append(pygame.Rect((0,0), wp(settings.bs_button_x, settings.bs_button_y)))
            self.bs_button_text.append(None)
            self.bs_button_text_rect.append(None)
        self.bs_center_x = settings.left_panel_x + settings.bs_id_box_marg[0] * 2 + settings.bs_id_box_x * 1.5 # Percent!
        self.bs_center_y = (self.bs_id_box[4].top + self.bs_id_box[1].bottom) / 2.0                            # Pixels!
        self.bs_button[0].midbottom = (wp(x=self.bs_center_x), self.bs_center_y - wp(y=1))
        self.bs_button[3].midtop =    (wp(x=self.bs_center_x), self.bs_center_y + wp(y=1))
        self.bs_button[1].midright =  (wp(x=self.bs_center_x - settings.bs_button_x / 2.0 - 0.5), self.bs_center_y)
        self.bs_button[2].midleft =   (wp(x=self.bs_center_x + settings.bs_button_x / 2.0 + 0.5), self.bs_center_y)

    def add_ally(self, ally):
        ally.team = self.player_team
        self.allies.append(ally)
        for x in xrange(6):
            if self.party[x] is None:
                self.party[x] = len(self.allies) - 1
                break

    def add_enemy(self, enemy, team="wild"):
        enemy.team = team
        for x in [1,0,2]:
            if self.enemies[x] is None:
                self.enemies[x] = enemy
                return True
        return False

    def quit(self):
        self.running = False
        self.in_battle = False
        self.is_story_time = False
        self.on_title = False
        pygame.quit()
        sys.exit()

    def escape(self, chance, user=None):
        rand_chance = random.randint(1, 100)
        if rand_chance <= chance:
            self.end_battle("escape")
        else:
            print "Couldn't Escape!"

    def enemy_turn(self):
        self.update_bs_buttons()
        self.turn[1] = "Enemy"
        print
        enemies_by_speed = []
        for enemy in self.enemies:
            if enemy is not None:
                if enemy.health > 0:
                    enemy.use_energy(-enemy.get_stat("agi"))
                    enemies_by_speed.append(enemy)
        enemies_by_speed.sort(key=lambda entity: entity.get_stat("agi"), reverse=True)
        for enemy in enemies_by_speed:
            if self.can_player_battle() and self.can_enemy_battle():
                targets, attacks = [], []
                for x in self.party:
                    if x is not None:
                        if self.allies[x].can_battle():
                            targets.append(self.allies[x])
                for x in enemy.attack_list:
                    if x is not None:
                        attacks.append(x)
                target = targets[random.randint(0, len(targets) - 1)]
                attack = attacks[random.randint(0, len(attacks) - 1)]
                # Add check to make sure attack can target enemy!
                attack.use(enemy, target)
        if self.can_player_battle() and self.can_enemy_battle():
            self.player_turn()

    def end_battle(self, result="", special_text=""):
        if result == "win":
            print "\nYou have defeated the enemy!"
        elif result == "lose":
            print "\nYou have been defeated!"
            # Heal allies, deduct points, etc.
        elif result == "escape":
            print "Got Away Safely!"
        elif result == "enemy_escape":
            print "The enemy ran away!"
        elif result == "special":
            print special_text
        else:
            print "Error! Result is '{}', which is not a supported type.".format(result)
            print "Try 'win', 'lose', 'escape', 'enemy_escape', or 'special'."
        self.in_battle = False
        if self.return_screen == "story":
            self.is_story_time = True
        elif self.return_screen == "title":
            self.on_title = True
        else:
            raise NameError("return_screen '{}' is not a valid screen name.".format(self.return_screen))
        self.enemies = [None, None, None]
        for ally in self.allies:
            ally.energy = ally.max_energy
            ally.str_mod = ["+", 0]
            ally.def_mod = ["+", 0]
            ally.dex_mod = ["+", 0]
            ally.agi_mod = ["+", 0]
            ally.int_mod = ["+", 0]
        self.update_bs_buttons()
        self.has_acted = []

        self.turn = [0, "Player"]           #### MOVE THIS TO START_BATTLE! ####

    def can_player_battle(self):
        for x in self.party:
            if x is not None:
                if self.allies[x].can_battle():
                    return True
        if self.in_battle:
            self.end_battle("lose")
        return False

    def can_enemy_battle(self):
        for enemy in self.enemies:
            if enemy is not None:
                if enemy.can_battle():
                    return True
        if self.in_battle:
            self.end_battle("win")
        return False

    def player_turn(self):
        self.turn[0] += 1
        self.turn[1] = "Player"
        print
        print "Turn #{}".format(self.turn[0])
        self.has_acted = []
        for x in self.party:
            if x is not None:
                if self.allies[x].can_battle():
                    print self.allies[x].get_stat("agi")
                    self.allies[x].use_energy(self.allies[x].get_stat("agi") / -2)
                else:
                    self.has_acted.append(self.allies[x]) # So that allies can't battle the same turn they are revived.
        self.can_player_battle()
        self.can_enemy_battle()

    def draw_screen_basics(self, draw_logo=False):
        screen.blit(background, (0, 0)) # Background
        left_panel_x_pix = wp(x=settings.left_panel_x) # Left Panel Width
        pygame.draw.line(screen, 0, (left_panel_x_pix, 0), (left_panel_x_pix, wp(y=100)), 2) # Left Panel Border
        pygame.draw.line(screen, 0, (0, left_panel_x_pix), (left_panel_x_pix, left_panel_x_pix), 2) # Entity Image Border
        if draw_logo:
            pygame.draw.line(screen, 0, wp(settings.left_panel_x, settings.top_panel_y), (wp(x=100) - top_right_logo.get_width(), wp(y=settings.top_panel_y)), 2) # Top Panel Border
            self.top_right_logo_rect = top_right_logo.get_rect()
            self.top_right_logo_rect.topright = wp(x=100) + 1, wp(y=0) - 2
            screen.blit(top_right_logo, self.top_right_logo_rect) # Logo (Top-Right)
            pygame.draw.rect(screen, 0, self.top_right_logo_rect, 2) # Logo Border
        else:
            pygame.draw.line(screen, 0, wp(settings.left_panel_x, settings.top_panel_y), (wp(x=100), wp(y=settings.top_panel_y)), 2) # Top Panel Border

    def draw_left_panel(self):
        self.lp_pmember_button = [None, None, None, None, None, None]
        for member in self.party: # Draws party member selector buttons in bottom left corner.
            if member is not None:
                if self.allies[member].lvl_xp[0] >= self.allies[member].lvl_xp[1]:
                    self.allies[member].level_up()
                member = self.party.index(member)
                self.lp_pmember_button[member] = pygame.Rect(((2 + wp(x=settings.lp_pm_box_x) * member), wp(y=90)), (wp(x=settings.lp_pm_box_x) - 2, wp(y=10) - 2))
                if self.lp_pmember_button[member].collidepoint(pygame.mouse.get_pos()):
                    self.lp_pmember_button[member].move_ip(0, -wp(y=1))
                    lp_pmember_name = font.render("{} ({})".format(self.allies[self.party[member]].name, self.allies[self.party[member]].lvl), True, BLACK)
                    lp_pmember_name_rect = lp_pmember_name.get_rect()
                    lp_pmember_name_rect.midbottom = (wp(settings.left_panel_x / 2.0, 89))
                    screen.blit(lp_pmember_name, lp_pmember_name_rect)
                pygame.draw.rect(screen, BLACK, self.lp_pmember_button[member], 2)

        ally = self.lp_selected_ally

        lp_image = ally.draw_image((0,0), self.frame, wp_x_y(SQUARE, settings.left_panel_x))

        lp_name = font.render(ally.name, True, BLACK)
        lp_name_rect = lp_name.get_rect()
        lp_name_rect.midtop = (wp(x=settings.left_panel_x / 2 + 0.5), wp(x=settings.left_panel_x) + 5)
        screen.blit(lp_name, lp_name_rect)

        lp_lvl = font.render("Lvl: {}".format(ally.lvl), True, BLACK)
        lp_lvl_rect = lp_lvl.get_rect()
        lp_lvl_rect.midtop = [lp_name_rect.centerx, lp_name_rect.bottom + wp(y=1)]
        screen.blit(lp_lvl, lp_lvl_rect)

        lp_health_rect = pygame.Rect(wp(x=1), lp_lvl_rect.bottom + wp(y=1), wp(x=settings.left_panel_x - 2) - 1, wp(y=settings.lp_bar_y - 1) - 1)
        pygame.draw.rect(screen, 0, lp_health_rect, 2)
        draw_health(ally, lp_health_rect)

        lp_energy_rect = pygame.Rect(wp(x=1), lp_lvl_rect.bottom + wp(y=1 + settings.lp_bar_y), wp(x=settings.left_panel_x - 2) - 1, wp(y=settings.lp_bar_y - 1) - 1)
        pygame.draw.rect(screen, 0, lp_energy_rect, 2)
        draw_energy(ally, lp_energy_rect)

        lp_xp_rect = pygame.Rect(wp(x=1), lp_lvl_rect.bottom + wp(y=1 + settings.lp_bar_y * 2), wp(x=settings.left_panel_x - 2) - 1, wp(y=settings.lp_bar_y - 1) - 1)
        pygame.draw.rect(screen, 0, lp_xp_rect, 2)
        draw_xp(ally, lp_xp_rect)

        lp_stats, lp_stat_num = [], 0
        lp_stats.append(font.render("Str: {}".format(ally.get_stat("str", True)), True, BLACK))
        lp_stats.append(font.render("Def: {}".format(ally.get_stat("def", True)), True, BLACK))
        lp_stats.append(font.render("Dex: {}".format(ally.get_stat("dex", True)), True, BLACK))
        lp_stats.append(font.render("Agi: {}".format(ally.get_stat("agi", True)), True, BLACK))
        lp_stats.append(font.render("Int: {}".format(ally.get_stat("int", True)), True, BLACK))
        lp_stats.append(font.render("Elm: {}".format(ally.element), True, BLACK))
        for stat in lp_stats:
            stat_rect = stat.get_rect()
            if lp_stat_num % 2 == 0:
                stat_rect.midleft = wp(x=1.5), wp(x=settings.left_panel_x) + wp(y=(lp_stat_num / 2) * (settings.font_size_x * 2) + settings.lp_bar_y * 5)
            else:
                stat_rect.midleft = wp(x=settings.left_panel_x - 7), wp(x=settings.left_panel_x) + wp(y=(lp_stat_num / 2) * (settings.font_size_x * 2) + settings.lp_bar_y * 5)
            screen.blit(stat, stat_rect)
            lp_stat_num += 1

    def draw_battle_screen(self):
        self.draw_screen_basics(True)
        self.draw_left_panel()

        index = 0
        for enemy in self.enemies: # Draws enemy IDs
            pygame.draw.rect(screen, 0, self.bs_id_box[index], 2)
            if enemy is not None:
                enemy.draw_image(frame=self.frame, pos=self.bs_id_box[index].topleft, size=self.bs_id_box[index].size)
                pygame.draw.rect(screen, 0, self.bs_id_box[index], 2)
                self.bs_id_health_rect[index].bottom = self.bs_id_box[index].top + 1
                self.bs_id_energy_rect[index].bottom = self.bs_id_health_rect[index].top + 1
                pygame.draw.rect(screen, 0, self.bs_id_health_rect[index], 1)
                pygame.draw.rect(screen, 0, self.bs_id_energy_rect[index], 1)
                draw_health(enemy, self.bs_id_health_rect[index], False, 1)
                draw_energy(enemy, self.bs_id_energy_rect[index], False, 1)
                self.bs_id_name[index] = font.render("{} Lvl.{}".format(enemy.name, enemy.lvl), True, BLACK)
                self.bs_id_name_rect[index] = self.bs_id_name[index].get_rect()
                self.bs_id_name_rect[index].midtop = self.bs_id_box[index].midbottom
                self.bs_id_name_rect[index].top += 2
                screen.blit(self.bs_id_name[index], self.bs_id_name_rect[index])
                if settings.bs_draw_enemy_xp:
                    self.bs_id_xp_rect[index].bottom = self.bs_id_energy_rect[index].top + 1
                    pygame.draw.rect(screen, 0, self.bs_id_xp_rect[index], 1)
                    draw_xp(enemy, self.bs_id_xp_rect[index], False, 1)
            index += 1

        index = 3
        for x in [1,0,2]: # Draws ally IDs.
            pygame.draw.rect(screen, 0, self.bs_id_box[index], 2)
            if self.party[x] is not None:
                member = self.allies[self.party[x]]
                member.draw_image(frame=self.frame, pos=self.bs_id_box[index].topleft, size=self.bs_id_box[index].size)
                if member is self.bs_selected_ally:
                    color = (255,0,0)
                else:
                    color = BLACK
                pygame.draw.rect(screen, color, self.bs_id_box[index], 2)
                self.bs_id_health_rect[index].top = self.bs_id_box[index].bottom
                self.bs_id_energy_rect[index].top = self.bs_id_health_rect[index].bottom - 1
                self.bs_id_xp_rect[index].top =     self.bs_id_energy_rect[index].bottom - 1
                pygame.draw.rect(screen, 0, self.bs_id_health_rect[index], 1)
                pygame.draw.rect(screen, 0, self.bs_id_energy_rect[index], 1)
                pygame.draw.rect(screen, 0, self.bs_id_xp_rect[index],     1)
                draw_health(member, self.bs_id_health_rect[index], False, 1)
                draw_energy(member, self.bs_id_energy_rect[index], False, 1)
                draw_xp(member,     self.bs_id_xp_rect[index],     False, 1)
                self.bs_id_name[index] = font.render("{} Lvl.{}".format(member.name, member.lvl), True, BLACK)
                self.bs_id_name_rect[index] = self.bs_id_name[index].get_rect()
                self.bs_id_name_rect[index].midbottom = self.bs_id_box[index].midtop
                self.bs_id_name_rect[index].bottom -= 2
                screen.blit(self.bs_id_name[index], self.bs_id_name_rect[index])
            index += 1

        mouse_pos = pygame.mouse.get_pos()

        if self.bs_button_state: # > 0 (Draws buttons.)
            for index in xrange(4):
                if self.bs_button_text[index] is None:
                    self.bs_button_text[index] = "--"
                if index == self.bs_selected_button:
                    pygame.draw.rect(screen, (255,0,0), self.bs_button[index], 2)
                else:
                    pygame.draw.rect(screen,   BLACK, self.bs_button[index], 2)
                if type(self.bs_button_text[index]) is str:
                    self.bs_button_text[index] = font.render(self.bs_button_text[index], True, BLACK)
                    self.bs_button_text_rect[index] = self.bs_button_text[index].get_rect()
                    self.bs_button_text_rect[index].center = self.bs_button[index].center
                screen.blit(self.bs_button_text[index], self.bs_button_text_rect[index])

        if not self.menu_open:
            for enemy in self.enemies: # Overlay. MUST DRAW LAST!
                if enemy is not None:
                    if self.bs_id_box[self.enemies.index(enemy)].collidepoint(mouse_pos):
                        bs_pop_stats, bs_pop_stats_rect = [], []
                        bs_pop_stats.append(font.render("HP: {}/{}".format(enemy.health, enemy.max_health), True, WHITE))
                        bs_pop_stats.append(font.render("EP: {}/{}".format(enemy.energy, enemy.max_energy), True, WHITE))
                        bs_pop_stats.append(font.render("Str: {}".format(enemy.get_stat("str", True)), True, WHITE))
                        bs_pop_stats.append(font.render("Def: {}".format(enemy.get_stat("def", True)), True, WHITE))
                        bs_pop_stats.append(font.render("Dex: {}".format(enemy.get_stat("dex", True)), True, WHITE))
                        bs_pop_stats.append(font.render("Agi: {}".format(enemy.get_stat("agi", True)), True, WHITE))
                        bs_pop_stats.append(font.render("Int: {}".format(enemy.get_stat("int", True)), True, WHITE))
                        bs_pop_stats.append(font.render("Elm: {}".format(enemy.element), True, WHITE))
                        height, width = 0, []
                        for x in xrange(len(bs_pop_stats)):
                            bs_pop_stats_rect.append(bs_pop_stats[x].get_rect())
                            if x == 0:
                                bs_pop_stats_rect[x].topleft = mouse_pos
                                bs_pop_stats_rect[x].left += settings.popup_offset_px[0] + 2
                                bs_pop_stats_rect[x].top += settings.popup_offset_px[1]
                            else:
                                bs_pop_stats_rect[x].topleft = bs_pop_stats_rect[x-1].bottomleft
                            bs_pop_stats_rect[x].top += 2
                            height += bs_pop_stats_rect[x].height + 2
                            width.append(bs_pop_stats_rect[x].width)
                        width = max(width) + 4
                        enemy_info_popup = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                        enemy_info_popup.fill((settings.menu_rgba))
                        enemy_info_popup_rect = enemy_info_popup.get_rect()
                        enemy_info_popup_rect.topleft = mouse_pos
                        enemy_info_popup_rect.top +=  settings.popup_offset_px[1]
                        enemy_info_popup_rect.left += settings.popup_offset_px[0]
                        screen.blit(enemy_info_popup, enemy_info_popup_rect)
                        pygame.draw.rect(screen, 0, enemy_info_popup_rect, 2)
                        for x in xrange(len(bs_pop_stats)):
                            screen.blit(bs_pop_stats[x], bs_pop_stats_rect[x])

    def is_clicked(self, btn_list, mouse_pos):
        for index in xrange(len(btn_list)):
            if btn_list[index] is not None:
                if btn_list[index].collidepoint(mouse_pos):
                    return index
        return None

    def get_button(self, mouse_pos):
        if self.menu_open:
            check_str = ["menu_popup_button"]
            check = [self.menu_button_rect]
        elif self.on_title:
            check_str = ["title_button"]
            check = [self.title_button]
        elif self.is_story_time:
            check_str = []
            check =     []
        else:
            check_str = ["bs_button", "bs_id_box",    "lp_pmember_button"]
            check =     [ self.bs_button,   self.bs_id_box, self.lp_pmember_button ]
        for index in xrange(len(check)):
            x = self.is_clicked(check[index], mouse_pos)
            if x is not None:
                #print [check_str[index], x] #TEMP
                return [check_str[index], x]

    def get_button_text(self, state, item_page=0):
        if state == 0:
            self.bs_button_text = [None, None, None, None]
        elif state == 1:
            self.bs_button_text = ["Attacks", "Skills", "Items", "Standby"]
        elif self.bs_selected_ally is not None:
            self.bs_button_text = []
            if state == 2:
                for attack in self.bs_selected_ally.attack_list:
                    if attack is not None:
                        self.bs_button_text.append(str(attack.name))
                    else:
                        self.bs_button_text.append(None)
            elif state == 3:
                for skill in self.bs_selected_ally.skill_list:
                    if skill is not None:
                        self.bs_button_text.append(str(skill.name))
                    else:
                        self.bs_button_text.append(None)
            elif state == 4:
                if item_page == 0:
                    if len(self.items) > 2:
                        self.items = sorted(self.items, key=lambda item: item.name)
                    for x in xrange(3):
                        if x >= len(self.items):
                            self.bs_button_text.append(None)
                        elif self.items[[1,0,2][x]] is None:
                            self.bs_button_text.append(None)
                        else:
                            self.bs_button_text.append("{} x {}".format(self.items[[1,0,2][x]].name, self.items[[1,0,2][x]].num))
                    if len(self.items) > 3:
                        self.bs_button_text.append("-->")
                    else:
                        self.bs_button_text.append(None)
                else:
                    self.bs_button_text = self.get_button_text(0)
                    for x in xrange(3):
                        if (item_page * 3) + x >= len(self.items):
                            self.bs_button_text[[1,0,2][x]] = None
                        else:
                            self.bs_button_text[[1,0,2][x]] = "{} x {}".format(self.items[item_page * 3 + x].name, self.items[item_page * 3 + x].num)
                    if item_page * 3 + 4 > len(self.items):
                        self.bs_button_text[3] = "<--"
                    else:
                        self.bs_button_text[3] = "-->"
        return self.bs_button_text

    def draw_start_menu(self, title, options):
        menu_open = True
        while menu_open:
            self.menu_button_rect, menu_popup_button_text, width, height = [], [], [], 0
            if title is not None:
                title_text = font.render(title, True, WHITE)
                title_rect = title_text.get_rect()
                width.append(title_rect.width + 5)
                height += title_rect.height + 2

            for x in xrange(len(options)):
                menu_popup_button_text.append(font.render(options[x], True, WHITE))
                self.menu_button_rect.append(menu_popup_button_text[x].get_rect())
                width.append(self.menu_button_rect[x].width + 5)
                height += self.menu_button_rect[x].height + 2

            width = max(width)
            menu_popup = pygame.Surface((width * 1.5, height), pygame.SRCALPHA, 32)
            menu_popup.fill((settings.menu_rgba))
            menu_popup_rect = menu_popup.get_rect()
            if self.in_battle:
                menu_popup_rect.centerx = wp(x=self.bs_center_x) - 1
                menu_popup_rect.centery = self.bs_center_y
            else:
                center = lambda x: int(x / 2 - 1)
                menu_popup_rect.center = (center(settings.win_size[0]), center(settings.win_size[1]))

            y_offset = 0
            if title is not None:
                title_rect.top = menu_popup_rect.top
                title_rect.top += 1
                title_rect.centerx = menu_popup_rect.centerx + 1
                y_offset += 1
            for x in xrange(len(options)):
                self.menu_button_rect[x].top = menu_popup_rect.top
                self.menu_button_rect[x].top += ((self.menu_button_rect[x].height + 2) * y_offset) + 1
                self.menu_button_rect[x].centerx = menu_popup_rect.centerx + 1
                y_offset += 1

            if self.in_battle:
                self.draw_battle_screen()
            else:
                self.draw_story_screen()
            screen.blit(menu_popup, menu_popup_rect) # Shade area before drawing border.
            pygame.draw.rect(screen, 0, menu_popup_rect, 2)
            # Draw Buttons Here.
            if title is not None:
                screen.blit(title_text, title_rect)
            for x in xrange(len(options)):
                screen.blit(menu_popup_button_text[x], self.menu_button_rect[x])
            pygame.display.flip()

            for menu_event in pygame.event.get():
                if menu_event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = menu_event.pos
                    mouse_button = menu_event.button
                    if mouse_button == LMB:
                        pressed = self.get_button(mouse_pos)
                        if pressed is not None:
                            pressed = options[pressed[1]]
                            if pressed == "Continue" or pressed == "Resume" or pressed == "Back" or pressed == "Return to Game":
                                menu_open = False
                            elif pressed == "Options" or pressed == "Settings":
                                self.draw_start_menu("Options:", ["Graphics", "Sound", "Misc", "Back"])
                            elif pressed == "End Turn":
                                if self.turn[1] == "Player":
                                    self.enemy_turn()
                                    menu_open = False
                            elif pressed == "Quit":
                                really_quit = self.draw_start_menu("Really Quit?", ["Yes", "No"])
                                if really_quit == "Yes":
                                    self.quit()
                            elif pressed == "Yes" or pressed == "No":
                                menu_open = False
                            elif pressed == "Save" or pressed == "Record" or pressed == "Save Game":
                                really_save = self.draw_start_menu("Would you like to save?", ["Yes", "No"])
                                if really_save == "Yes":
                                    self.save()
                                    menu_open = False
                            elif pressed == "Load" or pressed == "Load Game":
                                self.update_profile_list()
                                self.draw_start_menu("Load:", saved_games.keys() + ["Back"])
                                menu_open = False
                            elif pressed in saved_games:
                                menu_open = False
                                load_game(pressed)
                            ##DEBUG:
                            elif pressed == "Battle" or pressed == "Begin Battle":
                                if self.can_player_battle():
                                    game.add_enemy(Entity("Minor Fiend"))##, 2))
                                    game.add_enemy(Entity("Hornet"))##, 25))
                                    #game.add_enemy(Entity("Hornet"))##, 2))
                                    self.in_battle = True
                                    if self.is_story_time:
                                        self.return_screen = "story"
                                        self.is_story_time = False
                                    self.player_turn()
                                else:
                                    print "There's no will to fight!"
                                menu_open = False
                            elif pressed == "Add Item":
                                item_name = raw_input("What would you like to add? ")
                                item_num =  raw_input("How many? ")
                                self.add_item(Item(item_name, int(item_num)))
                                print
                                for x in self.items:
                                    print "{}: {}".format(x.name, x.num)
                            elif pressed == "Add Entity":
                                self.add_ally(Entity("Hornet", 3))
                    elif mouse_button == RMB:
                        pressed = "Right Click"
                        menu_open = False
                elif menu_event.type == pygame.KEYDOWN:
                    if menu_event.key == ESC:
                        pressed = "Escape"
                        menu_open = False
                elif menu_event.type == QUIT:
                    pressed = "Close Window"
                    self.quit()
        return pressed

    def battle(self):
        self.draw_battle_screen()
        pygame.display.flip()
        if self.menu_open:
            self.draw_start_menu("What will you do?", settings.battle_menu_options)
            self.menu_open = False

        for event in pygame.event.get():
            if not self.animating: # Instead, use a while loop to draw the screen and change things.
                if event.type == QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    mouse_button = event.button
                    if mouse_button == LMB:
                        pressed = self.get_button(mouse_pos)
                        if pressed is not None:
                            if pressed[0] == "lp_pmember_button":
                                self.lp_selected_ally = self.allies[self.party[pressed[1]]]
                            # Entity ID box selected.
                            elif pressed[0] == "bs_id_box":
                                # Ally selected.
                                if pressed[1] >= 3 and pressed[1] < 6:
                                    clicked_ally = self.party[[1,0,2][pressed[1] - 3]]
                                    if clicked_ally is not None:
                                        if self.bs_selected_button is not None:
                                            self.bs_selected_action.use(self.bs_selected_ally, self.allies[clicked_ally])
                                        else:
                                            if self.allies[clicked_ally] not in self.has_acted:
                                                if self.allies[clicked_ally].can_battle():
                                                    self.bs_selected_ally = self.allies[clicked_ally]
                                                    self.update_bs_buttons(1)
                                # Enemy selected.
                                elif pressed[1] >= 0 and pressed[1] < 3:
                                    if self.enemies[pressed[1]] is not None:
                                        # If an attack/skill/item has been selected.
                                        if self.bs_selected_button is not None:
                                            self.bs_selected_action.use(self.bs_selected_ally, self.enemies[pressed[1]])
                            elif pressed[0] == "bs_button":
                                # Choose Attacks, Skills, Items, or Standby.
                                if self.bs_button_state == 1:
                                    # Go to attack menu.
                                    if pressed[1] == 0:
                                        self.update_bs_buttons(2)
                                    # Go to skills menu.
                                    elif pressed[1] == 1:
                                        self.update_bs_buttons(3)
                                    # Go to item menu.
                                    elif pressed[1] == 2:
                                        self.update_bs_buttons(4)
                                    # Standby
                                    else:
                                        print "Standby"
                                        self.has_acted.append(self.bs_selected_ally)
                                        self.update_bs_buttons()
                                # Choose between available Attacks.
                                elif self.bs_button_state == 2:
                                    if self.bs_selected_ally.attack_list[pressed[1]] is not None:
                                        self.bs_selected_action = self.bs_selected_ally.attack_list[pressed[1]]
                                        if self.bs_selected_action.target != []:
                                            self.bs_selected_button = pressed[1]
                                        else:
                                            self.bs_selected_action.use(self.bs_selected_ally)
                                # Choose between available Skills.
                                elif self.bs_button_state == 3:
                                    if self.bs_selected_ally.skill_list[pressed[1]] is not None:
                                        self.bs_selected_action = self.bs_selected_ally.skill_list[pressed[1]]
                                        # If skill requires target.
                                        if self.bs_selected_action.target != []:
                                            self.bs_selected_button = pressed[1]
                                        else:
                                            self.bs_selected_action.use(self.bs_selected_ally)
                                # Choose between available Items.
                                elif self.bs_button_state == 4:
                                    # Next/First page.
                                    if pressed[1] == 3:
                                        if self.bs_item_page * 3 + 4 > len(self.items):
                                            self.bs_item_page = 0
                                        else:
                                            self.bs_item_page += 1
                                        self.update_bs_buttons(4, self.bs_item_page)
                                    else:
                                        self.bs_selected_action = [1,0,2][pressed[1]] + 3 * self.bs_item_page
                                        if self.bs_selected_action < len(self.items):
                                            self.bs_selected_action = self.items[self.bs_selected_action]
                                            if self.bs_selected_action.target != []:
                                                self.bs_selected_button = pressed[1]
                                            else:
                                                self.bs_selected_action.use(self.bs_selected_ally)
                        else:
                            self.update_bs_buttons()
                    # On right click.
                    elif mouse_button == RMB:
                        # Nothing selected.
                        if self.bs_button_state == 0:
                            # Open Menu.
                            self.menu_open = True
                            ##self.enemy_turn()
                        # Just ally selected.
                        if self.bs_button_state == 1:
                            self.update_bs_buttons()
                        # Attacks, Skills, or Items.
                        elif self.bs_button_state >= 2 and self.bs_button_state <= 4:
                            # Action already selected.
                            if self.bs_selected_button is not None:
                                self.update_bs_buttons(self.bs_button_state)
                            # Action not yet selected.
                            elif self.bs_item_page > 0:
                                self.bs_item_page -= 1
                                self.update_bs_buttons(4, self.bs_item_page)
                            else:
                                self.update_bs_buttons(1)
                elif event.type == pygame.KEYDOWN:
                    if event.key == ESC:
                        self.menu_open = True

    def draw_story_screen(self):
        screen.blit(background, (0, 0))
        char_box = pygame.Rect((400, 0), wp(100,100))
        mf_img = minor_fiend.draw_image((400, 0), self.frame, size=wp(52, 100))
        self.draw_tb(minor_fiend, "Long, long ago, in a land far, far away...")
        #story = font.render("Long, long ago, in a land far, far away...", True, BLACK)
        #story_rect = story.get_rect(topleft=wp(settings.left_panel_x + 2, settings.top_panel_y + 4))
        #screen.blit(story, story_rect)

    def story_time(self):
        self.draw_story_screen()
        pygame.display.flip()

        if self.menu_open:
            self.draw_start_menu("What would you like to do?", settings.menu_options)
            self.menu_open = False

        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                mouse_button = event.button
                if mouse_button == LMB:
                    pressed = self.get_button(mouse_pos)
                    ##if pressed is not None:
                        ##if pressed[0] == "lp_pmember_button":
                            ##self.lp_selected_ally = self.allies[self.party[pressed[1]]]
                elif mouse_button == RMB:
                    self.menu_open = True
            elif event.type == pygame.KEYDOWN:
                if event.key == ESC:
                    self.menu_open = True

    def save(self):
        items = self.items
        for x in xrange(len(items)):
            if items[x] is not None:
                items[x] = [items[x].name, items[x].num]
        save_data = [self.allies, self.party, items]##, settings]
        save_file = open(save_dir("{}.csav".format(self.player_team)), "w")
        pickle.dump(save_data, save_file)
        save_file.close()

    def add_item(self, item):
        if type(item) is list:
            for x in item:
                if type(x) is list:
                    self.add_item(Item(x[0], x[1]))
                elif type(x) is Item:
                    self.add_item(x)
                else: # if type(x) is str:
                    self.add_item(Item(x))
        elif type(item) is str:
            self.add_item(Item(x))
        else:
            items = self.items
            for x in xrange(len(items)):
                if items[x].name == item.name:
                    items[x].num += item.num
                    return True
            self.items.append(item)
        return True

    def update_profile_list(self):
        global saved_games
        saved_games = {}
        for file_name in os.listdir(save_dir()):
            if file_name.endswith(".csav"):
                saved_games[file_name.strip("csav").strip(".")] = save_dir(file_name)

    def title_screen(self):
        self.title_button, self.title_button_text, self.title_button_text_rect, self.title_button_state = [], [], [], 0
        #(pygame.Rect(wp(40, 50), wp(20, 10)))

        screen.blit(background, (0, 0))
        
        for x in xrange(4):
            index_button = pygame.Surface(wp(20, 9), pygame.SRCALPHA, 32)
            index_button.fill((settings.menu_rgba))
            self.title_button.append(index_button.get_rect(topleft=wp(40,50 + x * 10)))
            screen.blit(index_button, self.title_button[x])
            pygame.draw.rect(screen, BLACK, self.title_button[x], 2)
            index_button_text = font.render(settings.title_buttons[x], True, WHITE)
            index_button_text_rect = index_button_text.get_rect(center=self.title_button[x].center)
            screen.blit(index_button_text, index_button_text_rect)

        title = font.render("This will be the title screen.", True, BLACK)
        title_rect = title.get_rect(topleft=wp(settings.left_panel_x + 2, settings.top_panel_y + 4))
        screen.blit(title, title_rect)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                mouse_button = event.button
                if mouse_button == LMB:
                    pressed = self.get_button(mouse_pos)
                    if pressed is not None:
                        if pressed[0] == "title_button":
                            #print settings.title_buttons[pressed[1]] #TEMP
                            if pressed[1] == 0:
                                self.on_title = False
                                self.in_world = True
                                self.draw_sprites.append(Sprite("Minor Fiend", (64,0)))
                                self.draw_sprites.append(Sprite("Florwil", (128,0)))
                                self.draw_sprites.append(Sprite("Hornet", (192, 0)))
                                self.draw_sprites.append(Sprite("Green Bush", (512,256)))
                                self.draw_sprites.append(Sprite("Green Bush", (576,256)))
                                for x in blocks:
                                    Blocks[x] = Block(x)
                            if pressed[1] == 1:
                                self.quit()
                elif mouse_button == RMB:
                    self.on_title = False
                    self.is_story_time = True
            elif event.type == pygame.KEYDOWN:
                if event.key == ESC:
                    self.on_title = False
                    self.is_story_time = True

    def update_bs_buttons(self, state=0, item_page=0):
        if state == 0:
            self.bs_selected_ally = None
        self.bs_selected_button =   None
        self.bs_selected_action =   None
        self.bs_button_state = state
        self.bs_item_page = item_page
        self.bs_button_text = self.get_button_text(state, item_page)

    def draw_tb(self, char=None, text=None, mod=None):
        tb = pygame.Surface(wp(100, settings.tb_y), pygame.SRCALPHA, 32)
        tb.fill((settings.menu_rgba))
        tb_rect = tb.get_rect(midbottom=wp(50,100))
        screen.blit(tb, tb_rect)
        pygame.draw.line(screen, 0, wp(0, 100 - settings.tb_y), wp(100, 100 - settings.tb_y), 2)
        text_color = WHITE
        if mod is not None:
            if mod.has_key("color"):
                text_color = mod["color"]
        if text is not None:
            tb_text = font.render(text, True, text_color)
            tb_text_rect = tb_text.get_rect(topleft=wp(3, 100 - (settings.tb_y - 5)))
            screen.blit(tb_text, tb_text_rect)
        if char is not None:
            tb_char = font.render(char.name, True, text_color)
            tb_char_rect = tb_char.get_rect(topleft=wp(1, 100 - (settings.tb_y - 1)))
            screen.blit(tb_char, tb_char_rect)

    def draw_world(self):
        #screen.blit(background, (0,0))
        for x in xrange(len(self.grid)):
            for y in xrange(len(self.grid[x])):
                if x >= len(self.cur_map.blocks):
                    Blocks[self.cur_map.border].draw(self.grid[x][y], self.frame)
                elif y >= len(self.cur_map.blocks[x]):
                    Blocks[self.cur_map.border].draw(self.grid[x][y], self.frame)
                else:
                    Blocks[self.cur_map.blocks[x][y]].draw(self.grid[x][y], self.frame)
        if len(self.keys["move"]):
            if SHIFT in self.keys["other"]:
                debug.player_sprite.set_act("Run", table[self.keys["move"][0]])
            else:
                debug.player_sprite.set_act("Walk", table[self.keys["move"][0]])
        else:
            debug.player_sprite.set_act("Idle")
        for x in xrange(len(self.draw_sprites)):
            self.draw_sprites[x].draw()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key in move_keys:
                    self.keys["move"].append(event.key)
                    if SHIFT in self.keys["other"]:
                        debug.player_sprite.time_held["{}_{}".format("Run", table[event.key])] = 10
                    else:
                        debug.player_sprite.time_held["{}_{}".format("Walk", table[event.key])] = 10
                else:
                    self.keys["other"].append(event.key)
                    if event.key == SEMICOLON:
                        if debug.enable:
                            debug.change_player_sprite()
            elif event.type == pygame.KEYUP:
                if event.key in move_keys:
                    if event.key in self.keys["move"]:
                        self.keys["move"].remove(event.key)
                    debug.player_sprite.reset_idle()
                else:
                    if event.key in self.keys["other"]:
                        self.keys["other"].remove(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == RMB:
                    self.in_world = False
                    self.is_story_time = True
        if SHIFT in self.keys["other"]:
            STEP = 4
        else:
            STEP = 2
        for i in xrange(len(self.keys["move"])):
            if self.keys["move"][i] == W:
                new_pos = (debug.player_sprite.pos[0], debug.player_sprite.pos[1] - (STEP / (i + 1)))
            if self.keys["move"][i] == A:
                new_pos = (debug.player_sprite.pos[0] - (STEP / (i + 1)), debug.player_sprite.pos[1])
            if self.keys["move"][i] == S:
                new_pos = (debug.player_sprite.pos[0], debug.player_sprite.pos[1] + (STEP / (i + 1)))
            if self.keys["move"][i] == D:
                new_pos = (debug.player_sprite.pos[0] + (STEP / (i + 1)), debug.player_sprite.pos[1])
            if Blocks[self.cur_map.blocks[new_pos[0] / 32][new_pos[1] / 32]].can_enter(debug.player_sprite.movement):
                debug.player_sprite.pos = new_pos

class Entity(object):
    def __init__(self, name, lvl=1, team="none", player=False):
        object.__init__(self)
        self.original_name = name
        self.name = name
        self.lvl = 1
        self.is_fainted = False
        self.team = team
        self.is_player = player
        if self.is_player:
            self.original_name = "Player"
            name = "Player"

        if name not in entities:
            print "{} is not a valid entity name!".format(name)
            name = "default"

        self.default_expression = entities[name]["expressions"][0]
        on = self.original_name
        if not self.original_name in entity_images:
            entity_images[on] = {"base":[]}
            img_path = lambda filename="": img_dir("{}\\{}".format(on, filename))
            img_ext = enitity_img_extension
            if os.path.exists(img_path("base\\")):
                index = 1
                while True:
                    file = img_path("base\\{}{}".format(index, img_ext))
                    if os.path.isfile(file):
                        entity_images[on]["base"].append(pygame.image.load(file).convert_alpha())
                    else:
                        break
                    index += 1
            else:
                entity_images[on]["base"].append(pygame.image.load(img_dir("default.png")).convert_alpha())

            for img_type in entities[name]["expressions"] + settings.entity_img_types:
                entity_images[on][img_type] = []
                file = img_path("{}{}".format(img_type, img_ext))
                if os.path.isfile(file):
                    entity_images[on][img_type] = pygame.image.load(file).convert_alpha()
                else:
                    if entity_images[on].has_key(self.default_expression):
                        entity_images[on][img_type] = entity_images[on][self.default_expression]
                    else:
                        print "Error: No image for {} {}".format(self.original_name, img_type)
                        entity_images[on][img_type] = pygame.image.load(img_dir("default.png")).convert_alpha()

        # Load these.
        self.base_health =       entities[name]["base_health"]
        self.base_energy =       entities[name]["base_energy"]
        self.base_strength =     entities[name]["base_strength"]
        self.base_defense =      entities[name]["base_defense"]
        self.base_dexterity =    entities[name]["base_dexterity"]
        self.base_agility =      entities[name]["base_agility"]
        self.base_intelligence = entities[name]["base_intelligence"]
        self.element =           entities[name]["element"]
        self.attack_list =       [None, None, None, None]
        self.skill_list =        [None, None, None, None]

        for x in xrange(4):
            #print entities[name]["attacks"], self.attack_list, x #TEMP
            if len(entities[name]["attacks"]) > x:
                self.attack_list[x] = Attack(entities[name]["attacks"][x])
            if len(entities[name]["skills"]) > x:
                self.skill_list[x] = Skill(entities[name]["skills"][x])

        self.max_health =   int(self.base_health)
        self.max_energy =   int(self.base_energy)
        self.strength =     int(self.base_strength)
        self.defense =      int(self.base_defense)
        self.dexterity =    int(self.base_dexterity)
        self.agility =      int(self.base_agility)
        self.intelligence = int(self.base_intelligence)
        self.lvl_xp = [0, 4 * self.lvl] # [Current XP toward level up, XP needed for level up]

        for x in xrange(lvl - 1):
            self.level_up()

        self.health = self.max_health
        self.energy = self.max_energy

        self.str_mod, self.def_mod, self.dex_mod, self.agi_mod, self.int_mod = ["+", 0], ["+", 0], ["+", 0], ["+", 0], ["+", 0]

    def level_up(self):
        self.lvl += 1
        self.max_health += random.randint(1, 3)
        self.max_energy += random.randint(1, 2)
        stat_plus = [0, 1, 1, 2]
        self.strength +=     stat_plus[random.randint(0, 3)]
        self.defense +=      stat_plus[random.randint(0, 3)]
        self.dexterity +=    stat_plus[random.randint(0, 3)]
        self.agility +=      stat_plus[random.randint(0, 3)]
        self.intelligence += stat_plus[random.randint(0, 3)]
        self.lvl_xp = [0, 4 * self.lvl]
        self.xp = 4 * ((self.lvl - 1) * self.lvl) / 2
        self.health = self.max_health
        self.energy = self.max_energy

    def draw_image(self, pos=(0,0), frame=0, size="bs", expression=None):
        img_frame = lambda frame, wait, num_imgs: int(frame / (wait / float(num_imgs))) % num_imgs
        frame = img_frame(frame, settings.entity_animation_wait, len(entity_images[self.original_name]["base"]))
        if size == "bs":
            size = (settings.bs_id_box_x, settings.bs_id_box_y)
        if expression is None: # For in battle.
            if self.is_fainted:
                expression = "fainted"
            else:
                expression = "full_health"
        img_rect = pygame.Rect(pos, (1,1))
        screen.blit(pygame.transform.smoothscale(entity_images[self.original_name]["base"][frame], size), img_rect)
        try:
            screen.blit(pygame.transform.smoothscale(entity_images[self.original_name][expression], size), img_rect)
            return entity_images[self.original_name]["base"]
        except TypeError:
            e = "No Image for '{} {}'".format(self.name, expression)
            if not errors.count(e):
                errors.append(e)
                print e # Add Error function.
            return pygame.Surface(size)

    def take_damage(self, amount):
        amount = int(round(amount))
        if amount > 0:
            print "{} took {} damage!".format(self.name, amount)
        elif amount < 0:
            if self.health <= 0:
                print "{} was revived!".format(self.name)
                self.is_fainted = False
            print "{} regained {} health!".format(self.name, -amount)
        else:
            print "Not even a scratch!"
        self.health -= amount
        self.health = int(round(self.health))
        if self.health <= 0:
            self.health = 0
            self.faint()
        elif self.health > self.max_health:
            self.health = self.max_health

    def use_energy(self, amount):
        amount = int(math.ceil(amount))
        if self.energy - amount < 0:
            return False
        elif self.energy - amount > self.max_energy:
            self.energy = self.max_energy
        else:
            self.energy -= amount
        return True

    def buff(self, type, amount):
        rand_factor = [-0.2, -0.1, 0.0, 0.1, 0.2][random.randint(0, 4)]
        amount += rand_factor
        amount = int(math.ceil(amount))
        if amount >= 0:
            mod_type = "+"
        else:
            mod_type = "-"
        if   type == "strength":
            self.str_mod[0] = mod_type
            self.str_mod[1] += amount
        elif type == "defense":
            self.def_mod[0] = mod_type
            self.def_mod[1] += amount
        elif type == "dexterity":
            self.dex_mod[0] = mod_type
            self.dex_mod[1] += amount
        elif type == "agility":
            self.agi_mod[0] = mod_type
            self.agi_mod[1] += amount
        elif type == "intelligence":
            self.int_mod[0] = mod_type
            self.int_mod[1] += amount

    def faint(self):
        print "{} has fainted!".format(self.name)
        self.is_fainted = True
        game.can_player_battle()
        game.can_enemy_battle()

    def can_battle(self):
        if self.health > 0:
            return True
        else:
            if not self.is_fainted:
                self.faint()
            return False

    def get_stat(self, stat, for_display=False):
        stat = str(stat).lower()
        mod = ["+", 0]

        if   stat == "str" or stat == "strength":
            stat = self.strength
            mod = self.str_mod
        elif stat == "def" or stat == "defense":
            stat = self.defense
            mod = self.def_mod
        elif stat == "dex" or stat == "dexterity":
            stat = self.dexterity
            mod = self.dex_mod
        elif stat == "agi" or stat == "agility":
            stat = self.strength
            mod = self.agi_mod
        elif stat == "int" or stat == "intelligence":
            stat = self.strength
            mod = self.int_mod

        if for_display:
            mod_str = ""
            if mod[1] != 0:
                mod_str = "{}{}".format(mod[0], abs(mod[1]))
            stat = "{}{}".format(stat, mod_str)
        else:
            stat += mod[1]

        return stat

class Attack(object):
    def __init__(self, name, lvl=1):
        object.__init__(self)
        self.name = name
        self.lvl = int(lvl)

        if name not in attacks:
            print "{} is not a valid attack name!".format(name)
            name = "default"

        self.damage =             attacks[name]["damage"]
        self.accuracy =           attacks[name]["accuracy"]        # For a 25% chance, enter 25. Definite hit is -1.
        self.type =               attacks[name]["type"]            # "Str", "Int", "Elm"
        self.element =            attacks[name]["element"]         # "N/A", "Psn", "Drk"
        self.energy_cost =        attacks[name]["energy_cost"]
        self.target =             attacks[name]["target"]          # Always "enemy" or "all_enemies"?

    def use(self, user, target=None):
        if user.can_battle():
            if self.can_target(user, target):
                if user.use_energy(self.energy_cost):
                    msg, end = "{} used {}{}!", ""
                    if target is not None and user is not target:
                        end = " on {}".format(target.name)
                    print msg.format(user.name, self.name, end)
                    if self.accuracy == -1:
                        hit = True
                    else:
                        hit = random.randint(1, 100) < self.accuracy
                    if hit:
                        if self.type == "physical":
                            dmg = (self.damage + user.strength) / 3.0
                            # Remove dmg for target def.
                        elif self.type == "mental":
                            dmg = (self.damage + user.intelligence) / 3.0
                            # Remove dmg for target int.
                        elif self.type == "elemental":
                            dmg = (self.damage + user.strength) / 3.0
                            # Modify dmg based on attack, user, and target elm.
                            # Remove dmg for target def.
                        rand_factor = [0.8, 0.9, 1.0, 1.1, 1.2][random.randint(0, 4)]
                        dmg *= rand_factor
                        target.take_damage(dmg)
                    else:
                        print "The attack missed!"
                    game.has_acted.append(user)
                    game.update_bs_buttons()
                else:
                    print "{} doesn't have enough energy!".format(user.name)
            else:
                print "Unable to target {} with {}!".format(target.name, self.name)
        else:
            print "{} is unable to battle!".format(user.name)

    def can_target(self, user, target):
        if len(self.target) == 0: # If target is not required.
            return True
        for potential_target in self.target:
            if potential_target == "enemy":
                if user.team != target.team:
                    if not target.is_fainted:
                        return True
            elif potential_target == "ally":
                if user.team == target.team:
                    if not target.is_fainted:
                        if target is not user:
                            return True
            elif potential_target == "fainted_enemy":
                if user.team != target.team:
                    if target.is_fainted:
                        return True
            elif potential_target == "fainted_ally":
                if user.team == target.team:
                    if target.is_fainted:
                        return True
            elif potential_target == "self":
                if user is target:
                    return True
            elif potential_target == "all_allies" or potential_target == "all_enemies" or potential_target == "all":
                return True
        return False

class Skill(object):
    def __init__(self, name, lvl=1):
        object.__init__(self)
        self.name = name
        self.lvl = int(lvl)

        if name not in skills:
            print "{} is not a valid skill name!".format(name)
            name = "default"

        self.energy_cost =        skills[name]["energy_cost"]      # Skills cannot increase self.energy, only items can.
        self.target =             skills[name]["target"]           # "ally", "all_allies", "fainted_ally", "enemy", "all_enemies", "fainted_enemy", "self", or empty. # Maybe "closest_enemy" and "furthest_enemy"?
        self.effect =             skills[name]["effect"]           # See Notes.txt:Effects
        del name, lvl

    def use(self, user, target=None):
        if user.can_battle():
            if self.can_target(user, target):
                if user.use_energy(self.energy_cost):
                    msg, end = "{} used {}{}!", ""
                    if target is not None and user is not target:
                        end = " on {}".format(target.name)
                    print msg.format(user.name, self.name, end)
                    #print self.effect, len(self.effect)
                    for x in self.effect:
                        if   x[0] == "health_mod":
                            target.take_damage(x[1] * -1)
                        elif x[0] == "energy_mod":
                            target.use_energy(x[1] * -1)
                        elif x[0] == "stat_mod":
                            target.buff(x[1], x[2])
                        elif x[0] == "escape":
                            game.escape(x[1], self)
                    game.has_acted.append(user)
                    game.update_bs_buttons()
                    del msg, end, x
                else:
                    print "{} doesn't have enough energy!".format(user.name)
            else:
                print "Unable to target {} with {}!".format(target.name, self.name)
        else:
            print "{} is unable to battle!".format(user.name)
        del user, target

    def can_target(self, user, target):
        if len(self.target) == 0: # If target is not required.
            return True
        for potential_target in self.target:
            if potential_target == "enemy":
                if user.team != target.team:
                    if not target.is_fainted:
                        return True
            elif potential_target == "ally":
                if user.team == target.team:
                    if not target.is_fainted:
                        if target is not user:
                            return True
            elif potential_target == "fainted_enemy":
                if user.team != target.team:
                    if target.is_fainted:
                        return True
            elif potential_target == "fainted_ally":
                if user.team == target.team:
                    if target.is_fainted:
                        return True
            elif potential_target == "self":
                if user is target:
                    return True
            elif potential_target == "all_allies" or potential_target == "all_enemies" or potential_target == "all":
                return True
        return False

class Item(object):
    def __init__(self, name, num=1):
        object.__init__(self)
        self.name = name
        self.num =  num

        if name not in items:
            print "{} is not a valid item name!".format(name)
            name = "default"

        self.target =             items[name]["target"]
        self.effect =             items[name]["effect"]
        del name, num

    def use(self, user, target=None):
        if user.can_battle():
            if self.can_target(user, target):
                msg, end = "{} used {}{}!", ""
                if target is not None and user is not target:
                    end = " on {}".format(target.name)
                print msg.format(user.name, self.name, end)
                for x in self.effect:
                    if   x[0] == "health_mod":
                        target.take_damage(x[1] * -1)
                    elif x[0] == "energy_mod":
                        target.use_energy(x[1] * -1)
                    elif x[0] == "stat_mod":
                        target.buff(x[1], x[2])
                    elif x[0] == "escape":
                        game.escape(x[1], self)
                self.num -= 1
                if self.num <= 0:
                    game.items.pop(game.items.index(self))
                    if len(game.items) < 2:
                        game.items.append(None)
                game.has_acted.append(user)
                game.update_bs_buttons()
                del msg, end, x
            else:
                print "Unable to target {} with {}!".format(target.name, self.name)
        else:
            print "{} is unable to battle!".format(user.name)
        del user, target

    def can_target(self, user, target):
        if len(self.target) == 0: # If target is not required.
            return True
        for potential_target in self.target:
            if potential_target == "enemy":
                if user.team != target.team:
                    if not target.is_fainted:
                        return True
            elif potential_target == "ally":
                if user.team == target.team:
                    if not target.is_fainted:
                        if target is not user:
                            return True
            elif potential_target == "fainted_enemy":
                if user.team != target.team:
                    if target.is_fainted:
                        return True
            elif potential_target == "fainted_ally":
                if user.team == target.team:
                    if target.is_fainted:
                        return True
            elif potential_target == "self":
                if user is target:
                    return True
            elif potential_target == "all_allies" or potential_target == "all_enemies" or potential_target == "all":
                return True
        return False

class Sprite(object):
    def __init__(self, name, position=(0,0)):
        self.name = name
        self.group = "Idle_Down"
        self.frame = 0
        self.time_held = {}
        self.pos = position
        
        if name not in sprites:
            print "{} is not a valid sprite name!".format(name)
            name = "default"

        self.type =     sprites[name]["type"]
        self.width =    sprites[name]["width"]
        self.height =   sprites[name]["height"]
        self.default =  sprites[name]["default"]
        self.movement = sprites[name]["movement"]
        
        for x in sprite_acts:
            for y in sprite_dirs:
                self.time_held["{}_{}".format(x, y)] = 0
        self.action = self.default.split("_")[0]
        self.facing = self.default.split("_")[1]
        self.size = (self.width, self.height)
        if self.type == "World":
            self.path = lambda filename: img_dir("World\\sprites\\{}\\{}".format(self.name, filename))
        else:
            self.path = lambda filename: img_dir("{}\\sprites\\{}".format(self.name, filename))
        del name, position

        if not self.name in loaded_sprites:
            loaded_sprites[self.name] = {}
            for action in sprite_acts:
                img_pack = self.path("{}{}".format(action, sprite_img_extension))
                #print img_pack
                if os.path.isfile(img_pack):
                    for direction in sprite_dirs:
                        tmp = pygame.image.load(img_pack)
                        y = sprite_dirs.index(direction) * self.size[1]
                        folder = "{}_{}".format(action, direction)
                        loaded_sprites[self.name][folder] = []
                        for x in xrange(0, tmp.get_width(), self.size[0]):
                            tmp2 = load_sprite(img_pack, (x, y), (self.size[0], self.size[1]))
                            loaded_sprites[self.name][folder].append(tmp2)
                    del tmp, tmp2, y
                else:
                    for direction in sprite_dirs:
                        folder = "{}_{}".format(action, direction)
                        #print self.path(folder)
                        loaded_sprites[self.name][folder] = []
                        if os.path.isdir(self.path(folder)):
                            x = 0
                            while True:
                                file = self.path("{}\\{}{}".format(folder, x, sprite_img_extension))
                                #print file
                                if os.path.isfile(file):
                                    loaded_sprites[self.name][folder].append(load_sprite(file))
                                else:
                                    break
                                x += 1
                            del file, x
                        if not len(loaded_sprites[self.name][folder]):
                            loaded_sprites[self.name][folder].append(load_sprite(img_dir("sprite_error.png")))
            del action, img_pack, direction, folder

    def animate(self):
        self.group = "{}_{}".format(self.action, self.facing)
        self.frame = (self.time_held[self.group] / (40 / len(loaded_sprites[self.name][self.group]))) % len(loaded_sprites[self.name][self.group])
        self.time_held[self.group] += 1

    def get_rect(self):
        return pygame.Rect(self.pos, loaded_sprites[self.name][self.group][0].get_size())

    def reset_idle(self):
        for x in sprite_dirs:
            self.time_held["Idle_{}".format(x)] = 0

    def draw(self, pos=None):
        self.animate()
        if pos is not None:
            self.pos = pos
        screen.blit(loaded_sprites[self.name][self.group][self.frame], self.pos)
        del pos
    
    def set_act(self, action=None, facing=None):
        if action is not None:
            self.action = action
        if facing is not None:
            self.facing = facing

class Location(object):
    def __init__(self, name):
        self.name = name
        
        if name not in locations:
            print "{} is not a valid location name!".format(name)
            name = "default"

        tmp_blocks =   locations[name]["blocks"]
        self.border =  locations[name]["border"]
        self.sprites = locations[name]["sprites"]
        self.items =   locations[name]["items"]
        
        self.blocks = []
        for y in xrange(len(tmp_blocks)):
            tmp_blocks[y] = tmp_blocks[y].split(" ")
            for x in xrange(len(tmp_blocks[y])):
                if x >= len(self.blocks):
                    self.blocks.append([])
                self.blocks[x].append(int(tmp_blocks[y][x]))

class Block(object):
    def __init__(self, id):
        if id not in blocks:
            print "{} is not a valid block id!".format(id)
            id = 0
        self.id = id

        self.name =     blocks[self.id]["name"]
        self.type =     blocks[self.id]["type"]
        self.movement = blocks[self.id]["movement"]

        img = img_dir("World\\{}\\{}.jpg".format(self.type, self.name.replace(" ", "_")))

        if not self.id in loaded_blocks:
            loaded_blocks[self.id] = []
            if os.path.isfile(img):
                img = pygame.image.load(img)
                for x in xrange(0, img.get_width(), BLOCK):
                    tmp = pygame.Surface((BLOCK, BLOCK))
                    tmp.blit(img, (0,0), (x, 0, BLOCK, BLOCK))
                    loaded_blocks[self.id].append(tmp)

    def draw(self, pos, frame):
        frame = (frame / (40 / len(loaded_blocks[self.id]))) % len(loaded_blocks[self.id])
        screen.blit(loaded_blocks[self.id][frame], pos)
        del pos, frame

    def can_enter(self, sprite_movements):
        for x in sprite_movements:
            if x in self.movement:
                return True
        return False

### ADD THESE TO ENTITY ###
def draw_health(entity, health_rect, draw_text=True, rect_outline=2, color=HPRED):
    health_per = float(entity.health) / entity.max_health
    if health_per > 1:
        health_per = 1
    if health_per > 0:
        health = pygame.Rect((health_rect.x + rect_outline, health_rect.y + rect_outline), ((health_rect.width - (rect_outline + 1)) * health_per, health_rect.height - (rect_outline + 1)))
        pygame.draw.rect(screen, color, health)
        del health
    if draw_text:
        health_text = font.render("{}/{}".format(int(entity.health), int(entity.max_health)), True, BLACK)
        health_text_rect = health_text.get_rect()
        health_text_rect.center = health_rect.center
        screen.blit(health_text, health_text_rect)
        del health_text, health_text_rect
    del health_per, health_rect, draw_text, rect_outline, color

def draw_energy(entity, energy_rect, draw_text=True, rect_outline=2, color=MPBLU):
    energy_per = float(entity.energy) / entity.max_energy
    if energy_per > 1:
        energy_per = 1
    if energy_per > 0:
        energy = pygame.Rect((energy_rect.x + rect_outline, energy_rect.y + rect_outline), ((energy_rect.width - (rect_outline + 1)) * energy_per, energy_rect.height - (rect_outline + 1)))
        pygame.draw.rect(screen, color, energy)
        del energy
    if draw_text:
        energy_text = font.render("{}/{}".format(int(entity.energy), int(entity.max_energy)), True, BLACK)
        energy_text_rect = energy_text.get_rect()
        energy_text_rect.center = energy_rect.center
        screen.blit(energy_text, energy_text_rect)
        del energy_text, energy_text_rect
    del energy_per, energy_rect, draw_text, rect_outline, color

def draw_xp(entity, xp_rect, draw_text=True, rect_outline=2, color=XPGRN):
    xp_per = float(entity.lvl_xp[0]) / entity.lvl_xp[1]
    if xp_per > 1:
        xp_per = 1
    if xp_per > 0:
        xp = pygame.Rect((xp_rect.x + rect_outline, xp_rect.y + rect_outline), ((xp_rect.width - (rect_outline + 1)) * xp_per, xp_rect.height - (rect_outline + 1)))
        pygame.draw.rect(screen, color, xp)
        del xp
    if draw_text:
        xp_text = font.render("{}/{}".format(int(entity.lvl_xp[0]), int(entity.lvl_xp[1])), True, BLACK)
        xp_text_rect = xp_text.get_rect()
        xp_text_rect.center = xp_rect.center
        screen.blit(xp_text, xp_text_rect)
        del xp_text, xp_text_rect
    del xp_per, xp_rect, draw_text, rect_outline, color
###########################

def load_sprite(file, topleft=(0,0), size=(64,64)):
    tmp = pygame.image.load(file).convert()
    img = pygame.Surface(size)
    img.blit(tmp, (0,0), topleft+size)
    del tmp, topleft, size, file
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

def start_game(data=None):
    global game
    if data is not None:
        game = Crimson(data[0][0])
        game.allies = data[0]
        game.party = data[1]
        game.items = []
        game.add_item(data[2])
        game.menu_open = False
        for ally in game.allies:
            x = Entity(ally.original_name) # Ensures all necessary images are loaded.
        del x
    else:
        player_entity = Entity(settings.player_name, player=True)
        game = Crimson(player_entity)
        game.add_item([Item("Health Potion"), Item("Energy Potion"), Item("Smoke Bomb"), Item("Small Stone", 3), Item("Energy Drain"), Item("Revival Token")])
        global minor_fiend
        minor_fiend = Entity("Minor Fiend")##, 10)
        florwil = Entity("Florwil")
        game.add_ally(minor_fiend)
        game.add_ally(florwil)
        ##hornet = Entity("Hornet")
        ##game.add_ally(hornet)
        game.running = True
    del data

start_game()
debug.change_player_sprite("Player")
#debug.change_player_sprite("Blue Water")
game.draw_sprites.append(debug.player_sprite)
print "Done"
while game.running:
    game.frame += 1
    CLOCK.tick(40)
    #if game.frame % 10 == 0:
        #print CLOCK.get_fps()
    if game.on_title:
        game.title_screen()
    elif game.in_battle:
        game.battle()
    elif game.is_story_time:
        game.story_time()
    elif game.in_world:
        game.draw_world()
game.quit()
