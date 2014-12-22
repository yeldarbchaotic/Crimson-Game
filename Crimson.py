import pygame
from pygame.locals import *
import math
import random
import json
import os
import copy
import pickle

# Define Constants
BLACK = (0,0,0)
WHITE = (255,255,255)
LMB = 1
RMB = 3

class Settings(object):
    def __init__(self):
        object.__init__(self)
        self.player_name = "Player One"
        self.bs_draw_enemy_xp = False
        self.top_panel_y = 15
        self.left_panel_x = 15
        self.tr_logo_y = 50
        self.lp_bar_y = 7
        self.lp_pm_box_x = self.left_panel_x / 6.0
        self.font_size_x = 1.85
        self.bs_id_box_x = 12.5
        self.bs_id_box_y = 25
        self.bs_id_box_marg = [1, 1]
        self.bs_button_x = 12
        self.bs_button_y = 7
        self.bs_bar_y = 1
        self.win_size = [1024, 512]
        self.popup_offset_px = [8, 16]
        self.menu_options = ["Continue", "Save", "Load", "Options", "Quit"]
        self.battle_menu_options = ["End Turn", "Options", "Return to Game", "Quit"] # "Quicksave", "Quickload", "Auto-Battle"?
        self.menu_options += ["Battle"] #### DEBUG ####
        self.entity_img_types = ["full_health", "half_health", "low_health", "fainted", "sleeping"]
        self.entity_animation_wait = 15

    def change_player_name(self, new_name):
        new_name = str(new_name)
        if new_name != "":
            self.player_name = new_name

settings = Settings()
settings.change_player_name(raw_input("Enter your name: "))

print "Loading...",

# Creates the pygame window.
pygame.init()
screen = pygame.display.set_mode(settings.win_size)#, FULLSCREEN)
pygame.display.set_caption("Crimson - The Game v0.0.1")
#pygame.display.toggle_fullscreen()

# Loads the images and prepares the screen.
game_dir = os.path.dirname(os.path.realpath(__file__)) + "\\"
img_dir = game_dir + "images\\"
save_dir = game_dir + "save\\"
logo =       pygame.image.load(img_dir + "Logo.png")
background = pygame.transform.smoothscale(pygame.image.load(img_dir + "Background.png"), settings.win_size)

# For maintaining aspect ratio when scaling.
x_y = lambda img, x: int((x / float(img.get_width())) * img.get_height())
y_x = lambda img, y: int((y / float(img.get_height())) * img.get_width())

# Stands for window percent.
def wp(x=None, y=None):
    """Returns the number of pixels, given a set of percentages."""
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

#############################################################################{
################################# SETTINGS! #################################
#############################################################################

settings.bs_draw_enemy_xp = True

# Define the values to be used when drawing the UI (%).

top_right_logo = pygame.transform.smoothscale(logo, (y_x(logo, wp(y=settings.tr_logo_y)), wp(y=settings.tr_logo_y)))
font = pygame.font.SysFont("Arial", wp(x=settings.font_size_x))
entity_images = {}
saved_games = {}
for file_name in os.listdir(save_dir):
    if file_name.endswith(".csav"):
        saved_games[file_name.strip("csav").strip(".")] = save_dir + file_name

