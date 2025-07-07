import sys
import pygame
from pygame.locals import *

FRAME_RATE = 60.0
SCREEN_SIZE = (800, 800)
TILE_SIZE = SCREEN_SIZE[0] / 4

def init_pygame():
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    pygame.font.init()

    success = True
    if not pygame.display.get_init:
        success = False
    if not pygame.font.get_init():
        success = False
    if not pygame.mixer.get_init():
        success = False
    return success

assert init_pygame()

game_screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('XOXO (Python)')
clock = pygame.time.Clock()

def handle_input(key_name):
    if(key_name == "Q"):
       sys.exit()

def update(screen, time):
    pygame.display.update()

def main():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                key_name = pygame.key.name(event.key)
                handle_input(key_name)

        milliseconds = clock.tick(FRAME_RATE)
        seconds = milliseconds / 1000.0
        update(game_screen, seconds)

        sleep_time = (1000.0 / FRAME_RATE) - milliseconds
        if sleep_time > 0.0:
            pygame.time.wait(int(sleep_time))
        else:
            pygame.time.wait(1)

main()