#############################################################################
#############################################################################
#############################################################################}

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
        self.animating = False ########## USE THIS!!!
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
        self.bs_center_y = (self.bs_id_box[4].top + self.bs_id_box[1].bottom) / 2.0                                      # Pixels!
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

    def add_enemy(self, enemy):
        enemy.team = "wild"
        for x in [1,0,2]:
            if self.enemies[x] is None:
                self.enemies[x] = enemy
                return True
        return False

    def quit(self):
        self.running = False
        self.in_battle = False
        pygame.quit()
        exit()

    def escape(self, chance, user=None):
        rand_chance = random.randint(1, 100)
        if rand_chance <= chance:
            self.end_battle("escape")
        else:
            print "Couldn't Escape!"

    def enemy_turn(self):
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
            attack.use(enemy, target)
        if self.can_player_battle() and self.can_enemy_battle():
            self.player_turn()

    def end_battle(self, result="", special_text=""):

        if result == "win":
            print "\nYou have defeated the enemy!"
        elif result == "lose":
            print "\nYou have been defeated!"
            self.quit()
        elif result == "escape":
            print "Got Away Safely!"
        elif result == "enemy_escape":
            print "The enemy ran away!"
        elif result == "special":
            print special_text
        else:
            print "Error! Result is '" + str(result) + "', which is not a supported type. Try 'win', 'lose', 'escape', 'enemy_escape', or 'special'."
        self.in_battle = False
        self.enemies = [None, None, None]
        for ally in self.allies:
            ally.energy = ally.max_energy
            ally.str_mod = ["+", 0]
            ally.def_mod = ["+", 0]
            ally.dex_mod = ["+", 0]
            ally.agi_mod = ["+", 0]
            ally.int_mod = ["+", 0]
        self.bs_selected_button = None
        self.bs_selected_ally =   None
        self.bs_selected_action = None
        self.bs_item_page = 0
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
        print "Turn #" + str(self.turn[0])
        self.has_acted = []
        for x in self.party:
            if x is not None:
                if self.allies[x].can_battle():
                    self.allies[x].use_energy(self.allies[x].get_stat("agi") / -2)
                else:
                    self.has_acted.append(self.allies[x]) # So that allies can't battle the same turn they are revived.
        self.can_player_battle()
        self.can_enemy_battle()

    def draw_screen_basics(self):
        screen.blit(background, (0, 0))
        left_panel_x_pix = wp(x=settings.left_panel_x)
        pygame.draw.line(screen, 0, (left_panel_x_pix, 0), (left_panel_x_pix, wp(y=100)), 2)
        pygame.draw.line(screen, 0, wp(settings.left_panel_x, settings.top_panel_y), (wp(x=100) - top_right_logo.get_width(), wp(y=settings.top_panel_y)), 2)
        pygame.draw.line(screen, 0, (0, left_panel_x_pix), (left_panel_x_pix, left_panel_x_pix), 2)
        self.top_right_logo_rect = top_right_logo.get_rect()
        self.top_right_logo_rect.topright = wp(x=100) + 1, wp(y=0) - 2
        screen.blit(top_right_logo, self.top_right_logo_rect)
        pygame.draw.rect(screen, 0, self.top_right_logo_rect, 2)

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
                    lp_pmember_name = font.render(self.allies[self.party[member]].name + " (" + str(self.allies[self.party[member]].lvl) + ")", True, BLACK)
                    lp_pmember_name_rect = lp_pmember_name.get_rect()
                    lp_pmember_name_rect.midbottom = (wp(settings.left_panel_x / 2.0, 89))
                    screen.blit(lp_pmember_name, lp_pmember_name_rect)
                pygame.draw.rect(screen, BLACK, self.lp_pmember_button[member], 2)

        ally = self.lp_selected_ally

        lp_image = ally.get_image(self.frame)
        lp_image = pygame.transform.smoothscale(lp_image, (wp(x=settings.left_panel_x), wp(x=settings.left_panel_x)))
        screen.blit(lp_image, (0, 0))

        lp_name = font.render(ally.name, True, BLACK)
        lp_name_rect = lp_name.get_rect()
        lp_name_rect.midtop = (wp(x=settings.left_panel_x / 2 + 0.5), lp_image.get_height() + 5)
        screen.blit(lp_name, lp_name_rect)

        lp_lvl = font.render("Lvl: " + str(ally.lvl), True, BLACK)
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
        lp_stats.append(font.render("Str: " + ally.get_stat("str", True), True, BLACK))
        lp_stats.append(font.render("Def: " + ally.get_stat("def", True), True, BLACK))
        lp_stats.append(font.render("Dex: " + ally.get_stat("dex", True), True, BLACK))
        lp_stats.append(font.render("Agi: " + ally.get_stat("agi", True), True, BLACK))
        lp_stats.append(font.render("Int: " + ally.get_stat("int", True), True, BLACK))
        lp_stats.append(font.render("Elm: " + str(ally.element), True, BLACK))
        for stat in lp_stats:
            stat_rect = stat.get_rect()
            if lp_stat_num % 2 == 0:
                stat_rect.midleft = wp(x=1.5), lp_image.get_height() + wp(y=(lp_stat_num / 2) * (settings.font_size_x * 2) + settings.lp_bar_y * 5)
            else:
                stat_rect.midleft = wp(x=settings.left_panel_x - 7), lp_image.get_height() + wp(y=(lp_stat_num / 2) * (settings.font_size_x * 2) + settings.lp_bar_y * 5)
            screen.blit(stat, stat_rect)
            lp_stat_num += 1

    def draw_battle_screen(self):
        self.draw_screen_basics()
        self.draw_left_panel()

        index = 0
        for enemy in self.enemies: # Draws enemy IDs
            pygame.draw.rect(screen, 0, self.bs_id_box[index], 2)
            if enemy is not None:
                screen.blit(enemy.get_image(self.frame), self.bs_id_box[index])
                pygame.draw.rect(screen, 0, self.bs_id_box[index], 2)
                self.bs_id_health_rect[index].bottom = self.bs_id_box[index].top + 1
                self.bs_id_energy_rect[index].bottom = self.bs_id_health_rect[index].top + 1
                pygame.draw.rect(screen, 0, self.bs_id_health_rect[index], 1)
                pygame.draw.rect(screen, 0, self.bs_id_energy_rect[index], 1)
                draw_health(enemy, self.bs_id_health_rect[index], False, 1)
                draw_energy(enemy, self.bs_id_energy_rect[index], False, 1)
                self.bs_id_name[index] = font.render(enemy.name + " Lvl." + str(enemy.lvl), True, BLACK)
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
                screen.blit(member.get_image(self.frame), self.bs_id_box[index])
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
                self.bs_id_name[index] = font.render(member.name + " Lvl." + str(member.lvl), True, BLACK)
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
                        bs_pop_stats.append(font.render("HP: " + str(enemy.health) + "/" +  str(enemy.max_health), True, WHITE))
                        bs_pop_stats.append(font.render("EP: " + str(enemy.energy) + "/" +  str(enemy.max_energy), True, WHITE))
                        bs_pop_stats.append(font.render("Str: " + enemy.get_stat("str", True), True, WHITE))
                        bs_pop_stats.append(font.render("Def: " + enemy.get_stat("def", True), True, WHITE))
                        bs_pop_stats.append(font.render("Dex: " + enemy.get_stat("dex", True), True, WHITE))
                        bs_pop_stats.append(font.render("Agi: " + enemy.get_stat("agi", True), True, WHITE))
                        bs_pop_stats.append(font.render("Int: " + enemy.get_stat("int", True), True, WHITE))
                        bs_pop_stats.append(font.render("Elm: " + str(enemy.element), True, WHITE))
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
                        enemy_info_popup.fill((25,25,25,200))
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
        else:
            check_str = ["bs_button", "bs_id_box",    "lp_pmember_button"]
            check =     [ self.bs_button,   self.bs_id_box, self.lp_pmember_button ]
        for index in xrange(len(check)):
            x = self.is_clicked(check[index], mouse_pos)
            if x is not None:
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
                            self.bs_button_text.append(self.items[[1,0,2][x]].name + " x " + str(self.items[[1,0,2][x]].num))
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
                            self.bs_button_text[[1,0,2][x]] = self.items[item_page * 3 + x].name + " x " + str(self.items[x + 3 * item_page].num)
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
            menu_popup.fill((25,25,25,200))
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
            pygame.draw.rect(screen, 0, menu_popup_rect, 2)
            screen.blit(menu_popup, menu_popup_rect)
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
                                    save_data = [self.allies, self.party, self.items]#, settings]
                                    save_file = open(save_dir + str(self.player_team) + ".csav", "w")
                                    pickle.dump(save_data, save_file)
                                    save_file.close()
                                    menu_open = False
                            elif pressed == "Load" or pressed == "Load Game":
                                self.draw_start_menu("Load:", saved_games.keys() + ["Back"])
                            elif pressed in saved_games:
                                menu_open = False
                                self.menu_open = False
                                load_game(pressed)
                            elif pressed == "Battle" or pressed == "Begin Battle":
                                enemy_minor_fiend = Entity("Minor Fiend", 2)
                                game.add_enemy(enemy_minor_fiend)
                                enemy_hornet = Entity("Hornet", 25)
                                game.add_enemy(enemy_hornet)
                                #enemy_hornet2 = Entity("Hornet", 2)
                                #game.add_enemy(enemy_hornet2)
                                self.in_battle = True
                                menu_open = False
                                self.player_turn()
                    elif mouse_button == RMB:
                        pressed = "Right Click"
                        menu_open = False
                elif menu_event.type == pygame.KEYDOWN:
                    if menu_event.key == pygame.K_ESCAPE:
                        pressed = "Escape"
                        menu_open = False
                elif menu_event.type == pygame.QUIT:
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
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    mouse_button = event.button # Left(1), middle(2), or right(3) mouse button, scrollup(4) or scrolldown(5).
                    if mouse_button == 1:
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
                                            if self.bs_selected_action.can_target(self.bs_selected_ally, self.allies[clicked_ally]):
                                                self.bs_selected_action.use(self.bs_selected_ally, self.allies[clicked_ally])
                                                self.bs_selected_button = None
                                                self.bs_selected_action = None
                                                self.bs_selected_ally =   None
                                                self.bs_button_text =     self.get_button_text(0)
                                                self.bs_button_state =    0
                                        else:
                                            if self.allies[clicked_ally] not in self.has_acted:
                                                if self.allies[clicked_ally].can_battle():
                                                    self.bs_selected_ally = self.allies[clicked_ally]
                                                    self.bs_button_text = self.get_button_text(1)
                                                    self.bs_button_state = 1
                                                    self.bs_selected_button = None
                                                    self.bs_selected_action = None
                                # Enemy selected.
                                elif pressed[1] >= 0 and pressed[1] < 3:
                                    if self.enemies[pressed[1]] is not None:
                                        # If an attack/skill/item has been selected.
                                        if self.bs_selected_button is not None:
                                            if self.bs_selected_action.can_target(self.bs_selected_ally, self.enemies[pressed[1]]):
                                                self.bs_selected_action.use(self.bs_selected_ally, self.enemies[pressed[1]])
                                                self.bs_selected_button = None
                                                self.bs_selected_action = None
                                                self.bs_selected_ally =   None
                                                self.bs_button_text =     self.get_button_text(0)
                                                self.bs_button_state =    0
                            elif pressed[0] == "bs_button":
                                # Choose Attacks, Skills, Items, or Standby.
                                if self.bs_button_state == 1:
                                    # Go to attack menu.
                                    if pressed[1] == 0:
                                        self.bs_button_state = 2
                                        self.bs_button_text =  self.get_button_text(2)
                                    # Go to skills menu.
                                    elif pressed[1] == 1:
                                        self.bs_button_state = 3
                                        self.bs_button_text =  self.get_button_text(3)
                                    # Go to item menu.
                                    elif pressed[1] == 2:
                                        self.bs_button_state = 4
                                        self.bs_button_text  = self.get_button_text(4)
                                        self.bs_item_page = 0
                                    # Standby
                                    else:
                                        print "Standby"
                                        self.bs_button_state = 0
                                        self.bs_selected_ally = None
                                        self.bs_button_text = self.get_button_text(0)
                                        self.has_acted.append(self.bs_selected_ally)
                                # Choose between available Attacks.
                                elif self.bs_button_state == 2:
                                    if self.bs_selected_ally.attack_list[pressed[1]] is not None:
                                        self.bs_selected_action = self.bs_selected_ally.attack_list[pressed[1]]
                                        if self.bs_selected_action.target is not None:
                                            self.bs_selected_button = pressed[1]
                                        else:
                                            if self.bs_selected_action.can_target(self.bs_selected_ally, None):
                                                self.bs_selected_action.use(self.bs_selected_ally)
                                                self.bs_selected_action = None
                                                self.bs_selected_button = None
                                                self.bs_selected_ally =   None
                                                self.bs_button_text =     self.get_button_text(0)
                                                self.bs_button_state =    0
                                # Choose between available Skills.
                                elif self.bs_button_state == 3:
                                    if self.bs_selected_ally.skill_list[pressed[1]] is not None:
                                        self.bs_selected_action = self.bs_selected_ally.skill_list[pressed[1]]
                                        # If skill requires target.
                                        if self.bs_selected_action.target is not None:
                                            self.bs_selected_button = pressed[1]
                                        else:
                                            if self.bs_selected_action.can_target(self.bs_selected_ally, None):
                                                self.bs_selected_action.use(self.bs_selected_ally)
                                                self.bs_selected_action = None
                                                self.bs_selected_button = None
                                                self.bs_selected_ally =   None
                                                self.bs_button_text =     self.get_button_text(0)
                                                self.bs_button_state =    0
                                # Choose between available Items.
                                elif self.bs_button_state == 4:
                                    # Next/First page.
                                    self.bs_selected_button = None
                                    self.bs_selected_action = None
                                    if pressed[1] == 3:
                                        if self.bs_item_page * 3 + 4 > len(self.items):
                                            self.bs_item_page = 0
                                        else:
                                            self.bs_item_page += 1
                                        self.bs_button_text = self.get_button_text(4, self.bs_item_page)
                                    else:
                                        self.bs_selected_action = [1,0,2][pressed[1]] + 3 * self.bs_item_page
                                        if self.bs_selected_action < len(self.items):
                                            self.bs_selected_action = self.items[self.bs_selected_action]
                                            if self.bs_selected_action.target is not None:
                                                self.bs_selected_button = pressed[1]
                                            else:
                                                if self.bs_selected_action.can_target(self.bs_selected_ally, None):
                                                    self.bs_selected_action.use(self.bs_selected_ally)
                                                    self.bs_selected_action = None
                                                    self.bs_selected_button = None
                                                    self.bs_selected_ally =   None
                                                    self.bs_button_text =     self.get_button_text(0)
                                                    self.bs_button_state =    0
                        else:
                            self.bs_button_state =    0
                            self.bs_selected_ally =   None
                            self.bs_button_text =     self.get_button_text(0)
                            self.bs_selected_button = None
                            self.bs_selected_action = None
                    # On right click.
                    elif mouse_button == 3:
                        # Nothing selected.
                        if self.bs_button_state == 0:
                            # Open Menu.
                            self.menu_open = True
                            #self.enemy_turn()
                        # Just ally selected.
                        if self.bs_button_state == 1:
                            self.bs_selected_ally = None
                            self.bs_button_text = self.get_button_text(0)
                            self.bs_button_state = 0
                        # Attacks, Skills, or Items.
                        elif self.bs_button_state == 2 or self.bs_button_state == 3 or self.bs_button_state == 4:
                            # Action already selected.
                            if self.bs_selected_button is not None:
                                self.bs_selected_button = None
                                self.bs_selected_action = None
                            # Action not yet selected.
                            elif self.bs_item_page > 0:
                                self.bs_item_page -= 1
                                self.bs_button_text = self.get_button_text(4, self.bs_item_page)
                            else:
                                self.bs_button_state = 1
                                self.bs_button_text =  self.get_button_text(1)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.menu_open = True

    def draw_story_screen(self):
        self.draw_screen_basics()
        self.draw_left_panel()
        story = font.render("Long, long ago, in a land far, far away...", True, BLACK)
        story_rect = story.get_rect(topleft=wp(settings.left_panel_x + 2, settings.top_panel_y + 4))
        screen.blit(story, story_rect)

    def story_time(self):
        self.draw_story_screen()
        pygame.display.flip()

        if self.menu_open:
            self.draw_start_menu("What would you like to do?", settings.menu_options)
            self.menu_open = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                mouse_button = event.button # Left(1), middle(2), or right(3) mouse button, scrollup(4) or scrolldown(5).
                if mouse_button == 1:
                    pressed = self.get_button(mouse_pos)
                    if pressed is not None:
                        if pressed[0] == "lp_pmember_button":
                            self.lp_selected_ally = self.allies[self.party[pressed[1]]]
                elif mouse_button == 3:
                    self.menu_open = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu_open = True

class Entity(object):
    def __init__(self, name, lvl=1, team="none"):
        object.__init__(self)
        self.original_name = name
        self.name = name
        self.lvl = 1
        self.is_fainted = False
        self.team = team

        json_entities = open(game_dir + "entities.json")
        entities = json.load(json_entities)

        if name not in entities:
            name = "default"

        if not self.original_name in entity_images:
            entity_images[self.original_name] = {}
            img_path = img_dir + self.original_name + "\\"
            img_ext = entities[name]["image_extension"]
            if os.path.exists(img_path):
                for img_type in settings.entity_img_types:
                    entity_images[self.original_name][img_type] = []
                    path = img_path + img_type + "\\"
                    if os.path.exists(path):
                        num, cont = 1, True
                        while cont:
                            file = path + str(num) + img_ext
                            if os.path.isfile(file):
                                entity_images[self.original_name][img_type].append(pygame.image.load(file))
                                entity_images[self.original_name][img_type][num-1] = pygame.transform.smoothscale(entity_images[self.original_name][img_type][num-1], wp(settings.bs_id_box_x, settings.bs_id_box_y))
                            else:
                                cont = False
                            num += 1
                    elif img_type != "full_health":
                        entity_images[self.original_name][img_type] = entity_images[self.original_name]["full_health"]
                    else:
                        entity_images[self.original_name][img_type].append(pygame.image.load(img_dir + "default.png"))
                        entity_images[self.original_name][img_type][0] = pygame.transform.smoothscale(entity_images[self.original_name][img_type][0], wp(settings.bs_id_box_x, settings.bs_id_box_y))
            elif os.path.isfile(img_dir + self.original_name + ".png"):
                file = pygame.image.load(img_dir + self.original_name + ".png")
                for img_type in settings.entity_img_types:
                    if img_type != "full_health":
                        entity_images[self.original_name][img_type] = entity_images[self.original_name]["full_health"]
                    else:
                        entity_images[self.original_name][img_type] = [pygame.transform.smoothscale(file, wp(settings.bs_id_box_x, settings.bs_id_box_y))]
            else:
                for img_type in settings.entity_img_types:
                    print img_type
                    entity_images[self.original_name][img_type] = [pygame.image.load(img_dir + "default.png")]
                    entity_images[self.original_name][img_type][0] = pygame.transform.smoothscale(entity_images[self.original_name][img_type][0], wp(settings.bs_id_box_x, settings.bs_id_box_y))

        # Load these.
        self.base_health =       entities[name]["base_health"]
        self.base_energy =       entities[name]["base_energy"]
        self.base_strength =     entities[name]["base_strength"]
        self.base_defense =      entities[name]["base_defense"]
        self.base_dexterity =    entities[name]["base_dexterity"]
        self.base_agility =      entities[name]["base_agility"]
        self.base_intelligence = entities[name]["base_intelligence"]
        self.element =           entities[name]["element"]
        self.attack_list =       entities[name]["attacks"]
        self.skill_list =        entities[name]["skills"]

        for x in xrange(4):
            if self.attack_list[x] is not None:
                self.attack_list[x] = Attack(self.attack_list[x])
            if self.skill_list[x] is not None:
                self.skill_list[x] = Skill(self.skill_list[x])

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

    def get_image(self, frame):
        img_frame = lambda frame, wait, num_imgs: int(frame / (wait / float(num_imgs))) % num_imgs
        if self.is_fainted:
            status = "fainted"
        else:
            status = "full_health"
        return entity_images[self.original_name][status][img_frame(frame, settings.entity_animation_wait, len(entity_images[self.original_name][status]))]

    def take_damage(self, amount):
        rand_factor = [-0.2, -0.1, 0.0, 0.1, 0.2][random.randint(0, 4)] # Move this to attack function.
        amount += amount * rand_factor
        amount = int(round(amount))
        if amount > 0:
            print self.name, "took", amount, "damage!"
        elif amount < 0:
            if self.health <= 0:
                print self.name, "was revived!"
            print self.name, "regained", -amount, "health!"
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
        print self.name, "has fainted!"
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
            stat = str(stat)
            if mod[1] != 0:
                stat += mod[0] + str(abs(mod[1]))
        else:
            stat += mod[1]

        return stat

class Attack(object):
    def __init__(self, name, lvl=1):
        object.__init__(self)
        self.name = name
        self.lvl = int(lvl)

        json_attacks = open(game_dir + "attacks.json")
        attacks = json.load(json_attacks)

        if name not in attacks:
            name = "default"

        self.damage =             attacks[name]["damage"]
        self.accuracy =           attacks[name]["accuracy"]        # For a 25% chance, enter 25. Definite hit is -1.
        self.type =               attacks[name]["type"]            # "Str", "Int"
        self.element =            attacks[name]["element"]         # "N/A", "Psn", "Drk"
        self.energy_cost =        attacks[name]["energy_cost"]
        self.target =             attacks[name]["target"]          # Always "enemy" or "all_enemies"?
        self.can_target_self =    attacks[name]["can_target_self"] # Always False?
        self.can_target_fainted = attacks[name]["can_target_fainted"]

    def use(self, user, target=None):
        if user.can_battle():
            if user.use_energy(self.energy_cost):
                msg = user.name + " used " + self.name
                if target is not None and user is not target:
                    msg += " on " + target.name
                print msg + "!"
                if self.accuracy == -1:
                    hit = True
                else:
                    hit = random.randint(1, 100) < self.accuracy
                if hit:
                    target.take_damage(self.damage)
                else:
                    print "The attack missed!"
                game.has_acted.append(user)
            else:
                print user.name, "doesn't have enough energy!"
        else:
            print user.name, "is unable to battle!"

    def can_target(self, user, target):
        if self.target == "enemy":
            if user.team != target.team:
                if target.is_fainted:
                    if self.can_target_fainted:
                        return True
                else:
                    return True
        elif self.target == "ally":
            if user.team == target.team:
                if user is target:
                    if self.can_target_self:
                        return True
                elif target.is_fainted:
                    if self.can_target_fainted:
                        return True
                else:
                    return True
        elif self.target == "entity":
            if user is target:
                if self.can_target_self:
                    return True
            elif target.is_fainted:
                if self.can_target_fainted:
                    return True
            else:
                return True
        elif target is None:
            if self.target is None:
                return True
        elif self.target == "self":
            if user is target:
                return True
        elif self.target == "all_allies" or self.target == "all_enemies":
            return True
        return False

class Skill(object):
    def __init__(self, name, lvl=1):
        object.__init__(self)
        self.name = name
        self.lvl = int(lvl)

        json_skills = open(game_dir + "skills.json")
        skills = json.load(json_skills)

        if name not in skills:
            name = "default"

        self.energy_cost =        skills[name]["energy_cost"]      # Skills cannot increase self.energy, only items can.
        self.target =             skills[name]["target"]           # "ally", "all_allies", "enemy", "all_enemies", "self", "entity", or null. # Maybe "closest_enemy" and "furthest_enemy"?
        self.can_target_self =    skills[name]["can_target_self"]  # If this is True and target is "all_allies", self will also be included.
        self.effect =             skills[name]["effect"]           # See Notes.txt:Effects
        self.can_target_fainted = skills[name]["can_target_fainted"]

    def use(self, user, target=None):
        if user.can_battle():
            if user.use_energy(self.energy_cost):
                msg = user.name + " used " + self.name
                if target is not None and user is not target:
                    msg += " on " + target.name
                print msg + "!"
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
            else:
                print user.name, "doesn't have enough energy!"
        else:
            print user.name, "is unable to battle!"

    def can_target(self, user, target):
        if self.target == "enemy":
            if user.team != target.team:
                if target.is_fainted:
                    if self.can_target_fainted:
                        return True
                else:
                    return True
        elif self.target == "ally":
            if user.team == target.team:
                if user is target:
                    if self.can_target_self:
                        return True
                elif target.is_fainted:
                    if self.can_target_fainted:
                        return True
                else:
                    return True
        elif self.target == "entity":
            if user is target:
                if self.can_target_self:
                    return True
            elif target.is_fainted:
                if self.can_target_fainted:
                    return True
            else:
                return True
        elif target is None:
            if self.target is None:
                return True
        elif self.target == "self":
            if user is target:
                return True
        elif self.target == "all_allies" or self.target == "all_enemies":
            return True
        return False

class Item(object):
    def __init__(self, name, num=1):
        object.__init__(self)
        self.name = name
        self.num =  num

        json_items = open(game_dir + "items.json")
        items = json.load(json_items)

        if name not in items:
            name = "default"

        self.target =             items[name]["target"]
        self.effect =             items[name]["effect"]
        self.can_target_self =    items[name]["can_target_self"]
        self.can_target_fainted = items[name]["can_target_fainted"]

    def use(self, user, target=None):
        if user.can_battle():
            msg = user.name + " used " + self.name
            if target is not None and user is not target:
                msg += " on " + target.name
            print msg + "!"
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
        else:
            print user.name, "is unable to battle!"

    def can_target(self, user, target):
        if self.target == "enemy":
            if user.team != target.team:
                if target.is_fainted:
                    if self.can_target_fainted:
                        return True
                else:
                    return True
        elif self.target == "ally":
            if user.team == target.team:
                if user is target:
                    if self.can_target_self:
                        return True
                elif target.is_fainted:
                    if self.can_target_fainted:
                        return True
                else:
                    return True
        elif self.target == "entity":
            if user is target:
                if self.can_target_self:
                    return True
            elif target.is_fainted:
                if self.can_target_fainted:
                    return True
            else:
                return True
        elif target is None:
            if self.target is None:
                return True
        elif self.target == "self":
            if user is target:
                return True
        elif self.target == "all_allies" or self.target == "all_enemies":
            return True
        return False

### ADD THESE TO ENTITY ###
def draw_health(entity, health_rect, draw_text=True, rect_outline=2, color=(255,0,0)):
    health_per = float(entity.health) / entity.max_health
    if health_per > 1:
        health_per = 1
    if health_per > 0:
        health = pygame.Rect((health_rect.x + rect_outline, health_rect.y + rect_outline), ((health_rect.width - (rect_outline + 1)) * health_per, health_rect.height - (rect_outline + 1)))
        pygame.draw.rect(screen, color, health)
    if draw_text:
        health_text = font.render(str(int(entity.health)) + "/" + str(int(entity.max_health)), True, BLACK)
        health_text_rect = health_text.get_rect()
        health_text_rect.center = health_rect.center
        screen.blit(health_text, health_text_rect)

def draw_energy(entity, energy_rect, draw_text=True, rect_outline=2, color=(0,125,255)):
    energy_per = float(entity.energy) / entity.max_energy
    if energy_per > 1:
        energy_per = 1
    if energy_per > 0:
        energy = pygame.Rect((energy_rect.x + rect_outline, energy_rect.y + rect_outline), ((energy_rect.width - (rect_outline + 1)) * energy_per, energy_rect.height - (rect_outline + 1)))
        pygame.draw.rect(screen, color, energy)
    if draw_text:
        energy_text = font.render(str(int(entity.energy)) + "/" + str(int(entity.max_energy)), True, BLACK)
        energy_text_rect = energy_text.get_rect()
        energy_text_rect.center = energy_rect.center
        screen.blit(energy_text, energy_text_rect)

def draw_xp(entity, xp_rect, draw_text=True, rect_outline=2, color=(0,175,0)):
    xp_per = float(entity.lvl_xp[0]) / entity.lvl_xp[1]
    if xp_per > 1:
        xp_per = 1
    if xp_per > 0:
        xp = pygame.Rect((xp_rect.x + rect_outline, xp_rect.y + rect_outline), ((xp_rect.width - (rect_outline + 1)) * xp_per, xp_rect.height - (rect_outline + 1)))
        pygame.draw.rect(screen, color, xp)
    if draw_text:
        xp_text = font.render(str(int(entity.lvl_xp[0])) + "/" + str(int(entity.lvl_xp[1])), True, BLACK)
        xp_text_rect = xp_text.get_rect()
        xp_text_rect.center = xp_rect.center
        screen.blit(xp_text, xp_text_rect)
###########################

def start_game(data=None):
    global game
    if data is not None:
        game = Crimson(data[0][0])
        game.allies = data[0]
        game.party = data[1]
        game.items = data[2]
        game.menu_open = False
        for ally in game.allies:
            x = Entity(ally.original_name) # Ensures all necessary images are loaded.
    else:
        player = Entity(settings.player_name)
        game = Crimson(player)
        game.items = [Item("Health Potion"), Item("Energy Potion"), Item("Smoke Bomb"), Item("Small Stone", 3), Item("Energy Drain"), Item("Revival Token")] # game.add_item(self, item)
        minor_fiend = Entity("Minor Fiend", 10)
        game.add_ally(minor_fiend)
        #hornet = Entity("Hornet")
        #game.add_ally(hornet)
        game.running = True
        #game.in_battle = True

start_game()
print "Done"
while game.running:
    game.frame += 1
    if game.in_battle:
        game.battle()
    else:
        game.story_time()
game.quit()
